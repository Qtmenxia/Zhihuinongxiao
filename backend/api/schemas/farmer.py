"""
农户相关的Pydantic Schema
用于API请求/响应的数据验证和序列化
"""
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator,ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum



# ==================== 枚举类型 ====================

class FarmerTierEnum(str, Enum):
    """农户订阅层级枚举"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"


# ==================== 请求Schema ====================

class FarmerRegisterRequest(BaseModel):
    """农户注册请求"""
    name: str = Field(..., min_length=2, max_length=100, description="农户姓名")
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    email: Optional[EmailStr] = Field(None, description="邮箱（可选）")
    
    # 地址信息
    province: str = Field(..., max_length=50, description="省份")
    city: str = Field(..., max_length=50, description="城市")
    county: str = Field(..., max_length=50, description="县/区")
    village: Optional[str] = Field(None, max_length=100, description="村庄（可选）")
    
    # ✅ Pydantic v2 使用 field_validator
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """验证手机号格式"""
        if not v.isdigit():
            raise ValueError('手机号只能包含数字')
        if not v.startswith('1'):
            raise ValueError('手机号必须以1开头')
        if len(v) != 11:
            raise ValueError('手机号必须是11位')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码强度"""
        if len(v) < 6:
            raise ValueError('密码长度不能少于6位')
        if len(v) > 50:
            raise ValueError('密码长度不能超过50位')
        # 可选：添加更严格的密码策略
        # if not any(char.isdigit() for char in v):
        #     raise ValueError('密码必须包含至少一个数字')
        # if not any(char.isalpha() for char in v):
        #     raise ValueError('密码必须包含至少一个字母')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "张三",
                "phone": "13800138000",
                "password": "secure123",
                "email": "zhangsan@example.com",
                "province": "山西省",
                "city": "临汾市",
                "county": "蒲县",
                "village": "被子垣村"
            }
        }


class FarmerLoginRequest(BaseModel):
    """农户登录请求"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """验证手机号格式"""
        if not v.isdigit() or len(v) != 11:
            raise ValueError('手机号格式错误')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone": "13800138000",
                "password": "demo123456"
            }
        }


class FarmerUpdateRequest(BaseModel):
    """农户信息更新请求"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    province: Optional[str] = Field(None, max_length=50)
    city: Optional[str] = Field(None, max_length=50)
    county: Optional[str] = Field(None, max_length=50)
    village: Optional[str] = Field(None, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "新名称",
                "email": "newemail@example.com",
                "village": "新村庄"
            }
        }


class PasswordChangeRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")
    confirm_password: str = Field(..., description="确认新密码")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """验证新密码强度"""
        if len(v) < 6:
            raise ValueError('新密码长度不能少于6位')
        return v
    
    # ✅ Pydantic v2 使用 model_validator 进行模型级验证
    @model_validator(mode='after')
    def validate_passwords_match(self):
        """验证两次输入的新密码是否一致"""
        if self.new_password != self.confirm_password:
            raise ValueError('两次输入的新密码不一致')
        if self.old_password == self.new_password:
            raise ValueError('新密码不能与旧密码相同')
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "oldpass123",
                "new_password": "newpass456",
                "confirm_password": "newpass456"
            }
        }


# ==================== 响应Schema ====================

class FarmerResponse(BaseModel):
    """农户信息响应"""
    id: str
    name: str
    phone: str
    email: Optional[str] = None
    
    # 地址信息
    province: str
    city: str
    county: str
    village: Optional[str] = None
    
    # 认证信息
    is_verified: bool
    certification_type: Optional[str] = None
    
    # 订阅信息
    tier: FarmerTierEnum
    services_count: int
    api_calls_today: int
    
    # 佣金设置
    enable_commission: bool
    commission_rate: int
    
    # 时间戳
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra = {
            "example": {
                "id": "farmer_puzhou_001",
                "name": "被子垣果园",
                "phone": "13800138000",
                "email": "biziyuan@example.com",
                "province": "山西省",
                "city": "临汾市",
                "county": "蒲县",
                "village": "被子垣村",
                "is_verified": True,
                "certification_type": "中国农大科技小院认证",
                "tier": "basic",
                "services_count": 3,
                "api_calls_today": 45,
                "enable_commission": False,
                "commission_rate": 5,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T12:30:00Z"
            }
        })


class FarmerLoginResponse(BaseModel):
    """登录响应"""
    access_token: str = Field(..., description="JWT访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    farmer: FarmerResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "farmer": {
                    "id": "farmer_puzhou_001",
                    "name": "被子垣果园",
                    "phone": "13800138000",
                    "tier": "basic"
                }
            }
        }


class FarmerQuotaResponse(BaseModel):
    """配额信息响应"""
    tier: FarmerTierEnum
    services_count: int
    max_services: int
    api_calls_today: int
    max_requests_per_day: int
    remaining_services: int
    remaining_requests: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "tier": "basic",
                "services_count": 3,
                "max_services": 10,
                "api_calls_today": 45,
                "max_requests_per_day": 1000,
                "remaining_services": 7,
                "remaining_requests": 955
            }
        }


class FarmerStatsResponse(BaseModel):
    """农户统计信息响应"""
    total_orders: int
    total_revenue: float
    total_services: int
    total_api_calls: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_orders": 128,
                "total_revenue": 15680.50,
                "total_services": 5,
                "total_api_calls": 3456
            }
        }
