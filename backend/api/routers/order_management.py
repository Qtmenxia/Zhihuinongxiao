"""
订单管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
import uuid
from datetime import datetime, timezone

from backend.api.dependencies import (
    get_session,
    get_current_farmer,
    get_pagination_params,
    PaginationParams
)
from backend.api.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderListResponse,
    OrderStatusUpdate,
    OrderStatistics
)
from backend.models.order import Order, OrderStatus
from backend.models.farmer import Farmer
from backend.models.product import Product

router = APIRouter()


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建订单",
    description="创建新订单"
)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    创建订单
    
    Args:
        order_data: 订单信息
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 验证产品并计算金额
    subtotal = 0.0
    for item in order_data.items:
        result = await db.execute(
            select(Product).where(
                Product.sku_code == item.sku_code,
                Product.farmer_id == current_farmer.id
            )
        )
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with SKU '{item.sku_code}' not found"
            )
        
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}. Available: {product.stock}"
            )
        
        subtotal += item.subtotal
    
    # 计算运费
    from backend.config.product_config import SHIPPING_CONFIG
    shipping_fee = 0.0 if subtotal >= SHIPPING_CONFIG["free_shipping_threshold"] else SHIPPING_CONFIG["default_shipping_fee"]
    
    # 计算总金额
    total_amount = subtotal + shipping_fee
    
    # 创建订单
    order = Order(
        id=f"order_{uuid.uuid4().hex[:12]}",
        farmer_id=current_farmer.id,
        customer_id=order_data.customer_id,
        items=[item.dict() for item in order_data.items],
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        discount=0.0,
        total_amount=total_amount,
        payment_method=order_data.payment_method,
        shipping_address=order_data.shipping_address.dict(),
        customer_note=order_data.customer_note,
        status=OrderStatus.PENDING,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(order)
    
    # 减少库存
    for item in order_data.items:
        result = await db.execute(
            select(Product).where(Product.sku_code == item.sku_code)
        )
        product = result.scalar_one()
        product.stock -= item.quantity
    
    await db.commit()
    await db.refresh(order)
    
    return OrderResponse.model_validate(order)


@router.get(
    "",
    response_model=OrderListResponse,
    summary="获取订单列表",
    description="获取当前农户的订单列表"
)
async def list_orders(
    status_filter: Optional[str] = Query(None, description="订单状态筛选"),
    customer_id: Optional[str] = Query(None, description="客户ID筛选"),
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    获取订单列表
    
    Args:
        status_filter: 状态筛选
        customer_id: 客户ID筛选
        pagination: 分页参数
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 构建查询
    query = select(Order).where(Order.farmer_id == current_farmer.id)
    
    if status_filter:
        try:
            status_enum = OrderStatus(status_filter)
            query = query.where(Order.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    if customer_id:
        query = query.where(Order.customer_id == customer_id)
    
    # 计算总数
    count_query = select(func.count()).select_from(Order).where(
        Order.farmer_id == current_farmer.id
    )
    if status_filter:
        count_query = count_query.where(Order.status == status_enum)
    if customer_id:
        count_query = count_query.where(Order.customer_id == customer_id)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页查询
    query = query.order_by(Order.created_at.desc())
    query = query.offset(pagination.offset).limit(pagination.limit)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    # 转换为响应模型
    items = [OrderResponse.model_validate(o) for o in orders]
    
    return OrderListResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        has_more=(pagination.offset + len(items)) < total
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="获取订单详情",
    description="获取指定订单的详细信息"
)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    获取订单详情
    
    Args:
        order_id: 订单ID
        db: 数据库会话
        current_farmer: 当前农户
    """
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.farmer_id == current_farmer.id
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return OrderResponse.model_validate(order)


@router.put(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="更新订单状态",
    description="更新订单状态(如发货、完成等)"
)
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    更新订单状态
    
    Args:
        order_id: 订单ID
        status_update: 状态更新信息
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 查询订单
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.farmer_id == current_farmer.id
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # 验证状态转换
    try:
        new_status = OrderStatus(status_update.status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {status_update.status}"
        )
    
    # 更新状态
    order.status = new_status
    
    # 更新时间戳
    if new_status == OrderStatus.PAID:
        order.paid_at = datetime.now(timezone.utc)
    elif new_status == OrderStatus.SHIPPED:
        order.shipped_at = datetime.now(timezone.utc)
        if status_update.tracking_number:
            order.tracking_number = status_update.tracking_number
    elif new_status == OrderStatus.COMPLETED:
        order.completed_at = datetime.now(timezone.utc)
    
    # 更新备注
    if status_update.farmer_note:
        order.farmer_note = status_update.farmer_note
    
    order.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(order)
    
    return OrderResponse.model_validate(order)


@router.get(
    "/statistics/summary",
    response_model=OrderStatistics,
    summary="获取订单统计",
    description="获取当前农户的订单统计数据"
)
async def get_order_statistics(
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    获取订单统计
    
    Args:
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 统计总订单数
    total_result = await db.execute(
        select(func.count()).select_from(Order).where(
            Order.farmer_id == current_farmer.id
        )
    )
    total_orders = total_result.scalar()
    
    # 按状态统计
    status_counts = {}
    for status in OrderStatus:
        result = await db.execute(
            select(func.count()).select_from(Order).where(
                Order.farmer_id == current_farmer.id,
                Order.status == status
            )
        )
        status_counts[status.value] = result.scalar()
    
    # 统计总收入(已完成订单)
    revenue_result = await db.execute(
        select(func.sum(Order.total_amount)).where(
            Order.farmer_id == current_farmer.id,
            Order.status == OrderStatus.COMPLETED
        )
    )
    total_revenue = revenue_result.scalar() or 0.0
    
    # 计算平均订单金额
    average_order_value = total_revenue / status_counts.get("completed", 1)
    
    return OrderStatistics(
        total_orders=total_orders,
        pending_orders=status_counts.get("pending", 0),
        paid_orders=status_counts.get("paid", 0),
        shipped_orders=status_counts.get("shipped", 0),
        completed_orders=status_counts.get("completed", 0),
        cancelled_orders=status_counts.get("cancelled", 0),
        total_revenue=total_revenue,
        average_order_value=average_order_value
    )
