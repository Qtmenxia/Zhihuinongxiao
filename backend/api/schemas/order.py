"""
订单相关的Pydantic数据模型
"""
from pydantic import BaseModel, Field, field_validator, model_validator,ConfigDict
from typing import Optional, List
from datetime import datetime


class OrderItem(BaseModel):
    """订单商品项"""
    sku_code: str = Field(..., description="SKU编码")
    product_name: str = Field(..., description="产品名称")
    quantity: int = Field(..., gt=0, description="数量")
    price: float = Field(..., gt=0, description="单价")
    
    @property
    def subtotal(self) -> float:
        return self.quantity * self.price


class ShippingAddress(BaseModel):
    """收货地址"""
    name: str = Field(..., description="收货人姓名")
    phone: str = Field(..., description="收货人电话")
    province: str = Field(..., description="省份")
    city: str = Field(..., description="城市")
    district: str = Field(..., description="区县")
    detail: str = Field(..., description="详细地址")
    
    @field_validator('phone')
    @classmethod
    def phone_must_be_valid(cls, v):
        import re
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


class OrderCreate(BaseModel):
    """订单创建请求"""
    customer_id: str = Field(..., description="客户ID")
    items: List[OrderItem] = Field(..., min_items=1, description="订单商品列表")
    shipping_address: ShippingAddress = Field(..., description="收货地址")
    payment_method: str = Field(..., description="支付方式", example="wechat")
    customer_note: Optional[str] = Field(None, max_length=500, description="买家留言")
    
    @field_validator('payment_method')
    @classmethod
    def payment_method_must_be_valid(cls, v):
        valid_methods = ['wechat', 'alipay']
        if v not in valid_methods:
            raise ValueError(f'支付方式必须是: {", ".join(valid_methods)}')
        return v


class OrderResponse(BaseModel):
    """订单响应"""
    id: str
    farmer_id: str
    customer_id: str
    items: List[dict]
    
    # 金额
    subtotal: float
    shipping_fee: float
    discount: float
    total_amount: float
    
    # 支付信息
    payment_method: str
    payment_transaction_id: Optional[str] = None
    paid_at: Optional[datetime] = None
    
    # 配送信息
    shipping_address: dict
    shipping_method: Optional[str] = None
    tracking_number: Optional[str] = None
    shipped_at: Optional[datetime] = None
    
    # 状态
    status: str
    
    # 备注
    customer_note: Optional[str] = None
    farmer_note: Optional[str] = None
    
    # 时间戳
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    """订单列表响应"""
    items: List[OrderResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class OrderStatusUpdate(BaseModel):
    """订单状态更新请求"""
    status: str = Field(..., description="新状态")
    tracking_number: Optional[str] = Field(None, description="物流单号")
    farmer_note: Optional[str] = Field(None, description="农户备注")
    
    @field_validator('status')
    @classmethod
    def status_must_be_valid(cls, v):
        valid_statuses = ['pending', 'paid', 'shipped', 'completed', 'cancelled', 'refunded']
        if v not in valid_statuses:
            raise ValueError(f'状态必须是: {", ".join(valid_statuses)}')
        return v


class OrderStatistics(BaseModel):
    """订单统计"""
    total_orders: int
    pending_orders: int
    paid_orders: int
    shipped_orders: int
    completed_orders: int
    cancelled_orders: int
    total_revenue: float
    average_order_value: float
