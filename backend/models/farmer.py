"""
农户数据模型
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from backend.models.base import Base, TimestampMixin
import enum
from datetime import datetime


class FarmerTier(str, enum.Enum):
    """农户订阅等级"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"


class Farmer(Base, TimestampMixin):
    """农户表"""
    __tablename__ = "farmers"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    email = Column(String(100))
    
    # 地址信息
    province = Column(String(50))
    city = Column(String(50))
    county = Column(String(50), index=True)
    village = Column(String(100))
    
    # 认证信息
    is_verified = Column(Boolean, default=False)
    certification_type = Column(String(50))
    certification_doc = Column(String(500))
    
    # 订阅信息
    tier = Column(SQLEnum(FarmerTier), default=FarmerTier.FREE, nullable=False)
    subscription_start = Column(DateTime)
    subscription_end = Column(DateTime)
    
    # 额度控制
    services_count = Column(Integer, default=0)
    api_calls_today = Column(Integer, default=0)
    
    # 财务设置
    enable_commission = Column(Boolean, default=False)
    commission_rate = Column(Integer, default=5)
    
    # 关联关系
    products = relationship("Product", back_populates="farmer", cascade="all, delete-orphan")
    services = relationship("MCPService", back_populates="farmer", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="farmer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Farmer(id={self.id}, name={self.name}, tier={self.tier.value})>"
