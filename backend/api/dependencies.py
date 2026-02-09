"""
FastAPI依赖注入
提供通用的依赖项，如数据库会话、当前用户等
"""
from fastapi import Depends, HTTPException, status, Header,Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import Optional, AsyncGenerator
import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
import uuid
from typing import Optional

from backend.database.connection import AsyncSessionLocal
from backend.models.farmer import Farmer, FarmerTier
from backend.config.settings import settings
from backend.database.connection import get_db, get_async_db


# JWT认证方案
security = HTTPBearer()


# ==================== 数据库会话依赖 ====================

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取异步数据库会话（推荐用于异步路由）
    
    Yields:
        AsyncSession: 异步数据库会话
    """
    async for session in get_async_db():
        yield session


def get_sync_session() -> Session:
    """
    获取同步数据库会话（用于同步路由）
    
    Returns:
        Session: 数据库会话
    """
    return next(get_db())


# ==================== 认证相关依赖 ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data: 要编码的数据（通常包含farmer_id）
        expires_delta: 过期时间增量
        
    Returns:
        str: JWT令牌
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    解码JWT令牌
    
    Args:
        token: JWT令牌字符串
        
    Returns:
        dict: 解码后的数据
        
    Raises:
        HTTPException: 令牌无效或过期
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_farmer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_session)
) -> Farmer:
    """
    获取当前认证的农户
    
    Args:
        credentials: HTTP Bearer认证凭据
        db: 数据库会话
        
    Returns:
        Farmer: 当前农户对象
        
    Raises:
        HTTPException: 认证失败
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    farmer_id: str = payload.get("farmer_id")
    if farmer_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    # 从数据库查询农户
    from sqlalchemy import select
    result = await db.execute(select(Farmer).where(Farmer.id == farmer_id))
    farmer = result.scalar_one_or_none()
    
    if farmer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Farmer not found"
        )
    
    return farmer


async def get_optional_current_farmer(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_session)
) -> Optional[Farmer]:
    """
    获取可选的当前农户（用于部分公开接口）
    
    Args:
        authorization: Authorization头
        db: 数据库会话
        
    Returns:
        Optional[Farmer]: 农户对象（未认证时返回None）
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_access_token(token)
        farmer_id = payload.get("farmer_id")
        
        if farmer_id:
            from sqlalchemy import select
            result = await db.execute(select(Farmer).where(Farmer.id == farmer_id))
            return result.scalar_one_or_none()
    except:
        pass
    
    return None


# ==================== 权限检查依赖 ====================

def check_farmer_tier(required_tier: str):
    """
    检查农户订阅等级的依赖工厂
    
    Args:
        required_tier: 要求的最低等级（"free", "basic", "professional"）
        
    Returns:
        依赖函数
    """
    tier_hierarchy = {"free": 0, "basic": 1, "professional": 2}
    
    async def _check_tier(current_farmer: Farmer = Depends(get_current_farmer)):
        current_tier_level = tier_hierarchy.get(current_farmer.tier.value, 0)
        required_tier_level = tier_hierarchy.get(required_tier, 0)
        
        if current_tier_level < required_tier_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires '{required_tier}' tier or higher. Please upgrade your subscription."
            )
        
        return current_farmer
    
    return _check_tier


def check_service_quota():
    """
    检查服务生成配额的依赖
    """
    async def _check_quota(
        current_farmer: Farmer = Depends(get_current_farmer),
        db: AsyncSession = Depends(get_session)
    ):
        from backend.services.cost_calculator import CostCalculator
        
        calculator = CostCalculator()
        max_services = calculator.PRICING_TIERS[current_farmer.tier.value]["max_services"]
        
        if current_farmer.services_count >= max_services:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Service quota exceeded. Current tier allows {max_services} services. Please upgrade or delete unused services."
            )
        
        return current_farmer
    
    return _check_quota


def check_api_rate_limit():
    """
    检查API调用频率限制的依赖
    """
    async def _check_rate_limit(
        current_farmer: Farmer = Depends(get_current_farmer),
        db: AsyncSession = Depends(get_session)
    ):
        from backend.services.cost_calculator import CostCalculator
        
        calculator = CostCalculator()
        max_calls = calculator.PRICING_TIERS[current_farmer.tier.value]["max_requests_per_day"]
        
        if current_farmer.api_calls_today >= max_calls:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily API call limit exceeded ({max_calls} calls). Limit resets at midnight."
            )
        
        # 增加调用计数（实际应用中应该用Redis等更高效的方案）
        current_farmer.api_calls_today += 1
        await db.commit()
        
        return current_farmer
    
    return _check_rate_limit


# ==================== 分页依赖 ====================

class PaginationParams:
    """分页参数"""
    
    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
        max_page_size: int = 100
    ):
        self.page = max(1, page)
        self.page_size = min(max(1, page_size), max_page_size)
        self.skip = (self.page - 1) * self.page_size
        self.limit = self.page_size
    
    @property
    def offset(self) -> int:
        return self.skip


def get_pagination_params(
    page: int = 1,
    page_size: int = 20
) -> PaginationParams:
    """
    获取分页参数
    
    Args:
        page: 页码（从1开始）
        page_size: 每页数量
        
    Returns:
        PaginationParams: 分页参数对象
    """
    return PaginationParams(page=page, page_size=page_size)


# ==================== 请求ID依赖 ====================

import uuid

async def get_request_id(x_request_id: Optional[str] = Header(None)) -> str:
    """
    获取或生成请求ID（用于日志追踪）
    
    Args:
        x_request_id: 客户端提供的请求ID
        
    Returns:
        str: 请求ID
    """
    return x_request_id if x_request_id else str(uuid.uuid4())

async def get_session() -> AsyncSession:
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_farmer_v2(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_session)
) -> Farmer:
    """获取当前认证农户（备用版本）"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        farmer_id = payload.get("sub") or payload.get("farmer_id")
        if not farmer_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证令牌已过期或无效"
        )
    
    result = await db.execute(select(Farmer).where(Farmer.id == farmer_id))
    farmer = result.scalar_one_or_none()
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="农户不存在"
        )
    
    return farmer


def check_service_quota(required_quota: int = 1):
    """
    检查服务配额的依赖工厂
    
    Args:
        required_quota: 需要的配额数量
    """
    async def _check_quota(
        current_farmer: Farmer = Depends(get_current_farmer)
    ) -> Farmer:
        # 根据农户等级设置配额限制
        quota_limits = {
            FarmerTier.FREE: 3,
            FarmerTier.BASIC: 20,
            FarmerTier.PRO: 100,
            FarmerTier.ENTERPRISE: 1000
        }
        
        max_services = quota_limits.get(current_farmer.tier, 3)
        
        if current_farmer.services_count + required_quota > max_services:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"服务配额已满。当前等级 {current_farmer.tier.value} 最多可创建 {max_services} 个服务，"
                       f"已创建 {current_farmer.services_count} 个。请升级套餐。"
            )
        
        return current_farmer
    
    return _check_quota


def get_request_id(request: Request) -> str:
    """获取或生成请求ID"""
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())[:8]
    return request_id