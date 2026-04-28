from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.database import get_async_session
from app.models import Memory, Avatar, MemoryType
from app.schemas import (
    ApiResponse,
    MemoryBase, MemoryListResponse, MemoryCreateRequest, MemoryUpdateRequest
)

router = APIRouter(tags=["记忆管理"])


@router.get("/memories", response_model=ApiResponse[MemoryListResponse])
async def get_memories(
    avatar_id: Optional[str] = None,
    type: Optional[MemoryType] = None,
    tag: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        query = select(Memory).where(Memory.deleted_at.is_(None))
        
        if avatar_id:
            query = query.where(Memory.avatar_id == avatar_id)
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取记忆列表失败: {str(e)}")


@router.get("/memories/{memory_id}", response_model=ApiResponse)
async def get_memory(
    memory_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(Memory).where(Memory.id == memory_id, Memory.deleted_at.is_(None))
        result = await db.execute(stmt)
        memory = result.scalar_one_or_none()
        
        if not memory:
            raise HTTPException(status_code=404, detail="记忆不存在")
        
        return ApiResponse(
            success=True,
            data={
                "id": memory.id,
                "avatarId": memory.avatar_id,
                "title": memory.title,
                "type": memory.type,
                "content": memory.content,
                "description": memory.description,
                "tags": memory.tags,
                "metadata": memory.meta_data,
                "createdAt": memory.created_at,
                "updatedAt": memory.updated_at
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取记忆详情失败: {str(e)}")


@router.post("/memories", response_model=ApiResponse)
async def create_memory(
    request: MemoryCreateRequest,
    db: AsyncSession = Depends(get_async_session)
):
    if not request.avatar_id or not request.title or not request.content:
        raise HTTPException(status_code=400, detail="缺少必要参数: avatar_id, title, content 为必填项")
    
    valid_types = [MemoryType.TEXT, MemoryType.IMAGE, MemoryType.VIDEO]
    if request.type not in valid_types:
        raise HTTPException(status_code=400, detail="不支持的记忆类型，仅支持 text、image、video")
    
    try:
        avatar_stmt = select(Avatar).where(Avatar.id == request.avatar_id, Avatar.deleted_at.is_(None))
        avatar_result = await db.execute(avatar_stmt)
        avatar = avatar_result.scalar_one_or_none()
        
        if not avatar:
            raise HTTPException(status_code=404, detail="关联的数字人不存在")
        
        import time
        import random
        memory_id = f"memory_{int(time.time() * 1000)}_{''.join(random.choices('abcdef0123456789', k=6))}"
        
        now = datetime.now()
        
        memory = Memory(
            id=memory_id,
            avatar_id=request.avatar_id,
            title=request.title,
            type=request.type,
            content=request.content,
            description=request.description,
            tags=request.tags,
            meta_data=request.meta_data,
            created_at=now,
            updated_at=now
        )
        
        db.add(memory)
        await db.commit()
        
        return ApiResponse(
            success=True,
            data={
                "id": memory.id,
                "avatarId": memory.avatar_id,
                "title": memory.title,
                "type": memory.type,
                "createdAt": memory.created_at,
                "message": "记忆创建成功"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建记忆失败: {str(e)}")


@router.put("/memories/{memory_id}", response_model=ApiResponse)
async def update_memory(
    memory_id: str,
    request: MemoryUpdateRequest,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(Memory).where(Memory.id == memory_id, Memory.deleted_at.is_(None))
        result = await db.execute(stmt)
        memory = result.scalar_one_or_none()
        
        if not memory:
            raise HTTPException(status_code=404, detail="记忆不存在")
        
        if request.title:
            memory.title = request.title
        if request.type:
            valid_types = [MemoryType.TEXT, MemoryType.IMAGE, MemoryType.VIDEO]
            if request.type not in valid_types:
                raise HTTPException(status_code=400, detail="不支持的记忆类型")
            memory.type = request.type
        if request.content:
            memory.content = request.content
        if request.description is not None:
            memory.description = request.description
        if request.tags is not None:
            memory.tags = request.tags
        if request.meta_data is not None:
            memory.meta_data = request.meta_data
        
        memory.updated_at = datetime.now()
        
        await db.commit()
        
        return ApiResponse(
            success=True,
            data={
                "id": memory.id,
                "title": memory.title,
                "type": memory.type,
                "updatedAt": memory.updated_at,
                "message": "记忆更新成功"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新记忆失败: {str(e)}")


@router.delete("/memories/{memory_id}", response_model=ApiResponse)
async def delete_memory(
    memory_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(Memory).where(Memory.id == memory_id, Memory.deleted_at.is_(None))
        result = await db.execute(stmt)
        memory = result.scalar_one_or_none()
        
        if not memory:
            raise HTTPException(status_code=404, detail="记忆不存在")
        
        memory.deleted_at = datetime.now()
        await db.commit()
        
        return ApiResponse(
            success=True,
            message="记忆已删除"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除记忆失败: {str(e)}")


@router.post("/memories/batch", response_model=ApiResponse)
async def batch_create_memories(
    request: dict,
    db: AsyncSession = Depends(get_async_session)
):
    memories = request.get("memories", [])
    
    if not memories or len(memories) == 0:
        raise HTTPException(status_code=400, detail="请提供至少一个记忆")
    
    results = []
    errors = []
    
    import time
    import random
    
    for i, memory_data in enumerate(memories):
        try:
            if not memory_data.get("avatarId") or not memory_data.get("title") or not memory_data.get("content"):
                raise ValueError("缺少必要参数")
            
            valid_types = ["text", "image", "video"]
            if memory_data.get("type") and memory_data["type"] not in valid_types:
                raise ValueError("不支持的记忆类型")
            
            avatar_stmt = select(Avatar).where(
                Avatar.id == memory_data["avatarId"],
                Avatar.deleted_at.is_(None)
            )
            avatar_result = await db.execute(avatar_stmt)
            avatar = avatar_result.scalar_one_or_none()
            
            if not avatar:
                raise ValueError("关联的数字人不存在")
            
            memory_id = f"memory_{int(time.time() * 1000)}_{i}"
            now = datetime.now()
            
            memory = Memory(
                id=memory_id,
                avatar_id=memory_data["avatarId"],
                title=memory_data["title"],
                type=memory_data.get("type", "text"),
                content=memory_data["content"],
                description=memory_data.get("description"),
                tags=memory_data.get("tags"),
                meta_data=memory_data.get("metadata"),
                created_at=now,
                updated_at=now
            )
            
            db.add(memory)
            results.append({
                "index": i,
                "success": True,
                "id": memory.id,
                "title": memory.title
            })
            
        except Exception as e:
            errors.append({
                "index": i,
                "success": False,
                "error": str(e)
            })
    
    if len(results) > 0:
        await db.commit()
    
    return ApiResponse(
        success=True,
        data={
            "total": len(memories),
            "successCount": len(results),
            "errorCount": len(errors),
            "results": results,
            "errors": errors
        }
    )
