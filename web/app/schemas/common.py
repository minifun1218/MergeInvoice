"""
通用响应模式
"""
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")


class PageRequest(BaseModel):
    """分页请求"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100, alias="pageSize")

    class Config:
        populate_by_name = True


class PageResponse(BaseModel, Generic[T]):
    """分页响应"""
    data: List[T]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")

    class Config:
        populate_by_name = True


class ApiResponse(BaseModel, Generic[T]):
    """API统一响应"""
    code: int = 0
    message: str = "success"
    data: Optional[T] = None
