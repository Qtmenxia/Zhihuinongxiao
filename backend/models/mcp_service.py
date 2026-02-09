"""
MCP服务数据模型
"""
from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, Text, Enum as SQLEnum, Boolean, DateTime
from sqlalchemy.orm import relationship
from backend.models.base import Base, TimestampMixin
import enum
from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, Enum, JSON
from datetime import datetime, timezone

from backend.models.base import Base


class ServiceStatus(str, enum.Enum):
    """服务状态"""
    PENDING = "PENDING"
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DEPLOYED = "DEPLOYED"


class MCPService(Base, TimestampMixin):
    """MCP服务表"""
    __tablename__ = "mcp_services"
    
    id = Column(String(50), primary_key=True)
    farmer_id = Column(String(50), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 基础信息
    name = Column(String(200), index=True)
    description = Column(Text)
    original_requirement = Column(Text, nullable=False)
    
    # 生成信息
    model_used = Column(String(50))
    status = Column(SQLEnum(ServiceStatus), default=ServiceStatus.GENERATING, nullable=False, index=True)
    
    # 代码与文件
    file_path = Column(String(500))
    code = Column(Text)
    readme = Column(Text)
    requirements = Column(Text)
    
    # 成本与质量
    generation_cost = Column(Float)
    generation_time = Column(Integer)
    quality_score = Column(Float)
    test_pass_rate = Column(Float)
    
    # 部署信息
    is_deployed = Column(Boolean, default=False, index=True)
    deployed_at = Column(DateTime)
    endpoints = Column(JSON)
    deploy_port = Column(Integer)        # 部署端口
    
    # 运行统计
    total_calls = Column(Integer, default=0)
    total_errors = Column(Integer, default=0)
    avg_latency = Column(Float)
    
     # 调用统计
    call_count = Column(Integer, default=0)
    last_called_at = Column(DateTime)

    # 时间戳
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc))
    
    # 优化历史
    refinement_count = Column(Integer, default=0)
    parent_service_id = Column(String(50))
    
    # 关联
    farmer = relationship("Farmer", back_populates="services")
    logs = relationship("ServiceLog", back_populates="service", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MCPService(id={self.id}, name={self.name}, status={self.status.value})>"
