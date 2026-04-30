from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, or_
from sqlalchemy.orm import selectinload
import uuid
import re
import secrets
import string

from app.database import get_async_session
from app.models import (
    User, Family, FamilyUser, FamilyMember, FamilyInvitation,
    FamilyRole, InvitationStatus, MemberStatus, Gender,
    CollaborationLink, CollaborationLinkStatus
)
from app.schemas import (
    ApiResponse,
    UserResponse,
    FamilyBase,
    FamilyUserBase, FamilyUserListResponse, ChangeRoleRequest,
    InvitationBase, InvitationCreateRequest, InvitationListResponse,
    AcceptInvitationRequest, RejectInvitationRequest,
    UserFamilyInfo, MyFamilyStatus, UserFamilyListItem,
    CollaborationLinkBase, CollaborationLinkListResponse,
    CreateCollaborationLinkRequest, UpdateCollaborationLinkRequest,
    JoinByLinkRequest, FamilyCreateRequest
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


def generate_link_code(length: int = 12) -> str:
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


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
        is_transferring_head = request.new_role == FamilyRole.HEAD

        if is_transferring_head:
            if family_user.role != FamilyRole.HEAD.value:
                raise HTTPException(status_code=403, detail="只有族长才能指定新族长")
            if request.user_id == current_user.id:
                raise HTTPException(status_code=400, detail="不能转让给自己")

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

        if is_transferring_head:
            family_user.role = FamilyRole.ADMIN.value
            family.head_user_id = target_fu.user_id

        await db.commit()
        await db.refresh(target_fu)

        if is_transferring_head:
            await db.refresh(family_user)
            await db.refresh(family)

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
        message = "角色已更新"
        if is_transferring_head:
            message = "族长已成功转让"

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
            message=message
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


@router.get("/my/family/status", response_model=ApiResponse[MyFamilyStatus])
async def get_my_family_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        family_users_stmt = (
            select(FamilyUser)
            .where(FamilyUser.user_id == current_user.id)
            .options(selectinload(FamilyUser.family))
            .order_by(FamilyUser.created_at)
        )
        family_users_result = await db.execute(family_users_stmt)
        family_users = family_users_result.scalars().all()

        if not family_users:
            return ApiResponse(
                success=True,
                data=MyFamilyStatus(
                    hasFamily=False,
                    families=[],
                    ownedFamily=None,
                    totalFamilies=0
                )
            )

        family_list = []
        owned_family = None

        for family_user in family_users:
            if not family_user.family:
                continue

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

            is_head = family_user.role == FamilyRole.HEAD.value
            family_item = UserFamilyListItem(
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
                memberCount=members_count,
                isHead=is_head
            )
            family_list.append(family_item)

            if is_head:
                owned_family = family_item

        return ApiResponse(
            success=True,
            data=MyFamilyStatus(
                hasFamily=len(family_list) > 0,
                families=family_list,
                ownedFamily=owned_family,
                totalFamilies=len(family_list)
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取家族状态失败: {str(e)}")


@router.get("/my/family", response_model=ApiResponse[UserFamilyInfo])
async def get_my_family_info(
    family_id: Optional[str] = Query(None, alias="familyId"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        if family_id:
            family_user_stmt = (
                select(FamilyUser)
                .where(
                    FamilyUser.user_id == current_user.id,
                    FamilyUser.family_id == family_id
                )
                .options(selectinload(FamilyUser.family))
            )
        else:
            family_user_stmt = (
                select(FamilyUser)
                .where(FamilyUser.user_id == current_user.id)
                .options(selectinload(FamilyUser.family))
                .order_by(FamilyUser.created_at)
            )

        family_user_result = await db.execute(family_user_stmt)
        family_user = family_user_result.scalar_one_or_none() if family_id else family_user_result.scalars().first()

        if not family_user or not family_user.family:
            raise HTTPException(
                status_code=404,
                detail="用户未关联任何家族，请先创建或加入家族"
            )

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


@router.post("/family/create", response_model=ApiResponse[UserFamilyInfo])
async def create_family(
    request: FamilyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        existing_owned_family_stmt = select(Family).where(
            Family.head_user_id == current_user.id
        )
        existing_owned_family_result = await db.execute(existing_owned_family_stmt)
        existing_owned_family = existing_owned_family_result.scalar_one_or_none()

        if existing_owned_family:
            raise HTTPException(
                status_code=400,
                detail="您已创建过一个家族，作为族长只能拥有一个家族。您可以加入其他家族作为共建者。"
            )

        if not request.surname or not request.surname.strip():
            raise HTTPException(
                status_code=400,
                detail="姓氏不能为空"
            )

        default_zi_bei = ["元", "亨", "利", "贞", "仁", "义", "礼", "智", "信"]
        zi_bei = request.zi_bei if request.zi_bei else default_zi_bei

        family = Family(
            id=str(uuid.uuid4()),
            hall_name=request.hall_name,
            surname=request.surname.strip(),
            ancestor=request.ancestor,
            description=request.description,
            zi_bei=zi_bei,
            head_user_id=current_user.id
        )
        db.add(family)

        family_user = FamilyUser(
            id=str(uuid.uuid4()),
            family_id=family.id,
            user_id=current_user.id,
            role=FamilyRole.HEAD.value
        )
        db.add(family_user)

        await db.commit()
        await db.refresh(family)
        await db.refresh(family_user)

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
                memberCount=0
            ),
            message="家族创建成功，您已成为族长"
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"创建家族失败: {str(e)}")


@router.post("/collaboration/links", response_model=ApiResponse[CollaborationLinkBase])
async def create_collaboration_link(
    request: CreateCollaborationLinkRequest,
    request_obj: Request,
    user_and_family: tuple = Depends(admin_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        link_code = generate_link_code()
        max_attempts = 10
        for _ in range(max_attempts):
            existing_stmt = select(CollaborationLink).where(
                CollaborationLink.link_code == link_code
            )
            existing_result = await db.execute(existing_stmt)
            existing = existing_result.scalar_one_or_none()
            if not existing:
                break
            link_code = generate_link_code()

        expires_at = None
        if request.expiresInDays:
            expires_at = datetime.utcnow() + timedelta(days=request.expiresInDays)

        link = CollaborationLink(
            id=str(uuid.uuid4()),
            family_id=family.id,
            inviter_id=current_user.id,
            link_code=link_code,
            role=request.role.value,
            status=CollaborationLinkStatus.ACTIVE.value,
            is_visible=True,
            used_count=0,
            max_uses=request.maxUses,
            expires_at=expires_at
        )
        db.add(link)
        await db.commit()
        await db.refresh(link)

        return ApiResponse(
            success=True,
            data=CollaborationLinkBase(
                id=link.id,
                familyId=link.family_id,
                inviterId=link.inviter_id,
                linkCode=link.link_code,
                role=FamilyRole(link.role),
                status=CollaborationLinkStatus(link.status),
                isVisible=link.is_visible,
                usedCount=link.used_count,
                maxUses=link.max_uses,
                expiresAt=link.expires_at,
                usedByUserId=link.used_by_user_id,
                usedAt=link.used_at,
                createdAt=link.created_at,
                updatedAt=link.updated_at
            ),
            message="共建链接创建成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"创建共建链接失败: {str(e)}")


@router.get("/collaboration/links", response_model=ApiResponse[CollaborationLinkListResponse])
async def list_collaboration_links(
    status: Optional[str] = Query(None),
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        query = (
            select(CollaborationLink)
            .where(CollaborationLink.family_id == family.id)
            .options(
                selectinload(CollaborationLink.inviter),
                selectinload(CollaborationLink.family)
            )
        )

        if status:
            query = query.where(CollaborationLink.status == status)

        query = query.order_by(CollaborationLink.created_at.desc())
        result = await db.execute(query)
        links = result.scalars().all()

        link_list = []
        for link in links:
            inviter_resp = UserResponse.model_validate(link.inviter) if link.inviter else None
            family_resp = FamilyBase.model_validate(link.family) if link.family else None
            link_list.append(CollaborationLinkBase(
                id=link.id,
                familyId=link.family_id,
                inviterId=link.inviter_id,
                linkCode=link.link_code,
                role=FamilyRole(link.role),
                status=CollaborationLinkStatus(link.status),
                isVisible=link.is_visible,
                usedCount=link.used_count,
                maxUses=link.max_uses,
                expiresAt=link.expires_at,
                usedByUserId=link.used_by_user_id,
                usedAt=link.used_at,
                inviter=inviter_resp,
                family=family_resp,
                createdAt=link.created_at,
                updatedAt=link.updated_at
            ))

        return ApiResponse(
            success=True,
            data=CollaborationLinkListResponse(
                total=len(link_list),
                links=link_list
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取共建链接列表失败: {str(e)}")


@router.put("/collaboration/links/{link_id}", response_model=ApiResponse[CollaborationLinkBase])
async def update_collaboration_link(
    link_id: str,
    request: UpdateCollaborationLinkRequest,
    user_and_family: tuple = Depends(admin_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        link_stmt = (
            select(CollaborationLink)
            .where(
                CollaborationLink.id == link_id,
                CollaborationLink.family_id == family.id
            )
        )
        link_result = await db.execute(link_stmt)
        link = link_result.scalar_one_or_none()

        if not link:
            raise HTTPException(status_code=404, detail="链接不存在或不属于当前家族")

        if request.role is not None:
            link.role = request.role.value
        if request.isVisible is not None:
            link.is_visible = request.isVisible

        await db.commit()
        await db.refresh(link)

        return ApiResponse(
            success=True,
            data=CollaborationLinkBase(
                id=link.id,
                familyId=link.family_id,
                inviterId=link.inviter_id,
                linkCode=link.link_code,
                role=FamilyRole(link.role),
                status=CollaborationLinkStatus(link.status),
                isVisible=link.is_visible,
                usedCount=link.used_count,
                maxUses=link.max_uses,
                expiresAt=link.expires_at,
                usedByUserId=link.used_by_user_id,
                usedAt=link.used_at,
                createdAt=link.created_at,
                updatedAt=link.updated_at
            ),
            message="链接已更新"
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新链接失败: {str(e)}")


@router.post("/collaboration/links/{link_id}/reset", response_model=ApiResponse[CollaborationLinkBase])
async def reset_collaboration_link(
    link_id: str,
    user_and_family: tuple = Depends(admin_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        link_stmt = (
            select(CollaborationLink)
            .where(
                CollaborationLink.id == link_id,
                CollaborationLink.family_id == family.id
            )
        )
        link_result = await db.execute(link_stmt)
        link = link_result.scalar_one_or_none()

        if not link:
            raise HTTPException(status_code=404, detail="链接不存在或不属于当前家族")

        new_link_code = generate_link_code()
        max_attempts = 10
        for _ in range(max_attempts):
            existing_stmt = select(CollaborationLink).where(
                CollaborationLink.link_code == new_link_code
            )
            existing_result = await db.execute(existing_stmt)
            existing = existing_result.scalar_one_or_none()
            if not existing:
                break
            new_link_code = generate_link_code()

        link.link_code = new_link_code
        link.status = CollaborationLinkStatus.ACTIVE.value
        link.used_count = 0
        link.used_by_user_id = None
        link.used_at = None

        await db.commit()
        await db.refresh(link)

        return ApiResponse(
            success=True,
            data=CollaborationLinkBase(
                id=link.id,
                familyId=link.family_id,
                inviterId=link.inviter_id,
                linkCode=link.link_code,
                role=FamilyRole(link.role),
                status=CollaborationLinkStatus(link.status),
                isVisible=link.is_visible,
                usedCount=link.used_count,
                maxUses=link.max_uses,
                expiresAt=link.expires_at,
                usedByUserId=link.used_by_user_id,
                usedAt=link.used_at,
                createdAt=link.created_at,
                updatedAt=link.updated_at
            ),
            message="链接已重置"
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"重置链接失败: {str(e)}")


@router.post("/collaboration/join", response_model=ApiResponse[UserFamilyInfo])
async def join_by_link(
    request: JoinByLinkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        link_code = request.linkCode.strip().upper()

        link_stmt = (
            select(CollaborationLink)
            .where(CollaborationLink.link_code == link_code)
            .options(selectinload(CollaborationLink.family))
        )
        link_result = await db.execute(link_stmt)
        link = link_result.scalar_one_or_none()

        if not link:
            raise HTTPException(status_code=404, detail="链接不存在")

        if link.status != CollaborationLinkStatus.ACTIVE.value:
            raise HTTPException(
                status_code=400,
                detail=f"链接状态无效: {link.status}"
            )

        if not link.is_visible:
            raise HTTPException(status_code=404, detail="链接不存在")

        if link.used_count >= link.max_uses:
            raise HTTPException(status_code=400, detail="链接已被使用完毕")

        if link.expires_at and datetime.utcnow() > link.expires_at:
            link.status = CollaborationLinkStatus.EXPIRED.value
            await db.commit()
            raise HTTPException(status_code=400, detail="链接已过期")

        family = link.family
        if not family:
            raise HTTPException(status_code=404, detail="链接关联的家族不存在")

        existing_fu_stmt = select(FamilyUser).where(
            FamilyUser.user_id == current_user.id,
            FamilyUser.family_id == family.id
        )
        existing_fu_result = await db.execute(existing_fu_stmt)
        existing_fu = existing_fu_result.scalar_one_or_none()

        if existing_fu:
            raise HTTPException(
                status_code=400,
                detail="您已加入该家族"
            )

        family_user = FamilyUser(
            id=str(uuid.uuid4()),
            family_id=family.id,
            user_id=current_user.id,
            role=link.role
        )
        db.add(family_user)

        link.used_count += 1
        link.used_at = datetime.utcnow()

        if link.used_count >= link.max_uses:
            link.status = CollaborationLinkStatus.USED.value

        await db.commit()
        await db.refresh(family_user)
        await db.refresh(link)

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
            ),
            message="成功加入家族"
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"加入家族失败: {str(e)}")
