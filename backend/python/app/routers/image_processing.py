from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database import get_async_session
from app.schemas import (
    ApiResponse,
    CreateProcessTaskRequest, ProcessTaskResponse,
    ProcessTaskStatusResponse, ProcessTaskListResponse,
    BatchProcessRequest, BatchProcessResponse,
    RetryTaskRequest, ProcessTaskCancelResponse,
    ImageProcessType, ImageProcessStatus, ExportFormat
)
from app.services.image_processing_service import (
    image_processing_service, ImageProcessingError
)

router = APIRouter(prefix="/image-processing", tags=["AI影像处理"])
logger = logging.getLogger(__name__)


@router.post("/tasks", response_model=ApiResponse[ProcessTaskResponse])
async def create_task(
    request: CreateProcessTaskRequest,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        result = await image_processing_service.create_process_task(db, request)
        return ApiResponse(success=True, data=result)
    except ImageProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.post("/tasks/batch", response_model=ApiResponse[BatchProcessResponse])
async def create_batch_tasks(
    request: BatchProcessRequest,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        result = await image_processing_service.batch_create_tasks(db, request)
        return ApiResponse(success=True, data=result)
    except ImageProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"批量创建任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量创建任务失败: {str(e)}")


@router.get("/tasks/{task_id}", response_model=ApiResponse[ProcessTaskStatusResponse])
async def get_task_status(
    task_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        result = await image_processing_service.get_task_status(db, task_id)
        return ApiResponse(success=True, data=result)
    except ImageProcessingError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取任务状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")


@router.get("/galleries/{gallery_id}/tasks", response_model=ApiResponse[ProcessTaskListResponse])
async def get_gallery_tasks(
    gallery_id: str,
    status: Optional[ImageProcessStatus] = Query(None, description="任务状态过滤"),
    task_type: Optional[ImageProcessType] = Query(None, description="任务类型过滤"),
    limit: int = Query(50, ge=1, le=200, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        result = await image_processing_service.get_gallery_tasks(
            db, gallery_id, status=status, task_type=task_type, limit=limit, offset=offset
        )
        return ApiResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"获取影集任务列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")


@router.post("/tasks/{task_id}/retry", response_model=ApiResponse[ProcessTaskResponse])
async def retry_task(
    task_id: str,
    request: Optional[RetryTaskRequest] = None,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        reset_retry_count = request.reset_retry_count if request else False
        result = await image_processing_service.retry_task(db, task_id, reset_retry_count)
        return ApiResponse(success=True, data=result)
    except ImageProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"重试任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"重试任务失败: {str(e)}")


@router.post("/tasks/{task_id}/cancel", response_model=ApiResponse[ProcessTaskCancelResponse])
async def cancel_task(
    task_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        result = await image_processing_service.cancel_task(db, task_id)
        return ApiResponse(success=True, data=result)
    except ImageProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"取消任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}")


@router.get("/tasks/{task_id}/result")
async def get_task_result(
    task_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        result = await image_processing_service.get_processed_result(db, task_id)
        return ApiResponse(success=True, data=result)
    except ImageProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取任务结果失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务结果失败: {str(e)}")


@router.get("/types")
async def get_process_types():
    types = [
        {"type": ImageProcessType.RESTORATION.value, "name": "老照片修复", "description": "去除划痕、污渍，恢复色彩"},
        {"type": ImageProcessType.ENHANCEMENT.value, "name": "高清放大", "description": "AI超分辨率增强，放大不失真"},
        {"type": ImageProcessType.DYNAMIC_PORTRAIT.value, "name": "动态肖像生成", "description": "让静态照片动起来"},
        {"type": ImageProcessType.CROSS_GENERATION.value, "name": "跨年代合照合成", "description": "合成不同年代的照片"},
        {"type": ImageProcessType.VIDEO_HIGHLIGHTS.value, "name": "视频集锦生成", "description": "多张照片合成精彩视频"},
        {"type": ImageProcessType.AI_SCENE.value, "name": "AI场景生成", "description": "根据描述生成AI场景"}
    ]
    return ApiResponse(success=True, data={"types": types})


@router.get("/export/formats")
async def get_export_formats():
    formats = [
        {"format": ExportFormat.JPG.value, "name": "JPEG图像", "description": "通用有损压缩格式"},
        {"format": ExportFormat.PNG.value, "name": "PNG图像", "description": "无损压缩，支持透明"},
        {"format": ExportFormat.WEBP.value, "name": "WebP图像", "description": "Google高效格式"},
        {"format": ExportFormat.MP4.value, "name": "MP4视频", "description": "通用视频格式"},
        {"format": ExportFormat.GIF.value, "name": "GIF动图", "description": "动态图像格式"}
    ]
    return ApiResponse(success=True, data={"formats": formats})


@router.get("/health")
async def health_check():
    return ApiResponse(
        success=True,
        data={
            "status": "healthy",
            "queue_worker_running": image_processing_service._is_running
        }
    )
