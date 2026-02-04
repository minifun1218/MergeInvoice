"""
数据验证层 (Template/Schema)
"""
from app.schemas.common import ApiResponse, PageRequest, PageResponse
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    DashboardStats,
)
from app.schemas.merge_task import (
    MergeTaskCreate,
    MergeTaskResponse,
)
from app.schemas.draft import DraftCreate, DraftResponse

__all__ = [
    "ApiResponse",
    "PageRequest",
    "PageResponse",
    "InvoiceCreate",
    "InvoiceUpdate",
    "InvoiceResponse",
    "DashboardStats",
    "MergeTaskCreate",
    "MergeTaskResponse",
    "DraftCreate",
    "DraftResponse",
]
