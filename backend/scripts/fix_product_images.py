# -*- coding: utf-8 -*-
"""
统一产品图片路径 - 使用真实上传的图片
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from backend.database.connection import AsyncSessionLocal
from backend.models.product import Product


async def fix_product_images():
    """修复产品图片路径"""
    async with AsyncSessionLocal() as db:
        print("\n" + "=" * 80)
        print("统一产品图片路径")
        print("=" * 80)
        
        # 产品名称到真实图片的映射（基于你上传的图片）
        product_image_mapping = {
            "土豆": "/uploads/images/20260215_142412_448811eb.webp",
            "玉米": "/uploads/images/20260215_142438_215dfb75.webp",
            "南瓜": "/uploads/images/20260215_142510_f53e23ab.webp",
            "黑豆": "/uploads/images/20260215_142529_182ae014.webp",
            "绿豆": "/uploads/images/20260215_142547_82eb68b2.webp",
            "花椒": "/uploads/images/20260215_142604_b985e288.webp",
            "红枣": "/uploads/images/20260215_142627_a621d43e.webp",
            "小米": "/uploads/images/20260215_142657_1698670e.webp",
            "山药": "/uploads/images/20260215_142717_ff125a12.webp",
            "土蜂蜜": "/uploads/images/20260215_142758_437e5725.webp",
            "黑木耳": "/uploads/images/20260215_142814_8edb03cf.webp",
            "山西老陈醋": "/uploads/images/20260215_142832_29a6f6d2.webp",
            # 前面3个产品使用之前的图片
            "有机苹果": "/uploads/images/20260214_204912_97a59bd4.jpg",
            "土鸡蛋": "/uploads/images/20260214_205000_199a4ed5.webp",
            "核桃": "/uploads/images/20260214_205036_6331d887.webp",
        }
        
        # 获取所有产品
        result = await db.execute(select(Product))
        products = result.scalars().all()
        
        print(f"\n找到 {len(products)} 个产品\n")
        
        updated_count = 0
        
        for product in products:
            old_images = product.images
            
            # 如果产品名称在映射中，使用真实图片
            if product.name in product_image_mapping:
                new_image = product_image_mapping[product.name]
                product.images = [new_image]
                updated_count += 1
                print(f"[OK] {product.name}")
                print(f"     旧: {old_images}")
                print(f"     新: {product.images}")
                print()
            else:
                print(f"[SKIP] {product.name} - 未找到对应图片")
                print()
        
        if updated_count > 0:
            await db.commit()
            print(f"\n[SUCCESS] 成功更新 {updated_count} 个产品的图片路径")
        else:
            print(f"\n[INFO] 没有需要更新的产品")
        
        # 显示最终结果
        print("\n" + "=" * 80)
        print("最终产品图片列表")
        print("=" * 80)
        
        result = await db.execute(select(Product))
        products = result.scalars().all()
        
        for i, product in enumerate(products, 1):
            images_str = product.images[0] if product.images else '无'
            print(f"{i:2d}. {product.name:15s} | {images_str}")
        
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(fix_product_images())

