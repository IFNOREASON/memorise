import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime, func, String, text
from datetime import datetime
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库连接管理器，支持自动重连和健康检查"""

    def __init__(self):
        self._engine: Optional[create_async_engine] = None
        self._session_maker: Optional[async_sessionmaker] = None
        self._health_check_task: Optional[asyncio.Task] = None
        self._is_running = False

    def create_engine(self):
        """创建数据库引擎，优化Windows下的连接配置"""
        connect_args = {
            "timeout": 60,
            "command_timeout": 60,
            "statement_cache_size": 0,
            "server_settings": {
                "jit": "off",
                "search_path": "public"
            }
        }

        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            isolation_level="READ COMMITTED",
            connect_args=connect_args
        )

        return engine

    def initialize(self):
        """初始化数据库连接"""
        self._engine = self.create_engine()
        self._session_maker = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        logger.info("数据库连接管理器已初始化")

    @property
    def engine(self):
        if self._engine is None:
            self.initialize()
        return self._engine

    @property
    def session_maker(self):
        if self._session_maker is None:
            self.initialize()
        return self._session_maker

    async def check_connection(self) -> bool:
        """检查数据库连接是否健康"""
        try:
            async with self.session_maker() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.warning(f"数据库连接健康检查失败: {e}")
            return False

    async def reconnect(self):
        """强制重连数据库"""
        logger.info("正在重新连接数据库...")
        if self._engine:
            await self._engine.dispose()
        self.initialize()
        await init_db()
        logger.info("数据库重连完成")

    async def health_check_loop(self, check_interval: int = 60):
        """定期健康检查循环"""
        while self._is_running:
            try:
                is_healthy = await self.check_connection()
                if not is_healthy:
                    logger.warning("数据库连接不健康，尝试重连...")
                    await self.reconnect()
            except Exception as e:
                logger.error(f"健康检查任务错误: {e}")
            await asyncio.sleep(check_interval)

    async def start_health_check(self):
        """启动健康检查任务"""
        if not self._is_running:
            self._is_running = True
            self._health_check_task = asyncio.create_task(
                self.health_check_loop(),
                name="db_health_check"
            )
            logger.info("数据库健康检查任务已启动")

    async def stop_health_check(self):
        """停止健康检查任务"""
        self._is_running = False
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None
            logger.info("数据库健康检查任务已停止")

    async def dispose(self):
        """关闭所有连接"""
        await self.stop_health_check()
        if self._engine:
            await self._engine.dispose()
            logger.info("数据库连接池已关闭")


db_manager = DatabaseManager()


@asynccontextmanager
async def get_db_session():
    """获取数据库会话的上下文管理器"""
    session = db_manager.session_maker()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """依赖注入用的会话生成器"""
    async with db_manager.session_maker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


async def init_db() -> None:
    """初始化数据库表"""
    try:
        async with db_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise
