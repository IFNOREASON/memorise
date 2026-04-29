from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, or_
from sqlalchemy.orm import selectinload
import uuid

from app.database import get_async_session
from app.models import (
    Family, FamilyMember, MemberMedia, MemberStatus, Gender, MediaType,
    User, FamilyUser
)
from app.schemas import (
    ApiResponse,
    FamilyBase, FamilyCreateRequest, FamilyUpdateRequest, FamilyDetailResponse,
    FamilyMemberBase, FamilyMemberCreateRequest, FamilyMemberUpdateRequest, FamilyMemberListResponse,
    MemberMediaBase, MemberMediaCreateRequest
)
from app.permissions import (
    viewer_required, editor_required, admin_required,
    has_permission, PermissionLevel
)
from app.services.log_service import log_service

router = APIRouter(tags=["家族族谱管理"])


def generate_id() -> str:
    return str(uuid.uuid4())


async def get_family_member_by_id(db: AsyncSession, member_id: str, family_id: str) -> Optional[FamilyMember]:
    stmt = (
        select(FamilyMember)
        .where(
            FamilyMember.id == member_id,
            FamilyMember.family_id == family_id,
            FamilyMember.deleted_at.is_(None)
        )
        .options(selectinload(FamilyMember.medias))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@router.get("/family", response_model=ApiResponse[FamilyDetailResponse])
async def get_family(
    request_obj: Request,
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        members_stmt = (
            select(FamilyMember)
            .where(FamilyMember.family_id == family.id, FamilyMember.deleted_at.is_(None))
            .options(selectinload(FamilyMember.medias))
            .order_by(FamilyMember.generation, FamilyMember.name)
        )
        members_result = await db.execute(members_stmt)
        members = members_result.scalars().all()

        member_list = []
        for m in members:
            media_list = [
                MemberMediaBase(
                    id=mm.id,
                    url=mm.url,
                    type=mm.type,
                    date_time=mm.date_time,
                    location=mm.location,
                    duration=mm.duration
                ) for mm in (m.medias or [])
            ]
            member_list.append(FamilyMemberBase(
                id=m.id,
                familyId=m.family_id,
                name=m.name,
                gender=m.gender,
                generation=m.generation,
                birthYear=m.birth_year,
                deathYear=m.death_year,
                spouse=m.spouse,
                fatherId=m.father_id,
                residence=m.residence,
                note=m.note,
                status=m.status,
                medias=media_list if media_list else None,
                createdAt=m.created_at,
                updatedAt=m.updated_at
            ))

        return ApiResponse(
            success=True,
            data=FamilyDetailResponse(
                family=FamilyBase(
                    id=family.id,
                    hallName=family.hall_name,
                    surname=family.surname,
                    ancestor=family.ancestor,
                    description=family.description,
                    ziBei=family.zi_bei,
                    createdAt=family.created_at,
                    updatedAt=family.updated_at
                ),
                memberCount=len(member_list),
                members=member_list
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取家族信息失败: {str(e)}")


@router.post("/family", response_model=ApiResponse[FamilyBase])
async def create_family(
    request: FamilyCreateRequest,
    current_user: User = Depends(editor_required),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        family = Family(
            id=generate_id(),
            hall_name=request.hall_name,
            surname=request.surname,
            ancestor=request.ancestor,
            description=request.description,
            zi_bei=request.zi_bei
        )
        db.add(family)
        await db.commit()
        await db.refresh(family)

        return ApiResponse(
            success=True,
            data=FamilyBase(
                id=family.id,
                hallName=family.hall_name,
                surname=family.surname,
                ancestor=family.ancestor,
                description=family.description,
                ziBei=family.zi_bei,
                createdAt=family.created_at,
                updatedAt=family.updated_at
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建家族失败: {str(e)}")


@router.put("/family", response_model=ApiResponse[FamilyBase])
async def update_family(
    request: FamilyUpdateRequest,
    request_obj: Request,
    user_and_family: tuple = Depends(admin_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        original_family = Family(
            id=family.id,
            hall_name=family.hall_name,
            surname=family.surname,
            ancestor=family.ancestor,
            description=family.description,
            zi_bei=family.zi_bei.copy() if family.zi_bei else None
        )

        if request.hall_name is not None:
            family.hall_name = request.hall_name
        if request.surname is not None:
            family.surname = request.surname
        if request.ancestor is not None:
            family.ancestor = request.ancestor
        if request.description is not None:
            family.description = request.description
        if request.zi_bei is not None:
            family.zi_bei = request.zi_bei

        await db.commit()
        await db.refresh(family)

        await log_service.log_family_update(
            db=db,
            user=current_user,
            original_family=original_family,
            updated_family=family,
            ip_address=request_obj.client.host if request_obj.client else None,
            user_agent=request_obj.headers.get("user-agent")
        )

        return ApiResponse(
            success=True,
            data=FamilyBase(
                id=family.id,
                hallName=family.hall_name,
                surname=family.surname,
                ancestor=family.ancestor,
                description=family.description,
                ziBei=family.zi_bei,
                createdAt=family.created_at,
                updatedAt=family.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新家族失败: {str(e)}")


@router.get("/family/members", response_model=ApiResponse[FamilyMemberListResponse])
async def get_members(
    status: Optional[str] = None,
    search: Optional[str] = None,
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        query = (
            select(FamilyMember)
            .where(FamilyMember.family_id == family.id, FamilyMember.deleted_at.is_(None))
            .options(selectinload(FamilyMember.medias))
        )

        if status:
            query = query.where(FamilyMember.status == status)
        if search:
            query = query.where(FamilyMember.name.contains(search))

        query = query.order_by(FamilyMember.generation, FamilyMember.name)

        result = await db.execute(query)
        members = result.scalars().all()

        member_list = []
        for m in members:
            media_list = [
                MemberMediaBase(
                    id=mm.id,
                    url=mm.url,
                    type=mm.type,
                    date_time=mm.date_time,
                    location=mm.location,
                    duration=mm.duration
                ) for mm in (m.medias or [])
            ]
            member_list.append(FamilyMemberBase(
                id=m.id,
                familyId=m.family_id,
                name=m.name,
                gender=m.gender,
                generation=m.generation,
                birthYear=m.birth_year,
                deathYear=m.death_year,
                spouse=m.spouse,
                fatherId=m.father_id,
                residence=m.residence,
                note=m.note,
                status=m.status,
                medias=media_list if media_list else None,
                createdAt=m.created_at,
                updatedAt=m.updated_at
            ))

        return ApiResponse(
            success=True,
            data=FamilyMemberListResponse(
                total=len(member_list),
                members=member_list
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取成员列表失败: {str(e)}")


@router.get("/family/members/{member_id}", response_model=ApiResponse[FamilyMemberBase])
async def get_member(
    member_id: str,
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        member = await get_family_member_by_id(db, member_id, family.id)

        if not member:
            raise HTTPException(status_code=404, detail="成员不存在")

        media_list = [
            MemberMediaBase(
                id=mm.id,
                url=mm.url,
                type=mm.type,
                date_time=mm.date_time,
                location=mm.location,
                duration=mm.duration
            ) for mm in (member.medias or [])
        ]

        return ApiResponse(
            success=True,
            data=FamilyMemberBase(
                id=member.id,
                familyId=member.family_id,
                name=member.name,
                gender=member.gender,
                generation=member.generation,
                birthYear=member.birth_year,
                deathYear=member.death_year,
                spouse=member.spouse,
                fatherId=member.father_id,
                residence=member.residence,
                note=member.note,
                status=member.status,
                medias=media_list if media_list else None,
                createdAt=member.created_at,
                updatedAt=member.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取成员信息失败: {str(e)}")


@router.post("/family/members", response_model=ApiResponse[FamilyMemberBase])
async def create_member(
    request: FamilyMemberCreateRequest,
    request_obj: Request,
    user_and_family: tuple = Depends(editor_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        if not request.name.strip():
            raise HTTPException(status_code=400, detail="姓名不能为空")

        member = FamilyMember(
            id=generate_id(),
            family_id=family.id,
            name=request.name,
            gender=request.gender,
            generation=request.generation,
            birth_year=request.birth_year,
            death_year=request.death_year,
            spouse=request.spouse,
            father_id=request.father_id if request.father_id else None,
            residence=request.residence,
            note=request.note,
            status=request.status
        )
        db.add(member)
        await db.commit()
        await db.refresh(member)

        await log_service.log_member_create(
            db=db,
            user=current_user,
            member=member,
            ip_address=request_obj.client.host if request_obj.client else None,
            user_agent=request_obj.headers.get("user-agent")
        )

        return ApiResponse(
            success=True,
            data=FamilyMemberBase(
                id=member.id,
                familyId=member.family_id,
                name=member.name,
                gender=member.gender,
                generation=member.generation,
                birthYear=member.birth_year,
                deathYear=member.death_year,
                spouse=member.spouse,
                fatherId=member.father_id,
                residence=member.residence,
                note=member.note,
                status=member.status,
                medias=None,
                createdAt=member.created_at,
                updatedAt=member.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建成员失败: {str(e)}")


@router.put("/family/members/{member_id}", response_model=ApiResponse[FamilyMemberBase])
async def update_member(
    member_id: str,
    request: FamilyMemberUpdateRequest,
    request_obj: Request,
    user_and_family: tuple = Depends(editor_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        member = await get_family_member_by_id(db, member_id, family.id)

        if not member:
            raise HTTPException(status_code=404, detail="成员不存在")

        original_member = FamilyMember(
            id=member.id,
            family_id=member.family_id,
            name=member.name,
            gender=member.gender,
            generation=member.generation,
            birth_year=member.birth_year,
            death_year=member.death_year,
            spouse=member.spouse,
            father_id=member.father_id,
            residence=member.residence,
            note=member.note,
            status=member.status
        )

        if request.name is not None:
            member.name = request.name
        if request.gender is not None:
            member.gender = request.gender
        if request.generation is not None:
            member.generation = request.generation
        if request.birth_year is not None:
            member.birth_year = request.birth_year
        if request.death_year is not None:
            member.death_year = request.death_year
        if request.spouse is not None:
            member.spouse = request.spouse
        if request.father_id is not None:
            member.father_id = request.father_id if request.father_id else None
        if request.residence is not None:
            member.residence = request.residence
        if request.note is not None:
            member.note = request.note
        if request.status is not None:
            member.status = request.status

        await db.commit()
        await db.refresh(member)

        await log_service.log_member_update(
            db=db,
            user=current_user,
            original_member=original_member,
            updated_member=member,
            ip_address=request_obj.client.host if request_obj.client else None,
            user_agent=request_obj.headers.get("user-agent")
        )

        return ApiResponse(
            success=True,
            data=FamilyMemberBase(
                id=member.id,
                familyId=member.family_id,
                name=member.name,
                gender=member.gender,
                generation=member.generation,
                birthYear=member.birth_year,
                deathYear=member.death_year,
                spouse=member.spouse,
                fatherId=member.father_id,
                residence=member.residence,
                note=member.note,
                status=member.status,
                medias=None,
                createdAt=member.created_at,
                updatedAt=member.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新成员失败: {str(e)}")


@router.delete("/family/members/{member_id}", response_model=ApiResponse)
async def delete_member(
    member_id: str,
    request_obj: Request,
    user_and_family: tuple = Depends(admin_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        member = await get_family_member_by_id(db, member_id, family.id)

        if not member:
            raise HTTPException(status_code=404, detail="成员不存在")

        member.deleted_at = datetime.now()
        await db.commit()

        await log_service.log_member_delete(
            db=db,
            user=current_user,
            member=member,
            ip_address=request_obj.client.host if request_obj.client else None,
            user_agent=request_obj.headers.get("user-agent")
        )

        return ApiResponse(
            success=True,
            message="成员已删除"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除成员失败: {str(e)}")


@router.get("/family/members/{member_id}/medias", response_model=ApiResponse[List[MemberMediaBase]])
async def get_member_medias(
    member_id: str,
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        member = await get_family_member_by_id(db, member_id, family.id)

        if not member:
            raise HTTPException(status_code=404, detail="成员不存在")

        stmt = select(MemberMedia).where(MemberMedia.member_id == member_id).order_by(MemberMedia.created_at)
        result = await db.execute(stmt)
        medias = result.scalars().all()

        media_list = [
            MemberMediaBase(
                id=m.id,
                url=m.url,
                type=m.type,
                date_time=m.date_time,
                location=m.location,
                duration=m.duration
            ) for m in medias
        ]

        return ApiResponse(success=True, data=media_list)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取成员影像失败: {str(e)}")


@router.post("/family/members/{member_id}/medias", response_model=ApiResponse[MemberMediaBase])
async def create_member_media(
    member_id: str,
    request: MemberMediaCreateRequest,
    user_and_family: tuple = Depends(editor_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        member = await get_family_member_by_id(db, member_id, family.id)

        if not member:
            raise HTTPException(status_code=404, detail="成员不存在")

        media = MemberMedia(
            id=generate_id(),
            member_id=member_id,
            url=request.url,
            type=request.type,
            date_time=request.date_time,
            location=request.location,
            duration=request.duration
        )
        db.add(media)
        await db.commit()
        await db.refresh(media)

        return ApiResponse(
            success=True,
            data=MemberMediaBase(
                id=media.id,
                url=media.url,
                type=media.type,
                date_time=media.date_time,
                location=media.location,
                duration=media.duration
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加成员影像失败: {str(e)}")


@router.delete("/family/members/{member_id}/medias/{media_id}", response_model=ApiResponse)
async def delete_member_media(
    member_id: str,
    media_id: str,
    user_and_family: tuple = Depends(editor_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family

    try:
        member = await get_family_member_by_id(db, member_id, family.id)
        if not member:
            raise HTTPException(status_code=404, detail="成员不存在")

        stmt = select(MemberMedia).where(MemberMedia.id == media_id, MemberMedia.member_id == member_id)
        result = await db.execute(stmt)
        media = result.scalar_one_or_none()

        if not media:
            raise HTTPException(status_code=404, detail="影像不存在")

        await db.execute(delete(MemberMedia).where(MemberMedia.id == media_id))
        await db.commit()

        return ApiResponse(success=True, message="影像已删除")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除影像失败: {str(e)}")
