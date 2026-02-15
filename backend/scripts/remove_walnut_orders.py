# -*- coding: utf-8 -*-
"""
删除包含核桃的订单
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from backend.database.connection import AsyncSessionLocal
from backend.models.farmer import Farmer
from backend.models.order import Order


async def remove_walnut_orders():
    """删除包含核桃的订单"""
    async with AsyncSessionLocal() as db:
        print("\n" + "=" * 80)
        print("删除包含核桃的订单")
        print("=" * 80)
        
        # 获取Demo农户
        result = await db.execute(
            select(Farmer).where(Farmer.phone == "13800138000")
        )
        farmer = result.scalar_one_or_none()
        
        if not farmer:
            print("[ERROR] 找不到Demo账号！")
            return
        
        # 获取所有订单
        result = await db.execute(
            select(Order).where(Order.farmer_id == farmer.id)
        )
        all_orders = result.scalars().all()
        
        print(f"\n当前订单总数: {len(all_orders)}")
        
        # 找出包含核桃的订单
        orders_to_delete = []
        for order in all_orders:
            for item in order.items:
                if item.get('product_name') == '核桃':
                    orders_to_delete.append(order)
                    print(f"   找到订单: {order.id} - 包含核桃")
                    break
        
        print(f"\n包含核桃的订单数: {len(orders_to_delete)}")
        
        if len(orders_to_delete) == 0:
            print("\n[INFO] 没有找到包含核桃的订单")
            return
        
        # 删除这些订单
        for order in orders_to_delete:
            await db.delete(order)
            print(f"   删除订单: {order.id}")
        
        await db.commit()
        print(f"\n[OK] 已删除 {len(orders_to_delete)} 个订单")
        
        # 获取剩余订单数
        result = await db.execute(
            select(Order).where(Order.farmer_id == farmer.id)
        )
        remaining_orders = result.scalars().all()
        print(f"剩余订单数: {len(remaining_orders)}")
        
        # 验证没有核桃
        walnut_count = 0
        for order in remaining_orders:
            for item in order.items:
                if item.get('product_name') == '核桃':
                    walnut_count += 1
        
        print("\n" + "=" * 80)
        if walnut_count == 0:
            print("[OK] 确认：所有订单中都不包含核桃")
        else:
            print(f"[WARNING] 警告：仍有 {walnut_count} 个订单项包含核桃")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(remove_walnut_orders())

