"""
视图层 (View) - API路由
"""
from fastapi import APIRouter

from app.views.invoice_view import router as invoice_router
from app.views.merge_view import router as merge_router
from app.views.draft_view import router as draft_router
from app.views.dashboard_view import router as dashboard_router
from app.views.auth_view import router as auth_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router, tags=["认证"])
api_router.include_router(dashboard_router, tags=["仪表板"])
api_router.include_router(invoice_router, tags=["发票管理"])
api_router.include_router(merge_router, tags=["合并任务"])
api_router.include_router(draft_router, tags=["草稿"])
