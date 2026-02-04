"""
仪表板视图
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ApiResponse, DashboardStats
from app.services import InvoiceService

router = APIRouter()


@router.get("/dashboard/stats", response_model=ApiResponse[DashboardStats])
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """获取仪表板统计数据"""
    stats = InvoiceService.get_dashboard_stats(db)
    return ApiResponse(code=0, message="success", data=stats)
