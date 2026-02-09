# -*- coding: utf-8 -*-
"""
重建数据库枚举类型
将farmertier枚举从小写改为大写
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from backend.database.connection import engine

def rebuild_enum():
    """重建枚举类型"""
    print("[INFO] Rebuilding farmertier enum...")
    
    with engine.connect() as conn:
        try:
            # 0. 删除CHECK约束
            print("[STEP 0] Dropping CHECK constraint...")
            conn.execute(text("ALTER TABLE farmers DROP CONSTRAINT IF EXISTS farmers_tier_check"))
            conn.commit()
            
            # 1. 先将tier列改为text类型
            print("[STEP 1] Converting tier column to text...")
            conn.execute(text("ALTER TABLE farmers ALTER COLUMN tier TYPE VARCHAR(20)"))
            conn.commit()
            
            # 2. 删除旧的枚举类型
            print("[STEP 2] Dropping old enum type...")
            conn.execute(text("DROP TYPE IF EXISTS farmertier CASCADE"))
            conn.commit()
            
            # 3. 创建新的枚举类型（大写）
            print("[STEP 3] Creating new enum type with uppercase values...")
            conn.execute(text("CREATE TYPE farmertier AS ENUM ('FREE', 'BASIC', 'PROFESSIONAL')"))
            conn.commit()
            
            # 4. 更新数据：小写转大写
            print("[STEP 4] Updating existing data...")
            conn.execute(text("UPDATE farmers SET tier = UPPER(tier)"))
            conn.commit()
            
            # 5. 将列改回枚举类型
            print("[STEP 5] Converting tier column back to enum...")
            conn.execute(text("ALTER TABLE farmers ALTER COLUMN tier TYPE farmertier USING tier::farmertier"))
            conn.commit()
            
            print("\n[SUCCESS] Enum type rebuilt successfully!")
            
            # 验证
            result = conn.execute(text("SELECT id, phone, tier FROM farmers LIMIT 5"))
            print("\n[INFO] Farmer data:")
            for row in result:
                print(f"  ID: {row[0]}, Phone: {row[1]}, Tier: {row[2]}")
                
        except Exception as e:
            print(f"\n[ERROR] Failed: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    rebuild_enum()

