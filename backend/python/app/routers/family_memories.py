from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from typing import Optional, List
from datetime import datetime
import uuid
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, and_

from app.database import get_async_session
from app.config import settings
from app.models import FamilyMemory, FamilyMemoryType, Family
from app.schemas import (
    ApiResponse,
    FamilyMemoryBase, FamilyMemoryCreateRequest, FamilyMemoryUpdateRequest,
    FamilyMemoryListResponse, FamilyMemoryTimelineResponse, FamilyMemoryTimelineItem
)

router = APIRouter(tags=["家族记忆管理"])


def generate_uuid() -> str:
    return str(uuid.uuid4())


def ensure_upload_dir():
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "family_memories"), exist_ok=True)


async def get_or_create_default_family(db: AsyncSession) -> Family:
    family_stmt = select(Family).limit(1)
    family_result = await db.execute(family_stmt)
    family = family_result.scalar_one_or_none()
    
    if not family:
        family = Family(
            id=generate_uuid(),
            surname="默认家族",
            hall_name="默认家族祠堂"
        )
        db.add(family)
        await db.commit()
    
    return family


@router.post("/family-memories", response_model=ApiResponse[FamilyMemoryBase])
async def create_family_memory(
    request: FamilyMemoryCreateRequest,
    db: AsyncSession = Depends(get_async_session)
):
    if not request.title:
        raise HTTPException(status_code=400, detail="记忆标题不能为空")
    
    try:
        family = await get_or_create_default_family(db)
        
        memory = FamilyMemory(
            id=generate_uuid(),
            family_id=family.id,
            title=request.title,
            type=request.type.value,
            description=request.description,
            content=request.content,
            event_date=request.event_date,
            location=request.location,
            media_url=request.media_url,
            media_type=request.media_type,
            tags=request.tags,
            meta_data=request.meta_data
        )
        
        db.add(memory)
        await db.commit()
        await db.refresh(memory)
        
        return ApiResponse(
            success=True,
            data=FamilyMemoryBase(
                id=memory.id,
                familyId=memory.family_id,
                title=memory.title,
                type=FamilyMemoryType(memory.type),
                description=memory.description,
                content=memory.content,
                eventDate=memory.event_date,
                location=memory.location,
                mediaUrl=memory.media_url,
                mediaType=memory.media_type,
                tags=memory.tags,
                createdAt=memory.created_at,
                updatedAt=memory.updated_at
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建家族记忆失败: {str(e)}")


@router.get("/family-memories", response_model=ApiResponse[FamilyMemoryListResponse])
async def get_family_memories(
    type: Optional[FamilyMemoryType] = None,
    keyword: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        query = select(FamilyMemory).where(FamilyMemory.deleted_at.is_(None))
        
        if type:
            query = query.where(FamilyMemory.type == type.value)
        
        if keyword:
            keyword_lower = f"%{keyword.lower()}%"
            query = query.where(
                func.lower(FamilyMemory.title).like(keyword_lower) |
                func.lower(FamilyMemory.description).like(keyword_lower) |
                func.lower(FamilyMemory.location).like(keyword_lower)
            )
        
        if start_date:
            query = query.where(FamilyMemory.event_date >= start_date)
        
        if end_date:
            query = query.where(FamilyMemory.event_date <= end_date)
        
        query = query.order_by(FamilyMemory.event_date.desc(), FamilyMemory.created_at.desc())
        
        result = await db.execute(query)
        memories = result.scalars().all()
        
        memory_list = [
            FamilyMemoryBase(
                id=m.id,
                familyId=m.family_id,
                title=m.title,
                type=FamilyMemoryType(m.type),
                description=m.description,
                content=m.content,
                eventDate=m.event_date,
                location=m.location,
                mediaUrl=m.media_url,
                mediaType=m.media_type,
                tags=m.tags,
                createdAt=m.created_at,
                updatedAt=m.updated_at
            ) for m in memories
        ]
        
        return ApiResponse(
            success=True,
            data=FamilyMemoryListResponse(
                total=len(memory_list),
                memories=memory_list
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取家族记忆列表失败: {str(e)}")


@router.get("/family-memories/timeline", response_model=ApiResponse[FamilyMemoryTimelineResponse])
async def get_family_memory_timeline(
    limit: int = 20,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        query = select(FamilyMemory).where(
            FamilyMemory.deleted_at.is_(None)
        ).order_by(
            FamilyMemory.event_date.desc(), 
            FamilyMemory.created_at.desc()
        ).limit(limit)
        
        result = await db.execute(query)
        memories = result.scalars().all()
        
        timeline_items = [
            FamilyMemoryTimelineItem(
                id=m.id,
                title=m.title,
                type=FamilyMemoryType(m.type),
                description=m.description,
                eventDate=m.event_date,
                location=m.location,
                mediaUrl=m.media_url,
                mediaType=m.media_type,
                createdAt=m.created_at
            ) for m in memories
        ]
        
        return ApiResponse(
            success=True,
            data=FamilyMemoryTimelineResponse(
                total=len(timeline_items),
                items=timeline_items
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取家族记忆时间轴失败: {str(e)}")


@router.get("/family-memories/{memory_id}", response_model=ApiResponse[FamilyMemoryBase])
async def get_family_memory(
    memory_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(FamilyMemory).where(
            FamilyMemory.id == memory_id,
            FamilyMemory.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        memory = result.scalar_one_or_none()
        
        if not memory:
            raise HTTPException(status_code=404, detail="家族记忆不存在")
        
        return ApiResponse(
            success=True,
            data=FamilyMemoryBase(
                id=memory.id,
                familyId=memory.family_id,
                title=memory.title,
                type=FamilyMemoryType(memory.type),
                description=memory.description,
                content=memory.content,
                eventDate=memory.event_date,
                location=memory.location,
                mediaUrl=memory.media_url,
                mediaType=memory.media_type,
                tags=memory.tags,
                createdAt=memory.created_at,
                updatedAt=memory.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取家族记忆详情失败: {str(e)}")


@router.put("/family-memories/{memory_id}", response_model=ApiResponse[FamilyMemoryBase])
async def update_family_memory(
    memory_id: str,
    request: FamilyMemoryUpdateRequest,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(FamilyMemory).where(
            FamilyMemory.id == memory_id,
            FamilyMemory.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        memory = result.scalar_one_or_none()
        
        if not memory:
            raise HTTPException(status_code=404, detail="家族记忆不存在")
        
        if request.title is not None:
            memory.title = request.title
        if request.type is not None:
            memory.type = request.type.value
        if request.description is not None:
            memory.description = request.description
        if request.content is not None:
            memory.content = request.content
        if request.event_date is not None:
            memory.event_date = request.event_date
        if request.location is not None:
            memory.location = request.location
        if request.media_url is not None:
            memory.media_url = request.media_url
        if request.media_type is not None:
            memory.media_type = request.media_type
        if request.tags is not None:
            memory.tags = request.tags
        if request.meta_data is not None:
            memory.meta_data = request.meta_data
        
        await db.commit()
        await db.refresh(memory)
        
        return ApiResponse(
            success=True,
            data=FamilyMemoryBase(
                id=memory.id,
                familyId=memory.family_id,
                title=memory.title,
                type=FamilyMemoryType(memory.type),
                description=memory.description,
                content=memory.content,
                eventDate=memory.event_date,
                location=memory.location,
                mediaUrl=memory.media_url,
                mediaType=memory.media_type,
                tags=memory.tags,
                createdAt=memory.created_at,
                updatedAt=memory.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新家族记忆失败: {str(e)}")


@router.delete("/family-memories/{memory_id}", response_model=ApiResponse)
async def delete_family_memory(
    memory_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(FamilyMemory).where(
            FamilyMemory.id == memory_id,
            FamilyMemory.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        memory = result.scalar_one_or_none()
        
        if not memory:
            raise HTTPException(status_code=404, detail="家族记忆不存在")
        
        memory.deleted_at = datetime.now()
        await db.commit()
        
        return ApiResponse(
            success=True,
            message="家族记忆已删除"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除家族记忆失败: {str(e)}")


@router.post("/family-memories/upload", response_model=ApiResponse[FamilyMemoryBase])
async def upload_family_memory_with_media(
    title: str = Form(...),
    type: FamilyMemoryType = Form(FamilyMemoryType.IMAGE),
    description: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    event_date: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        ensure_upload_dir()
        family = await get_or_create_default_family(db)
        
        media_url = None
        media_type = None
        
        if file and file.content_type:
            if file.content_type.startswith("image/") or file.content_type.startswith("video/"):
                file_ext = os.path.splitext(file.filename)[1].lower() if file.filename else ".jpg"
                new_filename = f"{generate_uuid()}{file_ext}"
                file_path = os.path.join(settings.UPLOAD_DIR, "family_memories", new_filename)
                
                content_data = await file.read()
                with open(file_path, "wb") as f:
                    f.write(content_data)
                
                media_url = f"/uploads/family_memories/{new_filename}"
                media_type = "image" if file.content_type.startswith("image/") else "video"
        
        tags_list = None
        if tags:
            tags_list = [t.strip() for t in tags.split(",") if t.strip()]
        
        memory = FamilyMemory(
            id=generate_uuid(),
            family_id=family.id,
            title=title,
            type=type.value,
            description=description,
            content=content,
            event_date=event_date if event_date else datetime.now().isoformat(),
            location=location,
            media_url=media_url,
            media_type=media_type,
            tags=tags_list
        )
        
        db.add(memory)
        await db.commit()
        await db.refresh(memory)
        
        return ApiResponse(
            success=True,
            data=FamilyMemoryBase(
                id=memory.id,
                familyId=memory.family_id,
                title=memory.title,
                type=FamilyMemoryType(memory.type),
                description=memory.description,
                content=memory.content,
                eventDate=memory.event_date,
                location=memory.location,
                mediaUrl=memory.media_url,
                mediaType=memory.media_type,
                tags=memory.tags,
                createdAt=memory.created_at,
                updatedAt=memory.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传家族记忆失败: {str(e)}")
