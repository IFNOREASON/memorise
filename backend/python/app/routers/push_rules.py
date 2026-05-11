from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, or_
from sqlalchemy.orm import selectinload
import uuid

from app.database import get_async_session
from app.models import (
    PushRule, PushChannel, AnniversaryType,
    Family, FamilyUser, User
)
from app.schemas import (
    ApiResponse,
    PushRuleBase, PushRuleCreateRequest, PushRuleUpdateRequest,
    PushRuleListResponse
)
from app.permissions import (
    viewer_required, editor_required, admin_required,
    has_permission, PermissionLevel
)

router = APIRouter(tags=["推送规则管理"])


def generate_id() -> str:
    return str(uuid.uuid4())


async def get_push_rule_by_id(db: AsyncSession, rule_id: str, family_id: str, user_id: str) -> Optional[PushRule]:
    stmt = (
        select(PushRule)
        .where(
            PushRule.id == rule_id,
            PushRule.family_id == family_id,
            PushRule.user_id == user_id
        )
        .options(selectinload(PushRule.user))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@router.get("/push-rules", response_model=ApiResponse[PushRuleListResponse])
async def get_push_rules(
    anniversary_type: Optional[str] = None,
    is_enabled: Optional[bool] = None,
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        query = (
            select(PushRule)
            .where(
                PushRule.family_id == family.id,
                PushRule.user_id == current_user.id
            )
            .options(selectinload(PushRule.user))
        )

        if anniversary_type:
            query = query.where(PushRule.anniversary_type == anniversary_type)
        if is_enabled is not None:
            query = query.where(PushRule.is_enabled == is_enabled)

        query = query.order_by(PushRule.created_at.desc())

        result = await db.execute(query)
        rules = result.scalars().all()

        rule_list = []
        for r in rules:
            rule_list.append(PushRuleBase(
                id=r.id,
                familyId=r.family_id,
                userId=r.user_id,
                anniversaryType=r.anniversary_type,
                pushChannels=[PushChannel(c) for c in r.push_channels] if r.push_channels else [],
                advanceDays=r.advance_days,
                pushTime=r.push_time,
                isEnabled=r.is_enabled,
                createdAt=r.created_at,
                updatedAt=r.updated_at
            ))

        return ApiResponse(
            success=True,
            data=PushRuleListResponse(
                total=len(rule_list),
                rules=rule_list
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取推送规则列表失败: {str(e)}")


@router.get("/push-rules/{rule_id}", response_model=ApiResponse[PushRuleBase])
async def get_push_rule(
    rule_id: str,
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        rule = await get_push_rule_by_id(db, rule_id, family.id, current_user.id)

        if not rule:
            raise HTTPException(status_code=404, detail="推送规则不存在")

        return ApiResponse(
            success=True,
            data=PushRuleBase(
                id=rule.id,
                familyId=rule.family_id,
                userId=rule.user_id,
                anniversaryType=rule.anniversary_type,
                pushChannels=[PushChannel(c) for c in rule.push_channels] if rule.push_channels else [],
                advanceDays=rule.advance_days,
                pushTime=rule.push_time,
                isEnabled=rule.is_enabled,
                createdAt=rule.created_at,
                updatedAt=rule.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取推送规则失败: {str(e)}")


@router.post("/push-rules", response_model=ApiResponse[PushRuleBase])
async def create_push_rule(
    request: PushRuleCreateRequest,
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        if request.advance_days < 0 or request.advance_days > 30:
            raise HTTPException(status_code=400, detail="提前天数应在 0-30 天之间")

        import re
        if not re.match(r'^\d{2}:\d{2}$', request.push_time):
            raise HTTPException(status_code=400, detail="推送时间格式错误，应为 HH:MM")

        existing_query = (
            select(PushRule)
            .where(
                PushRule.family_id == family.id,
                PushRule.user_id == current_user.id,
                PushRule.anniversary_type == (request.anniversary_type.value if request.anniversary_type else None)
            )
        )
        existing_result = await db.execute(existing_query)
        existing_rule = existing_result.scalar_one_or_none()

        if existing_rule:
            raise HTTPException(status_code=400, detail="该类型的推送规则已存在，请修改现有规则")

        rule = PushRule(
            id=generate_id(),
            family_id=family.id,
            user_id=current_user.id,
            anniversary_type=request.anniversary_type.value if request.anniversary_type else None,
            push_channels=[c.value for c in request.push_channels] if request.push_channels else [],
            advance_days=request.advance_days,
            push_time=request.push_time,
            is_enabled=True
        )
        db.add(rule)
        await db.commit()
        await db.refresh(rule)

        return ApiResponse(
            success=True,
            data=PushRuleBase(
                id=rule.id,
                familyId=rule.family_id,
                userId=rule.user_id,
                anniversaryType=rule.anniversary_type,
                pushChannels=[PushChannel(c) for c in rule.push_channels] if rule.push_channels else [],
                advanceDays=rule.advance_days,
                pushTime=rule.push_time,
                isEnabled=rule.is_enabled,
                createdAt=rule.created_at,
                updatedAt=rule.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建推送规则失败: {str(e)}")


@router.put("/push-rules/{rule_id}", response_model=ApiResponse[PushRuleBase])
async def update_push_rule(
    rule_id: str,
    request: PushRuleUpdateRequest,
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        rule = await get_push_rule_by_id(db, rule_id, family.id, current_user.id)

        if not rule:
            raise HTTPException(status_code=404, detail="推送规则不存在")

        if request.advance_days is not None:
            if request.advance_days < 0 or request.advance_days > 30:
                raise HTTPException(status_code=400, detail="提前天数应在 0-30 天之间")
            rule.advance_days = request.advance_days

        if request.push_time is not None:
            import re
            if not re.match(r'^\d{2}:\d{2}$', request.push_time):
                raise HTTPException(status_code=400, detail="推送时间格式错误，应为 HH:MM")
            rule.push_time = request.push_time

        if request.push_channels is not None:
            rule.push_channels = [c.value for c in request.push_channels] if request.push_channels else []

        if request.is_enabled is not None:
            rule.is_enabled = request.is_enabled

        if request.anniversary_type is not None:
            rule.anniversary_type = request.anniversary_type.value if request.anniversary_type else None

        await db.commit()
        await db.refresh(rule)

        return ApiResponse(
            success=True,
            data=PushRuleBase(
                id=rule.id,
                familyId=rule.family_id,
                userId=rule.user_id,
                anniversaryType=rule.anniversary_type,
                pushChannels=[PushChannel(c) for c in rule.push_channels] if rule.push_channels else [],
                advanceDays=rule.advance_days,
                pushTime=rule.push_time,
                isEnabled=rule.is_enabled,
                createdAt=rule.created_at,
                updatedAt=rule.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新推送规则失败: {str(e)}")


@router.delete("/push-rules/{rule_id}", response_model=ApiResponse)
async def delete_push_rule(
    rule_id: str,
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        rule = await get_push_rule_by_id(db, rule_id, family.id, current_user.id)

        if not rule:
            raise HTTPException(status_code=404, detail="推送规则不存在")

        await db.execute(delete(PushRule).where(PushRule.id == rule_id))
        await db.commit()

        return ApiResponse(
            success=True,
            message="推送规则已删除"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除推送规则失败: {str(e)}")
