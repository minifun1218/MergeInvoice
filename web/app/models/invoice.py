"""
发票数据模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Enum
import enum

from app.database import Base


class InvoiceStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REVIEWING = "reviewing"
    FAILED = "failed"


class InvoiceType(str, enum.Enum):
    VAT_SPECIAL = "vat_special"
    VAT_NORMAL = "vat_normal"
    FLIGHT = "flight"
    TAXI = "taxi"
    HOTEL = "hotel"
    OTHER = "other"


class FileType(str, enum.Enum):
    PDF = "pdf"
    JPG = "jpg"
    PNG = "png"
    OFD = "ofd"


class Invoice(Base):
    """发票表"""
    __tablename__ = "invoices"

    id = Column(String(32), primary_key=True, index=True)
    code = Column(String(50), nullable=False, comment="发票代码")
    number = Column(String(50), nullable=False, comment="发票号码")
    type = Column(String(20), default=InvoiceType.OTHER.value, comment="发票类型")
    seller_name = Column(String(200), nullable=False, comment="销方名称")
    buyer_name = Column(String(200), nullable=False, comment="购方名称")
    date = Column(String(20), nullable=False, comment="开票日期")
    amount = Column(Float, default=0.0, comment="金额(不含税)")
    tax_amount = Column(Float, default=0.0, comment="税额")
    total_amount = Column(Float, default=0.0, comment="价税合计")
    status = Column(String(20), default=InvoiceStatus.PENDING.value, comment="状态")
    file_url = Column(String(500), nullable=True, comment="原始文件URL")
    file_type = Column(String(10), default=FileType.PDF.value, comment="文件类型")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
