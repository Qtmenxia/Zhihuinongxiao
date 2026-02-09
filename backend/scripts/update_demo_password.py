# -*- coding: utf-8 -*-
"""
更新Demo账号密码
将 farmer_001 的密码更新为 demo123456
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
import bcrypt
from backend.database.connection import engine

def update_demo_password():
    """更新Demo账号密码"""
    print("[INFO] Updating demo account password...")
    
    # 生成密码哈希
    password_hash = bcrypt.hashpw(
        "demo123456".encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    with engine.connect() as conn:
        # 更新 farmer_001 的密码
        result = conn.execute(
            text("""
                UPDATE farmers 
                SET password_hash = :password_hash
                WHERE id = 'farmer_001'
            """),
            {"password_hash": password_hash}
        )
        conn.commit()
        
        print(f"[SUCCESS] Updated {result.rowcount} farmer password")
        
        # 验证
        result = conn.execute(
            text("SELECT id, name, phone, tier FROM farmers WHERE id = 'farmer_001'")
        )
        
        row = result.fetchone()
        if row:
            print("\n[INFO] Demo Account Details:")
            print(f"  ID: {row[0]}")
            print(f"  Name: {row[1]}")
            print(f"  Phone: {row[2]}")
            print(f"  Password: demo123456")
            print(f"  Tier: {row[3]}")
        
        print("\n[SUCCESS] Demo account is ready!")

if __name__ == "__main__":
    update_demo_password()

