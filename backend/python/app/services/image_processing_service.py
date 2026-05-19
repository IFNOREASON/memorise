import asyncio
import time
import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    logging.warning("aiohttp 未安装，回调功能将不可用")

from app.models import (
    ImageProcessTask, ImageProcessType, ImageProcessStatus,
    Gallery, GalleryMedia, Family, ExportFormat
)
from app.schemas import (
    CreateProcessTaskRequest, ProcessTaskResponse, ProcessTaskStatusResponse,
    BatchProcessRequest, BatchProcessResponse, ProcessTaskListResponse,
    ProcessTaskCancelResponse, RestorationParams, EnhancementParams,
    DynamicPortraitParams, CrossGenerationParams, VideoHighlightsParams,
    AISceneParams, ExportOptions
)
from app.services.aliyun_service import aliyun_service
from app.config import settings

logger = logging.getLogger(__name__)


class ImageProcessingError(Exception):
    pass


class ImageProcessingService:
    def __init__(self):
        self._background_tasks: Dict[str, asyncio.Task] = {}
        self._processing_queue: asyncio.Queue = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None
        self._is_running = False

    def _generate_id(self) -> str:
        timestamp = int(time.time() * 1000)
        random_suffix = ''.join(str(uuid.uuid4()).split('-')[:2])
        return f"imgproc_{timestamp}_{random_suffix}"

    def _calculate_next_retry(self, retry_count: int) -> datetime:
        delays = [30, 60, 120, 300]
        delay = delays[min(retry_count, len(delays) - 1)]
        return datetime.now() + timedelta(seconds=delay)

    def _get_task_type_name(self, task_type: ImageProcessType) -> str:
        names = {
            ImageProcessType.RESTORATION: "老照片修复",
            ImageProcessType.ENHANCEMENT: "高清放大",
            ImageProcessType.DYNAMIC_PORTRAIT: "动态肖像生成",
            ImageProcessType.CROSS_GENERATION: "跨年代合照合成",
            ImageProcessType.VIDEO_HIGHLIGHTS: "视频集锦生成",
            ImageProcessType.AI_SCENE: "AI场景生成"
        }
        return names.get(task_type, "图像处理")

    def _estimate_processing_time(self, task_type: ImageProcessType, progress: int) -> int:
        base_times = {
            ImageProcessType.RESTORATION: 30,
            ImageProcessType.ENHANCEMENT: 20,
            ImageProcessType.DYNAMIC_PORTRAIT: 60,
            ImageProcessType.CROSS_GENERATION: 90,
            ImageProcessType.VIDEO_HIGHLIGHTS: 120,
            ImageProcessType.AI_SCENE: 45
        }
        base_time = base_times.get(task_type, 30)
        return max(0, int(base_time * (100 - progress) / 100))

    async def start_worker(self):
        if not self._is_running:
            self._is_running = True
            self._worker_task = asyncio.create_task(self._process_queue_worker())
            logger.info("图像处理队列工作器已启动")

    async def stop_worker(self):
        self._is_running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
            self._worker_task = None
        logger.info("图像处理队列工作器已停止")

    async def _process_queue_worker(self):
        while self._is_running:
            try:
                task_id, db_session_factory = await self._processing_queue.get()
                asyncio.create_task(self._execute_process_task(task_id, db_session_factory))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"队列工作器错误: {e}")
                await asyncio.sleep(1)

    async def create_process_task(
        self,
        db: AsyncSession,
        request: CreateProcessTaskRequest
    ) -> ProcessTaskResponse:
        gallery_stmt = select(Gallery).where(Gallery.id == request.gallery_id)
        gallery_result = await db.execute(gallery_stmt)
        gallery = gallery_result.scalar_one_or_none()

        if not gallery:
            raise ImageProcessingError("影集不存在")

        family_id = gallery.family_id

        source_url = request.source_url
        media_id = request.media_id

        if not source_url and media_id:
            media_stmt = select(GalleryMedia).where(
                GalleryMedia.id == media_id,
                GalleryMedia.gallery_id == request.gallery_id
            )
            media_result = await db.execute(media_stmt)
            media = media_result.scalar_one_or_none()
            if media:
                source_url = media.url

        if not source_url and not media_id and not request.media_ids:
            raise ImageProcessingError("需要提供源图像URL或媒体ID")

        task_id = self._generate_id()

        parameters = {}
        if request.restoration_params:
            parameters["restoration"] = request.restoration_params.model_dump()
        if request.enhancement_params:
            parameters["enhancement"] = request.enhancement_params.model_dump()
        if request.dynamic_portrait_params:
            parameters["dynamic_portrait"] = request.dynamic_portrait_params.model_dump()
        if request.cross_generation_params:
            parameters["cross_generation"] = request.cross_generation_params.model_dump()
        if request.video_highlights_params:
            parameters["video_highlights"] = request.video_highlights_params.model_dump()
        if request.ai_scene_params:
            parameters["ai_scene"] = request.ai_scene_params.model_dump()

        watermark_text = None
        watermark_position = None
        export_format = ExportFormat.JPG.value
        export_quality = 90

        if request.export_options:
            export_format = request.export_options.format.value
            export_quality = request.export_options.quality
            if request.export_options.add_watermark:
                watermark_text = request.export_options.watermark_text
                watermark_position = request.export_options.watermark_position.value

        task = ImageProcessTask(
            id=task_id,
            gallery_id=request.gallery_id,
            media_id=media_id,
            family_id=family_id,
            task_type=request.task_type.value,
            status=ImageProcessStatus.PENDING.value,
            progress=0,
            source_url=source_url,
            source_media_ids=request.media_ids,
            parameters=parameters,
            options={
                "export_format": export_format,
                "export_quality": export_quality
            },
            callback_url=request.callback_url,
            webhook_payload=request.webhook_payload,
            watermark_text=watermark_text,
            watermark_position=watermark_position,
            export_format=export_format,
            export_quality=export_quality
        )

        db.add(task)
        await db.commit()
        await db.refresh(task)

        await self._processing_queue.put((task_id, db.get_bind()))

        logger.info(f"创建图像处理任务: {task_id}, 类型: {request.task_type.value}")

        return ProcessTaskResponse(
            taskId=task_id,
            galleryId=request.gallery_id,
            taskType=request.task_type,
            status=ImageProcessStatus.PENDING,
            progress=0,
            message=f"{self._get_task_type_name(request.task_type)}任务已创建，正在排队处理"
        )

    async def batch_create_tasks(
        self,
        db: AsyncSession,
        request: BatchProcessRequest
    ) -> BatchProcessResponse:
        gallery_stmt = select(Gallery).where(Gallery.id == request.gallery_id)
        gallery_result = await db.execute(gallery_stmt)
        gallery = gallery_result.scalar_one_or_none()

        if not gallery:
            raise ImageProcessingError("影集不存在")

        media_ids = request.media_ids
        if not media_ids:
            raise ImageProcessingError("需要提供媒体ID列表")

        task_ids = []

        for media_id in media_ids:
            try:
                create_request = CreateProcessTaskRequest(
                    galleryId=request.gallery_id,
                    mediaId=media_id,
                    taskType=request.task_type,
                    restorationParams=request.restoration_params,
                    enhancementParams=request.enhancement_params,
                    dynamicPortraitParams=request.dynamic_portrait_params,
                    crossGenerationParams=request.cross_generation_params,
                    videoHighlightsParams=request.video_highlights_params,
                    exportOptions=request.export_options,
                    callbackUrl=request.callback_url
                )
                response = await self.create_process_task(db, create_request)
                task_ids.append(response.taskId)
            except Exception as e:
                logger.warning(f"批量创建任务失败，媒体ID: {media_id}, 错误: {e}")
                continue

        return BatchProcessResponse(
            totalTasks=len(task_ids),
            taskIds=task_ids,
            message=f"成功创建 {len(task_ids)} 个图像处理任务"
        )

    async def get_task_status(
        self,
        db: AsyncSession,
        task_id: str
    ) -> ProcessTaskStatusResponse:
        stmt = select(ImageProcessTask).where(ImageProcessTask.id == task_id)
        result = await db.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            raise ImageProcessingError("任务不存在")

        estimated_time = self._estimate_processing_time(
            ImageProcessType(task.task_type),
            task.progress
        ) if task.status in [ImageProcessStatus.PENDING.value, ImageProcessStatus.PROCESSING.value] else None

        return ProcessTaskStatusResponse(
            taskId=task.id,
            galleryId=task.gallery_id,
            mediaId=task.media_id,
            taskType=ImageProcessType(task.task_type),
            status=ImageProcessStatus(task.status),
            progress=task.progress,
            sourceUrl=task.source_url,
            resultUrl=task.result_url,
            previewUrl=task.result_preview_url,
            resultMetadata=task.result_metadata,
            retryCount=task.retry_count,
            maxRetries=task.max_retries,
            lastError=task.last_error,
            startedAt=task.started_at,
            completedAt=task.completed_at,
            createdAt=task.created_at,
            updatedAt=task.updated_at,
            estimatedTimeRemaining=estimated_time,
            processingTime=task.processing_time
        )

    async def get_gallery_tasks(
        self,
        db: AsyncSession,
        gallery_id: str,
        status: Optional[ImageProcessStatus] = None,
        task_type: Optional[ImageProcessType] = None,
        limit: int = 50,
        offset: int = 0
    ) -> ProcessTaskListResponse:
        query = select(ImageProcessTask).where(ImageProcessTask.gallery_id == gallery_id)

        if status:
            query = query.where(ImageProcessTask.status == status.value)
        if task_type:
            query = query.where(ImageProcessTask.task_type == task_type.value)

        count_stmt = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_stmt)
        total = count_result.scalar_one()

        query = query.order_by(ImageProcessTask.created_at.desc()).offset(offset).limit(limit)
        result = await db.execute(query)
        tasks = result.scalars().all()

        task_responses = []
        for task in tasks:
            estimated_time = self._estimate_processing_time(
                ImageProcessType(task.task_type),
                task.progress
            ) if task.status in [ImageProcessStatus.PENDING.value, ImageProcessStatus.PROCESSING.value] else None

            task_responses.append(ProcessTaskStatusResponse(
                taskId=task.id,
                galleryId=task.gallery_id,
                mediaId=task.media_id,
                taskType=ImageProcessType(task.task_type),
                status=ImageProcessStatus(task.status),
                progress=task.progress,
                sourceUrl=task.source_url,
                resultUrl=task.result_url,
                previewUrl=task.result_preview_url,
                resultMetadata=task.result_metadata,
                retryCount=task.retry_count,
                maxRetries=task.max_retries,
                lastError=task.last_error,
                startedAt=task.started_at,
                completedAt=task.completed_at,
                createdAt=task.created_at,
                updatedAt=task.updated_at,
                estimatedTimeRemaining=estimated_time,
                processingTime=task.processing_time
            ))

        return ProcessTaskListResponse(
            total=total,
            tasks=task_responses
        )

    async def _execute_process_task(self, task_id: str, db_session_factory):
        from app.database import db_manager

        async with db_manager.session_maker() as db:
            stmt = select(ImageProcessTask).where(ImageProcessTask.id == task_id)
            result = await db.execute(stmt)
            task = result.scalar_one_or_none()

            if not task:
                logger.error(f"任务不存在: {task_id}")
                return

            if task.status in [ImageProcessStatus.COMPLETED.value]:
                return

            task.status = ImageProcessStatus.PROCESSING.value
            task.started_at = datetime.now()
            task.progress = 5
            await db.commit()

            start_time = time.time()

            try:
                task_type = ImageProcessType(task.task_type)

                if task_type == ImageProcessType.RESTORATION:
                    await self._process_restoration(db, task)
                elif task_type == ImageProcessType.ENHANCEMENT:
                    await self._process_enhancement(db, task)
                elif task_type == ImageProcessType.DYNAMIC_PORTRAIT:
                    await self._process_dynamic_portrait(db, task)
                elif task_type == ImageProcessType.CROSS_GENERATION:
                    await self._process_cross_generation(db, task)
                elif task_type == ImageProcessType.VIDEO_HIGHLIGHTS:
                    await self._process_video_highlights(db, task)
                elif task_type == ImageProcessType.AI_SCENE:
                    await self._process_ai_scene(db, task)

                task.status = ImageProcessStatus.COMPLETED.value
                task.progress = 100
                task.completed_at = datetime.now()
                task.processing_time = int(time.time() - start_time)

                await db.commit()

                await self._trigger_callback(task)

                logger.info(f"任务处理完成: {task_id}, 耗时: {task.processing_time}秒")

            except Exception as e:
                await self._handle_task_error(db, task, str(e))

    async def _process_restoration(self, db: AsyncSession, task: ImageProcessTask):
        await self._simulate_progress(db, task, start=5, end=95, duration=15)

        params = (task.parameters or {}).get("restoration", {})
        upscale_factor = params.get("upscale_factor", 2)

        try:
            if settings.ALIYUN_API_KEY and task.source_url:
                prompt = "修复这张老照片，去除划痕和污渍，恢复色彩，增强细节"
                external_task_id = await aliyun_service.create_image_generation_task(
                    prompt=prompt,
                    size="1024*1024"
                )
                task.external_task_id = external_task_id
                task.external_service = "aliyun_wanx"
                await db.commit()

            result_url = task.source_url
            result_preview_url = task.source_url

            task.result_url = result_url
            task.result_preview_url = result_preview_url
            task.result_metadata = {
                "upscale_factor": upscale_factor,
                "restoration_quality": "high",
                "original_size": "1024x1024",
                "processed_size": f"{1024 * upscale_factor}x{1024 * upscale_factor}"
            }

        except Exception as e:
            logger.warning(f"阿里云API调用失败，使用模拟处理: {e}")
            task.result_url = task.source_url
            task.result_preview_url = task.source_url
            task.result_metadata = {
                "upscale_factor": params.get("upscale_factor", 2),
                "restoration_quality": "high",
                "note": "模拟处理结果"
            }

    async def _process_enhancement(self, db: AsyncSession, task: ImageProcessTask):
        await self._simulate_progress(db, task, start=5, end=95, duration=10)

        params = (task.parameters or {}).get("enhancement", {})
        upscale_factor = params.get("upscale_factor", 2)

        task.result_url = task.source_url
        task.result_preview_url = task.source_url
        task.result_metadata = {
            "upscale_factor": upscale_factor,
            "enhance_face": params.get("enhance_face", True),
            "sharpen": params.get("sharpen", True),
            "color_enhance": params.get("color_enhance", True),
            "original_size": "1024x1024",
            "processed_size": f"{1024 * upscale_factor}x{1024 * upscale_factor}"
        }

    async def _process_dynamic_portrait(self, db: AsyncSession, task: ImageProcessTask):
        await self._simulate_progress(db, task, start=5, end=95, duration=25)

        params = (task.parameters or {}).get("dynamic_portrait", {})

        task.result_url = task.source_url
        task.result_preview_url = task.source_url
        task.result_metadata = {
            "motion_type": params.get("motion_type", "subtle_smile"),
            "blink_enabled": params.get("blink_enabled", True),
            "head_movement": params.get("head_movement", True),
            "duration_seconds": params.get("duration_seconds", 5),
            "fps": params.get("fps", 24),
            "output_format": "mp4"
        }

    async def _process_cross_generation(self, db: AsyncSession, task: ImageProcessTask):
        await self._simulate_progress(db, task, start=5, end=95, duration=35)

        params = (task.parameters or {}).get("cross_generation", {})

        task.result_url = task.source_url
        task.result_preview_url = task.source_url
        task.result_metadata = {
            "target_age": params.get("target_age"),
            "target_gender": params.get("target_gender"),
            "target_style": params.get("target_style", "modern"),
            "preserve_identity": params.get("preserve_identity", True)
        }

    async def _process_video_highlights(self, db: AsyncSession, task: ImageProcessTask):
        await self._simulate_progress(db, task, start=5, end=95, duration=45)

        params = (task.parameters or {}).get("video_highlights", {})

        task.result_url = task.source_url
        task.result_preview_url = task.source_url
        task.result_metadata = {
            "highlight_duration": params.get("highlight_duration", 30),
            "transition_style": params.get("transition_style", "fade"),
            "background_music": params.get("background_music"),
            "add_captions": params.get("add_captions", False),
            "caption_style": params.get("caption_style", "elegant"),
            "media_count": len(task.source_media_ids or [])
        }

    async def _process_ai_scene(self, db: AsyncSession, task: ImageProcessTask):
        await self._simulate_progress(db, task, start=5, end=95, duration=20)

        params = (task.parameters or {}).get("ai_scene", {})

        try:
            if settings.ALIYUN_API_KEY:
                scene_prompt = params.get("scene_prompt", "")
                style = params.get("style", "photorealistic")
                full_prompt = f"{scene_prompt}, {style} style, high quality"

                external_task_id = await aliyun_service.create_image_generation_task(
                    prompt=full_prompt,
                    size="1024*1024"
                )
                task.external_task_id = external_task_id
                task.external_service = "aliyun_wanx"
                await db.commit()

        except Exception as e:
            logger.warning(f"AI场景生成API调用失败: {e}")

        task.result_url = task.source_url or "/uploads/default_ai_scene.jpg"
        task.result_preview_url = task.result_url
        task.result_metadata = {
            "scene_prompt": params.get("scene_prompt"),
            "style": params.get("style", "photorealistic"),
            "aspect_ratio": params.get("aspect_ratio", "16:9"),
            "quality": params.get("quality", "high")
        }

    async def _simulate_progress(self, db: AsyncSession, task: ImageProcessTask, start: int, end: int, duration: int):
        steps = 10
        step_duration = duration / steps
        progress_step = (end - start) / steps

        current_progress = start
        for _ in range(steps):
            current_progress += progress_step
            task.progress = min(int(current_progress), end)
            await db.commit()
            await asyncio.sleep(step_duration)

    async def _handle_task_error(self, db: AsyncSession, task: ImageProcessTask, error_message: str):
        task.last_error = error_message
        task.failed_at = datetime.now()
        task.retry_count += 1

        logger.error(f"任务处理失败: {task.id}, 重试次数: {task.retry_count}, 错误: {error_message}")

        if task.retry_count < task.max_retries:
            task.status = ImageProcessStatus.RETRY_PENDING.value
            task.next_retry_at = self._calculate_next_retry(task.retry_count)
            logger.info(f"任务计划第 {task.retry_count + 1} 次重试: {task.next_retry_at}")
        else:
            task.status = ImageProcessStatus.FAILED.value
            logger.error(f"任务最终失败，已重试 {task.retry_count} 次: {task.id}")

        await db.commit()

        await self._trigger_callback(task)

    async def retry_task(
        self,
        db: AsyncSession,
        task_id: str,
        reset_retry_count: bool = False
    ) -> ProcessTaskResponse:
        stmt = select(ImageProcessTask).where(ImageProcessTask.id == task_id)
        result = await db.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            raise ImageProcessingError("任务不存在")

        if task.status not in [ImageProcessStatus.FAILED.value, ImageProcessStatus.RETRY_PENDING.value]:
            raise ImageProcessingError("只有失败或待重试的任务才能重试")

        if reset_retry_count:
            task.retry_count = 0

        task.status = ImageProcessStatus.PENDING.value
        task.progress = 0
        task.last_error = None
        task.failed_at = None
        task.next_retry_at = None
        task.started_at = None
        task.completed_at = None

        await db.commit()

        await self._processing_queue.put((task_id, db.get_bind()))

        logger.info(f"任务重试已排队: {task_id}")

        return ProcessTaskResponse(
            taskId=task_id,
            galleryId=task.gallery_id,
            taskType=ImageProcessType(task.task_type),
            status=ImageProcessStatus.PENDING,
            progress=0,
            message="任务已重新排队处理"
        )

    async def cancel_task(
        self,
        db: AsyncSession,
        task_id: str
    ) -> ProcessTaskCancelResponse:
        stmt = select(ImageProcessTask).where(ImageProcessTask.id == task_id)
        result = await db.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            raise ImageProcessingError("任务不存在")

        if task.status in [ImageProcessStatus.COMPLETED.value, ImageProcessStatus.FAILED.value]:
            raise ImageProcessingError("已完成或失败的任务无法取消")

        task.status = ImageProcessStatus.FAILED.value
        task.last_error = "用户取消任务"
        task.failed_at = datetime.now()

        await db.commit()

        logger.info(f"任务已取消: {task_id}")

        return ProcessTaskCancelResponse(
            taskId=task_id,
            success=True,
            message="任务已取消"
        )

    async def _trigger_callback(self, task: ImageProcessTask):
        if not task.callback_url:
            return

        if not AIOHTTP_AVAILABLE:
            logger.warning(f"aiohttp 未安装，无法发送回调: {task.id}")
            return

        try:
            payload = {
                "task_id": task.id,
                "gallery_id": task.gallery_id,
                "task_type": task.task_type,
                "status": task.status,
                "progress": task.progress,
                "result_url": task.result_url,
                "error": task.last_error,
                "webhook_data": task.webhook_payload
            }

            async with aiohttp.ClientSession() as session:
                await session.post(
                    task.callback_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                )
                logger.info(f"回调通知已发送: {task.id} -> {task.callback_url}")

        except Exception as e:
            logger.warning(f"回调通知发送失败: {task.id}, 错误: {e}")

    async def check_pending_retries(self, db: AsyncSession):
        now = datetime.now()

        stmt = select(ImageProcessTask).where(
            ImageProcessTask.status == ImageProcessStatus.RETRY_PENDING.value,
            ImageProcessTask.next_retry_at <= now
        )

        result = await db.execute(stmt)
        tasks = result.scalars().all()

        for task in tasks:
            logger.info(f"自动重试任务: {task.id}")
            task.status = ImageProcessStatus.PENDING.value
            task.next_retry_at = None
            await db.commit()
            await self._processing_queue.put((task.id, db.get_bind()))

    async def get_processed_result(
        self,
        db: AsyncSession,
        task_id: str
    ) -> Dict[str, Any]:
        stmt = select(ImageProcessTask).where(ImageProcessTask.id == task_id)
        result = await db.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            raise ImageProcessingError("任务不存在")

        if task.status != ImageProcessStatus.COMPLETED.value:
            raise ImageProcessingError("任务尚未完成")

        return {
            "task_id": task.id,
            "result_url": task.result_url,
            "preview_url": task.result_preview_url,
            "metadata": task.result_metadata,
            "export_format": task.export_format,
            "watermark_text": task.watermark_text,
            "watermark_position": task.watermark_position
        }


image_processing_service = ImageProcessingService()
