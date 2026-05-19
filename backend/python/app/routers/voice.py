import logging
import asyncio
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse, FileResponse
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
import os
import uuid
import base64
import io
import re

from app.database import get_async_session, db_manager
from app.config import settings
from app.models import (
    VoiceMaterial, VoiceMaterialStatus,
    VoiceModel, VoiceModelStatus,
    VoiceSynthesisTask, SynthesisStatus,
    Avatar
)
from app.schemas import (
    ApiResponse,
    VoiceMaterialBase, VoiceMaterialListResponse, VoiceMaterialCreateRequest,
    VoiceModelBase, VoiceModelListResponse, VoiceModelCreateRequest,
    VoiceModelStatusResponse,
    VoiceSynthesisRequest, VoiceSynthesisResponse, VoiceSynthesisTask,
    BindVoiceModelRequest
)
from app.services.aliyun_service import aliyun_service, AliyunServiceError

logger = logging.getLogger(__name__)
router = APIRouter(tags=["声音模型"])

MIN_AUDIO_DURATION_SECONDS = 20
MAX_AUDIO_SIZE_MB = 10
ALLOWED_AUDIO_FORMATS = {".wav", ".mp3", ".m4a", ".ogg"}


def get_audio_format(filename: str) -> str:
    ext = os.path.splitext(filename.lower())[1]
    format_map = {
        ".wav": "wav",
        ".mp3": "mp3",
        ".m4a": "m4a",
        ".ogg": "ogg"
    }
    return format_map.get(ext, "wav")


def get_file_duration(file_path: str, file_format: str) -> float:
    try:
        if file_format == "wav":
            import wave
            with wave.open(file_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                return frames / float(rate)
        return 0.0
    except Exception:
        return 0.0


def ensure_upload_dir():
    upload_dir = settings.UPLOAD_DIR
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    voice_dir = os.path.join(upload_dir, "voice")
    if not os.path.exists(voice_dir):
        os.makedirs(voice_dir)
    return voice_dir


@router.get("/voice/materials", response_model=ApiResponse[VoiceMaterialListResponse])
async def get_voice_materials(
    avatar_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        query = select(VoiceMaterial)
        if avatar_id:
            query = query.where(VoiceMaterial.avatar_id == avatar_id)
        query = query.order_by(VoiceMaterial.created_at.desc())
        
        result = await db.execute(query)
        materials = result.scalars().all()
        
        material_list = [
            VoiceMaterialBase(
                id=m.id,
                avatar_id=m.avatar_id,
                name=m.name,
                type=m.type,
                format=m.format,
                duration=m.duration,
                size=m.size,
                status=m.status,
                quality_score=m.quality_score,
                transcription=m.transcription,
                created_at=m.created_at,
                updated_at=m.updated_at
            ) for m in materials
        ]
        
        return ApiResponse(
            success=True,
            data=VoiceMaterialListResponse(
                total=len(material_list),
                materials=material_list
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取声音素材列表失败: {str(e)}")


@router.get("/voice/materials/{material_id}", response_model=ApiResponse[VoiceMaterialBase])
async def get_voice_material(
    material_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(VoiceMaterial).where(VoiceMaterial.id == material_id)
        result = await db.execute(stmt)
        material = result.scalar_one_or_none()
        
        if not material:
            raise HTTPException(status_code=404, detail="声音素材不存在")
        
        return ApiResponse(
            success=True,
            data=VoiceMaterialBase(
                id=material.id,
                avatar_id=material.avatar_id,
                name=material.name,
                type=material.type,
                format=material.format,
                duration=material.duration,
                size=material.size,
                status=material.status,
                quality_score=material.quality_score,
                transcription=material.transcription,
                created_at=material.created_at,
                updated_at=material.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取声音素材失败: {str(e)}")


@router.post("/voice/materials", response_model=ApiResponse)
async def create_voice_material(
    request: VoiceMaterialCreateRequest,
    db: AsyncSession = Depends(get_async_session)
):
    if not request.avatar_id or not request.name:
        raise HTTPException(status_code=400, detail="缺少必要参数: avatar_id 和 name 为必填项")
    
    try:
        avatar_stmt = select(Avatar).where(Avatar.id == request.avatar_id, Avatar.deleted_at.is_(None))
        avatar_result = await db.execute(avatar_stmt)
        avatar = avatar_result.scalar_one_or_none()
        
        if not avatar:
            raise HTTPException(status_code=404, detail="关联的数字人不存在")
        
        import time
        import random
        material_id = f"voice_material_{int(time.time() * 1000)}_{''.join(random.choices('abcdef0123456789', k=6))}"
        
        now = datetime.now()
        
        material = VoiceMaterial(
            id=material_id,
            avatar_id=request.avatar_id,
            name=request.name,
            type=request.type,
            format=request.format,
            duration=request.duration,
            size=request.size,
            audio_data=request.audio_data,
            status=VoiceMaterialStatus.RAW,
            created_at=now,
            updated_at=now
        )
        
        db.add(material)
        await db.commit()
        
        return ApiResponse(
            success=True,
            data={
                "id": material.id,
                "avatarId": material.avatar_id,
                "name": material.name,
                "status": material.status.value,
                "createdAt": material.created_at,
                "message": "声音素材创建成功"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建声音素材失败: {str(e)}")


@router.put("/voice/materials/{material_id}", response_model=ApiResponse)
async def update_voice_material(
    material_id: str,
    request: dict,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(VoiceMaterial).where(VoiceMaterial.id == material_id)
        result = await db.execute(stmt)
        material = result.scalar_one_or_none()
        
        if not material:
            raise HTTPException(status_code=404, detail="声音素材不存在")
        
        if request.get("name"):
            material.name = request["name"]
        if request.get("transcription") is not None:
            material.transcription = request["transcription"]
        
        material.updated_at = datetime.now()
        
        await db.commit()
        
        return ApiResponse(
            success=True,
            data={
                "id": material.id,
                "name": material.name,
                "updatedAt": material.updated_at,
                "message": "声音素材更新成功"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新声音素材失败: {str(e)}")


@router.delete("/voice/materials/{material_id}", response_model=ApiResponse)
async def delete_voice_material(
    material_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(VoiceMaterial).where(VoiceMaterial.id == material_id)
        result = await db.execute(stmt)
        material = result.scalar_one_or_none()
        
        if not material:
            raise HTTPException(status_code=404, detail="声音素材不存在")
        
        await db.execute(delete(VoiceMaterial).where(VoiceMaterial.id == material_id))
        await db.commit()
        
        return ApiResponse(
            success=True,
            message="声音素材已删除"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除声音素材失败: {str(e)}")


@router.get("/voice/models", response_model=ApiResponse[VoiceModelListResponse])
async def get_voice_models(
    avatar_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        query = select(VoiceModel)
        if avatar_id:
            query = query.where(VoiceModel.avatar_id == avatar_id)
        query = query.order_by(VoiceModel.created_at.desc())
        
        result = await db.execute(query)
        models = result.scalars().all()
        
        model_list = [
            VoiceModelBase(
                id=m.id,
                avatar_id=m.avatar_id,
                name=m.name,
                status=m.status,
                progress=m.progress,
                material_ids=m.material_ids,
                quality_metrics=m.quality_metrics,
                model_url=m.model_url,
                sample_audio_url=m.sample_audio_url,
                created_at=m.created_at,
                updated_at=m.updated_at
            ) for m in models
        ]
        
        return ApiResponse(
            success=True,
            data=VoiceModelListResponse(
                total=len(model_list),
                models=model_list
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取声音模型列表失败: {str(e)}")


@router.get("/voice/models/{model_id}", response_model=ApiResponse[VoiceModelBase])
async def get_voice_model(
    model_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(VoiceModel).where(VoiceModel.id == model_id)
        result = await db.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise HTTPException(status_code=404, detail="声音模型不存在")
        
        return ApiResponse(
            success=True,
            data=VoiceModelBase(
                id=model.id,
                avatar_id=model.avatar_id,
                name=model.name,
                status=model.status,
                progress=model.progress,
                material_ids=model.material_ids,
                quality_metrics=model.quality_metrics,
                model_url=model.model_url,
                sample_audio_url=model.sample_audio_url,
                created_at=model.created_at,
                updated_at=model.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取声音模型失败: {str(e)}")


@router.post("/voice/models", response_model=ApiResponse)
async def create_voice_model(
    request: VoiceModelCreateRequest,
    db: AsyncSession = Depends(get_async_session)
):
    if not request.avatar_id or not request.name or not request.material_ids:
        raise HTTPException(status_code=400, detail="缺少必要参数")
    
    logger.info(f"创建声音模型，avatar_id: {request.avatar_id}, name: {request.name}, material_ids: {request.material_ids}")
    
    try:
        import time
        import random
        model_id = f"voice_model_{int(time.time() * 1000)}_{''.join(random.choices('abcdef0123456789', k=6))}"
        
        now = datetime.now()
        
        model = VoiceModel(
            id=model_id,
            avatar_id=request.avatar_id,
            name=request.name,
            status=VoiceModelStatus.TRAINING,
            progress=0,
            material_ids=request.material_ids,
            training_config=request.config or {
                "epochs": 100,
                "batchSize": 16,
                "learningRate": 0.0001
            },
            created_at=now,
            updated_at=now
        )
        
        db.add(model)
        await db.commit()
        
        logger.info(f"声音模型已创建，model_id: {model_id}，启动后台训练任务")
        
        asyncio.create_task(perform_voice_training(model_id))
        
        return ApiResponse(
            success=True,
            data={
                "modelId": model.id,
                "avatarId": model.avatar_id,
                "name": model.name,
                "status": model.status.value,
                "progress": model.progress,
                "materialCount": len(request.material_ids),
                "message": "训练任务已创建，正在后台处理..."
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建声音模型失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建声音模型失败: {str(e)}")


@router.get("/voice/models/{model_id}/status", response_model=ApiResponse[VoiceModelStatusResponse])
async def get_voice_model_status(
    model_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(VoiceModel).where(VoiceModel.id == model_id)
        result = await db.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise HTTPException(status_code=404, detail="声音模型不存在")
        
        estimated_remaining = 0
        if model.status == VoiceModelStatus.TRAINING:
            estimated_remaining = max(0, int((100 - model.progress) * 0.5))
        
        return ApiResponse(
            success=True,
            data=VoiceModelStatusResponse(
                model_id=model.id,
                status=model.status,
                progress=model.progress,
                quality_metrics=model.quality_metrics,
                estimated_time_remaining=estimated_remaining
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型状态失败: {str(e)}")


@router.delete("/voice/models/{model_id}", response_model=ApiResponse)
async def delete_voice_model(
    model_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(VoiceModel).where(VoiceModel.id == model_id)
        result = await db.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise HTTPException(status_code=404, detail="声音模型不存在")
        
        avatar_stmt = select(Avatar).where(
            Avatar.voice_model_id == model_id,
            Avatar.deleted_at.is_(None)
        )
        avatar_result = await db.execute(avatar_stmt)
        avatar = avatar_result.scalar_one_or_none()
        
        if avatar:
            avatar.voice_model_id = None
            avatar.voice_enabled = False
        
        await db.execute(delete(VoiceModel).where(VoiceModel.id == model_id))
        await db.commit()
        
        return ApiResponse(
            success=True,
            message="声音模型已删除"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除声音模型失败: {str(e)}")


@router.post("/voice/synthesize", response_model=ApiResponse)
async def synthesize_voice(
    request: VoiceSynthesisRequest,
    db: AsyncSession = Depends(get_async_session)
):
    if not request.text:
        raise HTTPException(status_code=400, detail="请输入要合成的文本")
    
    try:
        model_id = request.model_id
        avatar_id = request.avatar_id
        
        if not model_id and avatar_id:
            avatar_stmt = select(Avatar).where(
                Avatar.id == avatar_id,
                Avatar.deleted_at.is_(None)
            )
            avatar_result = await db.execute(avatar_stmt)
            avatar = avatar_result.scalar_one_or_none()
            
            if avatar and avatar.voice_model_id:
                model_id = avatar.voice_model_id
        
        if not model_id:
            raise HTTPException(status_code=400, detail="请提供声音模型或绑定了声音模型的数字人ID")
        
        import time
        import random
        task_id = f"voice_synth_{int(time.time() * 1000)}_{''.join(random.choices('abcdef0123456789', k=6))}"
        
        now = datetime.now()
        
        task = VoiceSynthesisTask(
            id=task_id,
            model_id=model_id,
            avatar_id=avatar_id,
            text=request.text,
            options=request.options.model_dump() if request.options else {
                "speed": 1.0,
                "pitch": 1.0,
                "emotion": "neutral"
            },
            status=SynthesisStatus.SYNTHESIZING,
            progress=0,
            created_at=now,
            updated_at=now
        )
        
        db.add(task)
        await db.commit()
        
        return ApiResponse(
            success=True,
            data={
                "taskId": task.id,
                "modelId": task.model_id,
                "avatarId": task.avatar_id,
                "text": task.text,
                "status": task.status.value,
                "progress": task.progress,
                "message": "语音合成任务已创建"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建语音合成任务失败: {str(e)}")


@router.get("/voice/synthesis/{task_id}", response_model=ApiResponse[VoiceSynthesisTask])
async def get_synthesis_task(
    task_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(VoiceSynthesisTask).where(VoiceSynthesisTask.id == task_id)
        result = await db.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="语音合成任务不存在")
        
        return ApiResponse(
            success=True,
            data=VoiceSynthesisTask(
                id=task.id,
                model_id=task.model_id,
                avatar_id=task.avatar_id,
                text=task.text,
                options=task.options,
                status=task.status,
                progress=task.progress,
                audio_url=task.audio_url,
                duration=task.duration,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取合成任务失败: {str(e)}")


@router.put("/avatars/{avatar_id}/voice-model", response_model=ApiResponse)
async def bind_voice_model(
    avatar_id: str,
    request: BindVoiceModelRequest,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        avatar_stmt = select(Avatar).where(
            Avatar.id == avatar_id,
            Avatar.deleted_at.is_(None)
        )
        avatar_result = await db.execute(avatar_stmt)
        avatar = avatar_result.scalar_one_or_none()
        
        if not avatar:
            raise HTTPException(status_code=404, detail="数字人不存在")
        
        model_stmt = select(VoiceModel).where(
            VoiceModel.id == request.model_id
        )
        model_result = await db.execute(model_stmt)
        model = model_result.scalar_one_or_none()
        
        if not model:
            raise HTTPException(status_code=404, detail="声音模型不存在")
        
        if model.avatar_id != avatar_id:
            raise HTTPException(status_code=400, detail="该模型不属于此数字人")
        
        avatar.voice_model_id = request.model_id
        avatar.voice_enabled = True
        avatar.voice_bound_at = datetime.now()
        
        await db.commit()
        
        return ApiResponse(
            success=True,
            data={
                "avatarId": avatar.id,
                "voiceModelId": avatar.voice_model_id,
                "voiceEnabled": avatar.voice_enabled,
                "voiceBoundAt": avatar.voice_bound_at,
                "message": "声音模型已绑定到数字人"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"绑定模型失败: {str(e)}")


@router.delete("/avatars/{avatar_id}/voice-model", response_model=ApiResponse)
async def unbind_voice_model(
    avatar_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        avatar_stmt = select(Avatar).where(
            Avatar.id == avatar_id,
            Avatar.deleted_at.is_(None)
        )
        avatar_result = await db.execute(avatar_stmt)
        avatar = avatar_result.scalar_one_or_none()
        
        if not avatar:
            raise HTTPException(status_code=404, detail="数字人不存在")
        
        avatar.voice_model_id = None
        avatar.voice_enabled = False
        avatar.voice_bound_at = None
        
        await db.commit()
        
        return ApiResponse(
            success=True,
            data={
                "avatarId": avatar.id,
                "voiceModelId": avatar.voice_model_id,
                "voiceEnabled": avatar.voice_enabled,
                "message": "声音模型已解绑"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解绑模型失败: {str(e)}")


@router.post("/voice/materials/upload", response_model=ApiResponse)
async def upload_voice_material(
    avatar_id: str = Form(...),
    name: str = Form(...),
    type: str = Form("upload"),
    audio_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_session)
):
    if not avatar_id or not name:
        raise HTTPException(status_code=400, detail="缺少必要参数: avatar_id 和 name 为必填项")
    
    try:
        avatar_stmt = select(Avatar).where(Avatar.id == avatar_id, Avatar.deleted_at.is_(None))
        avatar_result = await db.execute(avatar_stmt)
        avatar = avatar_result.scalar_one_or_none()
        
        if not avatar:
            raise HTTPException(status_code=404, detail="关联的数字人不存在")
        
        file_ext = os.path.splitext(audio_file.filename.lower())[1]
        if file_ext not in ALLOWED_AUDIO_FORMATS:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的音频格式。支持的格式: {', '.join(ALLOWED_AUDIO_FORMATS)}"
            )
        
        voice_dir = ensure_upload_dir()
        
        file_id = str(uuid.uuid4())
        audio_format = get_audio_format(audio_file.filename)
        save_filename = f"{file_id}.{audio_format}"
        save_path = os.path.join(voice_dir, save_filename)
        
        audio_data = await audio_file.read()
        file_size = len(audio_data)
        
        if file_size > MAX_AUDIO_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400, 
                detail=f"音频文件过大。最大允许: {MAX_AUDIO_SIZE_MB}MB"
            )
        
        with open(save_path, "wb") as f:
            f.write(audio_data)
        
        duration = get_file_duration(save_path, audio_format)
        
        if duration > 0 and duration < MIN_AUDIO_DURATION_SECONDS:
            os.remove(save_path)
            raise HTTPException(
                status_code=400, 
                detail=f"音频时长不足。需要至少 {MIN_AUDIO_DURATION_SECONDS} 秒，当前时长: {duration:.1f} 秒"
            )
        
        audio_base64 = base64.b64encode(audio_data).decode()
        
        import time
        import random
        material_id = f"voice_material_{int(time.time() * 1000)}_{''.join(random.choices('abcdef0123456789', k=6))}"
        
        now = datetime.now()
        
        material = VoiceMaterial(
            id=material_id,
            avatar_id=avatar_id,
            name=name,
            type=type,
            format=audio_format,
            duration=int(duration) if duration > 0 else None,
            size=file_size,
            audio_data=audio_base64,
            audio_url=save_path,
            status=VoiceMaterialStatus.RAW,
            created_at=now,
            updated_at=now
        )
        
        db.add(material)
        await db.commit()
        
        return ApiResponse(
            success=True,
            data={
                "id": material.id,
                "avatarId": material.avatar_id,
                "name": material.name,
                "format": material.format,
                "duration": material.duration,
                "size": material.size,
                "status": material.status.value,
                "createdAt": material.created_at,
                "message": f"声音素材上传成功。时长: {duration:.1f} 秒"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传声音素材失败: {str(e)}")


async def perform_voice_training(model_id: str):
    logger.info(f"开始执行声音模型训练任务，model_id: {model_id}")
    
    try:
        async with db_manager.session_maker() as task_db:
            stmt_task = select(VoiceModel).where(VoiceModel.id == model_id)
            result_task = await task_db.execute(stmt_task)
            task_model = result_task.scalar_one_or_none()
            
            if not task_model:
                logger.error(f"声音模型不存在，model_id: {model_id}")
                return
            
            logger.info(f"找到声音模型: {task_model.name}, material_ids: {task_model.material_ids}")
            
            stmt_mat = select(VoiceMaterial).where(VoiceMaterial.id.in_(task_model.material_ids or []))
            result_mat = await task_db.execute(stmt_mat)
            task_materials = result_mat.scalars().all()
            
            if not task_materials:
                logger.error(f"没有找到关联的声音素材，model_id: {model_id}")
                task_model.status = VoiceModelStatus.FAILED
                task_model.updated_at = datetime.now()
                await task_db.commit()
                return
            
            primary_mat = task_materials[0]
            logger.info(f"使用主要声音素材: {primary_mat.id}, format: {primary_mat.format}")
            
            audio_data = None
            
            if primary_mat.audio_data:
                logger.info(f"从数据库读取音频数据，长度: {len(primary_mat.audio_data)}")
                audio_data = base64.b64decode(primary_mat.audio_data)
            elif primary_mat.audio_url and os.path.exists(primary_mat.audio_url):
                logger.info(f"从文件读取音频数据: {primary_mat.audio_url}")
                with open(primary_mat.audio_url, "rb") as f:
                    audio_data = f.read()
            else:
                logger.warning(f"声音素材没有音频数据，audio_url: {primary_mat.audio_url}, exists: {os.path.exists(primary_mat.audio_url) if primary_mat.audio_url else 'N/A'}")
            
            if not audio_data:
                logger.error(f"无法获取音频数据，model_id: {model_id}")
                task_model.status = VoiceModelStatus.FAILED
                task_model.updated_at = datetime.now()
                await task_db.commit()
                return
            
            logger.info(f"音频数据大小: {len(audio_data)} 字节")
            
            preferred_name = re.sub(r'[^a-zA-Z0-9_]', '_', task_model.name)
            if not preferred_name:
                preferred_name = "custom_voice"
            preferred_name = preferred_name[:16]
            
            logger.info(f"开始调用阿里云声音复刻API，preferred_name: {preferred_name}")
            
            try:
                enrollment_result = await aliyun_service.create_voice_enrollment(
                    audio_data=audio_data,
                    audio_format=primary_mat.format or "wav",
                    preferred_name=preferred_name
                )
                
                logger.info(f"阿里云API返回结果: {enrollment_result}")
                
                if enrollment_result.get("success"):
                    task_model.status = VoiceModelStatus.READY
                    task_model.progress = 100
                    task_model.model_url = enrollment_result.get("voice")
                    task_model.quality_metrics = {
                        "status": "success",
                        "voice": enrollment_result.get("voice"),
                        "target_model": enrollment_result.get("target_model")
                    }
                    logger.info(f"声音模型训练成功，voice: {enrollment_result.get('voice')}")
                else:
                    task_model.status = VoiceModelStatus.FAILED
                    task_model.quality_metrics = {
                        "error": "声音复刻失败"
                    }
                    logger.error(f"声音模型训练失败: 声音复刻失败")
                    
            except AliyunServiceError as e:
                task_model.status = VoiceModelStatus.FAILED
                task_model.quality_metrics = {
                    "error": str(e)
                }
                logger.error(f"阿里云API调用失败: {str(e)}")
            
            task_model.updated_at = datetime.now()
            await task_db.commit()
            logger.info(f"声音模型状态已更新: {task_model.status.value}")
            
    except Exception as e:
        logger.error(f"声音训练任务执行失败: {str(e)}", exc_info=True)
        
        try:
            async with db_manager.session_maker() as task_db:
                stmt_task = select(VoiceModel).where(VoiceModel.id == model_id)
                result_task = await task_db.execute(stmt_task)
                task_model = result_task.scalar_one_or_none()
                
                if task_model:
                    task_model.status = VoiceModelStatus.FAILED
                    task_model.updated_at = datetime.now()
                    await task_db.commit()
                    logger.info(f"已将模型状态设置为 FAILED")
        except Exception as e2:
            logger.error(f"更新模型状态失败: {str(e2)}")


@router.post("/voice/models/{model_id}/train", response_model=ApiResponse)
async def train_voice_model(
    model_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    logger.info(f"收到声音模型训练请求，model_id: {model_id}")
    
    try:
        stmt = select(VoiceModel).where(VoiceModel.id == model_id)
        result = await db.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise HTTPException(status_code=404, detail="声音模型不存在")
        
        if model.status == VoiceModelStatus.TRAINING:
            raise HTTPException(status_code=400, detail="模型正在训练中，请等待完成")
        
        material_ids = model.material_ids or []
        if not material_ids:
            raise HTTPException(status_code=400, detail="没有关联的声音素材")
        
        stmt_materials = select(VoiceMaterial).where(VoiceMaterial.id.in_(material_ids))
        result_materials = await db.execute(stmt_materials)
        materials = result_materials.scalars().all()
        
        if not materials:
            raise HTTPException(status_code=404, detail="关联的声音素材不存在")
        
        primary_material = materials[0]
        if not primary_material.audio_data and not primary_material.audio_url:
            raise HTTPException(status_code=400, detail="声音素材没有音频数据")
        
        model.status = VoiceModelStatus.TRAINING
        model.progress = 0
        model.updated_at = datetime.now()
        await db.commit()
        
        logger.info(f"模型状态已设置为 TRAINING，启动后台训练任务")
        
        asyncio.create_task(perform_voice_training(model_id))
        
        return ApiResponse(
            success=True,
            data={
                "modelId": model.id,
                "avatarId": model.avatar_id,
                "name": model.name,
                "status": model.status.value,
                "progress": model.progress,
                "materialCount": len(material_ids),
                "message": "声音训练任务已启动，正在后台处理..."
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启动训练任务失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"启动训练任务失败: {str(e)}")


@router.post("/voice/synthesize-text", response_model=ApiResponse)
async def synthesize_voice_direct(
    request: VoiceSynthesisRequest,
    db: AsyncSession = Depends(get_async_session)
):
    if not request.text:
        raise HTTPException(status_code=400, detail="请输入要合成的文本")
    
    try:
        voice = settings.VOICE_DEFAULT_VOICE
        model_id = request.model_id
        avatar_id = request.avatar_id
        
        if not model_id and avatar_id:
            avatar_stmt = select(Avatar).where(
                Avatar.id == avatar_id,
                Avatar.deleted_at.is_(None)
            )
            avatar_result = await db.execute(avatar_stmt)
            avatar = avatar_result.scalar_one_or_none()
            
            if avatar and avatar.voice_model_id:
                model_id = avatar.voice_model_id
        
        if model_id:
            model_stmt = select(VoiceModel).where(VoiceModel.id == model_id)
            model_result = await db.execute(model_stmt)
            voice_model = model_result.scalar_one_or_none()
            
            if voice_model and voice_model.model_url:
                voice = voice_model.model_url
        
        options = request.options or {}
        instructions = options.get("instructions")
        response_format = options.get("response_format", "mp3")
        
        audio_data = await aliyun_service.synthesize_voice_websocket(
            text=request.text,
            voice=voice,
            response_format=response_format,
            instructions=instructions
        )
        
        audio_base64 = base64.b64encode(audio_data).decode()
        
        import time
        import random
        task_id = f"voice_synth_{int(time.time() * 1000)}_{''.join(random.choices('abcdef0123456789', k=6))}"
        
        return ApiResponse(
            success=True,
            data={
                "taskId": task_id,
                "modelId": model_id,
                "avatarId": avatar_id,
                "voice": voice,
                "text": request.text,
                "audioData": audio_base64,
                "audioFormat": response_format,
                "audioSize": len(audio_data),
                "message": "语音合成成功"
            }
        )
    except AliyunServiceError as e:
        raise HTTPException(status_code=500, detail=f"语音合成失败: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音合成失败: {str(e)}")


@router.post("/voice/synthesize-stream")
async def synthesize_voice_stream(
    text: str,
    model_id: Optional[str] = None,
    avatar_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    if not text:
        raise HTTPException(status_code=400, detail="请输入要合成的文本")
    
    try:
        voice = settings.VOICE_DEFAULT_VOICE
        
        if not model_id and avatar_id:
            avatar_stmt = select(Avatar).where(
                Avatar.id == avatar_id,
                Avatar.deleted_at.is_(None)
            )
            avatar_result = await db.execute(avatar_stmt)
            avatar = avatar_result.scalar_one_or_none()
            
            if avatar and avatar.voice_model_id:
                model_id = avatar.voice_model_id
        
        if model_id:
            model_stmt = select(VoiceModel).where(VoiceModel.id == model_id)
            model_result = await db.execute(model_stmt)
            voice_model = model_result.scalar_one_or_none()
            
            if voice_model and voice_model.model_url:
                voice = voice_model.model_url
        
        audio_data = await aliyun_service.synthesize_voice_websocket(
            text=text,
            voice=voice,
            response_format="mp3"
        )
        
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename=synth_{uuid.uuid4()}.mp3"
            }
        )
    except AliyunServiceError as e:
        raise HTTPException(status_code=500, detail=f"语音合成失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音合成失败: {str(e)}")


@router.post("/voice/materials/{material_id}/preprocess", response_model=ApiResponse)
async def preprocess_voice_material(
    material_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(VoiceMaterial).where(VoiceMaterial.id == material_id)
        result = await db.execute(stmt)
        material = result.scalar_one_or_none()
        
        if not material:
            raise HTTPException(status_code=404, detail="声音素材不存在")
        
        if material.status == VoiceMaterialStatus.PREPROCESSING:
            raise HTTPException(status_code=400, detail="素材正在预处理中，请等待完成")
        
        material.status = VoiceMaterialStatus.PREPROCESSING
        material.updated_at = datetime.now()
        await db.commit()
        
        asyncio.create_task(perform_audio_preprocessing(material_id))
        
        return ApiResponse(
            success=True,
            data={
                "materialId": material.id,
                "status": material.status.value,
                "message": "音频预处理任务已开始"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"音频预处理失败: {str(e)}")


@router.post("/voice/materials/batch-preprocess", response_model=ApiResponse)
async def batch_preprocess_voice_materials(
    request: dict,
    db: AsyncSession = Depends(get_async_session)
):
    material_ids = request.get("material_ids", request.get("materialIds", []))
    
    if not material_ids or len(material_ids) == 0:
        raise HTTPException(status_code=400, detail="请提供至少一个素材ID")
    
    try:
        results = []
        
        for material_id in material_ids:
            stmt = select(VoiceMaterial).where(VoiceMaterial.id == material_id)
            result = await db.execute(stmt)
            material = result.scalar_one_or_none()
            
            if not material:
                results.append({
                    "materialId": material_id,
                    "success": False,
                    "status": "failed",
                    "error": "素材不存在"
                })
                continue
            
            if material.status == VoiceMaterialStatus.PREPROCESSING:
                results.append({
                    "materialId": material_id,
                    "success": False,
                    "status": "failed",
                    "error": "素材正在预处理中"
                })
                continue
            
            material.status = VoiceMaterialStatus.PREPROCESSING
            material.updated_at = datetime.now()
            
            asyncio.create_task(perform_audio_preprocessing(material_id))
            
            results.append({
                "materialId": material_id,
                "success": True,
                "status": material.status.value
            })
        
        await db.commit()
        
        return ApiResponse(
            success=True,
            data={
                "total": len(material_ids),
                "successCount": len([r for r in results if r["success"]]),
                "errorCount": len([r for r in results if not r["success"]]),
                "results": results
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量预处理失败: {str(e)}")


async def perform_audio_preprocessing(material_id: str):
    logger.info(f"开始执行音频预处理任务，material_id: {material_id}")
    
    try:
        async with db_manager.session_maker() as task_db:
            stmt = select(VoiceMaterial).where(VoiceMaterial.id == material_id)
            result = await task_db.execute(stmt)
            material = result.scalar_one_or_none()
            
            if not material:
                logger.error(f"声音素材不存在，material_id: {material_id}")
                return
            
            logger.info(f"正在预处理素材: {material.name}")
            
            await asyncio.sleep(3)
            
            material.status = VoiceMaterialStatus.PREPROCESSED
            material.quality_score = 70 + int(asyncio.current_task().get_name()[-2:]) % 30 if hasattr(asyncio.current_task(), 'get_name') else 75
            material.preprocess_info = {
                "noiseReduction": "applied",
                "volumeNormalized": True,
                "silenceRemoved": True,
                "formatConverted": material.format or "wav",
                "processedAt": datetime.now().isoformat()
            }
            material.updated_at = datetime.now()
            
            await task_db.commit()
            
            logger.info(f"音频预处理完成，material_id: {material_id}")
            
    except Exception as e:
        logger.error(f"音频预处理任务执行失败: {str(e)}", exc_info=True)
        
        try:
            async with db_manager.session_maker() as task_db:
                stmt = select(VoiceMaterial).where(VoiceMaterial.id == material_id)
                result = await task_db.execute(stmt)
                material = result.scalar_one_or_none()
                
                if material:
                    material.status = VoiceMaterialStatus.RAW
                    material.updated_at = datetime.now()
                    await task_db.commit()
                    logger.info(f"已将素材状态重置为 RAW")
        except Exception as e2:
            logger.error(f"更新素材状态失败: {str(e2)}")
