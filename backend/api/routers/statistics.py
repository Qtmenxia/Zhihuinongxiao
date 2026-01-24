"""
数据统计API路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime, timedelta

from backend.api.dependencies import get_session, get_current_farmer
from backend.models.farmer import Farmer
from backend.models.mcp_service import MCPService
from backend.models.order import Order
from backend.models.product import Product

router = APIRouter()


@router.get(
    "/dashboard",
    summary="获取仪表盘数据",
    description="获取农户后台仪表盘的统计数据"
)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    获取仪表盘统计数据
    
    Args:
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 服务统计
    services_result = await db.execute(
        select(func.count()).select_from(MCPService).where(
            MCPService.farmer_id == current_farmer.id
        )
    )
    services_count = services_result.scalar()
    
    # 订单统计(本月)
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    
    orders_result = await db.execute(
        select(func.count()).select_from(Order).where(
            Order.farmer_id == current_farmer.id,
            Order.created_at >= month_start
        )
    )
    orders_count = orders_result.scalar()
    
    # 收入统计(本月)
    revenue_result = await db.execute(
        select(func.sum(Order.total_amount)).where(
            Order.farmer_id == current_farmer.id,
            Order.status == "completed",
            Order.created_at >= month_start
        )
    )
    revenue = revenue_result.scalar() or 0.0
    
    # 成本统计(总计)
    cost_result = await db.execute(
        select(func.sum(MCPService.generation_cost)).where(
            MCPService.farmer_id == current_farmer.id
        )
    )
    total_cost = cost_result.scalar() or 0.0
    
    # API调用统计
    api_calls = current_farmer.api_calls_today
    
    return {
        "services_count": services_count,
        "quota_remaining": _calculate_quota_remaining(current_farmer),
        "orders_count": orders_count,
        "orders_growth": 0,  # 需要对比上月数据
        "revenue": revenue,
        "total_cost": total_cost,
        "api_calls": current_farmer.api_calls_today,
        "api_calls_today": current_farmer.api_calls_today
    }


@router.get(
    "/sales-trend",
    summary="获取销售趋势",
    description="获取最近N天的销售趋势数据"
)
async def get_sales_trend(
    days: int = Query(30, ge=7, le=90, description="天数"),
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    获取销售趋势
    
    Args:
        days: 统计天数
        db: 数据库会话
        current_farmer: 当前农户
    """
    from sqlalchemy import and_, cast, Date
    
    # 计算起始日期
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)
    
    # 按天统计订单和销售额
    daily_stats = []
    current_date = start_date
    
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        
        # 统计当天订单数
        orders_result = await db.execute(
            select(func.count()).select_from(Order).where(
                and_(
                    Order.farmer_id == current_farmer.id,
                    cast(Order.created_at, Date) == current_date
                )
            )
        )
        orders_count = orders_result.scalar()
        
        # 统计当天销售额
        revenue_result = await db.execute(
            select(func.sum(Order.total_amount)).where(
                and_(
                    Order.farmer_id == current_farmer.id,
                    Order.status == "completed",
                    cast(Order.created_at, Date) == current_date
                )
            )
        )
        revenue = revenue_result.scalar() or 0.0
        
        daily_stats.append({
            "date": current_date.isoformat(),
            "orders": orders_count,
            "revenue": revenue
        })
        
        current_date = next_date
    
    return {
        "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
        "data": daily_stats
    }


@router.get(
    "/product-sales",
    summary="获取产品销量分析",
    description="获取产品销量排行"
)
async def get_product_sales(
    limit: int = Query(10, ge=5, le=50, description="返回数量"),
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    获取产品销量分析
    
    Args:
        limit: 返回数量
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 简化版本：从订单items中统计
    # 实际应该建立order_items关联表
    
    result = await db.execute(
        select(Order).where(Order.farmer_id == current_farmer.id)
    )
    orders = result.scalars().all()
    
    # 统计每个SKU的销量
    sku_sales = {}
    for order in orders:
        for item in order.items:
            sku = item.get("sku_code")
            quantity = item.get("quantity", 0)
            
            if sku not in sku_sales:
                sku_sales[sku] = {
                    "sku_code": sku,
                    "product_name": item.get("product_name", "Unknown"),
                    "quantity": 0,
                    "revenue": 0.0
                }
            
            sku_sales[sku]["quantity"] += quantity
            sku_sales[sku]["revenue"] += item.get("price", 0) * quantity
    
    # 排序并限制数量
    sorted_sales = sorted(
        sku_sales.values(),
        key=lambda x: x["quantity"],
        reverse=True
    )[:limit]
    
    return {
        "top_products": sorted_sales
    }


@router.get(
    "/service-performance",
    summary="获取服务性能统计",
    description="获取MCP服务的性能指标"
)
async def get_service_performance(
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    获取服务性能统计
    
    Args:
        db: 数据库会话
        current_farmer: 当前农户
    """
    from backend.models.service_log import ServiceLog
    from sqlalchemy import and_
    
    # 获取所有服务
    services_result = await db.execute(
        select(MCPService).where(
            MCPService.farmer_id == current_farmer.id,
            MCPService.is_deployed == True
        )
    )
    services = services_result.scalars().all()
    
    service_stats = []
    
    for service in services:
        # 统计今日调用
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        calls_result = await db.execute(
            select(func.count()).select_from(ServiceLog).where(
                and_(
                    ServiceLog.service_id == service.id,
                    ServiceLog.created_at >= today_start
                )
            )
        )
        calls_today = calls_result.scalar()
        
        # 统计错误率
        errors_result = await db.execute(
            select(func.count()).select_from(ServiceLog).where(
                and_(
                    ServiceLog.service_id == service.id,
                    ServiceLog.created_at >= today_start,
                    ServiceLog.status == "error"
                )
            )
        )
        errors = errors_result.scalar()
        error_rate = errors / calls_today if calls_today > 0 else 0.0
        
        service_stats.append({
            "service_id": service.id,
            "name": service.name,
            "status": "running" if service.is_deployed else "stopped",
            "calls": calls_today,
            "error_rate": error_rate
        })
    
    return {
        "services": service_stats
    }


@router.get(
    "/cost-analysis",
    summary="获取成本分析",
    description="获取服务生成成本分析"
)
async def get_cost_analysis(
    period: str = Query("month", description="统计周期: week/month/year"),
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    获取成本分析
    
    Args:
        period: 统计周期
        db: 数据库会话
        current_farmer: 当前农户
    """
    from sqlalchemy import and_
    
    # 计算时间范围
    now = datetime.utcnow()
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "year":
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(days=30)
    
    # 统计服务生成成本
    generation_cost_result = await db.execute(
        select(func.sum(MCPService.generation_cost)).where(
            and_(
                MCPService.farmer_id == current_farmer.id,
                MCPService.created_at >= start_date
            )
        )
    )
    generation_cost = generation_cost_result.scalar() or 0.0
    
    # 获取订阅费用
    from backend.services.cost_calculator import CostCalculator
    calculator = CostCalculator()
    subscription_fee = calculator.PRICING_TIERS[current_farmer.tier.value]["price"]
    
    # 计算总成本
    total_cost = generation_cost + subscription_fee
    
    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": now.isoformat(),
        "breakdown": {
            "service_generation": generation_cost,
            "subscription": subscription_fee,
            "api_calls": 0.0,  # 待实现
            "commission": 0.0  # 待实现
        },
        "total_cost_usd": total_cost,
        "total_cost_cny": total_cost * calculator.USD_TO_CNY
    }


def _calculate_quota_remaining(farmer: Farmer) -> int:
    """
    计算剩余服务配额
    
    Args:
        farmer: 农户对象
        
    Returns:
        int: 剩余配额
    """
    from backend.services.cost_calculator import CostCalculator
    calculator = CostCalculator()
    
    max_services = calculator.PRICING_TIERS[farmer.tier.value]["max_services"]
    remaining = max_services - farmer.services_count
    
    return max(0, remaining)
