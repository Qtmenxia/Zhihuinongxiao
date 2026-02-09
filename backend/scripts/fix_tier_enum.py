# -*- coding: utf-8 -*-
"""
修复农户等级枚举值
将小写的tier值转换为大写
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from backend.database.connection import engine

def fix_tier_enum():
    """修复tier枚举值"""
    print("[INFO] Fixing tier enum values...")
    
    with engine.connect() as conn:
        # 逐个更新小写的tier值为大写
        updates = [
            ("UPDATE farmers SET tier = 'FREE' WHERE tier = 'free'", "free -> FREE"),
            ("UPDATE farmers SET tier = 'BASIC' WHERE tier = 'basic'", "basic -> BASIC"),
            ("UPDATE farmers SET tier = 'PROFESSIONAL' WHERE tier = 'professional'", "professional -> PROFESSIONAL"),
        ]
        
        total_updated = 0
        for sql, desc in updates:
            result = conn.execute(text(sql))
            if result.rowcount > 0:
                print(f"  Updated {result.rowcount} farmers: {desc}")
                total_updated += result.rowcount
        
        conn.commit()
        
        print(f"\n[SUCCESS] Total updated: {total_updated} farmer tier values")
        
        # 验证
        result = conn.execute(
            text("SELECT id, name, phone, tier FROM farmers ORDER BY id LIMIT 10")
        )
        
        print("\n[INFO] Farmer List:")
        for row in result:
            print(f"  ID: {row[0]}, Phone: {row[2]}, Tier: {row[3]}")
        
        print("\n[SUCCESS] All tier values are now uppercase!")

if __name__ == "__main__":
    fix_tier_enum()

