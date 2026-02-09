"""
修复农户等级
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from backend.database.connection import engine

def fix_tiers():
    """更新农户等级"""
    print("正在更新农户等级...")
    
    with engine.connect() as conn:
        # 更新所有农户等级为 basic
        result = conn.execute(
            text("""
                UPDATE farmers 
                SET tier = 'basic'
                WHERE id IN ('farmer_001', 'farmer_002', 'farmer_003', 'farmer_004', 'farmer_005')
            """)
        )
        conn.commit()
        
        print(f"已更新 {result.rowcount} 个农户的等级")
        
        # 验证
        result = conn.execute(
            text("SELECT id, name, phone, tier FROM farmers ORDER BY id")
        )
        
        print("\n农户列表:")
        for row in result:
            print(f"  ID: {row[0]}, 名称: {row[1]}, 手机: {row[2]}, 等级: {row[3]}")
        
        print("\n所有农户等级已更新为: basic")

if __name__ == "__main__":
    fix_tiers()

