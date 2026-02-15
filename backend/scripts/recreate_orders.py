# -*- coding: utf-8 -*-
"""
清空现有订单并重新创建更美观的订单（每个订单1-3个商品）
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select, delete
from datetime import datetime, timezone, timedelta
import uuid
import random

from backend.database.connection import AsyncSessionLocal
from backend.models.farmer import Farmer
from backend.models.product import Product
from backend.models.customer import Customer
from backend.models.order import Order, OrderStatus


async def recreate_orders():
    """重新创建订单"""
    async with AsyncSessionLocal() as db:
        print("\n" + "=" * 80)
        print("重新创建订单数据")
        print("=" * 80)
        
        # 获取Demo农户
        result = await db.execute(
            select(Farmer).where(Farmer.phone == "13800138000")
        )
        farmer = result.scalar_one_or_none()
        
        if not farmer:
            print("[ERROR] 找不到Demo账号！")
            return
        
        print(f"\n[OK] 找到账号: {farmer.name}")
        
        # 删除现有订单
        print("\n删除现有订单...")
        result = await db.execute(
            delete(Order).where(Order.farmer_id == farmer.id)
        )
        await db.commit()
        print(f"[OK] 已删除旧订单")
        
        # 获取所有产品
        result = await db.execute(
            select(Product).where(Product.farmer_id == farmer.id)
        )
        all_products = result.scalars().all()
        print(f"[INFO] 产品数量: {len(all_products)}")
        
        # 获取所有客户
        result = await db.execute(
            select(Customer).where(Customer.farmer_id == farmer.id)
        )
        all_customers = result.scalars().all()
        print(f"[INFO] 客户数量: {len(all_customers)}")
        
        if len(all_products) == 0 or len(all_customers) == 0:
            print("[ERROR] 没有产品或客户")
            return
        
        # 创建30个订单，每个订单1-3个商品
        order_count = 30
        statuses = [OrderStatus.PENDING, OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.COMPLETED, OrderStatus.CANCELLED]
        
        print(f"\n开始创建 {order_count} 个订单（每个订单1-3个商品）...")
        
        for i in range(order_count):
            # 随机选择客户
            customer = random.choice(all_customers)
            
            # 随机选择1-3个商品（更美观）
            num_items = random.randint(1, 3)
            selected_products = random.sample(all_products, min(num_items, len(all_products)))
            
            # 计算订单金额
            subtotal = 0
            order_items = []
            
            for product in selected_products:
                quantity = random.randint(1, 5)  # 数量也减少
                item_subtotal = product.price * quantity
                subtotal += item_subtotal
                
                order_items.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "sku_code": product.sku_code,
                    "price": product.price,
                    "quantity": quantity,
                    "subtotal": item_subtotal
                })
            
            # 运费和折扣
            shipping_fee = 10.0 if subtotal < 100 else 0.0
            discount = 0.0
            total_amount = subtotal + shipping_fee - discount
            
            # 随机状态
            status = random.choice(statuses)
            
            # 创建时间（最近30天内）
            days_ago = random.randint(0, 30)
            created_time = datetime.now(timezone.utc) - timedelta(days=days_ago)
            
            # 配送地址
            shipping_address = {
                "name": customer.name,
                "phone": customer.phone,
                "address": customer.address
            }
            
            # 创建订单
            order = Order(
                id=f"order_{uuid.uuid4().hex[:12]}",
                farmer_id=farmer.id,
                customer_id=customer.id,
                items=order_items,
                subtotal=subtotal,
                shipping_fee=shipping_fee,
                discount=discount,
                total_amount=total_amount,
                shipping_address=shipping_address,
                status=status,
                payment_method="微信支付" if random.random() > 0.5 else "支付宝",
                customer_note=f"订单备注 {i+1}" if random.random() > 0.7 else None,
                created_at=created_time
            )
            
            db.add(order)
            print(f"   [OK] 订单 {i+1}/{order_count}: {len(order_items)}个商品 - {customer.name} - {total_amount:.2f}元 - {status.value}")
        
        await db.commit()
        print(f"\n[SUCCESS] 成功创建 {order_count} 个订单")
        
        # 统计信息
        from sqlalchemy import func
        
        print("\n" + "=" * 80)
        print("订单统计")
        print("=" * 80)
        
        for status in OrderStatus:
            result = await db.execute(
                select(func.count()).select_from(Order).where(
                    Order.farmer_id == farmer.id,
                    Order.status == status
                )
            )
            count = result.scalar()
            print(f"   {status.value}: {count} 个")
        
        result = await db.execute(
            select(func.sum(Order.total_amount)).where(
                Order.farmer_id == farmer.id,
                Order.status == OrderStatus.COMPLETED
            )
        )
        total_revenue = result.scalar() or 0.0
        print(f"\n   总销售额（已完成订单）: {total_revenue:.2f} 元")
        
        print("\n" + "=" * 80)
        print("完成！")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(recreate_orders())

