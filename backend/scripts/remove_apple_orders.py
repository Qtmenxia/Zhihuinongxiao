# -*- coding: utf-8 -*-
"""
删除包含有机苹果的订单，并重新生成订单
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


async def remove_apple_orders():
    """删除包含有机苹果的订单并重新生成"""
    async with AsyncSessionLocal() as db:
        print("\n" + "=" * 80)
        print("删除包含有机苹果的订单")
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
        
        # 找出包含有机苹果的订单
        orders_to_delete = []
        for order in all_orders:
            for item in order.items:
                if item.get('product_name') == '有机苹果':
                    orders_to_delete.append(order)
                    break
        
        print(f"包含有机苹果的订单数: {len(orders_to_delete)}")
        
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
        
        # 如果订单太少，补充一些新订单（不包含有机苹果）
        if len(remaining_orders) < 25:
            print(f"\n订单数量较少，补充到30个...")
            
            # 获取所有产品（排除有机苹果）
            result = await db.execute(
                select(Product).where(
                    Product.farmer_id == farmer.id,
                    Product.name != '有机苹果'
                )
            )
            products = result.scalars().all()
            
            # 获取所有客户
            result = await db.execute(
                select(Customer).where(Customer.farmer_id == farmer.id)
            )
            customers = result.scalars().all()
            
            if len(products) == 0 or len(customers) == 0:
                print("[ERROR] 没有产品或客户")
                return
            
            # 需要补充的订单数
            orders_to_add = 30 - len(remaining_orders)
            statuses = [OrderStatus.PENDING, OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.COMPLETED, OrderStatus.CANCELLED]
            
            print(f"\n创建 {orders_to_add} 个新订单...")
            
            for i in range(orders_to_add):
                # 随机选择客户
                customer = random.choice(customers)
                
                # 随机选择1-3个商品
                num_items = random.randint(1, 3)
                selected_products = random.sample(products, min(num_items, len(products)))
                
                # 计算订单金额
                subtotal = 0
                order_items = []
                
                for product in selected_products:
                    quantity = random.randint(1, 5)
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
                print(f"   [OK] 新订单 {i+1}/{orders_to_add}: {len(order_items)}个商品 - {customer.name} - {total_amount:.2f}元")
            
            await db.commit()
            print(f"\n[SUCCESS] 成功创建 {orders_to_add} 个新订单")
        
        # 最终统计
        result = await db.execute(
            select(Order).where(Order.farmer_id == farmer.id)
        )
        final_orders = result.scalars().all()
        
        print("\n" + "=" * 80)
        print(f"最终订单总数: {len(final_orders)}")
        print("=" * 80)
        
        # 验证没有有机苹果
        apple_count = 0
        for order in final_orders:
            for item in order.items:
                if item.get('product_name') == '有机苹果':
                    apple_count += 1
        
        if apple_count == 0:
            print("\n[OK] 确认：所有订单中都不包含有机苹果")
        else:
            print(f"\n[WARNING] 警告：仍有 {apple_count} 个订单项包含有机苹果")


if __name__ == "__main__":
    asyncio.run(remove_apple_orders())

