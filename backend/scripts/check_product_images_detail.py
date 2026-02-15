# -*- coding: utf-8 -*-
"""
检查产品表中的图片路径数据
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from backend.database.connection import AsyncSessionLocal
from backend.models.farmer import Farmer
from backend.models.product import Product
import json


async def check_images():
    """检查产品图片数据"""
    async with AsyncSessionLocal() as db:
        print("\n" + "=" * 80)
        print("检查产品图片路径")
        print("=" * 80)
        
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
        
        for i, product in enumerate(products, 1):
            print(f"{i}. 产品名称: {product.name}")
            print(f"   SKU: {product.sku_code}")
            print(f"   图片字段类型: {type(product.images)}")
            print(f"   图片数据: {product.images}")
            
            # 如果是JSON字符串，尝试解析
            if isinstance(product.images, str):
                try:
                    parsed = json.loads(product.images)
                    print(f"   解析后: {parsed}")
                except:
                    print(f"   无法解析为JSON")
            
            print()
        
        print("=" * 80)
        print("\n检查实际文件系统中的图片文件：")
        print("=" * 80)
        
        # 检查uploads目录
        uploads_dir = Path(__file__).parent.parent.parent / "uploads" / "images"
        print(f"\n图片目录: {uploads_dir}")
        print(f"目录是否存在: {uploads_dir.exists()}")
        
        if uploads_dir.exists():
            image_files = list(uploads_dir.glob("*"))
            print(f"\n找到 {len(image_files)} 个图片文件：")
            for img in image_files:
                print(f"   - {img.name} ({img.stat().st_size} bytes)")
        else:
            print("\n[WARNING] 图片目录不存在！")


if __name__ == "__main__":
    asyncio.run(check_images())

