import asyncio
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models import (
    Avatar, AvatarStatus, GenerationTask, TaskStatus, Photo,
    GenerationMethod, PhotoAngle
)
from app.schemas import (
    GenerateAvatarRequest, GenerateAvatarResponse, AvatarStatusResponse,
    FineTuneRequest, FineTuneResponse
)
from app.services.aliyun_service import aliyun_service, AliyunServiceError
from app.config import settings


class GenerationService:
    def __init__(self):
        self._background_tasks: Dict[str, asyncio.Task] = {}
        self._retry_delay = settings.RETRY_DELAY_SECONDS
        self._max_retries = settings.MAX_RETRY_COUNT
    
    def _generate_id(self, prefix: str) -> str:
        timestamp = int(time.time() * 1000)
        import random
        random_suffix = ''.join(random.choices('abcdef0123456789', k=6))
        return f"{prefix}_{timestamp}_{random_suffix}"
    
    def _calculate_next_retry(self, retry_count: int) -> datetime:
        delays = [60, 120, 300, 600]
        delay = delays[min(retry_count, len(delays) - 1)]
        return datetime.now() + timedelta(seconds=delay)
    
    async def create_avatar_generation(
        self,
        db: AsyncSession,
        request: GenerateAvatarRequest
    ) -> GenerateAvatarResponse:
        if not request.name or not request.relationship:
            raise ValueError("缺少必要参数: name 和 relationship 为必填项")
        
        if request.generation_method == "photo" and (not request.photos or len(request.photos) == 0):
            raise ValueError("照片生成方式需要提供照片数据")
        
        existing_stmt = (
            select(Avatar)
            .where(
                Avatar.name == request.name,
                Avatar.relationship == request.relationship,
                Avatar.deleted_at.is_(None)
            )
        )
        existing_result = await db.execute(existing_stmt)
        existing_avatar = existing_result.scalar_one_or_none()
        
        if existing_avatar:
            if existing_avatar.status in ["pending", "generating", "training", "retry_pending"]:
                raise ValueError(f"数字人 '{request.name}({request.relationship})' 正在生成中，请等待完成")
            elif existing_avatar.status == "active":
                raise ValueError(f"数字人 '{request.name}({request.relationship})' 已存在且已激活")
        
        avatar_id = self._generate_id("avatar")
        task_id = self._generate_id("task")
        
        avatar = Avatar(
            id=avatar_id,
            name=request.name,
            relationship=request.relationship,
            gender=request.gender,
            birth_year=request.birth_year,
            death_year=request.death_year,
            description=request.description,
            generation_method=request.generation_method,
            text_description=request.text_description.model_dump() if request.text_description else None,
            status=AvatarStatus.PENDING,
            progress=0
        )
        db.add(avatar)
        
        if request.photos and len(request.photos) > 0:
            for i, photo_data in enumerate(request.photos):
                photo = Photo(
                    id=self._generate_id("photo"),
                    avatar_id=avatar_id,
                    photo_data=photo_data,
                    sort_order=i
                )
                db.add(photo)
        
        task = GenerationTask(
            id=task_id,
            avatar_id=avatar_id,
            task_type="avatar_generation",
            status=TaskStatus.PENDING,
            progress=0,
            retry_count=0,
            max_retries=self._max_retries,
            request_payload=request.model_dump()
        )
        db.add(task)
        
        await db.commit()
        
        asyncio.create_task(self._start_generation_task(db, avatar_id, task_id))
        
        return GenerateAvatarResponse(
            taskId=task_id,
            avatarId=avatar_id,
            status="pending",
            message="数字人生成任务已创建"
        )
    
    async def _start_generation_task(
        self,
        db: AsyncSession,
        avatar_id: str,
        task_id: str
    ):
        task_key = f"{avatar_id}_{task_id}"
        
        if task_key in self._background_tasks:
            return
        
        async def run_task():
            try:
                await self._execute_generation(db, avatar_id, task_id)
            except Exception as e:
                print(f"生成任务执行错误: {e}")
            finally:
                self._background_tasks.pop(task_key, None)
        
        self._background_tasks[task_key] = asyncio.create_task(run_task())
    
    async def _execute_generation(
        self,
        db: AsyncSession,
        avatar_id: str,
        task_id: str
    ):
        stmt = (
            select(GenerationTask)
            .where(GenerationTask.id == task_id)
            .options(selectinload(GenerationTask.avatar))
        )
        result = await db.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            return
        
        avatar = task.avatar
        if not avatar:
            return
        
        task.status = TaskStatus.PROCESSING
        task.started_at = datetime.now()
        avatar.status = AvatarStatus.GENERATING
        avatar.progress = 5
        await db.commit()
        
        try:
            if avatar.generation_method == GenerationMethod.PHOTO:
                image_url, model_url = await self._generate_from_photos(db, avatar, task)
            else:
                image_url, model_url = await self._generate_from_text(db, avatar, task)
            
            avatar.avatar_url = image_url
            avatar.model_url = model_url or "/models/girl_speedsculpt.glb"
            avatar.status = AvatarStatus.ACTIVE
            avatar.progress = 100
            
            task.status = TaskStatus.COMPLETED
            task.progress = 100
            task.completed_at = datetime.now()
            
            await db.commit()
            
        except AliyunServiceError as e:
            await self._handle_generation_error(db, avatar, task, str(e))
        except Exception as e:
            await self._handle_generation_error(db, avatar, task, str(e))
    
    async def _generate_from_photos(
        self,
        db: AsyncSession,
        avatar: Avatar,
        task: GenerationTask
    ) -> tuple[Optional[str], Optional[str]]:
        avatar.progress = 10
        await db.commit()
        
        photo_stmt = select(Photo).where(Photo.avatar_id == avatar.id).order_by(Photo.sort_order)
        photo_result = await db.execute(photo_stmt)
        photos = photo_result.scalars().all()
        
        avatar.progress = 20
        await db.commit()
        
        if photos and len(photos) > 0:
            try:
                analysis = await aliyun_service.analyze_photos([p.photo_data for p in photos])
                
                for i, result in enumerate(analysis.analysis):
                    if i < len(photos):
                        try:
                            angle = PhotoAngle(result.detected_type)
                        except ValueError:
                            angle = PhotoAngle.FRONT
                        photos[i].detected_angle = angle
                        photos[i].confidence = result.confidence
                        photos[i].quality_score = result.quality_score
                        photos[i].features = result.features
                
                await db.commit()
            except Exception as e:
                print(f"照片分析警告: {e}")
        
        avatar.progress = 40
        await db.commit()
        
        description = avatar.description or f"{avatar.relationship} {avatar.name}"
        gender = avatar.gender
        
        prompt = await aliyun_service.generate_avatar_prompt(
            name=avatar.name,
            gender=gender,
            description=description,
            age_range="老年"
        )
        
        avatar.progress = 50
        await db.commit()
        
        try:
            external_task_id = await aliyun_service.create_image_generation_task(
                prompt=prompt,
                size="1024*1024"
            )
            
            task.external_task_id = external_task_id
            task.external_service = "aliyun_wanx"
            await db.commit()
            
            image_url = await self._poll_generation_status(external_task_id, avatar, task)
            
            if image_url:
                return image_url, None
            
        except AliyunServiceError as e:
            raise e
        
        return None, None
    
    async def _generate_from_text(
        self,
        db: AsyncSession,
        avatar: Avatar,
        task: GenerationTask
    ) -> tuple[Optional[str], Optional[str]]:
        avatar.progress = 20
        await db.commit()
        
        text_desc = avatar.text_description or {}
        overall = text_desc.get("overall", "")
        gender = avatar.gender
        
        description = overall if overall else avatar.description or f"{avatar.relationship} {avatar.name}"
        
        prompt = await aliyun_service.generate_avatar_prompt(
            name=avatar.name,
            gender=gender,
            description=description,
            age_range="老年"
        )
        
        avatar.progress = 40
        await db.commit()
        
        try:
            external_task_id = await aliyun_service.create_image_generation_task(
                prompt=prompt,
                size="1024*1024"
            )
            
            task.external_task_id = external_task_id
            task.external_service = "aliyun_wanx"
            await db.commit()
            
            image_url = await self._poll_generation_status(external_task_id, avatar, task)
            
            if image_url:
                return image_url, None
            
        except AliyunServiceError as e:
            raise e
        
        return None, None
    
    async def _poll_generation_status(
        self,
        external_task_id: str,
        avatar: Avatar,
        task: GenerationTask
    ) -> Optional[str]:
        max_polls = 60
        poll_interval = 5
        
        for i in range(max_polls):
            try:
                status, image_url = await aliyun_service.check_image_generation_status(external_task_id)
                
                progress = min(50 + int(i * 0.8), 95)
                avatar.progress = progress
                task.progress = progress
                
                if i % 5 == 0:
                    await task.session.commit() if hasattr(task, 'session') else None
                
                if status == "completed":
                    return image_url
                elif status == "failed":
                    raise AliyunServiceError("图像生成任务失败")
                
                await asyncio.sleep(poll_interval)
                
            except Exception as e:
                print(f"轮询状态错误: {e}")
                await asyncio.sleep(poll_interval)
        
        raise AliyunServiceError("图像生成超时")
    
    async def _handle_generation_error(
        self,
        db: AsyncSession,
        avatar: Avatar,
        task: GenerationTask,
        error_message: str
    ):
        task.last_error = error_message
        task.failed_at = datetime.now()
        task.retry_count += 1
        
        if task.retry_count < task.max_retries:
            task.status = TaskStatus.RETRY_PENDING
            avatar.status = AvatarStatus.RETRY_PENDING
            task.next_retry_at = self._calculate_next_retry(task.retry_count)
            
            print(f"生成任务失败，计划第 {task.retry_count + 1} 次重试: {task.next_retry_at}")
        else:
            task.status = TaskStatus.FAILED
            avatar.status = AvatarStatus.FAILED
            print(f"生成任务最终失败，已重试 {task.retry_count} 次: {error_message}")
        
        await db.commit()
    
    async def retry_failed_task(
        self,
        db: AsyncSession,
        avatar_id: str
    ) -> GenerateAvatarResponse:
        avatar_stmt = select(Avatar).where(Avatar.id == avatar_id)
        avatar_result = await db.execute(avatar_stmt)
        avatar = avatar_result.scalar_one_or_none()
        
        if not avatar:
            raise ValueError("数字人不存在")
        
        if avatar.status not in [AvatarStatus.FAILED, AvatarStatus.RETRY_PENDING]:
            raise ValueError("数字人状态不允许重试")
        
        task_stmt = (
            select(GenerationTask)
            .where(GenerationTask.avatar_id == avatar_id)
            .order_by(GenerationTask.created_at.desc())
        )
        task_result = await db.execute(task_stmt)
        task = task_result.scalar_one_or_none()
        
        if not task:
            raise ValueError("找不到相关生成任务")
        
        task.status = TaskStatus.PENDING
        task.retry_count = 0
        task.last_error = None
        task.failed_at = None
        task.next_retry_at = None
        
        avatar.status = AvatarStatus.PENDING
        avatar.progress = 0
        
        await db.commit()
        
        asyncio.create_task(self._start_generation_task(db, avatar_id, task.id))
        
        return GenerateAvatarResponse(
            taskId=task.id,
            avatarId=avatar_id,
            status="retrying",
            message="数字人生成任务已重新开始"
        )
    
    async def get_avatar_status(
        self,
        db: AsyncSession,
        avatar_id: str
    ) -> AvatarStatusResponse:
        stmt = select(Avatar).where(Avatar.id == avatar_id)
        result = await db.execute(stmt)
        avatar = result.scalar_one_or_none()
        
        if not avatar:
            raise ValueError("数字人不存在")
        
        estimated_remaining = 0
        if avatar.status in [AvatarStatus.GENERATING, AvatarStatus.TRAINING]:
            estimated_remaining = max(0, int((100 - avatar.progress) * 0.5))
        
        return AvatarStatusResponse(
            avatarId=avatar.id,
            status=avatar.status,
            progress=avatar.progress,
            generationMethod=avatar.generation_method,
            estimatedTimeRemaining=estimated_remaining
        )
    
    async def fine_tune_avatar(
        self,
        db: AsyncSession,
        avatar_id: str,
        request: FineTuneRequest
    ) -> FineTuneResponse:
        stmt = select(Avatar).where(Avatar.id == avatar_id)
        result = await db.execute(stmt)
        avatar = result.scalar_one_or_none()
        
        if not avatar:
            raise ValueError("数字人不存在")
        
        if avatar.status != AvatarStatus.ACTIVE:
            raise ValueError("只有已激活的数字人才能进行微调")
        
        avatar.fine_tune_adjustments = request.adjustments.model_dump(exclude_none=True)
        avatar.status = AvatarStatus.TRAINING
        avatar.progress = 0
        
        await db.commit()
        
        asyncio.create_task(self._simulate_fine_tune(db, avatar_id))
        
        return FineTuneResponse(
            success=True,
            avatarId=avatar_id,
            status="fine-tuning"
        )
    
    async def _simulate_fine_tune(self, db: AsyncSession, avatar_id: str):
        try:
            for progress in range(10, 101, 10):
                await asyncio.sleep(0.5)
                
                stmt = select(Avatar).where(Avatar.id == avatar_id)
                result = await db.execute(stmt)
                avatar = result.scalar_one_or_none()
                
                if avatar:
                    avatar.progress = progress
                    if progress == 100:
                        avatar.status = AvatarStatus.ACTIVE
                        avatar.fine_tuned_at = datetime.now()
                    await db.commit()
                    
        except Exception as e:
            print(f"微调任务错误: {e}")
    
    async def check_pending_retries(self, db: AsyncSession):
        now = datetime.now()
        
        stmt = (
            select(GenerationTask)
            .where(
                GenerationTask.status == TaskStatus.RETRY_PENDING,
                GenerationTask.next_retry_at <= now
            )
            .options(selectinload(GenerationTask.avatar))
        )
        
        result = await db.execute(stmt)
        tasks = result.scalars().all()
        
        for task in tasks:
            if task.avatar:
                print(f"自动重试任务: {task.id} (avatar: {task.avatar_id})")
                asyncio.create_task(self._start_generation_task(db, task.avatar_id, task.id))


generation_service = GenerationService()
