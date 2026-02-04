"""
合并任务数据模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Text
import enum

from app.database import Base


class MergeTaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class OutputType(str, enum.Enum):
    PDF = "pdf"
    ZIP = "zip"


class MergeTask(Base):
    """合并任务表"""
    __tablename__ = "merge_tasks"

    id = Column(String(32), primary_key=True, index=True)
    invoice_ids = Column(Text, nullable=False, comment="发票ID列表(JSON)")
    status = Column(String(20), default=MergeTaskStatus.PENDING.value, comment="状态")
    output_type = Column(String(10), default=OutputType.PDF.value, comment="输出类型")
    total_pages = Column(Integer, default=0, comment="总页数")
    total_amount = Column(Float, default=0.0, comment="总金额")
    download_url = Column(String(500), nullable=True, comment="下载链接")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
