from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, or_
from sqlalchemy.orm import selectinload
import uuid
import re

from app.database import get_async_session
from app.models import (
    User, Family, FamilyUser, FamilyMember, FamilyInvitation,
    FamilyRole, InvitationStatus, MemberStatus, Gender
)
from app.schemas import (
    ApiResponse,
    UserResponse,
    FamilyBase,
    FamilyUserBase, FamilyUserListResponse, ChangeRoleRequest,
    InvitationBase, InvitationCreateRequest, InvitationListResponse,
    AcceptInvitationRequest, RejectInvitationRequest,
    UserFamilyInfo
)
from app.routers.auth import get_current_user
from app.permissions import (
    PermissionLevel, has_permission, get_user_family_role,
    admin_required, head_required, viewer_required
)
from app.services.log_service import log_service

router = APIRouter(tags=["家族成员与权限管理"])


def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


async def get_or_create_default_family(db: AsyncSession) -> Family:
    stmt = select(Family).order_by(Family.created_at.desc())
    result = await db.execute(stmt)
    family = result.scalar_one_or_none()

    if not family:
        family = Family(
            id=str(uuid.uuid4()),
            hall_name="陇西堂",
            surname="李",
            ancestor="李太白",
            description="本族源自陇西李氏，世代耕读传家，忠厚立世。",
            zi_bei=["元", "亨", "利", "贞", "仁", "义", "礼", "智", "信"]
        )
        db.add(family)
        await db.commit()
        await db.refresh(family)

    return family


@router.get("/family/users", response_model=ApiResponse[FamilyUserListResponse])
async def get_family_users(
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        query = (
            select(FamilyUser)
            .where(FamilyUser.family_id == family.id)
            .options(selectinload(FamilyUser.user))
        )

        if role:
            query = query.where(FamilyUser.role == role)
        if search:
            query = query.join(User).where(
                or_(
                    User.username.contains(search),
                    User.nickname.contains(search)
                )
            )

        query = query.order_by(FamilyUser.created_at)
        result = await db.execute(query)
        family_users = result.scalars().all()

        user_list = []
        for fu in family_users:
            user_resp = None
            if fu.user:
                user_resp = UserResponse.model_validate(fu.user)
            user_list.append(FamilyUserBase(
                id=fu.id,
                familyId=fu.family_id,
                userId=fu.user_id,
                role=FamilyRole(fu.role),
                user=user_resp,
                createdAt=fu.created_at,
                updatedAt=fu.updated_at
            ))

        return ApiResponse(
            success=True,
            data=FamilyUserListResponse(
                total=len(user_list),
                familyUsers=user_list
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取家族用户列表失败: {str(e)}")


@router.put("/family/users/role", response_model=ApiResponse[FamilyUserBase])
async def change_user_role(
    request: ChangeRoleRequest,
    user_and_family: tuple = Depends(admin_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        if request.new_role == FamilyRole.HEAD:
            if family_user.role != FamilyRole.HEAD.value:
                raise HTTPException(status_code=403, detail="只有族长才能指定新族长")
        
        target_fu_stmt = (
            select(FamilyUser)
            .where(
                FamilyUser.user_id == request.user_id,
                FamilyUser.family_id == family.id
            )
            .options(selectinload(FamilyUser.user))
        )
        target_fu_result = await db.execute(target_fu_stmt)
        target_fu = target_fu_result.scalar_one_or_none()

        if not target_fu:
            raise HTTPException(status_code=404, detail="该用户不在家族中")

        old_role = target_fu.role
        target_fu.role = request.new_role.value
        await db.commit()
        await db.refresh(target_fu)

        if target_fu.user:
            await log_service.log_role_change(
                db=db,
                user=current_user,
                target_user=target_fu.user,
                family=family,
                old_role=old_role,
                new_role=request.new_role.value
            )

        user_resp = UserResponse.model_validate(target_fu.user) if target_fu.user else None
        return ApiResponse(
            success=True,
            data=FamilyUserBase(
                id=target_fu.id,
                familyId=target_fu.family_id,
                userId=target_fu.user_id,
                role=FamilyRole(target_fu.role),
                user=user_resp,
                createdAt=target_fu.created_at,
                updatedAt=target_fu.updated_at
            ),
            message="角色已更新"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新角色失败: {str(e)}")


@router.post("/family/invitations", response_model=ApiResponse[InvitationBase])
async def create_invitation(
    request: InvitationCreateRequest,
    request_obj: Request,
    user_and_family: tuple = Depends(admin_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        if not is_valid_email(request.invitee_email):
            raise HTTPException(status_code=400, detail="邮箱格式不正确")

        existing_inv_stmt = (
            select(FamilyInvitation)
            .where(
                FamilyInvitation.invitee_email == request.invitee_email,
                FamilyInvitation.family_id == family.id,
                FamilyInvitation.status == InvitationStatus.PENDING.value
            )
        )
        existing_inv_result = await db.execute(existing_inv_stmt)
        existing_inv = existing_inv_result.scalar_one_or_none()

        if existing_inv:
            raise HTTPException(status_code=400, detail="该邮箱已有未处理的邀请")

        target_user_stmt = select(User).where(User.username == request.invitee_email)
        target_user_result = await db.execute(target_user_stmt)
        target_user = target_user_result.scalar_one_or_none()

        if target_user:
            existing_fu_stmt = (
                select(FamilyUser)
                .where(
                    FamilyUser.user_id == target_user.id,
                    FamilyUser.family_id == family.id
                )
            )
            existing_fu_result = await db.execute(existing_fu_stmt)
            existing_fu = existing_fu_result.scalar_one_or_none()
            if existing_fu:
                raise HTTPException(status_code=400, detail="该用户已在家族中")

        expires_at = datetime.utcnow() + timedelta(days=7)
        invitation = FamilyInvitation(
            id=str(uuid.uuid4()),
            family_id=family.id,
            inviter_id=current_user.id,
            invitee_email=request.invitee_email,
            invitee_user_id=target_user.id if target_user else None,
            status=InvitationStatus.PENDING.value,
            role=request.role.value,
            message=request.message,
            expires_at=expires_at
        )
        db.add(invitation)
        await db.commit()
        await db.refresh(invitation)

        await log_service.log_invite(
            db=db,
            user=current_user,
            invitee_email=request.invitee_email,
            family=family,
            role=request.role.value,
            ip_address=request_obj.client.host if request_obj.client else None,
            user_agent=request_obj.headers.get("user-agent")
        )

        return ApiResponse(
            success=True,
            data=InvitationBase(
                id=invitation.id,
                familyId=invitation.family_id,
                inviterId=invitation.inviter_id,
                inviteeEmail=invitation.invitee_email,
                inviteeUserId=invitation.invitee_user_id,
                status=InvitationStatus(invitation.status),
                role=FamilyRole(invitation.role),
                message=invitation.message,
                expiresAt=invitation.expires_at,
                createdAt=invitation.created_at,
                updatedAt=invitation.updated_at
            ),
            message="邀请已发送"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建邀请失败: {str(e)}")


@router.get("/family/invitations", response_model=ApiResponse[InvitationListResponse])
async def get_invitations(
    status: Optional[str] = Query(None),
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        query = (
            select(FamilyInvitation)
            .where(FamilyInvitation.family_id == family.id)
            .options(
                selectinload(FamilyInvitation.inviter),
                selectinload(FamilyInvitation.family)
            )
        )

        if status:
            query = query.where(FamilyInvitation.status == status)

        query = query.order_by(FamilyInvitation.created_at.desc())
        result = await db.execute(query)
        invitations = result.scalars().all()

        inv_list = []
        for inv in invitations:
            inviter_resp = UserResponse.model_validate(inv.inviter) if inv.inviter else None
            family_resp = FamilyBase.model_validate(inv.family) if inv.family else None
            inv_list.append(InvitationBase(
                id=inv.id,
                familyId=inv.family_id,
                inviterId=inv.inviter_id,
                inviteeEmail=inv.invitee_email,
                inviteeUserId=inv.invitee_user_id,
                status=InvitationStatus(inv.status),
                role=FamilyRole(inv.role),
                message=inv.message,
                expiresAt=inv.expires_at,
                acceptedAt=inv.accepted_at,
                rejectedAt=inv.rejected_at,
                inviter=inviter_resp,
                family=family_resp,
                createdAt=inv.created_at,
                updatedAt=inv.updated_at
            ))

        return ApiResponse(
            success=True,
            data=InvitationListResponse(
                total=len(inv_list),
                invitations=inv_list
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取邀请列表失败: {str(e)}")


@router.get("/my/invitations", response_model=ApiResponse[InvitationListResponse])
async def get_my_invitations(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        query = (
            select(FamilyInvitation)
            .where(
                or_(
                    FamilyInvitation.invitee_user_id == current_user.id,
                    FamilyInvitation.invitee_email == current_user.username
                )
            )
            .options(
                selectinload(FamilyInvitation.inviter),
                selectinload(FamilyInvitation.family)
            )
        )

        if status:
            query = query.where(FamilyInvitation.status == status)

        query = query.order_by(FamilyInvitation.created_at.desc())
        result = await db.execute(query)
        invitations = result.scalars().all()

        inv_list = []
        for inv in invitations:
            inviter_resp = UserResponse.model_validate(inv.inviter) if inv.inviter else None
            family_resp = FamilyBase.model_validate(inv.family) if inv.family else None
            inv_list.append(InvitationBase(
                id=inv.id,
                familyId=inv.family_id,
                inviterId=inv.inviter_id,
                inviteeEmail=inv.invitee_email,
                inviteeUserId=inv.invitee_user_id,
                status=InvitationStatus(inv.status),
                role=FamilyRole(inv.role),
                message=inv.message,
                expiresAt=inv.expires_at,
                acceptedAt=inv.accepted_at,
                rejectedAt=inv.rejected_at,
                inviter=inviter_resp,
                family=family_resp,
                createdAt=inv.created_at,
                updatedAt=inv.updated_at
            ))

        return ApiResponse(
            success=True,
            data=InvitationListResponse(
                total=len(inv_list),
                invitations=inv_list
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取我的邀请失败: {str(e)}")


@router.post("/my/invitations/accept", response_model=ApiResponse[FamilyUserBase])
async def accept_invitation(
    request: AcceptInvitationRequest,
    request_obj: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        inv_stmt = (
            select(FamilyInvitation)
            .where(
                FamilyInvitation.id == request.invitation_id,
                or_(
                    FamilyInvitation.invitee_user_id == current_user.id,
                    FamilyInvitation.invitee_email == current_user.username
                )
            )
            .options(selectinload(FamilyInvitation.family))
        )
        inv_result = await db.execute(inv_stmt)
        invitation = inv_result.scalar_one_or_none()

        if not invitation:
            raise HTTPException(status_code=404, detail="邀请不存在或不属于您")

        if invitation.status == InvitationStatus.ACCEPTED.value:
            raise HTTPException(status_code=400, detail="该邀请已被接受")
        if invitation.status == InvitationStatus.REJECTED.value:
            raise HTTPException(status_code=400, detail="该邀请已被拒绝")
        if invitation.status == InvitationStatus.EXPIRED.value:
            raise HTTPException(status_code=400, detail="该邀请已过期")

        now = datetime.utcnow()
        if now > invitation.expires_at:
            invitation.status = InvitationStatus.EXPIRED.value
            await db.commit()
            raise HTTPException(status_code=400, detail="该邀请已过期")

        existing_fu_stmt = (
            select(FamilyUser)
            .where(
                FamilyUser.user_id == current_user.id,
                FamilyUser.family_id == invitation.family_id
            )
        )
        existing_fu_result = await db.execute(existing_fu_stmt)
        existing_fu = existing_fu_result.scalar_one_or_none()

        if existing_fu:
            raise HTTPException(status_code=400, detail="您已加入该家族")

        family_user = FamilyUser(
            id=str(uuid.uuid4()),
            family_id=invitation.family_id,
            user_id=current_user.id,
            role=invitation.role
        )
        db.add(family_user)

        invitation.status = InvitationStatus.ACCEPTED.value
        invitation.invitee_user_id = current_user.id
        invitation.accepted_at = now
        await db.commit()
        await db.refresh(family_user)

        return ApiResponse(
            success=True,
            data=FamilyUserBase(
                id=family_user.id,
                familyId=family_user.family_id,
                userId=family_user.user_id,
                role=FamilyRole(family_user.role),
                user=UserResponse.model_validate(current_user),
                createdAt=family_user.created_at,
                updatedAt=family_user.updated_at
            ),
            message="已成功加入家族"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"接受邀请失败: {str(e)}")


@router.post("/my/invitations/reject", response_model=ApiResponse)
async def reject_invitation(
    request: RejectInvitationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        inv_stmt = (
            select(FamilyInvitation)
            .where(
                FamilyInvitation.id == request.invitation_id,
                or_(
                    FamilyInvitation.invitee_user_id == current_user.id,
                    FamilyInvitation.invitee_email == current_user.username
                )
            )
        )
        inv_result = await db.execute(inv_stmt)
        invitation = inv_result.scalar_one_or_none()

        if not invitation:
            raise HTTPException(status_code=404, detail="邀请不存在或不属于您")

        if invitation.status != InvitationStatus.PENDING.value:
            raise HTTPException(status_code=400, detail="该邀请已被处理")

        invitation.status = InvitationStatus.REJECTED.value
        invitation.rejection_reason = request.reason
        invitation.rejected_at = datetime.utcnow()
        await db.commit()

        return ApiResponse(success=True, message="已拒绝邀请")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"拒绝邀请失败: {str(e)}")


@router.get("/my/family", response_model=ApiResponse[UserFamilyInfo])
async def get_my_family_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        family_user_stmt = (
            select(FamilyUser)
            .where(FamilyUser.user_id == current_user.id)
            .options(selectinload(FamilyUser.family))
        )
        family_user_result = await db.execute(family_user_stmt)
        family_user = family_user_result.scalar_one_or_none()

        if not family_user:
            family = await get_or_create_default_family(db)
            
            family_user = FamilyUser(
                id=str(uuid.uuid4()),
                family_id=family.id,
                user_id=current_user.id,
                role=FamilyRole.HEAD.value
            )
            db.add(family_user)
            await db.commit()
            await db.refresh(family_user)
            await db.refresh(family)
        else:
            family = family_user.family

        members_stmt = (
            select(FamilyMember)
            .where(
                FamilyMember.family_id == family.id,
                FamilyMember.deleted_at.is_(None)
            )
        )
        members_result = await db.execute(members_stmt)
        members_count = len(members_result.scalars().all())

        return ApiResponse(
            success=True,
            data=UserFamilyInfo(
                family=FamilyBase.model_validate(family),
                role=FamilyRole(family_user.role),
                familyUser=FamilyUserBase(
                    id=family_user.id,
                    familyId=family_user.family_id,
                    userId=family_user.user_id,
                    role=FamilyRole(family_user.role),
                    createdAt=family_user.created_at,
                    updatedAt=family_user.updated_at
                ),
                memberCount=members_count
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取家族信息失败: {str(e)}")
