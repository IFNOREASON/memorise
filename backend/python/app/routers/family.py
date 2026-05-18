from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, or_, func
from sqlalchemy.orm import selectinload
import uuid
import pandas as pd
import io
from io import BytesIO
from urllib.parse import quote

from app.database import get_async_session
from app.models import (
    Family, FamilyMember, MemberMedia, MemberStatus, Gender, MediaType,
    User, FamilyUser, OperationType, TargetType, Gallery, Avatar
)
from app.schemas import (
    ApiResponse,
    FamilyBase, FamilyCreateRequest, FamilyUpdateRequest, FamilyDetailResponse,
    FamilyMemberBase, FamilyMemberCreateRequest, FamilyMemberUpdateRequest, FamilyMemberListResponse,
    MemberMediaBase, MemberMediaCreateRequest, HomeStatsResponse
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


def parse_excel_file(content: bytes) -> pd.DataFrame:
    excel_file = BytesIO(content)
    df = pd.read_excel(excel_file)
    return df


def parse_csv_file(content: bytes) -> pd.DataFrame:
    csv_file = BytesIO(content)
    df = pd.read_csv(csv_file)
    return df


def normalize_column_name(name: str) -> str:
    name_map = {
        '姓名': 'name',
        '名字': 'name',
        '性别': 'gender',
        '世代': 'generation',
        '辈份': 'generation',
        '出生年份': 'birth_year',
        '出生年': 'birth_year',
        '去世年份': 'death_year',
        '去世年': 'death_year',
        '逝世年份': 'death_year',
        '配偶': 'spouse',
        '父亲': 'father_name',
        '父亲姓名': 'father_name',
        '现居地': 'residence',
        '居住地': 'residence',
        '备注': 'note',
        '状态': 'status'
    }
    return name_map.get(name.strip(), name.strip())


def parse_member_data(df: pd.DataFrame) -> List[dict]:
    df.columns = [normalize_column_name(col) for col in df.columns]
    
    members = []
    for _, row in df.iterrows():
        member = {}
        
        if 'name' in df.columns and pd.notna(row['name']):
            member['name'] = str(row['name']).strip()
        else:
            continue
        
        if 'gender' in df.columns and pd.notna(row['gender']):
            gender = str(row['gender']).strip()
            if gender in ['男', 'male', 'Male', 'M']:
                member['gender'] = 'male'
            elif gender in ['女', 'female', 'Female', 'F']:
                member['gender'] = 'female'
            else:
                member['gender'] = 'male'
        else:
            member['gender'] = 'male'
        
        if 'generation' in df.columns and pd.notna(row['generation']):
            try:
                member['generation'] = int(float(row['generation']))
            except:
                member['generation'] = 1
        else:
            member['generation'] = 1
        
        if 'birth_year' in df.columns and pd.notna(row['birth_year']):
            member['birth_year'] = str(row['birth_year']).strip()
        
        if 'death_year' in df.columns and pd.notna(row['death_year']):
            member['death_year'] = str(row['death_year']).strip()
        
        if 'spouse' in df.columns and pd.notna(row['spouse']):
            member['spouse'] = str(row['spouse']).strip()
        
        if 'father_name' in df.columns and pd.notna(row['father_name']):
            member['father_name'] = str(row['father_name']).strip()
        
        if 'residence' in df.columns and pd.notna(row['residence']):
            member['residence'] = str(row['residence']).strip()
        
        if 'note' in df.columns and pd.notna(row['note']):
            member['note'] = str(row['note']).strip()
        
        if 'status' in df.columns and pd.notna(row['status']):
            status = str(row['status']).strip()
            if status in ['在世', '存活', 'alive', 'Alive']:
                member['status'] = 'alive'
            elif status in ['已故', '去世', '逝世', 'deceased', 'Deceased']:
                member['status'] = 'deceased'
            else:
                member['status'] = 'alive'
        else:
            member['status'] = 'alive'
        
        members.append(member)
    
    return members


@router.post("/family/import/preview", response_model=ApiResponse)
async def import_preview(
    file: UploadFile = File(...),
    user_and_family: tuple = Depends(editor_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family
    
    try:
        content = await file.read()
        filename = file.filename.lower()
        
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = parse_excel_file(content)
        elif filename.endswith('.csv'):
            df = parse_csv_file(content)
        else:
            raise HTTPException(status_code=400, detail="不支持的文件格式，请上传 .xlsx, .xls 或 .csv 文件")
        
        members = parse_member_data(df)
        
        # 检测重复数据
        stmt = select(FamilyMember.name).where(
            FamilyMember.family_id == family.id,
            FamilyMember.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        existing_names = set(row[0] for row in result.all())
        
        duplicate_names = []
        new_members = []
        for member in members:
            if member['name'] in existing_names:
                duplicate_names.append(member['name'])
            else:
                new_members.append(member)
        
        return ApiResponse(
            success=True,
            data={
                "preview": members,
                "total_count": len(members),
                "new_count": len(new_members),
                "duplicate_count": len(duplicate_names),
                "duplicate_names": duplicate_names
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"文件解析失败: {str(e)}")


@router.post("/family/import", response_model=ApiResponse)
async def import_family_members(
    request_obj: Request,
    file: UploadFile = File(...),
    skip_duplicates: bool = Query(True, description="是否跳过重复数据"),
    user_and_family: tuple = Depends(editor_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family
    
    try:
        content = await file.read()
        filename = file.filename.lower()
        
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = parse_excel_file(content)
        elif filename.endswith('.csv'):
            df = parse_csv_file(content)
        else:
            raise HTTPException(status_code=400, detail="不支持的文件格式，请上传 .xlsx, .xls 或 .csv 文件")
        
        members_data = parse_member_data(df)
        
        if not members_data:
            raise HTTPException(status_code=400, detail="文件中没有有效的成员数据")
        
        # 获取现有成员
        stmt = select(FamilyMember).where(
            FamilyMember.family_id == family.id,
            FamilyMember.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        existing_members = result.scalars().all()
        existing_name_map = {m.name: m for m in existing_members}
        
        name_to_id = {}
        skipped_names = []
        imported_names = []
        
        for member_data in members_data:
            member_name = member_data['name']
            
            # 检查重复
            if member_name in existing_name_map:
                skipped_names.append(member_name)
                # 保留现有成员的ID用于父子关系
                name_to_id[member_name] = existing_name_map[member_name].id
                continue
            
            member = FamilyMember(
                id=generate_id(),
                family_id=family.id,
                name=member_data['name'],
                gender=member_data['gender'],
                generation=member_data['generation'],
                birth_year=member_data.get('birth_year'),
                death_year=member_data.get('death_year'),
                spouse=member_data.get('spouse'),
                residence=member_data.get('residence'),
                note=member_data.get('note'),
                status=member_data['status']
            )
            db.add(member)
            name_to_id[member_data['name']] = member.id
            imported_names.append(member_name)
        
        await db.flush()
        
        # 设置父子关系（包括现有成员和新导入成员）
        for member_data in members_data:
            member_name = member_data['name']
            
            # 只处理新导入成员的父子关系
            if member_name in imported_names and 'father_name' in member_data and member_data['father_name']:
                father_name = member_data['father_name']
                if father_name in name_to_id:
                    member_id = name_to_id[member_name]
                    stmt = (
                        update(FamilyMember)
                        .where(FamilyMember.id == member_id)
                        .values(father_id=name_to_id[father_name])
                    )
                    await db.execute(stmt)
        
        await db.commit()
        
        # 获取更新后的成员列表
        stmt = (
            select(FamilyMember)
            .where(FamilyMember.family_id == family.id, FamilyMember.deleted_at.is_(None))
            .order_by(FamilyMember.generation, FamilyMember.name)
        )
        result = await db.execute(stmt)
        members = result.scalars().all()
        
        member_list = []
        for m in members:
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
                createdAt=m.created_at,
                updatedAt=m.updated_at
            ))
        
        ip_address = request_obj.client.host if request_obj.client else None
        user_agent = request_obj.headers.get("user-agent")
        
        if imported_names:
            await log_service.create_log(
                db=db,
                user=current_user,
                operation=OperationType.CREATE,
                target_type=TargetType.FAMILY,
                target_id=family.id,
                description=f"导入了 {len(imported_names)} 条家族成员数据",
                ip_address=ip_address,
                user_agent=user_agent,
                after_data={"count": len(imported_names)},
                family_id=family.id
            )
        
        return ApiResponse(
            success=True,
            data={
                "imported_count": len(imported_names),
                "skipped_count": len(skipped_names),
                "skipped_names": skipped_names,
                "imported_names": imported_names,
                "members": member_list
            },
            message=f"成功导入 {len(imported_names)} 条数据，跳过 {len(skipped_names)} 条重复数据"
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.get("/family/export")
async def export_family_members(
    format: str = Query("xlsx", description="导出格式：xlsx 或 csv"),
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family
    
    try:
        stmt = (
            select(FamilyMember)
            .where(FamilyMember.family_id == family.id, FamilyMember.deleted_at.is_(None))
            .order_by(FamilyMember.generation, FamilyMember.name)
        )
        result = await db.execute(stmt)
        members = result.scalars().all()
        
        export_data = []
        for m in members:
            father_name = ""
            if m.father_id:
                father_stmt = select(FamilyMember.name).where(FamilyMember.id == m.father_id)
                father_result = await db.execute(father_stmt)
                father_name = father_result.scalar_one_or_none() or ""
            
            export_data.append({
                "姓名": m.name,
                "性别": "男" if m.gender == "male" else "女",
                "世代": m.generation,
                "出生年份": m.birth_year or "",
                "去世年份": m.death_year or "",
                "配偶": m.spouse or "",
                "父亲": father_name,
                "现居地": m.residence or "",
                "备注": m.note or "",
                "状态": "在世" if m.status == "alive" else "已故"
            })
        
        df = pd.DataFrame(export_data)
        
        output = BytesIO()
        
        if format.lower() == "csv":
            df.to_csv(output, index=False, encoding='utf-8-sig')
            media_type = "text/csv"
            filename = f"{family.surname}氏族谱数据.csv"
        else:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='家族成员')
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"{family.surname}氏族谱数据.xlsx"
        
        output.seek(0)
        
        encoded_filename = quote(filename)
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={encoded_filename}; filename*=UTF-8''{encoded_filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/home/stats", response_model=ApiResponse[HomeStatsResponse])
async def get_home_stats(
    user_and_family: tuple = Depends(viewer_required),
    db: AsyncSession = Depends(get_async_session)
):
    current_user, family, family_user = user_and_family
    
    try:
        member_count_stmt = select(func.count(FamilyMember.id)).where(
            FamilyMember.family_id == family.id,
            FamilyMember.deleted_at.is_(None)
        )
        member_count_result = await db.execute(member_count_stmt)
        member_count = member_count_result.scalar() or 0
        
        gallery_count_stmt = select(func.count(Gallery.id)).where(
            Gallery.family_id == family.id,
            Gallery.deleted_at.is_(None)
        )
        gallery_count_result = await db.execute(gallery_count_stmt)
        gallery_count = gallery_count_result.scalar() or 0
        
        avatar_count_stmt = select(func.count(Avatar.id)).where(Avatar.deleted_at.is_(None))
        avatar_count_result = await db.execute(avatar_count_stmt)
        avatar_count = avatar_count_result.scalar() or 0
        
        return ApiResponse(
            success=True,
            data=HomeStatsResponse(
                member_count=member_count,
                gallery_count=gallery_count,
                avatar_count=avatar_count
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取首页统计数据失败: {str(e)}")
