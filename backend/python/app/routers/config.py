from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.config import settings
from app.schemas import ApiResponse, UpdateConfigRequest

router = APIRouter(tags=["配置管理"])


class ConfigInfo(BaseModel):
    openai: Dict[str, Any]
    aliyun: Dict[str, Any]


@router.get("/config", response_model=ApiResponse[ConfigInfo])
async def get_config():
    return ApiResponse(
        success=True,
        data=ConfigInfo(
            openai={
                "apiKeyConfigured": False,
                "baseUrl": "https://api.openai.com/v1",
                "model": "gpt-4o"
            },
            aliyun={
                "apiKeyConfigured": bool(settings.ALIYUN_API_KEY),
                "baseUrl": settings.ALIYUN_BASE_URL,
                "imageModel": settings.ALIYUN_IMAGE_MODEL,
                "textModel": settings.ALIYUN_TEXT_MODEL
            }
        )
    )


@router.put("/config", response_model=ApiResponse)
async def update_config(request: UpdateConfigRequest):
    return ApiResponse(
        success=True,
        message="配置保存功能需要环境变量支持，请修改 .env 文件"
    )
