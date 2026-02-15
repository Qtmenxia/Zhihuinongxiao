# -*- coding: utf-8 -*-
"""
为缺失图片的产品创建占位图片
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from PIL import Image, ImageDraw, ImageFont
from backend.database.connection import AsyncSessionLocal
from backend.models.farmer import Farmer
from backend.models.product import Product


async def create_placeholder_images():
    """为缺失图片的产品创建占位图片"""
    async with AsyncSessionLocal() as db:
        print("\n" + "=" * 80)
        print("创建占位图片")
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
        
        # 图片目录
        uploads_dir = Path(__file__).parent.parent.parent / "uploads" / "images"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n图片目录: {uploads_dir}\n")
        
        # 检查每个产品的图片
        for product in products:
            if not product.images or len(product.images) == 0:
                print(f"[SKIP] {product.name}: 没有图片路径")
                continue
            
            # 获取第一张图片路径
            image_path = product.images[0]
            # 移除开头的 /uploads/images/
            if image_path.startswith('/uploads/images/'):
                filename = image_path.replace('/uploads/images/', '')
            else:
                filename = image_path
            
            full_path = uploads_dir / filename
            
            # 检查文件是否存在
            if full_path.exists():
                print(f"[OK] {product.name}: 图片存在 ({filename})")
            else:
                print(f"[MISSING] {product.name}: 图片不存在 ({filename})")
                print(f"   创建占位图片...")
                
                # 创建占位图片
                img = Image.new('RGB', (400, 400), color=(240, 240, 240))
                draw = ImageDraw.Draw(img)
                
                # 绘制产品名称
                try:
                    # 尝试使用系统字体
                    font = ImageFont.truetype("msyh.ttc", 48)  # 微软雅黑
                except:
                    font = ImageFont.load_default()
                
                # 计算文本位置（居中）
                text = product.name
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (400 - text_width) / 2
                y = (400 - text_height) / 2
                
                # 绘制文本
                draw.text((x, y), text, fill=(100, 100, 100), font=font)
                
                # 保存图片
                img.save(full_path)
                print(f"   [OK] 已创建占位图片: {filename}")
        
        print("\n" + "=" * 80)
        print("完成！")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(create_placeholder_images())

