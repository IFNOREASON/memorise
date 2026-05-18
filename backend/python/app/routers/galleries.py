from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from typing import Optional, List
from datetime import datetime
import uuid
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, and_
from sqlalchemy.orm import selectinload

from app.database import get_async_session
from app.config import settings
from app.models import Gallery, GalleryMedia, GalleryStatus, GalleryType, Family
from app.schemas import (
    ApiResponse,
    GalleryBase, GalleryCreateRequest, GalleryUpdateRequest,
    GalleryListResponse, GalleryDetailResponse,
    GalleryMediaBase, GalleryMediaCreateRequest, GalleryMediaListResponse
)

router = APIRouter(tags=["影集管理"])


def generate_uuid() -> str:
    return str(uuid.uuid4())


def ensure_upload_dir():
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "galleries"), exist_ok=True)


@router.post("/galleries", response_model=ApiResponse[GalleryBase])
async def create_gallery(
    request: GalleryCreateRequest,
    db: AsyncSession = Depends(get_async_session)
):
    if not request.name:
        raise HTTPException(status_code=400, detail="影集名称不能为空")
    
    try:
        family_stmt = select(Family).limit(1)
        family_result = await db.execute(family_stmt)
        family = family_result.scalar_one_or_none()
        
        if not family:
            family = Family(
                id=generate_uuid(),
                surname="默认家族",
                hall_name="默认家族祠堂"
            )
            db.add(family)
            await db.commit()
        
        gallery = Gallery(
            id=generate_uuid(),
            family_id=family.id,
            name=request.name,
            description=request.description,
            person_name=request.person_name,
            type=request.type.value if request.type else GalleryType.IMAGE.value,
            status=GalleryStatus.DRAFT.value,
            progress=0
        )
        
        db.add(gallery)
        await db.commit()
        await db.refresh(gallery)
        
        return ApiResponse(
            success=True,
            data=GalleryBase(
                id=gallery.id,
                familyId=gallery.family_id,
                name=gallery.name,
                description=gallery.description,
                personName=gallery.person_name,
                type=GalleryType(gallery.type),
                status=GalleryStatus(gallery.status),
                progress=gallery.progress,
                coverUrl=gallery.cover_url,
                mediaCount=0,
                createdAt=gallery.created_at,
                updatedAt=gallery.updated_at
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建影集失败: {str(e)}")


@router.get("/galleries", response_model=ApiResponse[GalleryListResponse])
async def get_galleries(
    status: Optional[GalleryStatus] = None,
    type: Optional[GalleryType] = None,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        query = select(Gallery).where(Gallery.deleted_at.is_(None))
        
        if status:
            query = query.where(Gallery.status == status.value)
        if type:
            query = query.where(Gallery.type == type.value)
        
        query = query.order_by(Gallery.created_at.desc())
        
        result = await db.execute(query)
        galleries = result.scalars().all()
        
        gallery_list = []
        for gallery in galleries:
            media_count_stmt = select(func.count(GalleryMedia.id)).where(
                GalleryMedia.gallery_id == gallery.id
            )
            media_count_result = await db.execute(media_count_stmt)
            media_count = media_count_result.scalar_one()
            
            gallery_list.append(GalleryBase(
                id=gallery.id,
                familyId=gallery.family_id,
                name=gallery.name,
                description=gallery.description,
                personName=gallery.person_name,
                type=GalleryType(gallery.type),
                status=GalleryStatus(gallery.status),
                progress=gallery.progress,
                coverUrl=gallery.cover_url,
                mediaCount=media_count,
                createdAt=gallery.created_at,
                updatedAt=gallery.updated_at
            ))
        
        return ApiResponse(
            success=True,
            data=GalleryListResponse(
                total=len(gallery_list),
                galleries=gallery_list
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取影集列表失败: {str(e)}")


@router.get("/galleries/{gallery_id}", response_model=ApiResponse[GalleryDetailResponse])
async def get_gallery(
    gallery_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(Gallery).where(
            Gallery.id == gallery_id,
            Gallery.deleted_at.is_(None)
        ).options(selectinload(Gallery.medias))
        
        result = await db.execute(stmt)
        gallery = result.scalar_one_or_none()
        
        if not gallery:
            raise HTTPException(status_code=404, detail="影集不存在")
        
        media_list = [
            GalleryMediaBase(
                id=m.id,
                galleryId=m.gallery_id,
                url=m.url,
                type=m.type,
                dateTime=m.date_time,
                location=m.location,
                duration=m.duration,
                audioUrl=m.audio_url,
                description=m.description,
                thumbnailUrl=m.thumbnail_url,
                sortOrder=m.sort_order,
                createdAt=m.created_at,
                updatedAt=m.updated_at
            ) for m in gallery.medias
        ]
        
        return ApiResponse(
            success=True,
            data=GalleryDetailResponse(
                gallery=GalleryBase(
                    id=gallery.id,
                    familyId=gallery.family_id,
                    name=gallery.name,
                    description=gallery.description,
                    personName=gallery.person_name,
                    type=GalleryType(gallery.type),
                    status=GalleryStatus(gallery.status),
                    progress=gallery.progress,
                    coverUrl=gallery.cover_url,
                    mediaCount=len(media_list),
                    createdAt=gallery.created_at,
                    updatedAt=gallery.updated_at
                ),
                medias=media_list
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取影集详情失败: {str(e)}")


@router.put("/galleries/{gallery_id}", response_model=ApiResponse[GalleryBase])
async def update_gallery(
    gallery_id: str,
    request: GalleryUpdateRequest,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(Gallery).where(
            Gallery.id == gallery_id,
            Gallery.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        gallery = result.scalar_one_or_none()
        
        if not gallery:
            raise HTTPException(status_code=404, detail="影集不存在")
        
        if request.name is not None:
            gallery.name = request.name
        if request.description is not None:
            gallery.description = request.description
        if request.person_name is not None:
            gallery.person_name = request.person_name
        if request.type is not None:
            gallery.type = request.type.value
        if request.status is not None:
            gallery.status = request.status.value
        if request.cover_url is not None:
            gallery.cover_url = request.cover_url
        
        await db.commit()
        await db.refresh(gallery)
        
        media_count_stmt = select(func.count(GalleryMedia.id)).where(
            GalleryMedia.gallery_id == gallery.id
        )
        media_count_result = await db.execute(media_count_stmt)
        media_count = media_count_result.scalar_one()
        
        return ApiResponse(
            success=True,
            data=GalleryBase(
                id=gallery.id,
                familyId=gallery.family_id,
                name=gallery.name,
                description=gallery.description,
                personName=gallery.person_name,
                type=GalleryType(gallery.type),
                status=GalleryStatus(gallery.status),
                progress=gallery.progress,
                coverUrl=gallery.cover_url,
                mediaCount=media_count,
                createdAt=gallery.created_at,
                updatedAt=gallery.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新影集失败: {str(e)}")


@router.delete("/galleries/{gallery_id}", response_model=ApiResponse)
async def delete_gallery(
    gallery_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(Gallery).where(
            Gallery.id == gallery_id,
            Gallery.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        gallery = result.scalar_one_or_none()
        
        if not gallery:
            raise HTTPException(status_code=404, detail="影集不存在")
        
        gallery.deleted_at = datetime.now()
        await db.commit()
        
        return ApiResponse(
            success=True,
            message="影集已删除"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除影集失败: {str(e)}")


@router.post("/galleries/{gallery_id}/medias", response_model=ApiResponse[GalleryMediaBase])
async def add_media(
    gallery_id: str,
    request: GalleryMediaCreateRequest,
    db: AsyncSession = Depends(get_async_session)
):
    if not request.url:
        raise HTTPException(status_code=400, detail="媒体URL不能为空")
    
    try:
        gallery_stmt = select(Gallery).where(
            Gallery.id == gallery_id,
            Gallery.deleted_at.is_(None)
        )
        gallery_result = await db.execute(gallery_stmt)
        gallery = gallery_result.scalar_one_or_none()
        
        if not gallery:
            raise HTTPException(status_code=404, detail="影集不存在")
        
        media = GalleryMedia(
            id=generate_uuid(),
            gallery_id=gallery_id,
            url=request.url,
            type=request.type.value,
            date_time=request.date_time,
            location=request.location,
            duration=request.duration,
            audio_url=request.audio_url,
            description=request.description,
            thumbnail_url=request.thumbnail_url
        )
        
        db.add(media)
        await db.commit()
        await db.refresh(media)
        
        return ApiResponse(
            success=True,
            data=GalleryMediaBase(
                id=media.id,
                galleryId=media.gallery_id,
                url=media.url,
                type=media.type,
                dateTime=media.date_time,
                location=media.location,
                duration=media.duration,
                audioUrl=media.audio_url,
                description=media.description,
                thumbnailUrl=media.thumbnail_url,
                sortOrder=media.sort_order,
                createdAt=media.created_at,
                updatedAt=media.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加媒体失败: {str(e)}")


@router.get("/galleries/{gallery_id}/medias", response_model=ApiResponse[GalleryMediaListResponse])
async def get_medias(
    gallery_id: str,
    type: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        gallery_stmt = select(Gallery).where(
            Gallery.id == gallery_id,
            Gallery.deleted_at.is_(None)
        )
        gallery_result = await db.execute(gallery_stmt)
        gallery = gallery_result.scalar_one_or_none()
        
        if not gallery:
            raise HTTPException(status_code=404, detail="影集不存在")
        
        query = select(GalleryMedia).where(GalleryMedia.gallery_id == gallery_id)
        
        if type:
            query = query.where(GalleryMedia.type == type)
        
        query = query.order_by(GalleryMedia.sort_order, GalleryMedia.created_at.desc())
        
        result = await db.execute(query)
        medias = result.scalars().all()
        
        media_list = [
            GalleryMediaBase(
                id=m.id,
                galleryId=m.gallery_id,
                url=m.url,
                type=m.type,
                dateTime=m.date_time,
                location=m.location,
                duration=m.duration,
                audioUrl=m.audio_url,
                description=m.description,
                thumbnailUrl=m.thumbnail_url,
                sortOrder=m.sort_order,
                createdAt=m.created_at,
                updatedAt=m.updated_at
            ) for m in medias
        ]
        
        return ApiResponse(
            success=True,
            data=GalleryMediaListResponse(
                total=len(media_list),
                medias=media_list
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取媒体列表失败: {str(e)}")


@router.delete("/galleries/{gallery_id}/medias/{media_id}", response_model=ApiResponse)
async def delete_media(
    gallery_id: str,
    media_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        gallery_stmt = select(Gallery).where(
            Gallery.id == gallery_id,
            Gallery.deleted_at.is_(None)
        )
        gallery_result = await db.execute(gallery_stmt)
        gallery = gallery_result.scalar_one_or_none()
        
        if not gallery:
            raise HTTPException(status_code=404, detail="影集不存在")
        
        media_stmt = select(GalleryMedia).where(
            GalleryMedia.id == media_id,
            GalleryMedia.gallery_id == gallery_id
        )
        media_result = await db.execute(media_stmt)
        media = media_result.scalar_one_or_none()
        
        if not media:
            raise HTTPException(status_code=404, detail="媒体不存在")
        
        await db.execute(delete(GalleryMedia).where(GalleryMedia.id == media_id))
        await db.commit()
        
        return ApiResponse(
            success=True,
            message="媒体已删除"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除媒体失败: {str(e)}")


@router.post("/galleries/{gallery_id}/medias/upload", response_model=ApiResponse[GalleryMediaBase])
async def upload_media(
    gallery_id: str,
    file: UploadFile = File(...),
    audio_file: Optional[UploadFile] = File(None),
    date_time: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    duration: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        ensure_upload_dir()
        
        gallery_stmt = select(Gallery).where(
            Gallery.id == gallery_id,
            Gallery.deleted_at.is_(None)
        )
        gallery_result = await db.execute(gallery_stmt)
        gallery = gallery_result.scalar_one_or_none()
        
        if not gallery:
            raise HTTPException(status_code=404, detail="影集不存在")
        
        if not file.content_type or not (file.content_type.startswith("image/") or file.content_type.startswith("video/")):
            raise HTTPException(status_code=400, detail="只支持图片或视频文件")
        
        file_ext = os.path.splitext(file.filename)[1].lower() if file.filename else ".jpg"
        new_filename = f"{generate_uuid()}{file_ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, "galleries", new_filename)
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        audio_url = None
        if audio_file and audio_file.content_type and audio_file.content_type.startswith("audio/"):
            audio_ext = os.path.splitext(audio_file.filename)[1].lower() if audio_file.filename else ".webm"
            audio_filename = f"{generate_uuid()}{audio_ext}"
            audio_path = os.path.join(settings.UPLOAD_DIR, "galleries", audio_filename)
            
            audio_content = await audio_file.read()
            with open(audio_path, "wb") as f:
                f.write(audio_content)
            
            audio_url = f"/uploads/galleries/{audio_filename}"
        
        media_type = "image" if file.content_type.startswith("image/") else "video"
        
        media = GalleryMedia(
            id=generate_uuid(),
            gallery_id=gallery_id,
            url=f"/uploads/galleries/{new_filename}",
            type=media_type,
            date_time=date_time if date_time else datetime.now().isoformat(),
            location=location,
            duration=duration,
            audio_url=audio_url,
            description=description
        )
        
        db.add(media)
        await db.commit()
        await db.refresh(media)
        
        return ApiResponse(
            success=True,
            data=GalleryMediaBase(
                id=media.id,
                galleryId=media.gallery_id,
                url=media.url,
                type=media.type,
                dateTime=media.date_time,
                location=media.location,
                duration=media.duration,
                audioUrl=media.audio_url,
                description=media.description,
                thumbnailUrl=media.thumbnail_url,
                sortOrder=media.sort_order,
                createdAt=media.created_at,
                updatedAt=media.updated_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传媒体失败: {str(e)}")


@router.get("/galleries/{gallery_id}/medias/search", response_model=ApiResponse[GalleryMediaListResponse])
async def search_medias(
    gallery_id: str,
    keyword: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    location: Optional[str] = None,
    type: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        gallery_stmt = select(Gallery).where(
            Gallery.id == gallery_id,
            Gallery.deleted_at.is_(None)
        )
        gallery_result = await db.execute(gallery_stmt)
        gallery = gallery_result.scalar_one_or_none()
        
        if not gallery:
            raise HTTPException(status_code=404, detail="影集不存在")
        
        query = select(GalleryMedia).where(GalleryMedia.gallery_id == gallery_id)
        
        if keyword:
            keyword_lower = f"%{keyword.lower()}%"
            query = query.where(
                func.lower(GalleryMedia.location).like(keyword_lower)
            )
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.where(GalleryMedia.date_time >= start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
                query = query.where(GalleryMedia.date_time <= end_dt)
            except ValueError:
                pass
        
        if location:
            loc_lower = f"%{location.lower()}%"
            query = query.where(func.lower(GalleryMedia.location).like(loc_lower))
        
        if type:
            query = query.where(GalleryMedia.type == type)
        
        query = query.order_by(GalleryMedia.date_time.desc(), GalleryMedia.created_at.desc())
        
        result = await db.execute(query)
        medias = result.scalars().all()
        
        media_list = [
            GalleryMediaBase(
                id=m.id,
                galleryId=m.gallery_id,
                url=m.url,
                type=m.type,
                dateTime=m.date_time,
                location=m.location,
                duration=m.duration,
                audioUrl=m.audio_url,
                description=m.description,
                thumbnailUrl=m.thumbnail_url,
                sortOrder=m.sort_order,
                createdAt=m.created_at,
                updatedAt=m.updated_at
            ) for m in medias
        ]
        
        return ApiResponse(
            success=True,
            data=GalleryMediaListResponse(
                total=len(media_list),
                medias=media_list
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索媒体失败: {str(e)}")
