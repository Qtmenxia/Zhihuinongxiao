# -*- coding: utf-8 -*-
"""
初始化Demo农户账号
创建一个真实的Demo账号到数据库中
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt
from datetime import datetime, timezone

from backend.database.connection import AsyncSessionLocal, init_db
from backend.models.farmer import Farmer, FarmerTier


async def create_demo_farmer():
    """创建Demo农户账号"""
    
    # 初始化数据库
    print("[INFO] Initializing database...")
    await init_db()
    
    async with AsyncSessionLocal() as db:
        # 检查Demo账号是否已存在
        result = await db.execute(
            select(Farmer).where(Farmer.phone == "13800138000")
        )
        existing_farmer = result.scalar_one_or_none()
        
        if existing_farmer:
            print("[SUCCESS] Demo account already exists")
            print(f"   ID: {existing_farmer.id}")
            print(f"   Name: {existing_farmer.name}")
            print(f"   Phone: {existing_farmer.phone}")
            print(f"   Tier: {existing_farmer.tier.value}")
            return
        
        # 创建Demo账号
        print("[INFO] Creating demo account...")
        
        # 哈希密码
        password_hash = bcrypt.hashpw(
            "demo123456".encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        demo_farmer = Farmer(
            id="farmer_demo_001",
            name="Puxian Beiziyuan Orchard",
            phone="13800138000",
            password_hash=password_hash,
            email="demo@zhinonglianxiao.com",
            province="Shanxi",
            city="Linfen",
            county="Puxian",
            village="Beiziyuan",
            tier=FarmerTier.BASIC,
            is_verified=True,
            certification_type="Organic Certification",
            services_count=0,
            api_calls_today=0,
            enable_commission=False,
            commission_rate=5,
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(demo_farmer)
        await db.commit()
        await db.refresh(demo_farmer)
        
        print("[SUCCESS] Demo account created successfully!")
        print(f"   ID: {demo_farmer.id}")
        print(f"   Name: {demo_farmer.name}")
        print(f"   Phone: {demo_farmer.phone}")
        print(f"   Password: demo123456")
        print(f"   Tier: {demo_farmer.tier.value}")
        print(f"   Email: {demo_farmer.email}")
        print(f"   Location: {demo_farmer.province} {demo_farmer.city} {demo_farmer.county} {demo_farmer.village}")


if __name__ == "__main__":
    print("=" * 60)
    print("ZhiNongLianXiao - Demo Account Initialization")
    print("=" * 60)
    
    try:
        asyncio.run(create_demo_farmer())
        print("\n[SUCCESS] Initialization completed!")
        print("\n[INFO] Login credentials:")
        print("   Phone: 13800138000")
        print("   Password: demo123456")
        print("=" * 60)
    except Exception as e:
        print(f"\n[ERROR] Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

