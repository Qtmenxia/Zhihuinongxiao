"""
客户管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, cast, String
from typing import Optional
import uuid
from datetime import datetime, timezone, timedelta

from backend.api.dependencies import (
    get_session,
    get_current_farmer,
    get_pagination_params,
    PaginationParams
)
from backend.api.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse,
    CustomerStatistics
)
from backend.models.customer import Customer
from backend.models.farmer import Farmer
from backend.models.order import Order, OrderStatus

router = APIRouter()


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建客户",
    description="创建新客户"
)
async def create_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    创建客户
    
    Args:
        customer_data: 客户信息
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 检查手机号是否已存在
    result = await db.execute(
        select(Customer).where(
            Customer.farmer_id == current_farmer.id,
            Customer.phone == customer_data.phone
        )
    )
    existing_customer = result.scalar_one_or_none()
    
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已存在"
        )
    
    # 创建客户
    customer = Customer(
        id=f"cust_{uuid.uuid4().hex[:12]}",
        farmer_id=current_farmer.id,
        name=customer_data.name,
        phone=customer_data.phone,
        email=customer_data.email,
        province=customer_data.province,
        city=customer_data.city,
        district=customer_data.district,
        address=customer_data.address,
        remark=customer_data.remark,
        level="普通客户",
        total_orders=0,
        total_amount=0.0,
        tags=[],
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    
    return CustomerResponse.model_validate(customer)


@router.get(
    "",
    response_model=CustomerListResponse,
    summary="获取客户列表",
    description="获取当前农户的客户列表"
)
async def list_customers(
    name: Optional[str] = Query(None, description="客户姓名筛选"),
    phone: Optional[str] = Query(None, description="手机号筛选"),
    level: Optional[str] = Query(None, description="客户等级筛选"),
    province: Optional[str] = Query(None, description="省份筛选"),
    city: Optional[str] = Query(None, description="城市筛选"),
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    获取客户列表
    
    Args:
        name: 姓名筛选
        phone: 手机号筛选
        level: 客户等级筛选
        province: 省份筛选
        city: 城市筛选
        pagination: 分页参数
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 构建查询
    query = select(Customer).where(Customer.farmer_id == current_farmer.id)
    count_query = select(func.count()).select_from(Customer).where(
        Customer.farmer_id == current_farmer.id
    )
    
    # 姓名筛选
    if name:
        query = query.where(Customer.name.like(f"%{name}%"))
        count_query = count_query.where(Customer.name.like(f"%{name}%"))
    
    # 手机号筛选
    if phone:
        query = query.where(Customer.phone.like(f"%{phone}%"))
        count_query = count_query.where(Customer.phone.like(f"%{phone}%"))
    
    # 客户等级筛选
    if level:
        query = query.where(Customer.level == level)
        count_query = count_query.where(Customer.level == level)
    
    # 省份筛选
    if province:
        query = query.where(Customer.province == province)
        count_query = count_query.where(Customer.province == province)
    
    # 城市筛选
    if city:
        query = query.where(Customer.city == city)
        count_query = count_query.where(Customer.city == city)
    
    # 计算总数
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页查询
    query = query.order_by(Customer.created_at.desc())
    query = query.offset(pagination.offset).limit(pagination.limit)
    
    result = await db.execute(query)
    customers = result.scalars().all()
    
    # 转换为响应模型
    items = [CustomerResponse.model_validate(c) for c in customers]
    
    return CustomerListResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        has_more=(pagination.offset + len(items)) < total
    )


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="获取客户详情",
    description="获取指定客户的详细信息"
)
async def get_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    获取客户详情
    
    Args:
        customer_id: 客户ID
        db: 数据库会话
        current_farmer: 当前农户
    """
    result = await db.execute(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.farmer_id == current_farmer.id
        )
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return CustomerResponse.model_validate(customer)


@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="更新客户信息",
    description="更新客户的基本信息"
)
async def update_customer(
    customer_id: str,
    customer_data: CustomerUpdate,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    更新客户信息
    
    Args:
        customer_id: 客户ID
        customer_data: 客户更新信息
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 查询客户
    result = await db.execute(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.farmer_id == current_farmer.id
        )
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # 如果更新手机号，检查是否重复
    if customer_data.phone and customer_data.phone != customer.phone:
        result = await db.execute(
            select(Customer).where(
                Customer.farmer_id == current_farmer.id,
                Customer.phone == customer_data.phone,
                Customer.id != customer_id
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该手机号已被其他客户使用"
            )
    
    # 更新字段
    update_data = customer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    customer.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(customer)
    
    return CustomerResponse.model_validate(customer)


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除客户",
    description="删除指定客户"
)
async def delete_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    删除客户
    
    Args:
        customer_id: 客户ID
        db: 数据库会话
        current_farmer: 当前农户
    """
    result = await db.execute(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.farmer_id == current_farmer.id
        )
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    await db.delete(customer)
    await db.commit()


@router.get(
    "/statistics/summary",
    response_model=CustomerStatistics,
    summary="获取客户统计",
    description="获取当前农户的客户统计数据"
)
async def get_customer_statistics(
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    获取客户统计
    
    Args:
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 统计总客户数
    total_result = await db.execute(
        select(func.count()).select_from(Customer).where(
            Customer.farmer_id == current_farmer.id
        )
    )
    total_customers = total_result.scalar()
    
    # 统计本月新增客户
    month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_result = await db.execute(
        select(func.count()).select_from(Customer).where(
            Customer.farmer_id == current_farmer.id,
            Customer.created_at >= month_start
        )
    )
    new_customers_this_month = new_result.scalar()
    
    # 统计活跃客户(最近30天有订单)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    active_result = await db.execute(
        select(func.count(func.distinct(Customer.id))).select_from(Customer).where(
            Customer.farmer_id == current_farmer.id,
            Customer.last_order_at >= thirty_days_ago
        )
    )
    active_customers = active_result.scalar()
    
    # 统计VIP客户
    vip_result = await db.execute(
        select(func.count()).select_from(Customer).where(
            Customer.farmer_id == current_farmer.id,
            Customer.level.in_(["VIP客户", "黄金客户", "钻石客户"])
        )
    )
    vip_customers = vip_result.scalar()
    
    # 统计客户总价值
    value_result = await db.execute(
        select(func.sum(Customer.total_amount)).where(
            Customer.farmer_id == current_farmer.id
        )
    )
    total_customer_value = value_result.scalar() or 0.0
    
    # 计算平均客户价值
    average_customer_value = total_customer_value / total_customers if total_customers > 0 else 0.0
    
    return CustomerStatistics(
        total_customers=total_customers,
        new_customers_this_month=new_customers_this_month,
        active_customers=active_customers,
        vip_customers=vip_customers,
        total_customer_value=total_customer_value,
        average_customer_value=average_customer_value
    )


@router.get(
    "/export/pdf",
    summary="导出客户PDF",
    description="导出客户列表为PDF文件"
)
async def export_customers_pdf(
    name: Optional[str] = Query(None, description="客户姓名筛选"),
    phone: Optional[str] = Query(None, description="手机号筛选"),
    level: Optional[str] = Query(None, description="客户等级筛选"),
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    导出客户PDF
    
    Args:
        name: 姓名筛选
        phone: 手机号筛选
        level: 客户等级筛选
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
    from reportlab.lib.enums import TA_CENTER
    import io
    
    # 注册中文字体
    try:
        pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
        font_name = 'SimSun'
    except:
        font_name = 'Helvetica'
    
    # 构建查询
    query = select(Customer).where(Customer.farmer_id == current_farmer.id)
    
    if name:
        query = query.where(Customer.name.like(f"%{name}%"))
    
    if phone:
        query = query.where(Customer.phone.like(f"%{phone}%"))
    
    if level:
        query = query.where(Customer.level == level)
    
    query = query.order_by(Customer.created_at.desc())
    result = await db.execute(query)
    customers = result.scalars().all()
    
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
    title = Paragraph('客户列表', title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.5*cm))
    
    # 表格数据
    data = [['客户编号', '客户姓名', '手机号', '地址', '客户等级', '订单数', '累计消费', '注册时间']]
    
    for customer in customers:
        address = f"{customer.province or ''} {customer.city or ''} {customer.district or ''}"
        data.append([
            customer.id,
            customer.name,
            customer.phone,
            address.strip() or '-',
            customer.level,
            str(customer.total_orders),
            f'¥{customer.total_amount:.2f}',
            customer.created_at.strftime('%Y-%m-%d') if customer.created_at else '-'
        ])
    
    # 创建表格
    table = Table(data, colWidths=[3*cm, 2.5*cm, 3*cm, 4*cm, 2.5*cm, 2*cm, 2.5*cm, 3*cm])
    
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
    total_amount = sum(c.total_amount for c in customers)
    summary_style = ParagraphStyle(
        'Summary',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        textColor=colors.HexColor('#374151')
    )
    summary = Paragraph(f'总客户数: {len(customers)} | 累计消费: ¥{total_amount:.2f}', summary_style)
    elements.append(summary)
    
    # 生成PDF
    doc.build(elements)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        }
    )

