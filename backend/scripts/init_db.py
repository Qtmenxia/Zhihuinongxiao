"""
数据库初始化脚本
创建必要的表和初始数据
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from datetime import datetime, timezone
import hashlib
import secrets
import logging

from backend.database.connection import async_engine, AsyncSessionLocal
from backend.models.base import Base
from backend.models.farmer import Farmer, FarmerTier
from backend.models.product import Product
from backend.config.settings import settings
from backend.config.product_config import PRODUCT_CATALOG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """简单的密码哈希（生产环境应使用bcrypt）"""
    salt = settings.SECRET_KEY[:16]
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


async def init_tables():
    """创建数据库表"""
    logger.info("Creating database tables...")
    
    # 导入所有模型以确保它们被注册
    from backend.models import farmer, product, order, mcp_service, service_log
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ Database tables created successfully")


async def create_demo_farmer():
    """创建演示农户账号"""
    logger.info("Creating demo farmer account...")
    
    async with AsyncSessionLocal() as session:
        # 检查是否已存在
        from sqlalchemy import select
        result = await session.execute(
            select(Farmer).where(Farmer.phone == "13800138000")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.info("Demo farmer already exists, skipping...")
            return
        
        # 创建演示账号
        demo_farmer = Farmer(
            id=f"farmer_{secrets.token_hex(8)}",
            name="蒲县被子垣果园",
            phone="13800138000",
            password_hash=hash_password("demo123456"),
            email="demo@zhinonglianxiao.com",
            province="山西省",
            city="临汾市",
            county="蒲县",
            village="被子垣村",
            is_verified=True,
            certification_type="有机认证",
            tier=FarmerTier.BASIC,
            subscription_start=datetime.now(timezone.utc)(),
            services_count=0,
            api_calls_today=0
        )
        
        session.add(demo_farmer)
        await session.commit()
        
        logger.info(f"✅ Demo farmer created: {demo_farmer.id}")
        return demo_farmer.id


async def init_products(farmer_id: str):
    """初始化产品数据"""
    logger.info("Initializing products...")
    
    if not farmer_id:
        logger.warning("No farmer_id provided, skipping product initialization")
        return
    
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        
        # 检查是否已有产品
        result = await session.execute(
            select(Product).where(Product.farmer_id == farmer_id)
        )
        if result.scalars().first():
            logger.info("Products already exist, skipping...")
            return
        
        # 添加预设产品
        for category, products in PRODUCT_CATALOG.items():
            for product_info in products:
                product = Product(
                    id=f"prod_{secrets.token_hex(6)}",
                    farmer_id=farmer_id,
                    name=product_info["name"],
                    category=category,
                    sku=product_info.get("sku", ""),
                    description=product_info.get("description", ""),
                    price=product_info["price"],
                    unit=product_info.get("unit", "盒"),
                    stock=product_info.get("stock", 100),
                    weight=product_info.get("weight"),
                    origin=product_info.get("origin", "山西蒲县"),
                    certification=product_info.get("certification"),
                    is_active=True,
                    created_at=datetime.now(timezone.utc)()
                )
                session.add(product)
        
        await session.commit()
        logger.info(f"✅ Products initialized for farmer {farmer_id}")


async def main():
    """主初始化流程"""
    logger.info("=" * 50)
    logger.info("智农链销 - 数据库初始化")
    logger.info("=" * 50)
    
    try:
        # 1. 创建表
        await init_tables()
        
        # 2. 创建演示账号
        farmer_id = await create_demo_farmer()
        
        # 3. 初始化产品
        await init_products(farmer_id)
        
        logger.info("=" * 50)
        logger.info("✅ 数据库初始化完成！")
        logger.info("=" * 50)
        logger.info("")
        logger.info("演示账号信息：")
        logger.info("  手机号: 13800138000")
        logger.info("  密码: demo123456")
        logger.info("")
        
    except Exception as e:
        logger.error(f"❌ 初始化失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
