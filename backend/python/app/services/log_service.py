from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from app.models import (
    OperationLog, OperationType, TargetType,
    User, Family, FamilyMember, FamilyUser
)


class LogService:
    @staticmethod
    async def create_log(
        db: AsyncSession,
        user: Optional[User],
        operation: OperationType,
        target_type: Optional[TargetType] = None,
        target_id: Optional[str] = None,
        description: Optional[str] = None,
        before_data: Optional[Dict[str, Any]] = None,
        after_data: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        family_id: Optional[str] = None
    ) -> OperationLog:
        log = OperationLog(
            id=str(uuid.uuid4()),
            family_id=family_id,
            user_id=user.id if user else None,
            operation=operation.value,
            target_type=target_type.value if target_type else None,
            target_id=target_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            before_data=before_data,
            after_data=after_data
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    @staticmethod
    async def log_member_create(
        db: AsyncSession,
        user: User,
        member: FamilyMember,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> OperationLog:
        return await LogService.create_log(
            db=db,
            user=user,
            operation=OperationType.CREATE,
            target_type=TargetType.FAMILY_MEMBER,
            target_id=member.id,
            description=f"创建了成员: {member.name}",
            after_data={
                "id": member.id,
                "name": member.name,
                "gender": member.gender,
                "generation": member.generation,
                "birth_year": member.birth_year,
                "death_year": member.death_year,
                "spouse": member.spouse,
                "father_id": member.father_id,
                "residence": member.residence,
                "status": member.status
            },
            ip_address=ip_address,
            user_agent=user_agent,
            family_id=member.family_id
        )

    @staticmethod
    async def log_member_update(
        db: AsyncSession,
        user: User,
        original_member: FamilyMember,
        updated_member: FamilyMember,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> OperationLog:
        changes = {}
        if original_member.name != updated_member.name:
            changes["name"] = {"before": original_member.name, "after": updated_member.name}
        if original_member.gender != updated_member.gender:
            changes["gender"] = {"before": original_member.gender, "after": updated_member.gender}
        if original_member.generation != updated_member.generation:
            changes["generation"] = {"before": original_member.generation, "after": updated_member.generation}
        if original_member.birth_year != updated_member.birth_year:
            changes["birth_year"] = {"before": original_member.birth_year, "after": updated_member.birth_year}
        if original_member.death_year != updated_member.death_year:
            changes["death_year"] = {"before": original_member.death_year, "after": updated_member.death_year}
        if original_member.spouse != updated_member.spouse:
            changes["spouse"] = {"before": original_member.spouse, "after": updated_member.spouse}
        if original_member.father_id != updated_member.father_id:
            changes["father_id"] = {"before": original_member.father_id, "after": updated_member.father_id}
        if original_member.residence != updated_member.residence:
            changes["residence"] = {"before": original_member.residence, "after": updated_member.residence}
        if original_member.note != updated_member.note:
            changes["note"] = {"before": original_member.note, "after": updated_member.note}
        if original_member.status != updated_member.status:
            changes["status"] = {"before": original_member.status, "after": updated_member.status}

        return await LogService.create_log(
            db=db,
            user=user,
            operation=OperationType.UPDATE,
            target_type=TargetType.FAMILY_MEMBER,
            target_id=updated_member.id,
            description=f"更新了成员: {updated_member.name}",
            before_data={
                "name": original_member.name,
                "gender": original_member.gender,
                "generation": original_member.generation,
                "birth_year": original_member.birth_year,
                "death_year": original_member.death_year,
                "spouse": original_member.spouse,
                "father_id": original_member.father_id,
                "residence": original_member.residence,
                "status": original_member.status
            },
            after_data={
                "name": updated_member.name,
                "gender": updated_member.gender,
                "generation": updated_member.generation,
                "birth_year": updated_member.birth_year,
                "death_year": updated_member.death_year,
                "spouse": updated_member.spouse,
                "father_id": updated_member.father_id,
                "residence": updated_member.residence,
                "status": updated_member.status
            },
            ip_address=ip_address,
            user_agent=user_agent,
            family_id=updated_member.family_id
        )

    @staticmethod
    async def log_member_delete(
        db: AsyncSession,
        user: User,
        member: FamilyMember,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> OperationLog:
        return await LogService.create_log(
            db=db,
            user=user,
            operation=OperationType.DELETE,
            target_type=TargetType.FAMILY_MEMBER,
            target_id=member.id,
            description=f"删除了成员: {member.name}",
            before_data={
                "id": member.id,
                "name": member.name,
                "gender": member.gender,
                "generation": member.generation,
                "birth_year": member.birth_year,
                "death_year": member.death_year,
                "spouse": member.spouse,
                "father_id": member.father_id,
                "residence": member.residence,
                "status": member.status
            },
            ip_address=ip_address,
            user_agent=user_agent,
            family_id=member.family_id
        )

    @staticmethod
    async def log_family_update(
        db: AsyncSession,
        user: User,
        original_family: Family,
        updated_family: Family,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> OperationLog:
        return await LogService.create_log(
            db=db,
            user=user,
            operation=OperationType.UPDATE,
            target_type=TargetType.FAMILY,
            target_id=updated_family.id,
            description="更新了家族信息",
            before_data={
                "hall_name": original_family.hall_name,
                "surname": original_family.surname,
                "ancestor": original_family.ancestor,
                "description": original_family.description,
                "zi_bei": original_family.zi_bei
            },
            after_data={
                "hall_name": updated_family.hall_name,
                "surname": updated_family.surname,
                "ancestor": updated_family.ancestor,
                "description": updated_family.description,
                "zi_bei": updated_family.zi_bei
            },
            ip_address=ip_address,
            user_agent=user_agent,
            family_id=updated_family.id
        )

    @staticmethod
    async def log_role_change(
        db: AsyncSession,
        user: User,
        target_user: User,
        family: Family,
        old_role: str,
        new_role: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> OperationLog:
        return await LogService.create_log(
            db=db,
            user=user,
            operation=OperationType.ROLE_CHANGE,
            target_type=TargetType.USER,
            target_id=target_user.id,
            description=f"将用户 {target_user.username} 的角色从 {old_role} 改为 {new_role}",
            before_data={"role": old_role},
            after_data={"role": new_role},
            ip_address=ip_address,
            user_agent=user_agent,
            family_id=family.id
        )

    @staticmethod
    async def log_invite(
        db: AsyncSession,
        user: User,
        invitee_email: str,
        family: Family,
        role: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> OperationLog:
        return await LogService.create_log(
            db=db,
            user=user,
            operation=OperationType.INVITE,
            target_type=TargetType.INVITATION,
            description=f"邀请了 {invitee_email} 加入家族，角色: {role}",
            after_data={"invitee_email": invitee_email, "role": role},
            ip_address=ip_address,
            user_agent=user_agent,
            family_id=family.id
        )

    @staticmethod
    async def log_approval(
        db: AsyncSession,
        user: User,
        approval_id: str,
        action: str,
        target_type: TargetType,
        target_id: str,
        family: Family,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> OperationLog:
        operation = OperationType.APPROVE if action == "approve" else OperationType.REJECT
        action_text = "批准" if action == "approve" else "拒绝"
        return await LogService.create_log(
            db=db,
            user=user,
            operation=operation,
            target_type=TargetType.APPROVAL,
            target_id=approval_id,
            description=f"{action_text}了审核申请",
            after_data={
                "approval_id": approval_id,
                "action": action,
                "target_type": target_type.value,
                "target_id": target_id
            },
            ip_address=ip_address,
            user_agent=user_agent,
            family_id=family.id
        )

    @staticmethod
    async def log_login(
        db: AsyncSession,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> OperationLog:
        return await LogService.create_log(
            db=db,
            user=user,
            operation=OperationType.LOGIN,
            description=f"用户登录",
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    async def log_logout(
        db: AsyncSession,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> OperationLog:
        return await LogService.create_log(
            db=db,
            user=user,
            operation=OperationType.LOGOUT,
            description=f"用户登出",
            ip_address=ip_address,
            user_agent=user_agent
        )


log_service = LogService()
