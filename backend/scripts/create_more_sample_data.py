# -*- coding: utf-8 -*-
"""
创建更多示例数据 - 商品和订单
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from datetime import datetime, timezone, timedelta
import uuid
import random

from backend.database.connection import AsyncSessionLocal
from backend.models.farmer import Farmer
from backend.models.product import Product
from backend.models.customer import Customer
from backend.models.order import Order, OrderStatus


async def create_more_data():
    """创建更多示例数据"""
    async with AsyncSessionLocal() as db:
        print("\n" + "=" * 80)
        print("开始创建更多示例数据")
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
        
        # ==================== 创建更多产品 ====================
        print("\n" + "=" * 80)
        print("创建更多产品")
        print("=" * 80)
        
        # 检查现有产品数量
        result = await db.execute(
            select(Product).where(Product.farmer_id == farmer.id)
        )
        existing_products = result.scalars().all()
        print(f"当前产品数量: {len(existing_products)}")
        
        # 如果产品数量已经足够，跳过创建
        if len(existing_products) >= 15:
            print("[INFO] 产品数量已足够，跳过创建新产品")
            all_products = existing_products
        else:
            new_products_data = [
            {
                "name": "山西老陈醋",
                "description": "传统工艺酿造，酸香浓郁，健康养生",
                "price": 28.00,
                "original_price": 35.00,
                "stock": 200,
                "category": "调味品",
                "specs": {"unit": "瓶", "volume": "500ml"},
                "selling_points": ["传统工艺", "无添加", "健康"],
                "images": ["vinegar1.jpg"],
                "sku_code": "VINEGAR001"
            },
            {
                "name": "黑木耳",
                "description": "野生黑木耳，营养丰富，口感爽脆",
                "price": 45.00,
                "original_price": 55.00,
                "stock": 150,
                "category": "干货",
                "specs": {"unit": "斤", "grade": "特级"},
                "selling_points": ["野生", "营养", "爽脆"],
                "images": ["fungus1.jpg"],
                "sku_code": "FUNGUS001"
            },
            {
                "name": "土蜂蜜",
                "description": "纯天然土蜂蜜，甜而不腻，营养价值高",
                "price": 68.00,
                "original_price": 80.00,
                "stock": 100,
                "category": "蜂产品",
                "specs": {"unit": "瓶", "weight": "500g"},
                "selling_points": ["纯天然", "无添加", "营养"],
                "images": ["honey1.jpg"],
                "sku_code": "HONEY001"
            },
            {
                "name": "山药",
                "description": "铁棍山药，口感细腻，健脾养胃",
                "price": 12.00,
                "original_price": 15.00,
                "stock": 500,
                "category": "蔬菜",
                "specs": {"unit": "斤", "type": "铁棍"},
                "selling_points": ["铁棍", "细腻", "养胃"],
                "images": ["yam1.jpg"],
                "sku_code": "YAM001"
            },
            {
                "name": "花椒",
                "description": "大红袍花椒，麻香浓郁，调味佳品",
                "price": 35.00,
                "original_price": 42.00,
                "stock": 80,
                "category": "调味品",
                "specs": {"unit": "两", "grade": "特级"},
                "selling_points": ["大红袍", "麻香", "优质"],
                "images": ["pepper1.jpg"],
                "sku_code": "PEPPER001"
            },
            {
                "name": "绿豆",
                "description": "优质绿豆，清热解毒，夏季佳品",
                "price": 6.00,
                "original_price": 8.00,
                "stock": 600,
                "category": "粮食",
                "specs": {"unit": "斤", "origin": "山西"},
                "selling_points": ["优质", "清热", "解毒"],
                "images": ["mungbean1.jpg"],
                "sku_code": "MUNGBEAN001"
            },
            {
                "name": "黑豆",
                "description": "有机黑豆，补肾养血，营养丰富",
                "price": 9.00,
                "original_price": 12.00,
                "stock": 400,
                "category": "粮食",
                "specs": {"unit": "斤", "type": "有机"},
                "selling_points": ["有机", "补肾", "养血"],
                "images": ["blackbean1.jpg"],
                "sku_code": "BLACKBEAN001"
            },
            {
                "name": "南瓜",
                "description": "板栗南瓜，香甜粉糯，营养美味",
                "price": 4.50,
                "original_price": 6.00,
                "stock": 800,
                "category": "蔬菜",
                "specs": {"unit": "斤", "type": "板栗"},
                "selling_points": ["香甜", "粉糯", "营养"],
                "images": ["pumpkin1.jpg"],
                "sku_code": "PUMPKIN001"
            },
            {
                "name": "玉米",
                "description": "甜玉米，新鲜采摘，口感香甜",
                "price": 3.00,
                "original_price": 4.00,
                "stock": 1000,
                "category": "蔬菜",
                "specs": {"unit": "根", "type": "甜玉米"},
                "selling_points": ["新鲜", "香甜", "营养"],
                "images": ["corn1.jpg"],
                "sku_code": "CORN001"
            },
            {
                "name": "土豆",
                "description": "高山土豆，口感绵密，适合多种烹饪",
                "price": 2.50,
                "original_price": 3.50,
                "stock": 1200,
                "category": "蔬菜",
                "specs": {"unit": "斤", "origin": "高山"},
                "selling_points": ["高山", "绵密", "优质"],
                "images": ["potato1.jpg"],
                "sku_code": "POTATO001"
            }
        ]
        
        created_products = []
        for prod_data in new_products_data:
            product = Product(
                id=f"prod_{uuid.uuid4().hex[:12]}",
                farmer_id=farmer.id,
                name=prod_data["name"],
                sku_code=prod_data["sku_code"],
                description=prod_data["description"],
                price=prod_data["price"],
                original_price=prod_data["original_price"],
                stock=prod_data["stock"],
                category=prod_data["category"],
                specs=prod_data["specs"],
                selling_points=prod_data["selling_points"],
                images=prod_data["images"],
                is_active=True,
                created_at=datetime.now(timezone.utc)
            )
            db.add(product)
            created_products.append(product)
            print(f"   [OK] 创建产品: {prod_data['name']} - {prod_data['price']}元")
        
        await db.commit()
        print(f"\n[SUCCESS] 成功创建 {len(new_products_data)} 个新产品")
        
        # 刷新产品列表
        for p in created_products:
            await db.refresh(p)
        
        # 获取所有产品
        result = await db.execute(
            select(Product).where(Product.farmer_id == farmer.id)
        )
        all_products = result.scalars().all()
        print(f"[INFO] 当前总产品数量: {len(all_products)}")
        
        # ==================== 创建更多客户 ====================
        print("\n" + "=" * 80)
        print("创建更多客户")
        print("=" * 80)
        
        result = await db.execute(
            select(Customer).where(Customer.farmer_id == farmer.id)
        )
        existing_customers = result.scalars().all()
        print(f"当前客户数量: {len(existing_customers)}")
        
        new_customers_data = [
            {
                "name": "赵六",
                "phone": "13900139004",
                "address": "深圳市南山区xxx科技园",
                "remark": "企业采购，需要发票"
            },
            {
                "name": "孙七",
                "phone": "13900139005",
                "address": "杭州市西湖区xxx路",
                "remark": "回头客，喜欢有机产品"
            },
            {
                "name": "周八",
                "phone": "13900139006",
                "address": "成都市武侯区xxx街",
                "remark": "VIP客户，每周采购"
            },
            {
                "name": "吴九",
                "phone": "13900139007",
                "address": "南京市鼓楼区xxx大道",
                "remark": "新客户，首次购买"
            },
            {
                "name": "郑十",
                "phone": "13900139008",
                "address": "西安市雁塔区xxx路",
                "remark": "批发客户，量大优惠"
            }
        ]
        
        created_customers = []
        for cust_data in new_customers_data:
            customer = Customer(
                id=f"cust_{uuid.uuid4().hex[:12]}",
                farmer_id=farmer.id,
                name=cust_data["name"],
                phone=cust_data["phone"],
                address=cust_data["address"],
                remark=cust_data["remark"],
                created_at=datetime.now(timezone.utc)
            )
            db.add(customer)
            created_customers.append(customer)
            print(f"   [OK] 创建客户: {cust_data['name']} - {cust_data['phone']}")
        
        await db.commit()
        print(f"\n[SUCCESS] 成功创建 {len(new_customers_data)} 个新客户")
        
        # 刷新客户列表
        for c in created_customers:
            await db.refresh(c)
        
        # 获取所有客户
        result = await db.execute(
            select(Customer).where(Customer.farmer_id == farmer.id)
        )
        all_customers = result.scalars().all()
        print(f"[INFO] 当前总客户数量: {len(all_customers)}")
        
        # ==================== 创建订单 ====================
        print("\n" + "=" * 80)
        print("创建订单数据")
        print("=" * 80)
        
        if len(all_products) == 0 or len(all_customers) == 0:
            print("[ERROR] 没有产品或客户，无法创建订单")
            return
        
        # 创建30个订单
        order_count = 30
        statuses = [OrderStatus.PENDING, OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.COMPLETED, OrderStatus.CANCELLED]
        
        for i in range(order_count):
            # 随机选择客户
            customer = random.choice(all_customers)
            
            # 随机选择1-5个产品
            num_items = random.randint(1, 5)
            selected_products = random.sample(all_products, min(num_items, len(all_products)))
            
            # 计算订单金额
            subtotal = 0
            order_items = []
            
            for product in selected_products:
                quantity = random.randint(1, 10)
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
                customer_note=f"订单备注 {i+1}",
                created_at=created_time
            )
            
            db.add(order)
            print(f"   [OK] 创建订单: {order.id} - {customer.name} - {total_amount:.2f}元 - {status.value}")
        
        await db.commit()
        print(f"\n[SUCCESS] 成功创建 {order_count} 个订单")
        
        # ==================== 统计信息 ====================
        print("\n" + "=" * 80)
        print("数据统计")
        print("=" * 80)
        
        # 统计各状态订单数量
        from sqlalchemy import func
        
        for status in OrderStatus:
            result = await db.execute(
                select(func.count()).select_from(Order).where(
                    Order.farmer_id == farmer.id,
                    Order.status == status
                )
            )
            count = result.scalar()
            print(f"   {status.value}: {count} 个")
        
        # 统计总销售额
        result = await db.execute(
            select(func.sum(Order.total_amount)).where(
                Order.farmer_id == farmer.id,
                Order.status == OrderStatus.COMPLETED
            )
        )
        total_revenue = result.scalar() or 0.0
        print(f"\n   总销售额（已完成订单）: {total_revenue:.2f} 元")
        
        # 统计今日订单
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        result = await db.execute(
            select(func.count()).select_from(Order).where(
                Order.farmer_id == farmer.id,
                Order.created_at >= today_start
            )
        )
        today_orders = result.scalar()
        print(f"   今日订单: {today_orders} 个")
        
        # 统计今日销售额
        result = await db.execute(
            select(func.sum(Order.total_amount)).where(
                Order.farmer_id == farmer.id,
                Order.created_at >= today_start,
                Order.status == OrderStatus.COMPLETED
            )
        )
        today_revenue = result.scalar() or 0.0
        print(f"   今日销售额: {today_revenue:.2f} 元")
        
        print("\n" + "=" * 80)
        print("数据创建完成！")
        print("=" * 80)
        print(f"\n最终统计:")
        print(f"   产品总数: {len(all_products)}")
        print(f"   客户总数: {len(all_customers)}")
        print(f"   订单总数: {order_count}")
        print(f"   总销售额: {total_revenue:.2f} 元")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(create_more_data())

