"""
成本记录相关的Pydantic模型
"""
from pydantic import BaseModel, Field, field_validator
from datetime import date as date_type, datetime
from typing import Optional


class CostRecordBase(BaseModel):
    """成本记录基础模型"""
    date: date_type = Field(..., description="成本发生日期")
    cost_type: str = Field(..., description="成本类型: material/labor/logistics/packaging/other", alias="type")
    category: str = Field(..., min_length=1, max_length=100, description="成本项目")
    quantity: float = Field(..., ge=0, description="数量/工时")
    unit_price: float = Field(..., ge=0, description="单价")
    amount: float = Field(..., ge=0, description="总金额")
    remark: Optional[str] = Field(None, description="备注")
    
    @field_validator('cost_type')
    @classmethod
    def validate_cost_type(cls, v):
        allowed_types = ['material', 'labor', 'logistics', 'packaging', 'other']
        if v not in allowed_types:
            raise ValueError(f'成本类型必须是以下之一: {", ".join(allowed_types)}')
        return v
    
    model_config = {
        "populate_by_name": True
    }


class CostRecordCreate(CostRecordBase):
    """创建成本记录请求"""
    pass


class CostRecordUpdate(BaseModel):
    """更新成本记录请求"""
    date: Optional[date_type] = None
    cost_type: Optional[str] = Field(None, alias="type")
    category: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None
    remark: Optional[str] = None
    
    @field_validator('cost_type')
    @classmethod
    def validate_cost_type(cls, v):
        if v is not None:
            allowed_types = ['material', 'labor', 'logistics', 'packaging', 'other']
            if v not in allowed_types:
                raise ValueError(f'成本类型必须是以下之一: {", ".join(allowed_types)}')
        return v
    
    model_config = {
        "populate_by_name": True
    }


class CostRecordResponse(CostRecordBase):
    """成本记录响应"""
    id: int
    farmer_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


class CostOverviewResponse(BaseModel):
    """成本概览响应"""
    total_cost: float = Field(..., description="总成本")
    total_trend: float = Field(..., description="环比趋势")
    material_cost: float = Field(..., description="原料成本")
    material_percent: float = Field(..., description="原料成本占比")
    labor_cost: float = Field(..., description="人工成本")
    labor_percent: float = Field(..., description="人工成本占比")
    other_cost: float = Field(..., description="其他成本")
    other_percent: float = Field(..., description="其他成本占比")


class CostTrendData(BaseModel):
    """成本趋势数据"""
    date: str
    material: float
    labor: float
    logistics: float
    packaging: float
    other: float
    total: float


class CostTrendResponse(BaseModel):
    """成本趋势响应"""
    period: str
    data: list[CostTrendData]

