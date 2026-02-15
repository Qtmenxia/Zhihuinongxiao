# -*- coding: utf-8 -*-
"""
检查产品图片字段
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from backend.database.connection import AsyncSessionLocal
from backend.models.product import Product


async def check_product_images():
    """检查产品图片"""
    async with AsyncSessionLocal() as db:
        print("\n" + "=" * 80)
        print("产品图片检查")
        print("=" * 80)
        
        result = await db.execute(select(Product))
        products = result.scalars().all()
        
        print(f"\n共有 {len(products)} 个产品\n")
        
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.name}")
            print(f"   SKU: {product.sku_code}")
            print(f"   图片字段: {product.images}")
            print(f"   图片类型: {type(product.images)}")
            if product.images:
                print(f"   图片数量: {len(product.images) if isinstance(product.images, list) else 'N/A'}")
            print()


if __name__ == "__main__":
    asyncio.run(check_product_images())

