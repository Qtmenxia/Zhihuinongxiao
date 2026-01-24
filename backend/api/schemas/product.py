"""
产品相关的Pydantic数据模型
"""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime


class ProductCreate(BaseModel):
    """产品创建请求"""
    name: str = Field(..., min_length=2, max_length=200, description="产品名称")
    sku_code: str = Field(..., description="SKU编码", example="YLX-158-9E")
    category: str = Field(..., description="产品类别", example="玉露香梨")
    
    # 规格与定价
    specs: dict = Field(..., description="产品规格", example={"枚数": 9, "规格": "85-95mm"})
    price: float = Field(..., gt=0, description="售价")
    original_price: Optional[float] = Field(None, description="原价(用于显示折扣)")
    
    # 库存
    stock: int = Field(0, ge=0, description="库存数量")
    stock_alert_threshold: int = Field(10, description="库存预警阈值")
    
    # 营销信息
    target_scene: Optional[str] = Field(None, description="目标场景", example="送礼/节日")
    packaging_type: Optional[str] = Field(None, description="包装类型", example="天地盖礼盒")
    selling_points: Optional[List[str]] = Field(None, description="卖点", example=["有机认证", "现摘现发"])
    
    # 媒体资源
    images: Optional[List[str]] = Field(None, description="图片URL列表")
    video_url: Optional[str] = Field(None, description="视频URL")
    
    # 溯源信息
    origin_info: Optional[dict] = Field(None, description="溯源信息")
    
    # 描述
    description: Optional[str] = Field(None, max_length=2000, description="产品描述")
    
    @field_validator('original_price')
    @classmethod
    def original_price_must_be_higher(cls, v, values):
        if v is not None and 'price' in values and v < values['price']:
            raise ValueError('原价必须高于售价')
        return v


class ProductUpdate(BaseModel):
    """产品更新请求"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    price: Optional[float] = Field(None, gt=0)
    original_price: Optional[float] = None
    stock: Optional[int] = Field(None, ge=0)
    stock_alert_threshold: Optional[int] = None
    target_scene: Optional[str] = None
    selling_points: Optional[List[str]] = None
    images: Optional[List[str]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class ProductResponse(BaseModel):
    """产品响应"""
    id: str
    farmer_id: str
    name: str
    sku_code: str
    category: str
    specs: dict
    price: float
    original_price: Optional[float] = None
    stock: int
    stock_alert_threshold: int
    target_scene: Optional[str] = None
    packaging_type: Optional[str] = None
    selling_points: Optional[List[str]] = None
    images: Optional[List[str]] = None
    video_url: Optional[str] = None
    origin_info: Optional[dict] = None
    description: Optional[str] = None
    is_active: bool
    is_featured: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """产品列表响应"""
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class ProductStockUpdate(BaseModel):
    """库存更新请求"""
    stock_change: int = Field(..., description="库存变化量(正数增加，负数减少)")
    reason: Optional[str] = Field(None, description="变更原因")
