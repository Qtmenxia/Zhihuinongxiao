"""
Alembic迁移环境配置
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Alembic配置对象
config = context.config

# 解析日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 导入所有模型（确保Base.metadata包含所有表）
from backend.models.base import Base
from backend.models.farmer import Farmer
from backend.models.product import Product
from backend.models.order import Order
from backend.models.mcp_service import MCPService
from backend.models.service_log import ServiceLog

# 设置目标元数据
target_metadata = Base.metadata

# 从环境变量读取数据库URL
from backend.config.settings import settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """
    离线模式运行迁移 - 仅生成SQL脚本，不连接数据库
    
    使用场景：
    - 在没有数据库连接的环境中生成SQL脚本
    - 需要先审查SQL再执行时
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    在线模式运行迁移 - 连接数据库并执行迁移
    
    使用场景：
    - 正常的数据库迁移操作
    - alembic upgrade head
    """
    # 从配置创建数据库引擎
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # 可选配置
            compare_type=True,  # 比较列类型变化
            compare_server_default=True,  # 比较默认值变化
        )

        with context.begin_transaction():
            context.run_migrations()


# 根据模式执行对应的迁移函数
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
