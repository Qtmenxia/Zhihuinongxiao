"""
API路由模块
"""
from backend.api.routers import (
    service_generation,
    farmer_management,
    product_management,
    order_management,
    customer_management,
    statistics,
    deploy_service,
    upload,
    cost_management
)

__all__ = [
    "service_generation",
    "farmer_management",
    "product_management",
    "order_management",
    "customer_management",
    "statistics",
    "deploy_service",
    "upload",
    "cost_management"
]
