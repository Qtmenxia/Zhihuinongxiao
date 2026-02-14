"""
产品管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
import uuid
from datetime import datetime, timezone
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER
import os

from backend.api.dependencies import (
    get_session,
    get_current_farmer,
    get_optional_current_farmer,
    get_pagination_params,
    PaginationParams
)
from backend.api.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    ProductStockUpdate
)
from backend.models.product import Product
from backend.models.farmer import Farmer

router = APIRouter()


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建产品",
    description="添加新产品到农户的产品库"
)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    创建新产品
    
    Args:
        product_data: 产品信息
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 检查SKU是否已存在
    result = await db.execute(
        select(Product).where(Product.sku_code == product_data.sku_code)
    )
    existing_product = result.scalar_one_or_none()
    
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"SKU code '{product_data.sku_code}' already exists"
        )
    
    # 创建产品
    product = Product(
        id=f"product_{uuid.uuid4().hex[:12]}",
        farmer_id=current_farmer.id,
        name=product_data.name,
        sku_code=product_data.sku_code,
        category=product_data.category,
        specs=product_data.specs,
        price=product_data.price,
        original_price=product_data.original_price or product_data.price * 1.25,
        stock=product_data.stock,
        stock_alert_threshold=product_data.stock_alert_threshold,
        target_scene=product_data.target_scene,
        packaging_type=product_data.packaging_type,
        selling_points=product_data.selling_points,
        images=product_data.images,
        video_url=product_data.video_url,
        origin_info=product_data.origin_info,
        description=product_data.description,
        is_active=True,
        is_featured=False,
        created_at=datetime.now(timezone.utc),
        updated_at=None
    )
    
    db.add(product)
    await db.commit()
    await db.refresh(product)
    
    return ProductResponse.model_validate(product)


@router.get(
    "",
    response_model=ProductListResponse,
    summary="获取产品列表",
    description="获取产品列表(支持分页和筛选，公开访问)"
)
async def list_products(
    category: Optional[str] = Query(None, description="产品类别筛选"),
    farmer_id: Optional[str] = Query(None, description="农户ID筛选"),
    featured: Optional[bool] = Query(None, description="仅显示特色产品"),
    is_active: Optional[bool] = Query(None, description="产品状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_session),
    current_farmer: Optional[Farmer] = Depends(get_optional_current_farmer)
):
    """
    获取产品列表
    
    Args:
        category: 类别筛选
        farmer_id: 农户ID筛选
        featured: 特色产品筛选
        is_active: 产品状态筛选（None=全部，True=在售，False=下架）
        keyword: 关键词搜索
        pagination: 分页参数
        db: 数据库会话
        current_farmer: 当前农户(可选)
    """
    # 构建查询 - 不再默认过滤 is_active
    query = select(Product)
    count_query = select(func.count()).select_from(Product)
    
    # 应用筛选条件
    conditions = []
    
    if category:
        conditions.append(Product.category == category)
    
    if farmer_id:
        conditions.append(Product.farmer_id == farmer_id)
    elif current_farmer:
        # 如果已登录但没指定farmer_id，显示当前农户的产品
        conditions.append(Product.farmer_id == current_farmer.id)
    
    if featured is not None:
        conditions.append(Product.is_featured == featured)
    
    # 状态筛选：None=全部，True=在售，False=下架
    if is_active is not None:
        conditions.append(Product.is_active == is_active)
    
    if keyword:
        from sqlalchemy import or_
        search_pattern = f"%{keyword}%"
        conditions.append(
            or_(
                Product.name.ilike(search_pattern),
                Product.description.ilike(search_pattern)
            )
        )
    
    # 应用所有条件
    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))
    
    # 计算总数
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页查询
    query = query.order_by(Product.created_at.desc())
    query = query.offset(pagination.offset).limit(pagination.limit)
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    # 转换为响应模型
    items = [ProductResponse.model_validate(p) for p in products]
    
    return ProductListResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        has_more=(pagination.offset + len(items)) < total
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="获取产品详情",
    description="获取指定产品的详细信息"
)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_session)
):
    """
    获取产品详情
    
    Args:
        product_id: 产品ID
        db: 数据库会话
    """
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return ProductResponse.model_validate(product)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="更新产品信息",
    description="更新产品的详细信息"
)
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    更新产品信息
    
    Args:
        product_id: 产品ID
        product_data: 更新数据
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 查询产品
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.farmer_id == current_farmer.id
        )
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # 更新字段
    update_dict = product_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(product, field, value)
    
    product.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(product)
    
    return ProductResponse.model_validate(product)


@router.delete(
    "/{product_id}",
    summary="删除产品",
    description="删除产品(软删除)"
)
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    删除产品(软删除)
    
    Args:
        product_id: 产品ID
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 查询产品
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.farmer_id == current_farmer.id
        )
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # 软删除
    product.is_active = False
    product.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    return {"message": "Product deleted successfully", "product_id": product_id}


@router.post(
    "/{product_id}/stock",
    response_model=ProductResponse,
    summary="更新产品库存",
    description="增加或减少产品库存"
)
async def update_product_stock(
    product_id: str,
    stock_update: ProductStockUpdate,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    更新产品库存
    
    Args:
        product_id: 产品ID
        stock_update: 库存更新信息
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 查询产品
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.farmer_id == current_farmer.id
        )
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # 更新库存
    new_stock = product.stock + stock_update.stock_change
    
    if new_stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Current: {product.stock}, requested change: {stock_update.stock_change}"
        )
    
    product.stock = new_stock
    product.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(product)
    
    return ProductResponse.model_validate(product)


@router.get(
    "/categories/list",
    summary="获取产品类别列表",
    description="获取所有可用的产品类别"
)
async def list_categories(
    db: AsyncSession = Depends(get_session)
):
    """
    获取产品类别列表
    
    Args:
        db: 数据库会话
    """
    from sqlalchemy import distinct
    
    result = await db.execute(
        select(distinct(Product.category)).where(Product.is_active == True)
    )
    categories = result.scalars().all()
    
    return {
        "categories": [c for c in categories if c]
    }


@router.get(
    "/export/pdf",
    summary="导出产品列表为PDF",
    description="导出当前筛选条件下的产品列表为PDF文件"
)
async def export_products_pdf(
    category: Optional[str] = Query(None, description="产品类别筛选"),
    is_active: Optional[bool] = Query(None, description="产品状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    导出产品列表为PDF
    
    Args:
        category: 类别筛选
        is_active: 产品状态筛选
        keyword: 关键词搜索
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 构建查询
    query = select(Product).where(Product.farmer_id == current_farmer.id)
    
    conditions = []
    if category:
        conditions.append(Product.category == category)
    if is_active is not None:
        conditions.append(Product.is_active == is_active)
    if keyword:
        from sqlalchemy import or_
        search_pattern = f"%{keyword}%"
        conditions.append(
            or_(
                Product.name.ilike(search_pattern),
                Product.description.ilike(search_pattern)
            )
        )
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(Product.created_at.desc())
    
    # 获取所有产品
    result = await db.execute(query)
    products = result.scalars().all()
    
    # 创建PDF
    buffer = BytesIO()
    
    # 注册中文字体（使用系统字体）
    try:
        # Windows系统字体路径
        font_path = "C:/Windows/Fonts/simhei.ttf"  # 黑体
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('SimHei', font_path))
            font_name = 'SimHei'
        else:
            # 如果没有中文字体，使用默认字体
            font_name = 'Helvetica'
    except:
        font_name = 'Helvetica'
    
    # 创建PDF文档（横向A4）
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    # 准备内容
    elements = []
    
    # 标题样式
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=getSampleStyleSheet()['Heading1'],
        fontName=font_name,
        fontSize=18,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    # 添加标题
    title = Paragraph(f"产品列表 - {current_farmer.name}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.5*cm))
    
    # 添加导出信息
    info_style = ParagraphStyle(
        'Info',
        parent=getSampleStyleSheet()['Normal'],
        fontName=font_name,
        fontSize=10,
        textColor=colors.HexColor('#6b7280')
    )
    export_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    info = Paragraph(f"导出时间: {export_time} | 产品数量: {len(products)}", info_style)
    elements.append(info)
    elements.append(Spacer(1, 0.5*cm))
    
    # 创建表格数据
    table_data = [
        ['序号', '产品名称', 'SKU', '分类', '价格(元)', '库存', '状态']
    ]
    
    for idx, product in enumerate(products, 1):
        table_data.append([
            str(idx),
            product.name[:20] if len(product.name) > 20 else product.name,
            product.sku_code,
            product.category,
            f"{product.price:.2f}",
            str(product.stock),
            '在售' if product.is_active else '下架'
        ])
    
    # 创建表格
    table = Table(table_data, colWidths=[2*cm, 6*cm, 4*cm, 3*cm, 3*cm, 2*cm, 2*cm])
    
    # 表格样式
    table.setStyle(TableStyle([
        # 表头样式
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # 表格内容样式
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1f2937')),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # 序号居中
        ('ALIGN', (4, 1), (-1, -1), 'CENTER'),  # 价格、库存、状态居中
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        
        # 网格线
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#3b82f6')),
        
        # 斑马纹
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
    ]))
    
    elements.append(table)
    
    # 生成PDF
    doc.build(elements)
    
    # 返回PDF文件
    buffer.seek(0)
    filename = f"products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
