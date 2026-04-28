from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import asyncio
from datetime import datetime

from app.config import settings
from app.database import init_db
from app.routers import (
    health_router,
    config_router,
    photos_router,
    avatars_router,
    memories_router,
    voice_router,
    chat_router
)
from app.services import generation_service
from app.database import AsyncSessionLocal

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("正在初始化数据库连接...")
    await init_db()
    logger.info("数据库连接已建立")
    
    logger.info("Memorise FastAPI Backend 已启动")
    logger.info(f"API Base: /api/v1")
    logger.info(f"端口: {settings.PORT}")
    logger.info(f"阿里云API已配置: {bool(settings.ALIYUN_API_KEY)}")
    
    retry_task = asyncio.create_task(check_pending_retries_periodically())
    
    yield
    
    retry_task.cancel()
    try:
        await retry_task
    except asyncio.CancelledError:
        pass
    
    logger.info("Memorise FastAPI Backend 已停止")


async def check_pending_retries_periodically():
    while True:
        try:
            async with AsyncSessionLocal() as db:
                await generation_service.check_pending_retries(db)
        except Exception as e:
            logger.error(f"检查待重试任务失败: {e}")
        
        await asyncio.sleep(settings.RETRY_DELAY_SECONDS)


app = FastAPI(
    title="Memorise API",
    description="数字人记忆管理系统 - FastAPI后端",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "服务器内部错误",
            "message": str(exc)
        }
    )


@app.get("/")
async def root():
    return {
        "name": "Memorise FastAPI Backend",
        "version": "2.0.0",
        "status": "ok",
        "api_prefix": "/api/v1",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.get("/api")
async def api_root():
    return {
        "name": "Memorise API",
        "version": "2.0.0",
        "endpoints": {
            "health": "/api/health",
            "config": "/api/config",
            "photos": "/api/photos",
            "avatars": "/api/avatars",
            "memories": "/api/memories",
            "voice": "/api/voice",
            "chat": "/api/chat"
        }
    }


api_prefix = "/api"

app.include_router(health_router, prefix=api_prefix)
app.include_router(config_router, prefix=api_prefix)
app.include_router(photos_router, prefix=api_prefix)
app.include_router(avatars_router, prefix=api_prefix)
app.include_router(memories_router, prefix=api_prefix)
app.include_router(voice_router, prefix=api_prefix)
app.include_router(chat_router, prefix=api_prefix)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
