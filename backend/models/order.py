"""
订单数据模型
"""
from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, Enum as SQLEnum, Text, DateTime
from sqlalchemy.orm import relationship
from backend.models.base import Base, TimestampMixin
import enum


class OrderStatus(str, enum.Enum):
    """订单状态"""
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Order(Base, TimestampMixin):
    """订单表"""
    __tablename__ = "orders"
    
    id = Column(String(50), primary_key=True)
    farmer_id = Column(String(50), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(String(50), index=True)
    
    # 订单商品
    items = Column(JSON, nullable=False)
    
    # 金额
    subtotal = Column(Float, nullable=False)
    shipping_fee = Column(Float, default=0)
    discount = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)
    
    # 支付信息
    payment_method = Column(String(50))
    payment_transaction_id = Column(String(100))
    paid_at = Column(DateTime)
    
    # 配送信息
    shipping_address = Column(JSON, nullable=False)
    shipping_method = Column(String(50))
    tracking_number = Column(String(100))
    shipped_at = Column(DateTime)
    
    # 状态
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True)
    
    # 备注
    customer_note = Column(Text)
    farmer_note = Column(Text)
    
    # 完成时间
    completed_at = Column(DateTime)
    
    # 关联
    farmer = relationship("Farmer", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(id={self.id}, status={self.status.value}, total={self.total_amount})>"
