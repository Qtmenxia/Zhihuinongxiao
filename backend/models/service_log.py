"""
服务日志数据模型
"""
from sqlalchemy import Column, String, Float, JSON, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from backend.models.base import Base
from datetime import datetime,timezone


class ServiceLog(Base):
    """服务调用日志表"""
    __tablename__ = "service_logs"
    
    id = Column(String(50), primary_key=True)
    service_id = Column(String(50), ForeignKey("mcp_services.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 调用信息
    tool_name = Column(String(100))
    input_params = Column(JSON)
    output_result = Column(Text)
    
    # 性能指标
    latency = Column(Float)
    status = Column(String(20), index=True)
    error_message = Column(Text)
    
    # 追踪
    request_id = Column(String(50), index=True)
    user_ip = Column(String(50))
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None), nullable=False, index=True)
    
    # 关联
    service = relationship("MCPService", back_populates="logs")
    
    def __repr__(self):
        return f"<ServiceLog(id={self.id}, tool={self.tool_name}, status={self.status})>"
