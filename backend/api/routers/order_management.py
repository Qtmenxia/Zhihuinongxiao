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
    order_id: Optional[str] = Query(None, description="订单编号筛选"),
    customer: Optional[str] = Query(None, description="客户信息筛选(姓名/手机号)"),
    start_date: Optional[str] = Query(None, description="开始日期(YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期(YYYY-MM-DD)"),
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    获取订单列表
    
    Args:
        status_filter: 状态筛选
        customer_id: 客户ID筛选
        order_id: 订单编号筛选
        customer: 客户信息筛选
        start_date: 开始日期
        end_date: 结束日期
        pagination: 分页参数
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 构建查询
    query = select(Order).where(Order.farmer_id == current_farmer.id)
    count_query = select(func.count()).select_from(Order).where(
        Order.farmer_id == current_farmer.id
    )
    
    # 状态筛选
    if status_filter:
        try:
            status_enum = OrderStatus(status_filter.upper())
            query = query.where(Order.status == status_enum)
            count_query = count_query.where(Order.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    # 客户ID筛选
    if customer_id:
        query = query.where(Order.customer_id == customer_id)
        count_query = count_query.where(Order.customer_id == customer_id)
    
    # 订单编号筛选
    if order_id:
        query = query.where(Order.id.like(f"%{order_id}%"))
        count_query = count_query.where(Order.id.like(f"%{order_id}%"))
    
    # 客户信息筛选(姓名或手机号)
    if customer:
        from sqlalchemy import or_, cast, String
        query = query.where(
            or_(
                cast(Order.shipping_address['name'], String).like(f"%{customer}%"),
                cast(Order.shipping_address['phone'], String).like(f"%{customer}%")
            )
        )
        count_query = count_query.where(
            or_(
                cast(Order.shipping_address['name'], String).like(f"%{customer}%"),
                cast(Order.shipping_address['phone'], String).like(f"%{customer}%")
            )
        )
    
    # 日期范围筛选
    if start_date:
        from datetime import datetime as dt
        start_dt = dt.strptime(start_date, "%Y-%m-%d")
        query = query.where(Order.created_at >= start_dt)
        count_query = count_query.where(Order.created_at >= start_dt)
    
    if end_date:
        from datetime import datetime as dt, timedelta
        end_dt = dt.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        query = query.where(Order.created_at < end_dt)
        count_query = count_query.where(Order.created_at < end_dt)
    
    # 计算总数
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
        new_status = OrderStatus(status_update.status.upper())
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
        if status_update.shipping_method:
            order.shipping_method = status_update.shipping_method
    elif new_status == OrderStatus.COMPLETED:
        order.completed_at = datetime.now(timezone.utc)
    
    # 更新备注
    if status_update.farmer_note:
        order.farmer_note = status_update.farmer_note
    
    order.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(order)
    
    return OrderResponse.model_validate(order)


@router.post(
    "/{order_id}/ship",
    response_model=OrderResponse,
    summary="订单发货",
    description="标记订单为已发货并添加物流信息"
)
async def ship_order(
    order_id: str,
    shipping_method: str,
    tracking_number: str,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    订单发货
    
    Args:
        order_id: 订单ID
        shipping_method: 物流公司
        tracking_number: 物流单号
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
    
    # 检查订单状态
    if order.status != OrderStatus.PAID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only paid orders can be shipped"
        )
    
    # 更新订单
    order.status = OrderStatus.SHIPPED
    order.shipping_method = shipping_method
    order.tracking_number = tracking_number
    order.shipped_at = datetime.now(timezone.utc)
    order.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(order)
    
    return OrderResponse.model_validate(order)


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    summary="取消订单",
    description="取消待支付的订单"
)
async def cancel_order(
    order_id: str,
    reason: str,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    取消订单
    
    Args:
        order_id: 订单ID
        reason: 取消原因
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
    
    # 检查订单状态
    if order.status not in [OrderStatus.PENDING, OrderStatus.PAID]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending or paid orders can be cancelled"
        )
    
    # 更新订单
    order.status = OrderStatus.CANCELLED
    order.farmer_note = f"取消原因: {reason}"
    order.updated_at = datetime.now(timezone.utc)
    
    # 恢复库存
    for item in order.items:
        result = await db.execute(
            select(Product).where(Product.sku_code == item['sku_code'])
        )
        product = result.scalar_one_or_none()
        if product:
            product.stock += item['quantity']
    
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
    completed_count = status_counts.get("COMPLETED", 0)
    average_order_value = total_revenue / completed_count if completed_count > 0 else 0.0
    
    return OrderStatistics(
        total_orders=total_orders,
        pending_orders=status_counts.get("PENDING", 0),
        paid_orders=status_counts.get("PAID", 0),
        shipped_orders=status_counts.get("SHIPPED", 0),
        completed_orders=status_counts.get("COMPLETED", 0),
        cancelled_orders=status_counts.get("CANCELLED", 0),
        total_revenue=total_revenue,
        average_order_value=average_order_value
    )


@router.get(
    "/export/pdf",
    summary="导出订单PDF",
    description="导出订单列表为PDF文件"
)
async def export_orders_pdf(
    status_filter: Optional[str] = Query(None, description="订单状态筛选"),
    order_id: Optional[str] = Query(None, description="订单编号筛选"),
    customer: Optional[str] = Query(None, description="客户信息筛选"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    导出订单PDF
    
    Args:
        status_filter: 状态筛选
        order_id: 订单编号筛选
        customer: 客户信息筛选
        start_date: 开始日期
        end_date: 结束日期
        db: 数据库会话
        current_farmer: 当前农户
    """
    from fastapi.responses import StreamingResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    import io
    
    # 注册中文字体
    try:
        pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
        font_name = 'SimSun'
    except:
        font_name = 'Helvetica'
    
    # 构建查询
    query = select(Order).where(Order.farmer_id == current_farmer.id)
    
    if status_filter:
        try:
            status_enum = OrderStatus(status_filter.upper())
            query = query.where(Order.status == status_enum)
        except ValueError:
            pass
    
    if order_id:
        query = query.where(Order.id.like(f"%{order_id}%"))
    
    if customer:
        from sqlalchemy import or_, cast, String
        query = query.where(
            or_(
                cast(Order.shipping_address['name'], String).like(f"%{customer}%"),
                cast(Order.shipping_address['phone'], String).like(f"%{customer}%")
            )
        )
    
    if start_date:
        from datetime import datetime as dt
        start_dt = dt.strptime(start_date, "%Y-%m-%d")
        query = query.where(Order.created_at >= start_dt)
    
    if end_date:
        from datetime import datetime as dt, timedelta
        end_dt = dt.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        query = query.where(Order.created_at < end_dt)
    
    query = query.order_by(Order.created_at.desc())
    result = await db.execute(query)
    orders = result.scalars().all()
    
    # 创建PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=1*cm, bottomMargin=1*cm)
    
    # 样式
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=16,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    # 构建内容
    elements = []
    
    # 标题
    title = Paragraph('订单列表', title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.5*cm))
    
    # 表格数据
    data = [['订单编号', '客户姓名', '联系电话', '订单金额', '订单状态', '下单时间']]
    
    status_map = {
        'PENDING': '待支付',
        'PAID': '已支付',
        'SHIPPED': '已发货',
        'COMPLETED': '已完成',
        'CANCELLED': '已取消',
        'REFUNDED': '已退款'
    }
    
    for order in orders:
        shipping_addr = order.shipping_address or {}
        data.append([
            order.id,
            shipping_addr.get('name', '-'),
            shipping_addr.get('phone', '-'),
            f'¥{order.total_amount:.2f}',
            status_map.get(order.status.value, order.status.value),
            order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else '-'
        ])
    
    # 创建表格
    table = Table(data, colWidths=[4*cm, 3*cm, 3*cm, 2.5*cm, 2.5*cm, 4*cm])
    
    # 表格样式
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(table)
    
    # 统计信息
    elements.append(Spacer(1, 0.5*cm))
    total_amount = sum(o.total_amount for o in orders)
    summary_style = ParagraphStyle(
        'Summary',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        textColor=colors.HexColor('#374151')
    )
    summary = Paragraph(f'总订单数: {len(orders)} | 总金额: ¥{total_amount:.2f}', summary_style)
    elements.append(summary)
    
    # 生成PDF
    doc.build(elements)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        }
    )
