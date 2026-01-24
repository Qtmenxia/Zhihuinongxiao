"""
产品管理API路由
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
        created_at=datetime.now(timezone.utc)()
    )
    
    db.add(product)
    await db.commit()
    await db.refresh(product)
    
    return ProductResponse.from_orm(product)


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
        keyword: 关键词搜索
        pagination: 分页参数
        db: 数据库会话
        current_farmer: 当前农户(可选)
    """
    # 构建查询
    query = select(Product).where(Product.is_active == True)
    
    # 应用筛选条件
    if category:
        query = query.where(Product.category == category)
    
    if farmer_id:
        query = query.where(Product.farmer_id == farmer_id)
    elif current_farmer:
        # 如果已登录但没指定farmer_id，显示当前农户的产品
        query = query.where(Product.farmer_id == current_farmer.id)
    
    if featured is not None:
        query = query.where(Product.is_featured == featured)
    
    if keyword:
        from sqlalchemy import or_
        search_pattern = f"%{keyword}%"
        query = query.where(
            or_(
                Product.name.ilike(search_pattern),
                Product.description.ilike(search_pattern)
            )
        )
    
    # 计算总数
    count_query = select(func.count()).select_from(Product).where(Product.is_active == True)
    if category:
        count_query = count_query.where(Product.category == category)
    if farmer_id:
        count_query = count_query.where(Product.farmer_id == farmer_id)
    elif current_farmer:
        count_query = count_query.where(Product.farmer_id == current_farmer.id)
    if featured is not None:
        count_query = count_query.where(Product.is_featured == featured)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页查询
    query = query.order_by(Product.created_at.desc())
    query = query.offset(pagination.offset).limit(pagination.limit)
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    # 转换为响应模型
    items = [ProductResponse.from_orm(p) for p in products]
    
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
    
    return ProductResponse.from_orm(product)


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
    
    product.updated_at = datetime.now(timezone.utc)()
    
    await db.commit()
    await db.refresh(product)
    
    return ProductResponse.from_orm(product)


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
    product.updated_at = datetime.now(timezone.utc)()
    
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
    product.updated_at = datetime.now(timezone.utc)()
    
    await db.commit()
    await db.refresh(product)
    
    return ProductResponse.from_orm(product)


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
