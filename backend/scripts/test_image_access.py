# -*- coding: utf-8 -*-
"""
测试图片访问完整流程
"""
import asyncio
import sys
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from backend.database.connection import AsyncSessionLocal
from backend.models.farmer import Farmer
from backend.models.product import Product


async def test_image_access():
    """测试图片访问"""
    print("\n" + "=" * 80)
    print("测试图片访问完整流程")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        # 获取Demo农户
        result = await db.execute(
            select(Farmer).where(Farmer.phone == "13800138000")
        )
        farmer = result.scalar_one_or_none()
        
        if not farmer:
            print("[ERROR] 找不到Demo账号！")
            return
        
        # 获取所有产品
        result = await db.execute(
            select(Product).where(Product.farmer_id == farmer.id)
        )
        products = result.scalars().all()
        
        print(f"\n找到 {len(products)} 个产品\n")
        
        # 测试每个产品的图片访问
        success_count = 0
        fail_count = 0
        
        for i, product in enumerate(products, 1):
            if not product.images or len(product.images) == 0:
                print(f"{i}. {product.name}: 没有图片")
                continue
            
            image_path = product.images[0]
            
            # 测试后端直接访问
            backend_url = f"http://localhost:8000{image_path}"
            
            try:
                response = requests.head(backend_url, timeout=2)
                if response.status_code == 200:
                    print(f"✅ {i}. {product.name}")
                    print(f"   URL: {backend_url}")
                    print(f"   状态: {response.status_code}")
                    success_count += 1
                else:
                    print(f"❌ {i}. {product.name}")
                    print(f"   URL: {backend_url}")
                    print(f"   状态: {response.status_code}")
                    fail_count += 1
            except Exception as e:
                print(f"❌ {i}. {product.name}")
                print(f"   URL: {backend_url}")
                print(f"   错误: {e}")
                fail_count += 1
        
        print("\n" + "=" * 80)
        print(f"测试结果: 成功 {success_count} 个, 失败 {fail_count} 个")
        print("=" * 80)
        
        if fail_count == 0:
            print("\n✅ 所有图片都可以正常访问！")
            print("\n前端访问方式：")
            print("1. 通过代理访问（开发环境）: http://localhost:3000/uploads/images/xxx.webp")
            print("2. 直接访问后端（生产环境）: http://localhost:8000/uploads/images/xxx.webp")
        else:
            print("\n⚠️ 部分图片无法访问，请检查后端服务器是否正在运行")


if __name__ == "__main__":
    asyncio.run(test_image_access())

