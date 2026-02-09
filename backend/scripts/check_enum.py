# -*- coding: utf-8 -*-
"""
检查数据库中的枚举定义
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from backend.database.connection import engine

def check_enum_values():
    """检查枚举值"""
    print("[INFO] Checking FarmerTier enum values in database...")
    
    with engine.connect() as conn:
        # 查询枚举类型的所有可能值
        result = conn.execute(
            text("SELECT unnest(enum_range(NULL::farmertier))")
        )
        
        print("\n[INFO] FarmerTier enum values:")
        for row in result:
            print(f"  - '{row[0]}'")
        
        # 查询当前农户使用的tier值
        result = conn.execute(
            text("SELECT DISTINCT tier FROM farmers ORDER BY tier")
        )
        
        print("\n[INFO] Current tier values in farmers table:")
        for row in result:
            print(f"  - '{row[0]}'")

if __name__ == "__main__":
    check_enum_values()

