"""
数据库连接管理
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from typing import AsyncGenerator, Generator
import logging

from backend.config.settings import settings

logger = logging.getLogger(__name__)

# 同步引擎(用于Alembic迁移等)
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# 异步引擎(推荐用于API)
async_database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
async_engine = create_async_engine(
    async_database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# 同步会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    """
    获取同步数据库会话
    
    用于同步代码和Alembic迁移
    
    Yields:
        Session: 数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取异步数据库会话
    
    推荐用于FastAPI路由
    
    Yields:
        AsyncSession: 异步数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    初始化数据库
    
    创建所有表(生产环境应使用Alembic迁移)
    """
    from backend.models.base import Base
    
    # 导入所有模型以确保它们被注册
    from backend.models import farmer, product, order, mcp_service, service_log
    
    logger.info("Initializing database tables...")
    
    async with async_engine.begin() as conn:
        # 生产环境注释掉这行，使用Alembic迁移
        if settings.DEBUG:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        else:
            logger.info("Skipping table creation (use Alembic in production)")


async def close_db():
    """
    关闭数据库连接
    
    应在应用关闭时调用
    """
    await async_engine.dispose()
    logger.info("Database connections closed")
