"""
客户相关的Pydantic数据模型
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime


class CustomerCreate(BaseModel):
    """客户创建请求"""
    name: str = Field(..., min_length=1, max_length=100, description="客户姓名")
    phone: str = Field(..., description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    province: Optional[str] = Field(None, description="省份")
    city: Optional[str] = Field(None, description="城市")
    district: Optional[str] = Field(None, description="区县")
    address: Optional[str] = Field(None, description="详细地址")
    remark: Optional[str] = Field(None, description="备注")
    
    @field_validator('phone')
    @classmethod
    def phone_must_be_valid(cls, v):
        import re
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


class CustomerUpdate(BaseModel):
    """客户更新请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="客户姓名")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    province: Optional[str] = Field(None, description="省份")
    city: Optional[str] = Field(None, description="城市")
    district: Optional[str] = Field(None, description="区县")
    address: Optional[str] = Field(None, description="详细地址")
    level: Optional[str] = Field(None, description="客户等级")
    remark: Optional[str] = Field(None, description="备注")
    
    @field_validator('phone')
    @classmethod
    def phone_must_be_valid(cls, v):
        if v is None:
            return v
        import re
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


class CustomerResponse(BaseModel):
    """客户响应"""
    id: str
    farmer_id: str
    name: str
    phone: str
    email: Optional[str] = None
    avatar: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    level: str
    total_orders: int
    total_amount: float
    tags: List[str] = []
    remark: Optional[str] = None
    last_order_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CustomerListResponse(BaseModel):
    """客户列表响应"""
    items: List[CustomerResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class CustomerStatistics(BaseModel):
    """客户统计"""
    total_customers: int
    new_customers_this_month: int
    active_customers: int
    vip_customers: int
    total_customer_value: float
    average_customer_value: float

