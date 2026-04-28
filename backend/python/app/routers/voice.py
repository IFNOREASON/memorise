from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.database import get_async_session
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

router = APIRouter(tags=["声音模型"])


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
        
        material.status = VoiceMaterialStatus.PREPROCESSING
        material.updated_at = datetime.now()
        await db.commit()
        
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
        raise HTTPException(status_code=500, detail=f"预处理失败: {str(e)}")


@router.post("/voice/materials/batch-preprocess", response_model=ApiResponse)
async def batch_preprocess_materials(
    request: dict,
    db: AsyncSession = Depends(get_async_session)
):
    material_ids = request.get("materialIds", [])
    
    if not material_ids:
        raise HTTPException(status_code=400, detail="请提供素材ID列表")
    
    try:
        results = []
        for material_id in material_ids:
            stmt = select(VoiceMaterial).where(VoiceMaterial.id == material_id)
            result = await db.execute(stmt)
            material = result.scalar_one_or_none()
            
            if material and material.status == VoiceMaterialStatus.RAW:
                material.status = VoiceMaterialStatus.PREPROCESSING
                material.updated_at = datetime.now()
                results.append({
                    "materialId": material_id,
                    "success": True,
                    "status": "preprocessing"
                })
            else:
                results.append({
                    "materialId": material_id,
                    "success": False,
                    "status": "failed",
                    "error": "素材不存在或状态不允许预处理"
                })
        
        await db.commit()
        
        return ApiResponse(
            success=True,
            data={
                "total": len(material_ids),
                "results": results,
                "message": f"已提交 {len([r for r in results if r['success']])} 个预处理任务"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量预处理失败: {str(e)}")


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
        
        return ApiResponse(
            success=True,
            data={
                "modelId": model.id,
                "avatarId": model.avatar_id,
                "name": model.name,
                "status": model.status.value,
                "progress": model.progress,
                "materialCount": len(request.material_ids),
                "message": "训练任务已创建"
            }
        )
    except Exception as e:
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
