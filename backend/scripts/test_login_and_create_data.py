# -*- coding: utf-8 -*-
"""
测试登录并创建测试数据
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
import bcrypt
from datetime import datetime, timezone
import uuid

from backend.database.connection import AsyncSessionLocal
from backend.models.farmer import Farmer
from backend.models.product import Product
from backend.models.customer import Customer


async def test_login_and_create_data():
    """测试登录并创建数据"""
    async with AsyncSessionLocal() as db:
        print("\n" + "=" * 80)
        print("步骤1: 验证Demo账号登录")
        print("=" * 80)
        
        # 查询Demo账号
        result = await db.execute(
            select(Farmer).where(Farmer.phone == "13800138000")
        )
        farmer = result.scalar_one_or_none()
        
        if not farmer:
            print("[ERROR] Demo账号不存在！")
            return
        
        print(f"[OK] 找到账号: {farmer.name} ({farmer.phone})")
        
        # 验证密码
        password = "demo123456"
        if bcrypt.checkpw(password.encode('utf-8'), farmer.password_hash.encode('utf-8')):
            print(f"[OK] 密码验证成功！")
        else:
            print(f"[ERROR] 密码验证失败！")
            return
        
        print("\n" + "=" * 80)
        print("步骤2: 创建测试产品数据")
        print("=" * 80)
        
        # 检查是否已有产品
        result = await db.execute(
            select(Product).where(Product.farmer_id == farmer.id)
        )
        existing_products = result.scalars().all()
        
        if existing_products:
            print(f"[OK] 已存在 {len(existing_products)} 个产品")
            for p in existing_products:
                unit = p.specs.get('unit', '件') if p.specs else '件'
                print(f"   - {p.name}: {p.price}元/{unit}")
        else:
            print("创建测试产品...")
            
            products_data = [
                {
                    "name": "有机苹果",
                    "description": "来自蒲县被子垣村的有机苹果，口感香甜，营养丰富",
                    "price": 15.00,
                    "original_price": 20.00,
                    "stock": 1000,
                    "category": "水果",
                    "specs": {"unit": "斤", "weight": "500g"},
                    "selling_points": ["有机认证", "产地直供", "新鲜采摘"],
                    "images": ["apple1.jpg", "apple2.jpg"],
                    "sku_code": "APPLE001"
                },
                {
                    "name": "土鸡蛋",
                    "description": "散养土鸡蛋，蛋黄金黄，营养价值高",
                    "price": 2.50,
                    "original_price": 3.00,
                    "stock": 500,
                    "category": "禽蛋",
                    "specs": {"unit": "个", "size": "大"},
                    "selling_points": ["散养", "无抗生素", "营养丰富"],
                    "images": ["egg1.jpg"],
                    "sku_code": "EGG001"
                },
                {
                    "name": "核桃",
                    "description": "山西特产核桃，皮薄肉厚，香脆可口",
                    "price": 25.00,
                    "original_price": 30.00,
                    "stock": 300,
                    "category": "坚果",
                    "specs": {"unit": "斤", "grade": "特级"},
                    "selling_points": ["皮薄", "肉厚", "香脆"],
                    "images": ["walnut1.jpg"],
                    "sku_code": "WALNUT001"
                },
                {
                    "name": "小米",
                    "description": "优质小米，熬粥香浓，营养丰富",
                    "price": 8.00,
                    "original_price": 10.00,
                    "stock": 800,
                    "category": "粮食",
                    "specs": {"unit": "斤", "origin": "山西"},
                    "selling_points": ["优质", "香浓", "营养"],
                    "images": ["millet1.jpg"],
                    "sku_code": "MILLET001"
                },
                {
                    "name": "红枣",
                    "description": "大红枣，肉厚核小，补血养颜",
                    "price": 18.00,
                    "original_price": 22.00,
                    "stock": 600,
                    "category": "干果",
                    "specs": {"unit": "斤", "size": "大"},
                    "selling_points": ["肉厚", "核小", "补血"],
                    "images": ["jujube1.jpg"],
                    "sku_code": "JUJUBE001"
                }
            ]
            
            for prod_data in products_data:
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
                print(f"   [OK] 创建产品: {prod_data['name']}")
            
            await db.commit()
            print(f"\n[OK] 成功创建 {len(products_data)} 个产品")
        
        print("\n" + "=" * 80)
        print("步骤3: 创建测试客户数据")
        print("=" * 80)
        
        # 检查是否已有客户
        result = await db.execute(
            select(Customer).where(Customer.farmer_id == farmer.id)
        )
        existing_customers = result.scalars().all()
        
        if existing_customers:
            print(f"[OK] 已存在 {len(existing_customers)} 个客户")
            for c in existing_customers:
                print(f"   - {c.name}: {c.phone}")
        else:
            print("创建测试客户...")
            
            customers_data = [
                {
                    "name": "张三",
                    "phone": "13900139001",
                    "address": "北京市朝阳区xxx街道",
                    "remark": "老客户，喜欢有机产品"
                },
                {
                    "name": "李四",
                    "phone": "13900139002",
                    "address": "上海市浦东新区xxx路",
                    "remark": "每月定期采购"
                },
                {
                    "name": "王五",
                    "phone": "13900139003",
                    "address": "广州市天河区xxx大道",
                    "remark": "批量采购客户"
                }
            ]
            
            for cust_data in customers_data:
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
                print(f"   [OK] 创建客户: {cust_data['name']}")
            
            await db.commit()
            print(f"\n[OK] 成功创建 {len(customers_data)} 个客户")
        
        print("\n" + "=" * 80)
        print("测试完成！")
        print("=" * 80)
        print("\n登录信息:")
        print(f"   手机号: 13800138000")
        print(f"   密码: demo123456")
        print(f"\n账号状态:")
        print(f"   农户ID: {farmer.id}")
        print(f"   姓名: {farmer.name}")
        print(f"   等级: {farmer.tier.value}")
        print(f"   邮箱: {farmer.email}")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_login_and_create_data())

