import asyncio
import bcrypt
from sqlalchemy import text
from backend.database.connection import AsyncSessionLocal

# 设定我们要重置的新密码
NEW_PASSWORD = "demo123456"
TARGET_PHONE = "13800138000"  # 演示账号的手机号

async def fix_password():
    print(f"正在重置用户 {TARGET_PHONE} 的密码为: {NEW_PASSWORD}")
    
    # 1. 生成合法的 Bcrypt 哈希
    # bcrypt.hashpw 要求 bytes 类型，所以要 encode
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(NEW_PASSWORD.encode('utf-8'), salt)
    hashed_str = hashed_bytes.decode('utf-8')
    
    print(f"生成的 Bcrypt 哈希值: {hashed_str}")
    
    # 2. 更新数据库
    async with AsyncSessionLocal() as session:
        # 执行 SQL 更新
        await session.execute(
            text("UPDATE farmers SET password_hash = :new_hash WHERE phone = :phone"),
            {"new_hash": hashed_str, "phone": TARGET_PHONE}
        )
        await session.commit()
        print("✅ 数据库更新成功！")

if __name__ == "__main__":
    # Windows 下著名的 EventLoop 策略问题（防止报错）
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(fix_password())
