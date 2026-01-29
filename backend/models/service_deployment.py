from sqlalchemy import Column, String, Integer, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.models.base import Base

class ServiceDeployment(Base):
    """服务部署历史记录表"""
    __tablename__ = "service_deployments"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(String(50), ForeignKey("mcp_services.id", ondelete="CASCADE"), nullable=False)
    farmer_id = Column(String(50), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String(200), nullable=False)
    product_category = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    origin = Column(String(100))
    stock = Column(Integer, nullable=False)
    description = Column(Text)
    certifications = Column(JSON)
    deployed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 关联到服务和农户
    service = relationship("MCPService")
    farmer = relationship("Farmer")
