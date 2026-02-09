"""
农户管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt
import uuid
from datetime import datetime, timedelta, timezone

from backend.api.dependencies import (
    get_session,
    get_current_farmer,
    create_access_token
)
from ..schemas.farmer import (
    FarmerRegisterRequest,
    FarmerLoginRequest,
    FarmerResponse,
    FarmerUpdateRequest,
    FarmerLoginResponse,
    FarmerStatsResponse,
    FarmerStatistics
)
from backend.models.farmer import Farmer, FarmerTier
from backend.config.settings import settings

router = APIRouter()


@router.post(
    "/register",
    response_model=FarmerLoginResponse,
    status_code=status.HTTP_201_CREATED,
    summary="农户注册",
    description="创建新的农户账号"
)
async def register_farmer(
    farmer_data: FarmerRegisterRequest,
    db: AsyncSession = Depends(get_session)
):
    """
    注册新农户
    
    Args:
        farmer_data: 注册信息
        db: 数据库会话
    """
    # 检查手机号是否已存在
    result = await db.execute(
        select(Farmer).where(Farmer.phone == farmer_data.phone)
    )
    existing_farmer = result.scalar_one_or_none()
    
    if existing_farmer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number already registered"
        )
    
    # 哈希密码
    password_hash = bcrypt.hashpw(
        farmer_data.password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    # 创建农户
    farmer = Farmer(
        id=f"farmer_{uuid.uuid4().hex[:12]}",
        name=farmer_data.name,
        phone=farmer_data.phone,
        password_hash=password_hash,
        email=farmer_data.email,
        province=farmer_data.province,
        city=farmer_data.city,
        county=farmer_data.county,
        village=farmer_data.village,
        tier=FarmerTier.FREE,
        is_verified=False,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(farmer)
    await db.commit()
    await db.refresh(farmer)
    
    # 生成访问令牌
    access_token = create_access_token(
        data={"farmer_id": farmer.id}
    )
    
    return FarmerLoginResponse(
        access_token=access_token,
        token_type="bearer",
        farmer=FarmerResponse.model_validate(farmer)
    )


@router.post(
    "/login",
    response_model=FarmerLoginResponse,
    summary="农户登录",
    description="使用手机号和密码登录"
)
async def login_farmer(
    login_data: FarmerLoginRequest,
    db: AsyncSession = Depends(get_session)
):
    """
    农户登录
    
    Args:
        login_data: 登录信息
        db: 数据库会话
    """
    # 临时Mock登录 - 数据库未连接时使用
    if login_data.phone == "13800138000" and login_data.password == "demo123456":
        # 创建Mock农户数据
        mock_farmer = FarmerResponse(
            id="farmer_demo_mock_001",
            name="蒲县被子垣果园",
            phone="13800138000",
            email="demo@zhinonglianxiao.com",
            province="山西省",
            city="临汾市",
            county="蒲县",
            village="被子垣村",
            tier="basic",
            is_verified=True,
            certification_type="有机认证",
            services_count=0,
            api_calls_today=0,
            enable_commission=False,
            commission_rate=5,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # 生成访问令牌
        access_token = create_access_token(
            data={"farmer_id": mock_farmer.id}
        )
        
        return FarmerLoginResponse(
            access_token=access_token,
            token_type="bearer",
            farmer=mock_farmer
        )
    
    # 正常数据库登录流程
    try:
        # 查询农户
        result = await db.execute(
            select(Farmer).where(Farmer.phone == login_data.phone)
        )
        farmer = result.scalar_one_or_none()
        
        if not farmer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid phone number or password"
            )
        
        # 验证密码
        if not bcrypt.checkpw(
            login_data.password.encode('utf-8'),
            farmer.password_hash.encode('utf-8')
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid phone number or password"
            )
        
        # 生成访问令牌
        access_token = create_access_token(
            data={"farmer_id": farmer.id}
        )
        
        return FarmerLoginResponse(
            access_token=access_token,
            token_type="bearer",
            farmer=FarmerResponse.model_validate(farmer)
        )
    except Exception as e:
        # 数据库连接失败时的提示
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed. Please use demo account: 13800138000 / demo123456. Error: {str(e)}"
        )


@router.get(
    "/me",
    response_model=FarmerResponse,
    summary="获取当前农户信息",
    description="获取当前登录农户的详细信息"
)
async def get_current_farmer_info(
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    获取当前农户信息
    
    Args:
        current_farmer: 当前农户
    """
    return FarmerResponse.model_validate(current_farmer)


@router.put(
    "/me",
    response_model=FarmerResponse,
    summary="更新农户信息",
    description="更新当前农户的个人信息"
)
async def update_farmer_info(
    update_data: FarmerUpdateRequest,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    更新农户信息
    
    Args:
        update_data: 更新数据
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 更新字段
    if update_data.name is not None:
        current_farmer.name = update_data.name
    if update_data.email is not None:
        current_farmer.email = update_data.email
    if update_data.village is not None:
        current_farmer.village = update_data.village
    
    current_farmer.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(current_farmer)
    
    return FarmerResponse.model_validate(current_farmer)


@router.get(
    "/me/statistics",
    response_model=FarmerStatistics,
    summary="获取农户统计信息",
    description="获取当前农户的业务统计数据"
)
async def get_farmer_statistics(
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    获取农户统计信息
    
    Args:
        db: 数据库会话
        current_farmer: 当前农户
    """
    from sqlalchemy import func
    from backend.models.mcp_service import MCPService
    from backend.models.order import Order
    
    # 统计服务数
    services_result = await db.execute(
        select(func.count()).select_from(MCPService).where(
            MCPService.farmer_id == current_farmer.id
        )
    )
    services_count = services_result.scalar()
    
    # 统计已部署服务
    deployed_result = await db.execute(
        select(func.count()).select_from(MCPService).where(
            MCPService.farmer_id == current_farmer.id,
            MCPService.is_deployed == True
        )
    )
    deployed_services = deployed_result.scalar()
    
    # 统计订单
    orders_result = await db.execute(
        select(func.count()).select_from(Order).where(
            Order.farmer_id == current_farmer.id
        )
    )
    total_orders = orders_result.scalar()
    
    # 统计收入
    revenue_result = await db.execute(
        select(func.sum(Order.total_amount)).where(
            Order.farmer_id == current_farmer.id,
            Order.status == "completed"
        )
    )
    total_revenue = revenue_result.scalar() or 0.0
    
    # 统计成本
    cost_result = await db.execute(
        select(func.sum(MCPService.generation_cost)).where(
            MCPService.farmer_id == current_farmer.id
        )
    )
    total_cost = cost_result.scalar() or 0.0
    
    return FarmerStatistics(
        farmer_id=current_farmer.id,
        services_count=services_count,
        deployed_services=deployed_services,
        total_orders=total_orders,
        total_revenue=total_revenue,
        total_cost=total_cost,
        api_calls_today=current_farmer.api_calls_today,
        api_calls_this_month=0  # 需要从日志统计
    )


@router.post(
    "/upgrade",
    response_model=FarmerResponse,
    summary="升级订阅等级",
    description="升级农户的订阅计划"
)
async def upgrade_subscription(
    target_tier: str,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    升级订阅等级
    
    Args:
        target_tier: 目标等级(basic, professional)
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 验证目标等级
    try:
        tier_enum = FarmerTier(target_tier)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier: {target_tier}"
        )
    
    # 检查是否为升级
    tier_hierarchy = {"free": 0, "basic": 1, "professional": 2}
    current_level = tier_hierarchy[current_farmer.tier.value]
    target_level = tier_hierarchy[target_tier]
    
    if target_level <= current_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only upgrade to higher tier"
        )
    
    # 更新订阅
    current_farmer.tier = tier_enum
    current_farmer.subscription_start = datetime.now(timezone.utc)
    current_farmer.subscription_end = datetime.now(timezone.utc) + timedelta(days=30)
    current_farmer.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(current_farmer)
    
    # TODO: 集成支付系统
    
    return FarmerResponse.model_validate(current_farmer)
