"""
配置模块
"""
from backend.config.settings import settings
from backend.config.product_config import PRODUCT_CATALOG, MARKETING_CAMPAIGNS, SHIPPING_CONFIG

__all__ = [
    "settings",
    "PRODUCT_CATALOG",
    "MARKETING_CAMPAIGNS",
    "SHIPPING_CONFIG"
]
