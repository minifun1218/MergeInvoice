"""
合并任务视图
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ApiResponse, PageResponse, MergeTaskCreate, MergeTaskResponse
from app.services import MergeService

router = APIRouter(prefix="/merge-tasks")


@router.post("", response_model=ApiResponse[MergeTaskResponse])
async def create_merge_task(
    request: MergeTaskCreate,
    db: Session = Depends(get_db),
):
    """创建合并任务"""
    if not request.invoice_ids:
        raise HTTPException(status_code=400, detail="请选择要合并的发票")

    task = await MergeService.create_task(db, request.invoice_ids, request.output_type)

    return ApiResponse(
        code=0,
        message="合并任务创建成功",
        data=MergeService.to_response(task)
    )


@router.get("/{task_id}", response_model=ApiResponse[MergeTaskResponse])
async def get_merge_task_detail(task_id: str, db: Session = Depends(get_db)):
    """获取合并任务详情"""
    task = MergeService.get_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return ApiResponse(
        code=0,
        message="success",
        data=MergeService.to_response(task)
    )


@router.get("", response_model=ApiResponse[PageResponse[MergeTaskResponse]])
async def get_merge_task_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取合并任务列表"""
    tasks, total = MergeService.get_list(db, page, pageSize)
    data = [MergeService.to_response(task) for task in tasks]

    return ApiResponse(
        code=0,
        message="success",
        data=PageResponse(
            data=data,
            total=total,
            page=page,
            pageSize=pageSize,
        )
    )


@router.get("/{task_id}/download")
async def download_merged_file(task_id: str, db: Session = Depends(get_db)):
    """下载合并后的文件 (重定向到 MinIO URL)"""
    download_url = MergeService.get_download_url(db, task_id)
    if not download_url:
        raise HTTPException(status_code=404, detail="文件不存在或任务未完成")

    return RedirectResponse(url=download_url)
