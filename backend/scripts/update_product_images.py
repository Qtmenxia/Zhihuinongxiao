# -*- coding: utf-8 -*-
"""
为产品添加真实图片路径
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from backend.database.connection import AsyncSessionLocal
from backend.models.product import Product


async def update_product_images():
    """为产品添加图片"""
    async with AsyncSessionLocal() as db:
        print("\n" + "=" * 80)
        print("更新产品图片")
        print("=" * 80)
        
        # 获取所有产品
        result = await db.execute(select(Product))
        products = result.scalars().all()
        
        print(f"\n找到 {len(products)} 个产品")
        
        # 为每个产品分配图片
        product_images = {
            "有机苹果": ["apple.jpg", "apple1.jpg", "apple2.jpg"],
            "土鸡蛋": ["egg.jpg", "egg1.jpg"],
            "核桃": ["walnut.jpg", "walnut1.jpg"],
            "小米": ["millet.jpg", "millet1.jpg"],
            "红枣": ["jujube.jpg", "jujube1.jpg", "date.jpg"],
            "山西老陈醋": ["vinegar.jpg", "vinegar1.jpg"],
            "黑木耳": ["fungus.jpg", "fungus1.jpg", "mushroom.jpg"],
            "土蜂蜜": ["honey.jpg", "honey1.jpg"],
            "山药": ["yam.jpg", "yam1.jpg"],
            "花椒": ["pepper.jpg", "pepper1.jpg", "sichuan-pepper.jpg"],
            "绿豆": ["mungbean.jpg", "mungbean1.jpg", "green-bean.jpg"],
            "黑豆": ["blackbean.jpg", "blackbean1.jpg", "black-bean.jpg"],
            "南瓜": ["pumpkin.jpg", "pumpkin1.jpg"],
            "玉米": ["corn.jpg", "corn1.jpg", "maize.jpg"],
            "土豆": ["potato.jpg", "potato1.jpg"]
        }
        
        updated_count = 0
        
        for product in products:
            # 如果产品已经有图片，跳过
            if product.images and len(product.images) > 0:
                print(f"[SKIP] {product.name} 已有图片: {product.images}")
                continue
            
            # 查找匹配的图片
            images = product_images.get(product.name, [])
            
            if images:
                product.images = images
                updated_count += 1
                print(f"[OK] {product.name} -> {images}")
            else:
                # 使用通用占位图片名
                product.images = [f"{product.sku_code.lower()}.jpg"]
                updated_count += 1
                print(f"[INFO] {product.name} -> 使用默认图片: {product.images}")
        
        if updated_count > 0:
            await db.commit()
            print(f"\n[SUCCESS] 成功更新 {updated_count} 个产品的图片")
        else:
            print(f"\n[INFO] 没有需要更新的产品")
        
        # 显示最终结果
        print("\n" + "=" * 80)
        print("产品图片列表")
        print("=" * 80)
        
        result = await db.execute(select(Product))
        products = result.scalars().all()
        
        for product in products:
            images_str = ', '.join(product.images) if product.images else '无'
            print(f"{product.name:15s} | {images_str}")
        
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(update_product_images())

