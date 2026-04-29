from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, or_
from sqlalchemy.orm import selectinload
import uuid

from app.database import get_async_session
from app.models import (
    User, Family, FamilyUser, FamilyMember, EditApproval,
    FamilyRole, ApprovalStatus, OperationType, TargetType, MemberStatus, Gender
)
from app.schemas import (
    ApiResponse,
    UserResponse,
    ApprovalBase, ApprovalCreateRequest, ApprovalProcessRequest, ApprovalListResponse
)
from app.routers.auth import get_current_user
from app.permissions import (
    PermissionLevel, has_permission, get_user_family_role,
    admin_required, editor_required, viewer_required
)
from app.services.log_service import log_service

router = APIRouter(tags=["审核机制管理"])


async def get_member_data(member: FamilyMember) -> Dict[str, Any]:
    return {
        "id": member.id,
        "family_id": member.family_id,
        "name": member.name,
        "gender": member.gender,
        "generation": member.generation,
        "birth_year": member.birth_year,
        "death_year": member.death_year,
        "spouse": member.spouse,
        "father_id": member.father_id,
        "residence": member.residence,
        "note": member.note,
        "status": member.status
    }


async def apply_member_changes(
    db: AsyncSession,
    member: FamilyMember,
    modified_data: Dict[str, Any]
) -> FamilyMember:
    if "name" in modified_data and modified_data["name"] is not None:
        member.name = modified_data["name"]
    if "gender" in modified_data and modified_data["gender"] is not None:
        member.gender = modified_data["gender"]
    if "generation" in modified_data and modified_data["generation"] is not None:
        member.generation = modified_data["generation"]
    if "birth_year" in modified_data and modified_data["birth_year"] is not None:
        member.birth_year = modified_data["birth_year"]
    if "death_year" in modified_data and modified_data["death_year"] is not None:
        member.death_year = modified_data["death_year"]
    if "spouse" in modified_data and modified_data["spouse"] is not None:
        member.spouse = modified_data["spouse"]
    if "father_id" in modified_data:
        member.father_id = modified_data["father_id"] if modified_data["father_id"] else None
    if "residence" in modified_data and modified_data["residence"] is not None:
        member.residence = modified_data["residence"]
    if "note" in modified_data and modified_data["note"] is not None:
        member.note = modified_data["note"]
    if "status" in modified_data and modified_data["status"] is not None:
        member.status = modified_data["status"]

    await db.commit()
    await db.refresh(member)
    return member


@router.post("/approvals", response_model=ApiResponse[ApprovalBase])
async def create_approval(
    request: ApprovalCreateRequest,
    request_obj: Request,
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
            raise HTTPException(status_code=403, detail="用户未关联任何家族")

        family = family_user.family

        original_data = None
        if request.operation in [OperationType.UPDATE, OperationType.DELETE]:
            if request.target_type == TargetType.FAMILY_MEMBER:
                member_stmt = (
                    select(FamilyMember)
                    .where(
                        FamilyMember.id == request.target_id,
                        FamilyMember.deleted_at.is_(None)
                    )
                )
                member_result = await db.execute(member_stmt)
                member = member_result.scalar_one_or_none()
                if member:
                    original_data = await get_member_data(member)

        approval = EditApproval(
            id=str(uuid.uuid4()),
            family_id=family.id,
            requester_id=current_user.id,
            target_type=request.target_type.value,
            target_id=request.target_id,
            operation=request.operation.value,
            original_data=original_data,
            modified_data=request.modified_data,
            status=ApprovalStatus.PENDING.value,
            comment=request.comment
        )
        db.add(approval)
        await db.commit()
        await db.refresh(approval)

        return ApiResponse(
            success=True,
            data=ApprovalBase(
                id=approval.id,
                familyId=approval.family_id,
                requesterId=approval.requester_id,
                approverId=approval.approver_id,
                targetType=TargetType(approval.target_type),
                targetId=approval.target_id,
                operation=OperationType(approval.operation),
                originalData=approval.original_data,
                modifiedData=approval.modified_data,
                status=ApprovalStatus(approval.status),
                comment=approval.comment,
                createdAt=approval.created_at,
                updatedAt=approval.updated_at
            ),
            message="审核申请已提交"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建审核申请失败: {str(e)}")


@router.get("/approvals", response_model=ApiResponse[ApprovalListResponse])
async def get_approvals(
    status: Optional[str] = Query(None),
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        query = (
            select(EditApproval)
            .where(EditApproval.family_id == family.id)
            .options(
                selectinload(EditApproval.requester),
                selectinload(EditApproval.approver)
            )
        )

        if status:
            query = query.where(EditApproval.status == status)

        query = query.order_by(EditApproval.created_at.desc())
        result = await db.execute(query)
        approvals = result.scalars().all()

        approval_list = []
        for app in approvals:
            requester_resp = UserResponse.model_validate(app.requester) if app.requester else None
            approver_resp = UserResponse.model_validate(app.approver) if app.approver else None
            approval_list.append(ApprovalBase(
                id=app.id,
                familyId=app.family_id,
                requesterId=app.requester_id,
                approverId=app.approver_id,
                targetType=TargetType(app.target_type),
                targetId=app.target_id,
                operation=OperationType(app.operation),
                originalData=app.original_data,
                modifiedData=app.modified_data,
                status=ApprovalStatus(app.status),
                comment=app.comment,
                approvedAt=app.approved_at,
                rejectedAt=app.rejected_at,
                rejectionReason=app.rejection_reason,
                requester=requester_resp,
                approver=approver_resp,
                createdAt=app.created_at,
                updatedAt=app.updated_at
            ))

        return ApiResponse(
            success=True,
            data=ApprovalListResponse(
                total=len(approval_list),
                approvals=approval_list
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取审核列表失败: {str(e)}")


@router.get("/approvals/pending", response_model=ApiResponse[ApprovalListResponse])
async def get_pending_approvals(
    user_and_family: tuple = Depends(admin_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        query = (
            select(EditApproval)
            .where(
                EditApproval.family_id == family.id,
                EditApproval.status == ApprovalStatus.PENDING.value
            )
            .options(
                selectinload(EditApproval.requester),
                selectinload(EditApproval.approver)
            )
            .order_by(EditApproval.created_at)
        )
        result = await db.execute(query)
        approvals = result.scalars().all()

        approval_list = []
        for app in approvals:
            requester_resp = UserResponse.model_validate(app.requester) if app.requester else None
            approver_resp = UserResponse.model_validate(app.approver) if app.approver else None
            approval_list.append(ApprovalBase(
                id=app.id,
                familyId=app.family_id,
                requesterId=app.requester_id,
                approverId=app.approver_id,
                targetType=TargetType(app.target_type),
                targetId=app.target_id,
                operation=OperationType(app.operation),
                originalData=app.original_data,
                modifiedData=app.modified_data,
                status=ApprovalStatus(app.status),
                comment=app.comment,
                approvedAt=app.approved_at,
                rejectedAt=app.rejected_at,
                rejectionReason=app.rejection_reason,
                requester=requester_resp,
                approver=approver_resp,
                createdAt=app.created_at,
                updatedAt=app.updated_at
            ))

        return ApiResponse(
            success=True,
            data=ApprovalListResponse(
                total=len(approval_list),
                approvals=approval_list
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取待审核列表失败: {str(e)}")


@router.get("/approvals/my", response_model=ApiResponse[ApprovalListResponse])
async def get_my_approvals(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        query = (
            select(EditApproval)
            .where(EditApproval.requester_id == current_user.id)
            .options(
                selectinload(EditApproval.requester),
                selectinload(EditApproval.approver)
            )
        )

        if status:
            query = query.where(EditApproval.status == status)

        query = query.order_by(EditApproval.created_at.desc())
        result = await db.execute(query)
        approvals = result.scalars().all()

        approval_list = []
        for app in approvals:
            requester_resp = UserResponse.model_validate(app.requester) if app.requester else None
            approver_resp = UserResponse.model_validate(app.approver) if app.approver else None
            approval_list.append(ApprovalBase(
                id=app.id,
                familyId=app.family_id,
                requesterId=app.requester_id,
                approverId=app.approver_id,
                targetType=TargetType(app.target_type),
                targetId=app.target_id,
                operation=OperationType(app.operation),
                originalData=app.original_data,
                modifiedData=app.modified_data,
                status=ApprovalStatus(app.status),
                comment=app.comment,
                approvedAt=app.approved_at,
                rejectedAt=app.rejected_at,
                rejectionReason=app.rejection_reason,
                requester=requester_resp,
                approver=approver_resp,
                createdAt=app.created_at,
                updatedAt=app.updated_at
            ))

        return ApiResponse(
            success=True,
            data=ApprovalListResponse(
                total=len(approval_list),
                approvals=approval_list
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取我的审核申请失败: {str(e)}")


@router.post("/approvals/approve", response_model=ApiResponse[ApprovalBase])
async def approve_approval(
    request: ApprovalProcessRequest,
    request_obj: Request,
    user_and_family: tuple = Depends(admin_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        approval_stmt = (
            select(EditApproval)
            .where(
                EditApproval.id == request.approval_id,
                EditApproval.family_id == family.id
            )
            .options(
                selectinload(EditApproval.requester),
                selectinload(EditApproval.approver)
            )
        )
        approval_result = await db.execute(approval_stmt)
        approval = approval_result.scalar_one_or_none()

        if not approval:
            raise HTTPException(status_code=404, detail="审核申请不存在")

        if approval.status != ApprovalStatus.PENDING.value:
            raise HTTPException(status_code=400, detail="该审核申请已被处理")

        now = datetime.utcnow()
        approval.status = ApprovalStatus.APPROVED.value
        approval.approver_id = current_user.id
        approval.approved_at = now

        if approval.operation == OperationType.UPDATE.value:
            if approval.target_type == TargetType.FAMILY_MEMBER.value:
                member_stmt = (
                    select(FamilyMember)
                    .where(
                        FamilyMember.id == approval.target_id,
                        FamilyMember.deleted_at.is_(None)
                    )
                )
                member_result = await db.execute(member_stmt)
                member = member_result.scalar_one_or_none()
                if member:
                    await apply_member_changes(db, member, approval.modified_data)

        elif approval.operation == OperationType.DELETE.value:
            if approval.target_type == TargetType.FAMILY_MEMBER.value:
                member_stmt = (
                    select(FamilyMember)
                    .where(
                        FamilyMember.id == approval.target_id,
                        FamilyMember.deleted_at.is_(None)
                    )
                )
                member_result = await db.execute(member_stmt)
                member = member_result.scalar_one_or_none()
                if member:
                    member.deleted_at = now
                    await db.commit()

        elif approval.operation == OperationType.CREATE.value:
            if approval.target_type == TargetType.FAMILY_MEMBER.value:
                member_data = approval.modified_data
                member = FamilyMember(
                    id=str(uuid.uuid4()),
                    family_id=family.id,
                    name=member_data.get("name", ""),
                    gender=member_data.get("gender", Gender.MALE.value),
                    generation=member_data.get("generation", 1),
                    birth_year=member_data.get("birth_year"),
                    death_year=member_data.get("death_year"),
                    spouse=member_data.get("spouse"),
                    father_id=member_data.get("father_id") if member_data.get("father_id") else None,
                    residence=member_data.get("residence"),
                    note=member_data.get("note"),
                    status=member_data.get("status", MemberStatus.ALIVE.value)
                )
                db.add(member)
                await db.commit()
                await db.refresh(member)

        await db.commit()
        await db.refresh(approval)

        await log_service.log_approval(
            db=db,
            user=current_user,
            approval_id=approval.id,
            action="approve",
            target_type=TargetType(approval.target_type),
            target_id=approval.target_id,
            family=family,
            ip_address=request_obj.client.host if request_obj.client else None,
            user_agent=request_obj.headers.get("user-agent")
        )

        requester_resp = UserResponse.model_validate(approval.requester) if approval.requester else None
        approver_resp = UserResponse.model_validate(approval.approver) if approval.approver else None
        return ApiResponse(
            success=True,
            data=ApprovalBase(
                id=approval.id,
                familyId=approval.family_id,
                requesterId=approval.requester_id,
                approverId=approval.approver_id,
                targetType=TargetType(approval.target_type),
                targetId=approval.target_id,
                operation=OperationType(approval.operation),
                originalData=approval.original_data,
                modifiedData=approval.modified_data,
                status=ApprovalStatus(approval.status),
                comment=approval.comment,
                approvedAt=approval.approved_at,
                rejectedAt=approval.rejected_at,
                rejectionReason=approval.rejection_reason,
                requester=requester_resp,
                approver=approver_resp,
                createdAt=approval.created_at,
                updatedAt=approval.updated_at
            ),
            message="审核已通过"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批准审核申请失败: {str(e)}")


@router.post("/approvals/reject", response_model=ApiResponse[ApprovalBase])
async def reject_approval(
    request: ApprovalProcessRequest,
    request_obj: Request,
    user_and_family: tuple = Depends(admin_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        approval_stmt = (
            select(EditApproval)
            .where(
                EditApproval.id == request.approval_id,
                EditApproval.family_id == family.id
            )
            .options(
                selectinload(EditApproval.requester),
                selectinload(EditApproval.approver)
            )
        )
        approval_result = await db.execute(approval_stmt)
        approval = approval_result.scalar_one_or_none()

        if not approval:
            raise HTTPException(status_code=404, detail="审核申请不存在")

        if approval.status != ApprovalStatus.PENDING.value:
            raise HTTPException(status_code=400, detail="该审核申请已被处理")

        now = datetime.utcnow()
        approval.status = ApprovalStatus.REJECTED.value
        approval.approver_id = current_user.id
        approval.rejection_reason = request.reason
        approval.rejected_at = now

        await db.commit()
        await db.refresh(approval)

        await log_service.log_approval(
            db=db,
            user=current_user,
            approval_id=approval.id,
            action="reject",
            target_type=TargetType(approval.target_type),
            target_id=approval.target_id,
            family=family,
            ip_address=request_obj.client.host if request_obj.client else None,
            user_agent=request_obj.headers.get("user-agent")
        )

        requester_resp = UserResponse.model_validate(approval.requester) if approval.requester else None
        approver_resp = UserResponse.model_validate(approval.approver) if approval.approver else None
        return ApiResponse(
            success=True,
            data=ApprovalBase(
                id=approval.id,
                familyId=approval.family_id,
                requesterId=approval.requester_id,
                approverId=approval.approver_id,
                targetType=TargetType(approval.target_type),
                targetId=approval.target_id,
                operation=OperationType(approval.operation),
                originalData=approval.original_data,
                modifiedData=approval.modified_data,
                status=ApprovalStatus(approval.status),
                comment=approval.comment,
                approvedAt=approval.approved_at,
                rejectedAt=approval.rejected_at,
                rejectionReason=approval.rejection_reason,
                requester=requester_resp,
                approver=approver_resp,
                createdAt=approval.created_at,
                updatedAt=approval.updated_at
            ),
            message="审核已拒绝"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"拒绝审核申请失败: {str(e)}")
