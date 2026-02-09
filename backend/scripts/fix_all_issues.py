"""
完整修复所有数据库问题
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from backend.database.connection import engine

def fix_all_issues():
    """修复所有数据库问题"""
    print("=" * 60)
    print("开始修复数据库...")
    print("=" * 60)
    
    with engine.connect() as conn:
        try:
            # 1. 删除并重新创建枚举类型
            print("\n1. 重新创建枚举类型...")
            conn.execute(text("DROP TYPE IF EXISTS farmertier CASCADE"))
            conn.execute(text("DROP TYPE IF EXISTS orderstatus CASCADE"))
            conn.execute(text("DROP TYPE IF EXISTS servicestatus CASCADE"))
            
            conn.execute(text("CREATE TYPE farmertier AS ENUM ('free', 'basic', 'professional')"))
            conn.execute(text("CREATE TYPE orderstatus AS ENUM ('pending', 'paid', 'shipped', 'completed', 'cancelled', 'refunded')"))
            conn.execute(text("CREATE TYPE servicestatus AS ENUM ('pending', 'planning', 'generating', 'testing', 'completed', 'failed', 'deployed')"))
            print("   枚举类型创建成功")
            
            # 2. 修改 farmers 表
            print("\n2. 修复 farmers 表...")
            conn.execute(text("ALTER TABLE farmers ALTER COLUMN tier DROP DEFAULT"))
            conn.execute(text("ALTER TABLE farmers ALTER COLUMN tier TYPE VARCHAR(20)"))
            conn.execute(text("UPDATE farmers SET tier = 'basic' WHERE tier NOT IN ('free', 'basic', 'professional')"))
            conn.execute(text("ALTER TABLE farmers ALTER COLUMN tier TYPE farmertier USING tier::farmertier"))
            conn.execute(text("ALTER TABLE farmers ALTER COLUMN tier SET DEFAULT 'free'::farmertier"))
            print("   farmers 表修复成功")
            
            # 3. 修改 orders 表
            print("\n3. 修复 orders 表...")
            conn.execute(text("ALTER TABLE orders ALTER COLUMN status DROP DEFAULT"))
            conn.execute(text("ALTER TABLE orders ALTER COLUMN status TYPE VARCHAR(20)"))
            conn.execute(text("""
                UPDATE orders 
                SET status = CASE 
                    WHEN status NOT IN ('pending', 'paid', 'shipped', 'completed', 'cancelled', 'refunded') 
                    THEN 'pending' 
                    ELSE status 
                END
            """))
            conn.execute(text("ALTER TABLE orders ALTER COLUMN status TYPE orderstatus USING status::orderstatus"))
            conn.execute(text("ALTER TABLE orders ALTER COLUMN status SET DEFAULT 'pending'::orderstatus"))
            print("   orders 表修复成功")
            
            # 4. 更新密码
            print("\n4. 更新农户密码...")
            bcrypt_hash = '$2b$12$5X30rxhtg28JckhxUUP4SOLAj8zUEC.TUjJ90HpAIaN0.Puz2yBl2'
            conn.execute(text("UPDATE farmers SET password_hash = :hash"), {"hash": bcrypt_hash})
            print("   密码更新成功")
            
            conn.commit()
            
            # 5. 验证数据
            print("\n5. 验证数据...")
            result = conn.execute(text("SELECT COUNT(*) FROM farmers"))
            farmer_count = result.scalar()
            
            result = conn.execute(text("SELECT COUNT(*) FROM products"))
            product_count = result.scalar()
            
            result = conn.execute(text("SELECT COUNT(*) FROM orders"))
            order_count = result.scalar()
            
            print(f"   农户数量: {farmer_count}")
            print(f"   产品数量: {product_count}")
            print(f"   订单数量: {order_count}")
            
            # 6. 显示农户信息
            print("\n6. 农户列表:")
            result = conn.execute(text("SELECT id, name, phone, tier FROM farmers ORDER BY id"))
            for row in result:
                print(f"   ID: {row[0]}, 名称: {row[1]}, 手机: {row[2]}, 等级: {row[3]}")
            
            print("\n" + "=" * 60)
            print("修复完成！")
            print("=" * 60)
            print("\n所有账号密码: demo123456")
            print("可用账号:")
            print("  - 13800138000 (蒲县被子垣果园)")
            print("  - 13800138001 (临汾红富士果园)")
            print("  - 13800138002 (吉县壶口苹果园)")
            print("  - 13800138003 (襄汾县优质核桃基地)")
            print("  - 13800138004 (洪洞大槐树农场)")
            
        except Exception as e:
            print(f"\n错误: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    fix_all_issues()

