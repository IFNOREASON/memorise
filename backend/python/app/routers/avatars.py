from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, or_, func
from sqlalchemy.orm import selectinload

from app.database import get_async_session
from app.models import (
    Avatar, AvatarStatus, Memory, Photo,
    VoiceModel, VoiceModelStatus
)
from app.schemas import (
    ApiResponse,
    GenerateAvatarRequest, GenerateAvatarResponse,
    AvatarStatusResponse, AvatarListResponse, AvatarBase, AvatarCreateResponse,
    UpdateAvatarRequest, FineTuneRequest, FineTuneResponse,
    MemoryBase, MemoryListResponse, MemoryCreateRequest, MemoryUpdateRequest,
    MemoryType, VoiceModelListResponse, VoiceModelBase,
    RetryGenerationRequest
)
from app.services import generation_service

router = APIRouter(tags=["数字人管理"])


@router.post("/avatars/generate", response_model=ApiResponse[GenerateAvatarResponse])
async def generate_avatar(
    request: GenerateAvatarRequest,
    db: AsyncSession = Depends(get_async_session)
):
    if not request.name or not request.relationship:
        raise HTTPException(status_code=400, detail="缺少必要参数: name 和 relationship 为必填项")
    
    try:
        result = await generation_service.create_avatar_generation(db, request)
        return ApiResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建生成任务失败: {str(e)}")


@router.get("/avatars/{avatar_id}/status", response_model=ApiResponse[AvatarStatusResponse])
async def get_avatar_status(
    avatar_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        result = await generation_service.get_avatar_status(db, avatar_id)
        return ApiResponse(success=True, data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询状态失败: {str(e)}")


@router.get("/avatars", response_model=ApiResponse[AvatarListResponse])
async def get_avatars(
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = (
            select(Avatar)
            .where(Avatar.deleted_at.is_(None))
            .order_by(Avatar.created_at.desc())
        )
        result = await db.execute(stmt)
        avatars = result.scalars().all()
        
        avatar_list = []
        for avatar in avatars:
            chat_count = 0
            
            avatar_list.append(AvatarBase(
                id=avatar.id,
                name=avatar.name,
                relationship=avatar.relationship,
                gender=avatar.gender,
                birth_year=avatar.birth_year,
                death_year=avatar.death_year,
                description=avatar.description,
                generation_method=avatar.generation_method,
                status=avatar.status,
                progress=avatar.progress,
                avatar=avatar.avatar_url,
                modelUrl=avatar.model_url,
                voice_model_id=avatar.voice_model_id,
                voice_enabled=avatar.voice_enabled,
                created_at=avatar.created_at
            ))
        
        return ApiResponse(
            success=True,
            data=AvatarListResponse(
                total=len(avatar_list),
                avatars=avatar_list
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数字人列表失败: {str(e)}")


@router.get("/avatars/{avatar_id}", response_model=ApiResponse[AvatarBase])
async def get_avatar(
    avatar_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(Avatar).where(Avatar.id == avatar_id, Avatar.deleted_at.is_(None))
        result = await db.execute(stmt)
        avatar = result.scalar_one_or_none()
        
        if not avatar:
            raise HTTPException(status_code=404, detail="数字人不存在")
        
        return ApiResponse(
            success=True,
            data=AvatarBase(
                id=avatar.id,
                name=avatar.name,
                relationship=avatar.relationship,
                gender=avatar.gender,
                birth_year=avatar.birth_year,
                death_year=avatar.death_year,
                description=avatar.description,
                generation_method=avatar.generation_method,
                status=avatar.status,
                progress=avatar.progress,
                avatar=avatar.avatar_url,
                modelUrl=avatar.model_url,
                voice_model_id=avatar.voice_model_id,
                voice_enabled=avatar.voice_enabled,
                created_at=avatar.created_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数字人信息失败: {str(e)}")


@router.put("/avatars/{avatar_id}", response_model=ApiResponse[AvatarCreateResponse])
async def update_avatar(
    avatar_id: str,
    request: UpdateAvatarRequest,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(Avatar).where(Avatar.id == avatar_id, Avatar.deleted_at.is_(None))
        result = await db.execute(stmt)
        avatar = result.scalar_one_or_none()
        
        if not avatar:
            raise HTTPException(status_code=404, detail="数字人不存在")
        
        if request.name:
            avatar.name = request.name
        if request.relationship:
            avatar.relationship = request.relationship
        if request.gender:
            avatar.gender = request.gender
        if request.birth_year is not None:
            avatar.birth_year = request.birth_year
        if request.death_year is not None:
            avatar.death_year = request.death_year
        if request.description is not None:
            avatar.description = request.description
        
        await db.commit()
        
        return ApiResponse(
            success=True,
            data=AvatarCreateResponse(
                id=avatar.id,
                name=avatar.name,
                relationship=avatar.relationship,
                gender=avatar.gender,
                birth_year=avatar.birth_year,
                death_year=avatar.death_year,
                description=avatar.description,
                status=avatar.status,
                progress=avatar.progress,
                created_at=avatar.created_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新数字人失败: {str(e)}")


@router.delete("/avatars/{avatar_id}", response_model=ApiResponse)
async def delete_avatar(
    avatar_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(Avatar).where(Avatar.id == avatar_id, Avatar.deleted_at.is_(None))
        result = await db.execute(stmt)
        avatar = result.scalar_one_or_none()
        
        if not avatar:
            raise HTTPException(status_code=404, detail="数字人不存在")
        
        avatar.deleted_at = datetime.now()
        
        await db.execute(
            delete(Memory).where(Memory.avatar_id == avatar_id)
        )
        
        await db.commit()
        
        return ApiResponse(
            success=True,
            message="数字人已删除，关联记忆也已删除"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除数字人失败: {str(e)}")


@router.post("/avatars/{avatar_id}/fine-tune", response_model=ApiResponse[FineTuneResponse])
async def fine_tune_avatar(
    avatar_id: str,
    request: FineTuneRequest,
    db: AsyncSession = Depends(get_async_session)
):
    if not request.adjustments:
        raise HTTPException(status_code=400, detail="缺少微调参数")
    
    try:
        result = await generation_service.fine_tune_avatar(db, avatar_id, request)
        return ApiResponse(success=True, data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"微调失败: {str(e)}")


@router.post("/avatars/retry", response_model=ApiResponse[GenerateAvatarResponse])
async def retry_failed_avatar(
    request: RetryGenerationRequest,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        result = await generation_service.retry_failed_task(db, request.avatar_id)
        return ApiResponse(success=True, data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重试失败: {str(e)}")


@router.get("/avatars/{avatar_id}/memories", response_model=ApiResponse[MemoryListResponse])
async def get_avatar_memories(
    avatar_id: str,
    type: Optional[MemoryType] = None,
    tag: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        avatar_stmt = select(Avatar).where(Avatar.id == avatar_id, Avatar.deleted_at.is_(None))
        avatar_result = await db.execute(avatar_stmt)
        avatar = avatar_result.scalar_one_or_none()
        
        if not avatar:
            raise HTTPException(status_code=404, detail="数字人不存在")
        
        query = select(Memory).where(Memory.avatar_id == avatar_id, Memory.deleted_at.is_(None))
        
        if type:
            query = query.where(Memory.type == type)
        if tag:
            query = query.where(Memory.tags.contains([tag]))
        
        query = query.order_by(Memory.created_at.desc())
        
        result = await db.execute(query)
        memories = result.scalars().all()
        
        memory_list = [
            MemoryBase(
                id=m.id,
                avatar_id=m.avatar_id,
                title=m.title,
                type=m.type,
                description=m.description,
                tags=m.tags,
                created_at=m.created_at,
                updated_at=m.updated_at
            ) for m in memories
        ]
        
        return ApiResponse(
            success=True,
            data=MemoryListResponse(
                total=len(memory_list),
                memories=memory_list
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取记忆列表失败: {str(e)}")
