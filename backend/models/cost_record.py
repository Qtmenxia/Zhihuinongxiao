"""
成本记录模型
"""
from sqlalchemy import Column, Integer, String, Float, Date, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.models.base import Base


class CostRecord(Base):
    """成本记录模型"""
    
    __tablename__ = "cost_records"
    
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(String(50), ForeignKey("farmers.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True, comment="成本发生日期")
    type = Column(String(50), nullable=False, index=True, comment="成本类型: material/labor/logistics/packaging/other")
    category = Column(String(100), nullable=False, comment="成本项目")
    quantity = Column(Float, nullable=False, default=0, comment="数量/工时")
    unit_price = Column(Float, nullable=False, default=0, comment="单价")
    amount = Column(Float, nullable=False, default=0, comment="总金额")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    farmer = relationship("Farmer", back_populates="cost_records")
    
    # 复合索引
    __table_args__ = (
        Index('idx_farmer_date', 'farmer_id', 'date'),
        Index('idx_farmer_type', 'farmer_id', 'type'),
    )
    
    def __repr__(self):
        return f"<CostRecord(id={self.id}, type={self.type}, amount={self.amount})>"

