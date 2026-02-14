"""
客户数据模型
"""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from backend.models.base import Base, TimestampMixin


class Customer(Base, TimestampMixin):
    """客户表"""
    __tablename__ = "customers"
    
    id = Column(String(50), primary_key=True)
    farmer_id = Column(String(50), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 基本信息
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False, index=True)
    email = Column(String(100))
    avatar = Column(String(500))
    
    # 地址信息
    province = Column(String(50))
    city = Column(String(50))
    district = Column(String(50))
    address = Column(Text)
    
    # 客户等级
    level = Column(String(20), default="普通客户")  # 普通客户、VIP客户、黄金客户等
    
    # 统计信息
    total_orders = Column(Integer, default=0)
    total_amount = Column(Float, default=0.0)
    
    # 标签
    tags = Column(JSON, default=list)
    
    # 备注
    remark = Column(Text)
    
    # 最后下单时间
    last_order_at = Column(DateTime)
    
    # 关联
    farmer = relationship("Farmer", back_populates="customers")
    
    def __repr__(self):
        return f"<Customer(id={self.id}, name={self.name}, phone={self.phone})>"

