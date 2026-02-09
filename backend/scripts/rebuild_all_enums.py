# -*- coding: utf-8 -*-
"""
重建所有数据库枚举类型为大写
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from backend.database.connection import engine

def rebuild_all_enums():
    """重建所有枚举类型"""
    print("[INFO] Rebuilding all enum types...")
    
    with engine.connect() as conn:
        try:
            # ========== OrderStatus ==========
            print("\n[1/2] Rebuilding OrderStatus enum...")
            
            # 删除约束
            conn.execute(text("ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_status_check"))
            conn.commit()
            
            # 转为text
            conn.execute(text("ALTER TABLE orders ALTER COLUMN status TYPE VARCHAR(20)"))
            conn.commit()
            
            # 删除旧枚举
            conn.execute(text("DROP TYPE IF EXISTS orderstatus CASCADE"))
            conn.commit()
            
            # 创建新枚举（大写）
            conn.execute(text("CREATE TYPE orderstatus AS ENUM ('PENDING', 'PAID', 'SHIPPED', 'COMPLETED', 'CANCELLED', 'REFUNDED')"))
            conn.commit()
            
            # 更新数据
            conn.execute(text("UPDATE orders SET status = UPPER(status)"))
            conn.commit()
            
            # 转回枚举
            conn.execute(text("ALTER TABLE orders ALTER COLUMN status TYPE orderstatus USING status::orderstatus"))
            conn.commit()
            
            print("  [SUCCESS] OrderStatus enum rebuilt")
            
            # ========== ServiceStatus ==========
            print("\n[2/2] Rebuilding ServiceStatus enum...")
            
            # 删除约束
            conn.execute(text("ALTER TABLE mcp_services DROP CONSTRAINT IF EXISTS mcp_services_status_check"))
            conn.commit()
            
            # 删除默认值
            conn.execute(text("ALTER TABLE mcp_services ALTER COLUMN status DROP DEFAULT"))
            conn.commit()
            
            # 转为text
            conn.execute(text("ALTER TABLE mcp_services ALTER COLUMN status TYPE VARCHAR(20)"))
            conn.commit()
            
            # 删除旧枚举
            conn.execute(text("DROP TYPE IF EXISTS servicestatus CASCADE"))
            conn.commit()
            
            # 创建新枚举（大写）
            conn.execute(text("CREATE TYPE servicestatus AS ENUM ('PENDING', 'GENERATING', 'COMPLETED', 'FAILED', 'DEPLOYED')"))
            conn.commit()
            
            # 更新数据
            conn.execute(text("UPDATE mcp_services SET status = UPPER(status)"))
            conn.commit()
            
            # 转回枚举
            conn.execute(text("ALTER TABLE mcp_services ALTER COLUMN status TYPE servicestatus USING status::servicestatus"))
            conn.commit()
            
            # 恢复默认值
            conn.execute(text("ALTER TABLE mcp_services ALTER COLUMN status SET DEFAULT 'PENDING'"))
            conn.commit()
            
            print("  [SUCCESS] ServiceStatus enum rebuilt")
            
            print("\n[SUCCESS] All enum types rebuilt successfully!")
            
            # 验证
            print("\n[INFO] Verification:")
            result = conn.execute(text("SELECT id, status FROM orders LIMIT 3"))
            print("  Orders:")
            for row in result:
                print(f"    {row[0]}: {row[1]}")
                
        except Exception as e:
            print(f"\n[ERROR] Failed: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    rebuild_all_enums()

