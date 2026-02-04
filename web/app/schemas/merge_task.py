"""
合并任务相关Schema
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class MergeTaskCreate(BaseModel):
    """创建合并任务"""
    invoice_ids: List[str] = Field(alias="invoiceIds")
    output_type: str = Field(default="pdf", alias="outputType")

    class Config:
        populate_by_name = True


class MergeTaskResponse(BaseModel):
    """合并任务响应"""
    id: str
    invoice_ids: List[str] = Field(alias="invoiceIds")
    status: str
    output_type: str = Field(alias="outputType")
    total_pages: int = Field(alias="totalPages")
    total_amount: float = Field(alias="totalAmount")
    created_at: str = Field(alias="createdAt")
    download_url: Optional[str] = Field(None, alias="downloadUrl")

    class Config:
        populate_by_name = True
        from_attributes = True
