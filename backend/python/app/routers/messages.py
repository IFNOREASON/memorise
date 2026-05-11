from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, or_, and_, func
from sqlalchemy.orm import selectinload
import uuid

from app.database import get_async_session
from app.models import (
    Message, MessageStatus, MessageType,
    Anniversary, Family, FamilyUser, User
)
from app.schemas import (
    ApiResponse,
    MessageBase, MessageListResponse, MessageMarkReadRequest
)
from app.permissions import (
    viewer_required, editor_required, admin_required,
    has_permission, PermissionLevel,
    get_current_user, get_current_user_with_family
)
from app.routers.auth import get_current_user

router = APIRouter(tags=["消息中心"])


def generate_id() -> str:
    return str(uuid.uuid4())


async def get_message_by_id(db: AsyncSession, message_id: str, user_id: str) -> Optional[Message]:
    stmt = (
        select(Message)
        .where(
            Message.id == message_id,
            Message.user_id == user_id,
            Message.deleted_at.is_(None)
        )
        .options(selectinload(Message.anniversary), selectinload(Message.family))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@router.get("/messages", response_model=ApiResponse[MessageListResponse])
async def get_messages(
    type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        count_query = (
            select(func.count(Message.id))
            .where(
                Message.user_id == current_user.id,
                Message.deleted_at.is_(None)
            )
        )

        if status:
            count_query = count_query.where(Message.status == status)
        if type:
            count_query = count_query.where(Message.type == type)

        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        unread_query = (
            select(func.count(Message.id))
            .where(
                Message.user_id == current_user.id,
                Message.status == "unread",
                Message.deleted_at.is_(None)
            )
        )
        unread_result = await db.execute(unread_query)
        unread_count = unread_result.scalar() or 0

        query = (
            select(Message)
            .where(
                Message.user_id == current_user.id,
                Message.deleted_at.is_(None)
            )
            .options(selectinload(Message.anniversary), selectinload(Message.family))
        )

        if status:
            query = query.where(Message.status == status)
        if type:
            query = query.where(Message.type == type)

        query = query.order_by(Message.created_at.desc()).offset(offset).limit(limit)

        result = await db.execute(query)
        messages = result.scalars().all()

        message_list = []
        for m in messages:
            message_list.append(MessageBase(
                id=m.id,
                userId=m.user_id,
                familyId=m.family_id,
                anniversaryId=m.anniversary_id,
                type=m.type,
                title=m.title,
                content=m.content,
                status=m.status,
                readAt=m.read_at,
                createdAt=m.created_at
            ))

        return ApiResponse(
            success=True,
            data=MessageListResponse(
                total=total,
                unreadCount=unread_count,
                messages=message_list
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取消息列表失败: {str(e)}")


@router.get("/messages/unread-count", response_model=ApiResponse[int])
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        query = (
            select(func.count(Message.id))
            .where(
                Message.user_id == current_user.id,
                Message.status == "unread",
                Message.deleted_at.is_(None)
            )
        )
        result = await db.execute(query)
        unread_count = result.scalar() or 0

        return ApiResponse(success=True, data=unread_count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取未读消息数失败: {str(e)}")


@router.get("/messages/{message_id}", response_model=ApiResponse[MessageBase])
async def get_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        message = await get_message_by_id(db, message_id, current_user.id)

        if not message:
            raise HTTPException(status_code=404, detail="消息不存在")

        if message.status == "unread":
            message.status = "read"
            message.read_at = datetime.now()
            await db.commit()
            await db.refresh(message)

        return ApiResponse(
            success=True,
            data=MessageBase(
                id=message.id,
                userId=message.user_id,
                familyId=message.family_id,
                anniversaryId=message.anniversary_id,
                type=message.type,
                title=message.title,
                content=message.content,
                status=message.status,
                readAt=message.read_at,
                createdAt=message.created_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取消息失败: {str(e)}")


@router.post("/messages/mark-read", response_model=ApiResponse)
async def mark_messages_read(
    request: MessageMarkReadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        if request.mark_all:
            stmt = (
                update(Message)
                .where(
                    Message.user_id == current_user.id,
                    Message.status == "unread",
                    Message.deleted_at.is_(None)
                )
                .values(
                    status="read",
                    read_at=datetime.now()
                )
            )
            await db.execute(stmt)
            await db.commit()

            return ApiResponse(success=True, message="所有消息已标记为已读")
        elif request.message_ids:
            stmt = (
                update(Message)
                .where(
                    Message.id.in_(request.message_ids),
                    Message.user_id == current_user.id,
                    Message.status == "unread",
                    Message.deleted_at.is_(None)
                )
                .values(
                    status="read",
                    read_at=datetime.now()
                )
            )
            await db.execute(stmt)
            await db.commit()

            return ApiResponse(success=True, message="消息已标记为已读")
        else:
            raise HTTPException(status_code=400, detail="请提供要标记的消息ID或设置 mark_all=true")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"标记消息已读失败: {str(e)}")


@router.delete("/messages/{message_id}", response_model=ApiResponse)
async def delete_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        message = await get_message_by_id(db, message_id, current_user.id)

        if not message:
            raise HTTPException(status_code=404, detail="消息不存在")

        message.deleted_at = datetime.now()
        message.status = "deleted"
        await db.commit()

        return ApiResponse(success=True, message="消息已删除")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除消息失败: {str(e)}")


@router.delete("/messages", response_model=ApiResponse)
async def delete_all_messages(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = (
            update(Message)
            .where(
                Message.user_id == current_user.id,
                Message.deleted_at.is_(None)
            )
            .values(
                deleted_at=datetime.now(),
                status="deleted"
            )
        )
        await db.execute(stmt)
        await db.commit()

        return ApiResponse(success=True, message="所有消息已删除")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除所有消息失败: {str(e)}")
