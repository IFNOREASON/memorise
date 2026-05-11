from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, or_, and_
from sqlalchemy.orm import selectinload
import uuid
import re

from app.database import get_async_session
from app.models import (
    Anniversary, AnniversaryType, RepeatType,
    FamilyMember, Family, FamilyUser
)
from app.schemas import (
    ApiResponse,
    AnniversaryBase, AnniversaryCreateRequest, AnniversaryUpdateRequest,
    AnniversaryListResponse, AnniversaryCalendarItem, AnniversaryCalendarResponse
)
from app.permissions import (
    viewer_required, editor_required, admin_required,
    has_permission, PermissionLevel
)
from app.services.log_service import log_service

router = APIRouter(tags=["纪念日管理"])


def generate_id() -> str:
    return str(uuid.uuid4())


def parse_date(date_str: str) -> tuple[Optional[int], int, int]:
    match = re.match(r'^(\d{4})?-?(\d{1,2})-(\d{1,2})$', date_str.strip())
    if not match:
        raise HTTPException(status_code=400, detail=f"日期格式错误: {date_str}，支持格式: YYYY-MM-DD 或 MM-DD")
    
    year_str, month_str, day_str = match.groups()
    year = int(year_str) if year_str else None
    month = int(month_str)
    day = int(day_str)
    
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail=f"月份无效: {month}")
    if day < 1 or day > 31:
        raise HTTPException(status_code=400, detail=f"日期无效: {day}")
    
    return year, month, day


async def get_anniversary_by_id(db: AsyncSession, anniversary_id: str, family_id: str) -> Optional[Anniversary]:
    stmt = (
        select(Anniversary)
        .where(
            Anniversary.id == anniversary_id,
            Anniversary.family_id == family_id,
            Anniversary.deleted_at.is_(None)
        )
        .options(selectinload(Anniversary.member))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def get_anniversary_type_label(anniversary_type: str) -> str:
    labels = {
        "birthday": "生日",
        "deathday": "忌日",
        "weddingday": "结婚日",
        "sacrificialday": "祭祀日"
    }
    return labels.get(anniversary_type, anniversary_type)


@router.get("/anniversaries", response_model=ApiResponse[AnniversaryListResponse])
async def get_anniversaries(
    type: Optional[str] = None,
    member_id: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        query = (
            select(Anniversary)
            .where(
                Anniversary.family_id == family.id,
                Anniversary.deleted_at.is_(None)
            )
            .options(selectinload(Anniversary.member))
        )

        if type:
            query = query.where(Anniversary.type == type)
        if member_id:
            query = query.where(Anniversary.member_id == member_id)
        if search:
            query = query.where(
                or_(
                    Anniversary.name.contains(search),
                    Anniversary.description.contains(search)
                )
            )
        if is_active is not None:
            query = query.where(Anniversary.is_active == is_active)

        query = query.order_by(Anniversary.month, Anniversary.day, Anniversary.created_at)

        result = await db.execute(query)
        anniversaries = result.scalars().all()

        anniversary_list = []
        for a in anniversaries:
            anniversary_list.append(AnniversaryBase(
                id=a.id,
                familyId=a.family_id,
                memberId=a.member_id,
                name=a.name,
                type=a.type,
                description=a.description,
                date=a.date,
                year=a.year,
                month=a.month,
                day=a.day,
                repeatType=a.repeat_type,
                isLunar=a.is_lunar,
                isActive=a.is_active,
                createdAt=a.created_at,
                updatedAt=a.updated_at
            ))

        return ApiResponse(
            success=True,
            data=AnniversaryListResponse(
                total=len(anniversary_list),
                anniversaries=anniversary_list
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取纪念日列表失败: {str(e)}")


@router.get("/anniversaries/calendar", response_model=ApiResponse[AnniversaryCalendarResponse])
async def get_anniversaries_calendar(
    year: Optional[int] = None,
    month: Optional[int] = None,
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        now = datetime.now()
        target_year = year if year else now.year
        target_month = month if month else now.month

        if target_month < 1 or target_month > 12:
            raise HTTPException(status_code=400, detail=f"无效的月份: {target_month}")

        query = (
            select(Anniversary)
            .where(
                Anniversary.family_id == family.id,
                Anniversary.deleted_at.is_(None),
                Anniversary.is_active == True,
                Anniversary.month == target_month
            )
            .options(selectinload(Anniversary.member))
            .order_by(Anniversary.day)
        )

        result = await db.execute(query)
        anniversaries = result.scalars().all()

        calendar_items = []
        for a in anniversaries:
            member_name = a.member.name if a.member else None
            calendar_items.append(AnniversaryCalendarItem(
                id=a.id,
                name=a.name,
                type=a.type,
                date=a.date,
                year=a.year,
                month=a.month,
                day=a.day,
                memberId=a.member_id,
                memberName=member_name,
                isLunar=a.is_lunar,
                description=a.description
            ))

        return ApiResponse(
            success=True,
            data=AnniversaryCalendarResponse(
                year=target_year,
                month=target_month,
                items=calendar_items
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日历数据失败: {str(e)}")


@router.get("/anniversaries/upcoming", response_model=ApiResponse[List[AnniversaryCalendarItem]])
async def get_upcoming_anniversaries(
    days: int = 7,
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        if days < 1 or days > 365:
            raise HTTPException(status_code=400, detail=f"天数范围无效: {days}，应在 1-365 之间")

        now = datetime.now()
        today_month = now.month
        today_day = now.day

        end_date = now + timedelta(days=days)
        end_month = end_date.month
        end_day = end_date.day

        query = (
            select(Anniversary)
            .where(
                Anniversary.family_id == family.id,
                Anniversary.deleted_at.is_(None),
                Anniversary.is_active == True
            )
            .options(selectinload(Anniversary.member))
        )

        if today_month == end_month:
            query = query.where(
                Anniversary.month == today_month,
                Anniversary.day >= today_day,
                Anniversary.day <= end_day
            )
        else:
            query = query.where(
                or_(
                    and_(Anniversary.month == today_month, Anniversary.day >= today_day),
                    and_(Anniversary.month > today_month, Anniversary.month < end_month),
                    and_(Anniversary.month == end_month, Anniversary.day <= end_day)
                )
            )

        query = query.order_by(Anniversary.month, Anniversary.day)

        result = await db.execute(query)
        anniversaries = result.scalars().all()

        calendar_items = []
        for a in anniversaries:
            member_name = a.member.name if a.member else None
            calendar_items.append(AnniversaryCalendarItem(
                id=a.id,
                name=a.name,
                type=a.type,
                date=a.date,
                year=a.year,
                month=a.month,
                day=a.day,
                memberId=a.member_id,
                memberName=member_name,
                isLunar=a.is_lunar,
                description=a.description
            ))

        return ApiResponse(success=True, data=calendar_items)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取即将到来的纪念日失败: {str(e)}")


@router.get("/anniversaries/{anniversary_id}", response_model=ApiResponse[AnniversaryBase])
async def get_anniversary(
    anniversary_id: str,
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        anniversary = await get_anniversary_by_id(db, anniversary_id, family.id)

        if not anniversary:
            raise HTTPException(status_code=404, detail="纪念日不存在")

        return ApiResponse(
            success=True,
            data=AnniversaryBase(
                id=anniversary.id,
                familyId=anniversary.family_id,
                memberId=anniversary.member_id,
                name=anniversary.name,
                type=anniversary.type,
                description=anniversary.description,
                date=anniversary.date,
                year=anniversary.year,
                month=anniversary.month,
                day=anniversary.day,
                repeatType=anniversary.repeat_type,
                isLunar=anniversary.is_lunar,
                isActive=anniversary.is_active,
                createdAt=anniversary.created_at,
                updatedAt=anniversary.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取纪念日信息失败: {str(e)}")


@router.post("/anniversaries", response_model=ApiResponse[AnniversaryBase])
async def create_anniversary(
    request: AnniversaryCreateRequest,
    request_obj: Request,
    user_and_family: tuple = Depends(editor_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        if not request.name.strip():
            raise HTTPException(status_code=400, detail="纪念日名称不能为空")

        year, month, day = parse_date(request.date)

        if request.member_id:
            member_stmt = select(FamilyMember).where(
                FamilyMember.id == request.member_id,
                FamilyMember.family_id == family.id,
                FamilyMember.deleted_at.is_(None)
            )
            member_result = await db.execute(member_stmt)
            member = member_result.scalar_one_or_none()
            if not member:
                raise HTTPException(status_code=404, detail="关联的成员不存在")

        anniversary = Anniversary(
            id=generate_id(),
            family_id=family.id,
            member_id=request.member_id,
            name=request.name,
            type=request.type.value,
            description=request.description,
            date=request.date,
            year=year if year else request.year,
            month=month,
            day=day,
            repeat_type=request.repeat_type.value,
            is_lunar=request.is_lunar,
            is_active=True
        )
        db.add(anniversary)
        await db.commit()
        await db.refresh(anniversary)

        return ApiResponse(
            success=True,
            data=AnniversaryBase(
                id=anniversary.id,
                familyId=anniversary.family_id,
                memberId=anniversary.member_id,
                name=anniversary.name,
                type=anniversary.type,
                description=anniversary.description,
                date=anniversary.date,
                year=anniversary.year,
                month=anniversary.month,
                day=anniversary.day,
                repeatType=anniversary.repeat_type,
                isLunar=anniversary.is_lunar,
                isActive=anniversary.is_active,
                createdAt=anniversary.created_at,
                updatedAt=anniversary.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建纪念日失败: {str(e)}")


@router.put("/anniversaries/{anniversary_id}", response_model=ApiResponse[AnniversaryBase])
async def update_anniversary(
    anniversary_id: str,
    request: AnniversaryUpdateRequest,
    request_obj: Request,
    user_and_family: tuple = Depends(editor_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        anniversary = await get_anniversary_by_id(db, anniversary_id, family.id)

        if not anniversary:
            raise HTTPException(status_code=404, detail="纪念日不存在")

        if request.member_id is not None and request.member_id != anniversary.member_id:
            if request.member_id:
                member_stmt = select(FamilyMember).where(
                    FamilyMember.id == request.member_id,
                    FamilyMember.family_id == family.id,
                    FamilyMember.deleted_at.is_(None)
                )
                member_result = await db.execute(member_stmt)
                member = member_result.scalar_one_or_none()
                if not member:
                    raise HTTPException(status_code=404, detail="关联的成员不存在")
            anniversary.member_id = request.member_id

        if request.name is not None:
            if not request.name.strip():
                raise HTTPException(status_code=400, detail="纪念日名称不能为空")
            anniversary.name = request.name

        if request.type is not None:
            anniversary.type = request.type.value

        if request.description is not None:
            anniversary.description = request.description

        if request.date is not None:
            year, month, day = parse_date(request.date)
            anniversary.date = request.date
            anniversary.year = year if year else request.year
            anniversary.month = month
            anniversary.day = day
        elif request.year is not None:
            anniversary.year = request.year

        if request.repeat_type is not None:
            anniversary.repeat_type = request.repeat_type.value

        if request.is_lunar is not None:
            anniversary.is_lunar = request.is_lunar

        if request.is_active is not None:
            anniversary.is_active = request.is_active

        await db.commit()
        await db.refresh(anniversary)

        return ApiResponse(
            success=True,
            data=AnniversaryBase(
                id=anniversary.id,
                familyId=anniversary.family_id,
                memberId=anniversary.member_id,
                name=anniversary.name,
                type=anniversary.type,
                description=anniversary.description,
                date=anniversary.date,
                year=anniversary.year,
                month=anniversary.month,
                day=anniversary.day,
                repeatType=anniversary.repeat_type,
                isLunar=anniversary.is_lunar,
                isActive=anniversary.is_active,
                createdAt=anniversary.created_at,
                updatedAt=anniversary.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新纪念日失败: {str(e)}")


@router.delete("/anniversaries/{anniversary_id}", response_model=ApiResponse)
async def delete_anniversary(
    anniversary_id: str,
    request_obj: Request,
    user_and_family: tuple = Depends(admin_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        anniversary = await get_anniversary_by_id(db, anniversary_id, family.id)

        if not anniversary:
            raise HTTPException(status_code=404, detail="纪念日不存在")

        anniversary.deleted_at = datetime.now()
        await db.commit()

        return ApiResponse(
            success=True,
            message="纪念日已删除"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除纪念日失败: {str(e)}")
