"""
SQLAlchemy基础模型类
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from datetime import datetime, timezone

Base = declarative_base()


class TimestampMixin:
    """时间戳Mixin"""
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
