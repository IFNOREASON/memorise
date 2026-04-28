from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.database import get_async_session
from app.models import (
    ChatSession, Avatar
)
from app.schemas import (
    ApiResponse,
    ChatSessionCreateRequest, ChatSessionResponse, ChatSessionListResponse,
    ChatMessage, ChatStreamRequest
)

router = APIRouter(tags=["聊天对话"])


@router.get("/chat/sessions", response_model=ApiResponse[ChatSessionListResponse])
async def get_chat_sessions(
    avatar_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        query = select(ChatSession)
        if avatar_id:
            query = query.where(ChatSession.avatar_id == avatar_id)
        query = query.order_by(ChatSession.updated_at.desc())
        
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        session_list = [
            ChatSessionResponse(
                id=s.id,
                avatar_id=s.avatar_id,
                avatar_name=s.avatar_name,
                avatar_avatar=s.avatar_avatar,
                title=s.title,
                message_count=s.message_count,
                created_at=s.created_at,
                updated_at=s.updated_at
            ) for s in sessions
        ]
        
        return ApiResponse(
            success=True,
            data=ChatSessionListResponse(
                total=len(session_list),
                sessions=session_list
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话列表失败: {str(e)}")


@router.post("/chat/sessions", response_model=ApiResponse)
async def create_chat_session(
    request: ChatSessionCreateRequest,
    db: AsyncSession = Depends(get_async_session)
):
    if not request.avatar_id:
        raise HTTPException(status_code=400, detail="缺少必要参数: avatar_id 为必填项")
    
    try:
        avatar_stmt = select(Avatar).where(
            Avatar.id == request.avatar_id,
            Avatar.deleted_at.is_(None)
        )
        avatar_result = await db.execute(avatar_stmt)
        avatar = avatar_result.scalar_one_or_none()
        
        if not avatar:
            raise HTTPException(status_code=404, detail="数字人不存在")
        
        if avatar.status not in ["active", "retry_pending"]:
            raise HTTPException(status_code=400, detail=f"数字人状态为 {avatar.status.value if hasattr(avatar.status, 'value') else avatar.status}，无法对话")
        
        import time
        import random
        session_id = f"chat_{int(time.time() * 1000)}_{''.join(random.choices('abcdef0123456789', k=6))}"
        
        now = datetime.now()
        
        title = f"与 {avatar.name} 的对话"
        if request.title:
            title = request.title
        
        session = ChatSession(
            id=session_id,
            avatar_id=request.avatar_id,
            avatar_name=avatar.name,
            avatar_avatar=avatar.avatar_url,
            title=title,
            message_count=0,
            messages=request.messages or [],
            created_at=now,
            updated_at=now
        )
        
        db.add(session)
        await db.commit()
        
        return ApiResponse(
            success=True,
            data={
                "sessionId": session.id,
                "avatarId": session.avatar_id,
                "avatarName": session.avatar_name,
                "title": session.title,
                "createdAt": session.created_at,
                "message": "对话会话已创建"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建会话失败: {str(e)}")


@router.get("/chat/sessions/{session_id}", response_model=ApiResponse)
async def get_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(ChatSession).where(ChatSession.id == session_id)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        avatar = None
        avatar_stmt = select(Avatar).where(
            Avatar.id == session.avatar_id,
            Avatar.deleted_at.is_(None)
        )
        avatar_result = await db.execute(avatar_stmt)
        avatar = avatar_result.scalar_one_or_none()
        
        return ApiResponse(
            success=True,
            data={
                "id": session.id,
                "avatarId": session.avatar_id,
                "avatarName": session.avatar_name,
                "avatarAvatar": session.avatar_avatar,
                "title": session.title,
                "messages": session.messages,
                "messageCount": session.message_count,
                "avatarStatus": avatar.status.value if avatar else None,
                "createdAt": session.created_at,
                "updatedAt": session.updated_at
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话详情失败: {str(e)}")


@router.put("/chat/sessions/{session_id}", response_model=ApiResponse)
async def update_chat_session(
    session_id: str,
    request: dict,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(ChatSession).where(ChatSession.id == session_id)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        if request.get("title"):
            session.title = request["title"]
        
        session.updated_at = datetime.now()
        
        await db.commit()
        
        return ApiResponse(
            success=True,
            data={
                "id": session.id,
                "title": session.title,
                "updatedAt": session.updated_at,
                "message": "会话已更新"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新会话失败: {str(e)}")


@router.delete("/chat/sessions/{session_id}", response_model=ApiResponse)
async def delete_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(ChatSession).where(ChatSession.id == session_id)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        await db.execute(delete(ChatSession).where(ChatSession.id == session_id))
        await db.commit()
        
        return ApiResponse(
            success=True,
            message="会话已删除"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除会话失败: {str(e)}")


@router.post("/chat/sessions/{session_id}/messages", response_model=ApiResponse)
async def send_chat_message(
    session_id: str,
    request: ChatStreamRequest,
    db: AsyncSession = Depends(get_async_session)
):
    if not request.messages or len(request.messages) == 0:
        raise HTTPException(status_code=400, detail="消息不能为空")
    
    try:
        stmt = select(ChatSession).where(ChatSession.id == session_id)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        avatar_stmt = select(Avatar).where(
            Avatar.id == session.avatar_id,
            Avatar.deleted_at.is_(None)
        )
        avatar_result = await db.execute(avatar_stmt)
        avatar = avatar_result.scalar_one_or_none()
        
        if not avatar:
            raise HTTPException(status_code=404, detail="关联的数字人不存在")
        
        if avatar.status not in ["active", "retry_pending"]:
            raise HTTPException(status_code=400, detail=f"数字人状态为 {avatar.status.value if hasattr(avatar.status, 'value') else avatar.status}，无法对话")
        
        messages = session.messages or []
        
        for msg in request.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp or datetime.now().isoformat()
            })
        
        messages = messages[-100:]
        
        from app.services import aliyun_service
        user_messages = [msg for msg in messages if msg["role"] == "user"]
        last_user_msg = user_messages[-1]["content"] if user_messages else "你好"
        
        ai_response = await aliyun_service.chat_with_avatar(
            avatar_name=avatar.name,
            relationship=avatar.relationship,
            description=avatar.description,
            messages=[
                {"role": "user", "content": last_user_msg}
            ]
        )
        
        assistant_msg = {
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        }
        messages.append(assistant_msg)
        
        session.messages = messages
        session.message_count = len(messages)
        session.updated_at = datetime.now()
        
        await db.commit()
        
        return ApiResponse(
            success=True,
            data={
                "sessionId": session.id,
                "message": {
                    "role": "assistant",
                    "content": ai_response,
                    "timestamp": assistant_msg["timestamp"]
                },
                "messageCount": session.message_count
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送消息失败: {str(e)}")
