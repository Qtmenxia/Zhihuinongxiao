"""
农户相关的Pydantic数据模型
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime


class FarmerRegister(BaseModel):
    """农户注册请求"""
    name: str = Field(..., min_length=2, max_length=100, description="农户姓名")
    phone: str = Field(..., description="手机号")
    password: str = Field(..., min_length=6, description="密码")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    
    # 地址信息
    province: str = Field(..., description="省份")
    city: str = Field(..., description="城市")
    county: str = Field(..., description="区县")
    village: Optional[str] = Field(None, description="村庄")
    
    @validator('phone')
    def phone_must_be_valid(cls, v):
        import re
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


class FarmerLogin(BaseModel):
    """农户登录请求"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")


class FarmerResponse(BaseModel):
    """农户信息响应"""
    id: str
    name: str
    phone: str
    email: Optional[str] = None
    
    # 地址
    province: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    village: Optional[str] = None
    
    # 认证信息
    is_verified: bool
    certification_type: Optional[str] = None
    
    # 订阅信息
    tier: str
    subscription_start: Optional[datetime] = None
    subscription_end: Optional[datetime] = None
    
    # 配额
    services_count: int
    api_calls_today: int
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class FarmerUpdate(BaseModel):
    """农户信息更新请求"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    village: Optional[str] = None


class FarmerLoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    farmer: FarmerResponse


class FarmerStatistics(BaseModel):
    """农户统计信息"""
    farmer_id: str
    services_count: int
    deployed_services: int
    total_orders: int
    total_revenue: float
    total_cost: float
    api_calls_today: int
    api_calls_this_month: int
