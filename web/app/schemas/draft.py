"""
草稿相关Schema
"""
from typing import List
from pydantic import BaseModel, Field


class DraftCreate(BaseModel):
    """创建草稿"""
    invoice_ids: List[str] = Field(alias="invoiceIds")

    class Config:
        populate_by_name = True


class DraftResponse(BaseModel):
    """草稿响应"""
    draft_id: str = Field(alias="draftId")

    class Config:
        populate_by_name = True
