from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.database import get_async_session
from app.models import (
    User, Family, FamilyUser, OperationLog,
    OperationType, TargetType
)
from app.schemas import (
    ApiResponse,
    UserResponse,
    OperationLogBase, OperationLogListResponse
)
from app.routers.auth import get_current_user
from app.permissions import viewer_required

router = APIRouter(tags=["操作日志管理"])


@router.get("/logs", response_model=ApiResponse[OperationLogListResponse])
async def get_operation_logs(
    operation: Optional[str] = Query(None),
    target_type: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        query = (
            select(OperationLog)
            .where(OperationLog.family_id == family.id)
            .options(selectinload(OperationLog.user))
        )

        if operation:
            query = query.where(OperationLog.operation == operation)
        if target_type:
            query = query.where(OperationLog.target_type == target_type)
        if user_id:
            query = query.where(OperationLog.user_id == user_id)

        count_query = query
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        query = query.order_by(desc(OperationLog.created_at)).offset(offset).limit(limit)
        result = await db.execute(query)
        logs = result.scalars().all()

        log_list = []
        for log in logs:
            user_resp = UserResponse.model_validate(log.user) if log.user else None
            log_list.append(OperationLogBase(
                id=log.id,
                familyId=log.family_id,
                userId=log.user_id,
                operation=OperationType(log.operation),
                targetType=TargetType(log.target_type) if log.target_type else None,
                targetId=log.target_id,
                description=log.description,
                ipAddress=log.ip_address,
                userAgent=log.user_agent,
                beforeData=log.before_data,
                afterData=log.after_data,
                user=user_resp,
                createdAt=log.created_at
            ))

        return ApiResponse(
            success=True,
            data=OperationLogListResponse(
                total=total,
                logs=log_list
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取操作日志失败: {str(e)}")


@router.get("/logs/my", response_model=ApiResponse[OperationLogListResponse])
async def get_my_operation_logs(
    operation: Optional[str] = Query(None),
    target_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        query = (
            select(OperationLog)
            .where(OperationLog.user_id == current_user.id)
            .options(selectinload(OperationLog.user))
        )

        if operation:
            query = query.where(OperationLog.operation == operation)
        if target_type:
            query = query.where(OperationLog.target_type == target_type)

        count_query = query
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        query = query.order_by(desc(OperationLog.created_at)).offset(offset).limit(limit)
        result = await db.execute(query)
        logs = result.scalars().all()

        log_list = []
        for log in logs:
            user_resp = UserResponse.model_validate(log.user) if log.user else None
            log_list.append(OperationLogBase(
                id=log.id,
                familyId=log.family_id,
                userId=log.user_id,
                operation=OperationType(log.operation),
                targetType=TargetType(log.target_type) if log.target_type else None,
                targetId=log.target_id,
                description=log.description,
                ipAddress=log.ip_address,
                userAgent=log.user_agent,
                beforeData=log.before_data,
                afterData=log.after_data,
                user=user_resp,
                createdAt=log.created_at
            ))

        return ApiResponse(
            success=True,
            data=OperationLogListResponse(
                total=total,
                logs=log_list
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取我的操作日志失败: {str(e)}")


@router.get("/logs/operations", response_model=ApiResponse[List[str]])
async def get_operation_types():
    try:
        types = [t.value for t in OperationType]
        return ApiResponse(success=True, data=types)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取操作类型失败: {str(e)}")


@router.get("/logs/target-types", response_model=ApiResponse[List[str]])
async def get_target_types():
    try:
        types = [t.value for t in TargetType]
        return ApiResponse(success=True, data=types)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取目标类型失败: {str(e)}")
