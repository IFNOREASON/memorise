from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas import (
    ApiResponse, PhotoAnalysisResponse, PhotoUploadRequest
)
from app.services import aliyun_service

router = APIRouter(tags=["照片分析"])


@router.post("/photos/analyze", response_model=ApiResponse[PhotoAnalysisResponse])
async def analyze_photos(request: PhotoUploadRequest):
    if not request.photos or len(request.photos) == 0:
        raise HTTPException(status_code=400, detail="请提供至少一张照片")
    
    try:
        result = await aliyun_service.analyze_photos(request.photos)
        return ApiResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"照片分析失败: {str(e)}")
