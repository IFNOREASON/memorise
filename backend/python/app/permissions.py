from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List, Callable
from functools import wraps
from enum import Enum

from app.database import get_async_session
from app.models import User, Family, FamilyUser, FamilyRole
from app.routers.auth import get_current_user


class PermissionLevel(str, Enum):
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"
    HEAD = "head"


PERMISSION_ORDER = {
    PermissionLevel.VIEWER: 0,
    PermissionLevel.EDITOR: 1,
    PermissionLevel.ADMIN: 2,
    PermissionLevel.HEAD: 3,
}


def has_permission(user_role: str, required_permission: PermissionLevel) -> bool:
    user_level = PERMISSION_ORDER.get(PermissionLevel(user_role), 0)
    required_level = PERMISSION_ORDER.get(required_permission, 3)
    return user_level >= required_level


async def get_user_family_role(
    db: AsyncSession,
    user_id: str,
    family_id: Optional[str] = None
) -> Optional[FamilyUser]:
    if family_id:
        stmt = select(FamilyUser).where(
            FamilyUser.user_id == user_id,
            FamilyUser.family_id == family_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    else:
        stmt = select(FamilyUser).where(FamilyUser.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


async def get_user_default_family(
    db: AsyncSession,
    user_id: str
) -> Optional[Family]:
    family_user_stmt = (
        select(FamilyUser)
        .where(FamilyUser.user_id == user_id)
        .order_by(FamilyUser.created_at)
    )
    family_user_result = await db.execute(family_user_stmt)
    family_user = family_user_result.scalars().first()
    
    if family_user:
        family_stmt = select(Family).where(Family.id == family_user.family_id)
        family_result = await db.execute(family_stmt)
        return family_result.scalar_one_or_none()
    return None


async def ensure_user_family(
    db: AsyncSession,
    user: User,
    family_id: Optional[str] = None
) -> tuple[Optional[Family], Optional[FamilyUser]]:
    if family_id:
        family_user = await get_user_family_role(db, user.id, family_id)
    else:
        family_user = await get_user_family_role(db, user.id)
    
    if family_user:
        family_stmt = select(Family).where(Family.id == family_user.family_id)
        family_result = await db.execute(family_stmt)
        family = family_result.scalar_one_or_none()
        return family, family_user
    
    return None, None


class PermissionChecker:
    def __init__(self, required_permission: PermissionLevel):
        self.required_permission = required_permission
    
    async def __call__(
        self,
        request: Request,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session)
    ) -> tuple[User, Family, FamilyUser]:
        family_id = request.headers.get("X-Family-Id")
        family, family_user = await ensure_user_family(db, current_user, family_id)
        
        if not family or not family_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户未关联任何家族"
            )
        
        if not has_permission(family_user.role, self.required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要 {self.required_permission.value} 或更高权限"
            )
        
        return current_user, family, family_user


async def get_current_user_with_family(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> tuple[User, Optional[Family], Optional[FamilyUser]]:
    family_id = request.headers.get("X-Family-Id")
    family, family_user = await ensure_user_family(db, current_user, family_id)
    return current_user, family, family_user


def require_permission(permission: PermissionLevel) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator


viewer_required = PermissionChecker(PermissionLevel.VIEWER)
editor_required = PermissionChecker(PermissionLevel.EDITOR)
admin_required = PermissionChecker(PermissionLevel.ADMIN)
head_required = PermissionChecker(PermissionLevel.HEAD)
