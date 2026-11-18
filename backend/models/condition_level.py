from . import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, DateTime, func
from datetime import datetime


class ConditionLevel(Base):
    """商品成色字典表；表名避开 MySQL 保留字 condition。"""
    __tablename__ = 'condition_levels'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default='0')
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
