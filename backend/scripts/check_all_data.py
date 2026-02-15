# -*- coding: utf-8 -*-
"""
检查数据库中的所有数据
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select, func
from backend.database.connection import AsyncSessionLocal
from backend.models.farmer import Farmer
from backend.models.product import Product
from backend.models.order import Order
from backend.models.customer import Customer
from backend.models.mcp_service import MCPService


async def check_all_data():
    """检查所有数据"""
    async with AsyncSessionLocal() as db:
        # 检查农户
        result = await db.execute(select(func.count()).select_from(Farmer))
        farmers_count = result.scalar()
        
        # 检查产品
        result = await db.execute(select(func.count()).select_from(Product))
        products_count = result.scalar()
        
        # 检查订单
        result = await db.execute(select(func.count()).select_from(Order))
        orders_count = result.scalar()
        
        # 检查客户
        result = await db.execute(select(func.count()).select_from(Customer))
        customers_count = result.scalar()
        
        # 检查服务
        result = await db.execute(select(func.count()).select_from(MCPService))
        services_count = result.scalar()
        
        print("\n" + "=" * 80)
        print("数据库数据统计")
        print("=" * 80)
        print(f"农户数量: {farmers_count}")
        print(f"产品数量: {products_count}")
        print(f"订单数量: {orders_count}")
        print(f"客户数量: {customers_count}")
        print(f"服务数量: {services_count}")
        print("=" * 80)
        
        # 显示所有农户
        if farmers_count > 0:
            result = await db.execute(select(Farmer))
            farmers = result.scalars().all()
            print("\n农户列表:")
            print("-" * 80)
            for f in farmers:
                print(f"ID: {f.id} | 姓名: {f.name} | 手机: {f.phone} | 等级: {f.tier.value}")
        
        # 显示所有产品
        if products_count > 0:
            result = await db.execute(select(Product))
            products = result.scalars().all()
            print("\n产品列表:")
            print("-" * 80)
            for p in products:
                print(f"ID: {p.id} | 名称: {p.name} | 价格: {p.price} | 农户ID: {p.farmer_id}")


if __name__ == "__main__":
    asyncio.run(check_all_data())

