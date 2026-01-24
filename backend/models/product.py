"""
产品数据模型
"""
from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from backend.models.base import Base, TimestampMixin


class Product(Base, TimestampMixin):
    """产品表"""
    __tablename__ = "products"
    
    id = Column(String(50), primary_key=True)
    farmer_id = Column(String(50), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 基础信息
    name = Column(String(200), nullable=False, index=True)
    sku_code = Column(String(50), unique=True, nullable=False, index=True)
    category = Column(String(100), index=True)
    
    # 规格与定价
    specs = Column(JSON)
    price = Column(Float, nullable=False)
    original_price = Column(Float)
    
    # 库存管理
    stock = Column(Integer, default=0)
    stock_alert_threshold = Column(Integer, default=10)
    
    # 营销信息
    target_scene = Column(String(100))
    packaging_type = Column(String(50))
    selling_points = Column(JSON)
    
    # 媒体资源
    images = Column(JSON)
    video_url = Column(String(500))
    
    # 溯源信息
    origin_info = Column(JSON)
    
    # 描述
    description = Column(Text)
    
    # 状态
    is_active = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False)
    
    # 关联
    farmer = relationship("Farmer", back_populates="products")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, sku={self.sku_code})>"
