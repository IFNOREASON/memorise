from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
import asyncio
from datetime import datetime
import os
import signal
import sys

from app.config import settings
from app.database import init_db, db_manager
from app.routers import (
    health_router,
    config_router,
    photos_router,
    avatars_router,
    memories_router,
    voice_router,
    chat_router,
    auth_router,
    family_router,
    anniversaries_router,
    push_rules_router,
    messages_router,
    galleries_router,
    family_memories_router,
    image_processing
)
from app.routers import membership, approval, logs
from app.services import generation_service
from app.services import anniversary_service
from app.services.image_processing_service import image_processing_service

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    """背景任务管理器，防止任务异常导致应用崩溃"""

    def __init__(self):
        self._tasks: dict[str, asyncio.Task] = {}
        self._running = False

    def create_task(self, coro, name: str):
        """创建带异常保护的背景任务"""
        if not self._running:
            self._running = True

        async def _protected_task():
            try:
                await coro
            except asyncio.CancelledError:
                logger.info(f"背景任务已取消: {name}")
            except Exception as e:
                logger.error(f"背景任务异常 {name}: {e}", exc_info=True)
                await asyncio.sleep(5)

        task = asyncio.create_task(_protected_task(), name=name)
        self._tasks[name] = task
        return task

    async def cancel_all(self):
        """取消所有背景任务"""
        self._running = False
        for name, task in self._tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        logger.info(f"已取消 {len(self._tasks)} 个背景任务")


task_manager = BackgroundTaskManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("正在启动 Memorise FastAPI Backend...")
    logger.info("=" * 60)

    try:
        logger.info("1/6 初始化数据库连接...")
        db_manager.initialize()
        await init_db()
        logger.info("✅ 数据库连接已建立")
    except Exception as e:
        logger.critical(f"❌ 数据库初始化失败: {e}", exc_info=True)
        raise

    try:
        logger.info("2/6 启动数据库健康检查...")
        await db_manager.start_health_check()
        logger.info("✅ 数据库健康检查已启动")
    except Exception as e:
        logger.error(f"❌ 启动健康检查失败: {e}")

    try:
        logger.info("3/6 启动背景任务...")
        task_manager.create_task(
            check_pending_retries_periodically(),
            "retry_checker"
        )
        task_manager.create_task(
            anniversary_service.anniversary_reminder_worker(),
            "anniversary_reminder"
        )
        task_manager.create_task(
            check_image_processing_retries_periodically(),
            "image_processing_retry"
        )
        logger.info("✅ 背景任务已启动")
    except Exception as e:
        logger.error(f"❌ 启动背景任务失败: {e}")

    try:
        logger.info("4/6 启动AI影像处理队列...")
        await image_processing_service.start_worker()
        logger.info("✅ AI影像处理队列已启动")
    except Exception as e:
        logger.error(f"❌ 启动影像处理队列失败: {e}")

    try:
        logger.info("5/6 初始化纪念日提醒任务...")
        await anniversary_service.create_recurring_reminder_tasks()
        logger.info("✅ 纪念日提醒任务初始化完成")
    except Exception as e:
        logger.error(f"❌ 初始化纪念日提醒任务失败: {e}")

    logger.info("6/6 服务启动完成!")
    logger.info("=" * 60)
    logger.info(f"API Base: /api")
    logger.info(f"端口: {settings.PORT}")
    logger.info(f"阿里云API已配置: {bool(settings.ALIYUN_API_KEY)}")
    logger.info(f"调试模式: {settings.DEBUG}")
    logger.info("=" * 60)

    yield

    logger.info("\n正在关闭服务...")

    try:
        await task_manager.cancel_all()
        logger.info("✅ 背景任务已关闭")
    except Exception as e:
        logger.error(f"关闭背景任务失败: {e}")

    try:
        await image_processing_service.stop_worker()
        logger.info("✅ AI影像处理队列已关闭")
    except Exception as e:
        logger.error(f"关闭影像处理队列失败: {e}")

    try:
        await db_manager.dispose()
        logger.info("✅ 数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接失败: {e}")

    logger.info("✅ 服务已正常停止")
    logger.info("=" * 60)


async def check_pending_retries_periodically():
    while True:
        try:
            async with db_manager.session_maker() as db:
                await generation_service.check_pending_retries(db)
        except OSError as e:
            if "121" in str(e) or "信号灯超时" in str(e):
                logger.warning("检测到数据库连接超时，尝试重连...")
                await db_manager.reconnect()
            else:
                logger.error(f"检查待重试任务失败 (OSError): {e}")
        except Exception as e:
            logger.error(f"检查待重试任务失败: {e}")

        await asyncio.sleep(settings.RETRY_DELAY_SECONDS)


async def check_image_processing_retries_periodically():
    while True:
        try:
            async with db_manager.session_maker() as db:
                await image_processing_service.check_pending_retries(db)
        except OSError as e:
            if "121" in str(e) or "信号灯超时" in str(e):
                logger.warning("检测到数据库连接超时，尝试重连...")
                await db_manager.reconnect()
            else:
                logger.error(f"检查影像处理待重试任务失败 (OSError): {e}")
        except Exception as e:
            logger.error(f"检查影像处理待重试任务失败: {e}")

        await asyncio.sleep(settings.RETRY_DELAY_SECONDS)


def handle_shutdown_signal(signal_num, frame):
    """处理系统关闭信号"""
    try:
        sig_name = signal.Signals(signal_num).name
    except ValueError:
        sig_name = f"UNKNOWN({signal_num})"
    logger.info(f"收到信号 {sig_name}，正在优雅关闭...")


try:
    signal.signal(signal.SIGINT, handle_shutdown_signal)
    signal.signal(signal.SIGTERM, handle_shutdown_signal)
except (AttributeError, ValueError, OSError) as e:
    logger.warning(f"无法注册信号处理器（Windows环境常见）: {e}")


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


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail if isinstance(exc.detail, str) else "请求失败",
            "message": None
        }
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

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(auth_router, prefix=api_prefix)
app.include_router(health_router, prefix=api_prefix)
app.include_router(config_router, prefix=api_prefix)
app.include_router(photos_router, prefix=api_prefix)
app.include_router(avatars_router, prefix=api_prefix)
app.include_router(memories_router, prefix=api_prefix)
app.include_router(voice_router, prefix=api_prefix)
app.include_router(chat_router, prefix=api_prefix)
app.include_router(family_router, prefix=api_prefix)
app.include_router(membership.router, prefix=api_prefix)
app.include_router(approval.router, prefix=api_prefix)
app.include_router(logs.router, prefix=api_prefix)
app.include_router(anniversaries_router, prefix=api_prefix)
app.include_router(push_rules_router, prefix=api_prefix)
app.include_router(messages_router, prefix=api_prefix)
app.include_router(galleries_router, prefix=api_prefix)
app.include_router(family_memories_router, prefix=api_prefix)
app.include_router(image_processing.router, prefix=api_prefix)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
