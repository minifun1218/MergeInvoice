"""
发票相关Schema
"""
from typing import Optional
from pydantic import BaseModel, Field


class InvoiceBase(BaseModel):
    """发票基础字段"""
    code: str = Field(description="发票代码")
    number: str = Field(description="发票号码")
    type: str = Field(default="other", description="发票类型")
    seller_name: str = Field(alias="sellerName", description="销方名称")
    buyer_name: str = Field(alias="buyerName", description="购方名称")
    date: str = Field(description="开票日期")
    amount: float = Field(default=0.0, description="金额(不含税)")
    tax_amount: float = Field(default=0.0, alias="taxAmount", description="税额")
    total_amount: float = Field(default=0.0, alias="totalAmount", description="价税合计")

    class Config:
        populate_by_name = True


class InvoiceCreate(InvoiceBase):
    """创建发票"""
    pass


class InvoiceUpdate(BaseModel):
    """更新发票"""
    code: Optional[str] = None
    number: Optional[str] = None
    type: Optional[str] = None
    seller_name: Optional[str] = Field(None, alias="sellerName")
    buyer_name: Optional[str] = Field(None, alias="buyerName")
    date: Optional[str] = None
    amount: Optional[float] = None
    tax_amount: Optional[float] = Field(None, alias="taxAmount")
    total_amount: Optional[float] = Field(None, alias="totalAmount")
    status: Optional[str] = None

    class Config:
        populate_by_name = True


class InvoiceResponse(BaseModel):
    """发票响应"""
    id: str
    code: str
    number: str
    type: str
    seller_name: str = Field(alias="sellerName")
    buyer_name: str = Field(alias="buyerName")
    date: str
    amount: float
    tax_amount: float = Field(alias="taxAmount")
    total_amount: float = Field(alias="totalAmount")
    status: str
    file_url: Optional[str] = Field(None, alias="fileUrl")
    file_type: str = Field(alias="fileType")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class DashboardStats(BaseModel):
    """仪表板统计"""
    processed_count: int = Field(alias="processedCount")
    processed_change: float = Field(alias="processedChange")
    pending_count: int = Field(alias="pendingCount")
    pending_change: float = Field(alias="pendingChange")
    saved_tax: float = Field(alias="savedTax")
    saved_change: float = Field(alias="savedChange")

    class Config:
        populate_by_name = True
