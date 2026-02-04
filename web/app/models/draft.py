"""
草稿数据模型
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text

from app.database import Base


class Draft(Base):
    """草稿表"""
    __tablename__ = "drafts"

    id = Column(String(32), primary_key=True, index=True)
    invoice_ids = Column(Text, nullable=False, comment="发票ID列表(JSON)")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
