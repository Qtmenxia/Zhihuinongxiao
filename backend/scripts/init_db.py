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

# === 新增这段代码来修复 WinError 64 ===
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# ======================================

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
            return existing.id 
        
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
            subscription_start=datetime.now(timezone.utc).replace(tzinfo=None),
            services_count=0,
            api_calls_today=0,
            enable_commission=False, # 模型里可能有默认值，建议显式写上
            commission_rate=5,       # 同上
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            updated_at=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        
        session.add(demo_farmer)
        await session.commit()
        
        logger.info(f"✅ Demo farmer created: {demo_farmer.id}")
        return demo_farmer.id


# 👇 这里的定义要加上 farmer_id 参数！
async def init_products(farmer_id):
    """初始化产品数据"""
    print("Initializing products from catalog...")
    
    # 在函数内部开启一个新的数据库会话
    async with AsyncSessionLocal() as session:
        count = 0
        
        # 遍历配置字典
        for category_key, category_data in PRODUCT_CATALOG.items():
            
            # 获取类别通用信息
            cat_name = category_data.get("category_name", category_key)
            cat_desc = category_data.get("description", "")
            origin = category_data.get("origin", "")
            
            # 获取该类别下的 SKU 列表
            skus = category_data.get("skus", [])
            
            for sku_data in skus:
                full_description = f"{cat_desc} 产地：{origin}"
                
                product = Product(
                    id=f"prod_{secrets.token_hex(8)}",
                    
                    # 👇【关键修复】这里正确使用了传入的 farmer_id 参数
                    # 之前报错是因为这里是 None，或者变量名写错了
                    farmer_id=farmer_id,  
                    
                    name=sku_data["name"],
                    sku_code=sku_data.get("sku_code", f"SKU_{secrets.token_hex(4).upper()}"),
                    price=float(sku_data.get("price", 0)),
                    stock=int(sku_data.get("stock", 0)),
                    
                    category=cat_name,
                    description=full_description,
                    specs=sku_data.get("specs", {}),
                    images=sku_data.get("images", []),
                    
                    is_active=True,
                    is_featured=False,
                    
                    # 依然保持去时区
                    created_at=datetime.now(timezone.utc).replace(tzinfo=None),
                    updated_at=datetime.now(timezone.utc).replace(tzinfo=None)
                )
                
                session.add(product)
                count += 1
        
        # 提交事务
        await session.commit()
        print(f"✅ Successfully initialized {count} products from catalog.")


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
