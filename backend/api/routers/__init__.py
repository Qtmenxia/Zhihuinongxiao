"""
API路由模块
"""
from backend.api.routers import (
    service_generation,
    farmer_management,
    product_management,
    order_management,
    statistics,
    deploy_service
)

__all__ = [
    "service_generation",
    "farmer_management",
    "product_management",
    "order_management",
    "statistics",
    "deploy_service"
]
