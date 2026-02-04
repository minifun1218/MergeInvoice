"""
草稿视图
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ApiResponse, DraftCreate, DraftResponse
from app.services import DraftService

router = APIRouter(prefix="/drafts")


@router.post("", response_model=ApiResponse[DraftResponse])
async def save_draft(
    request: DraftCreate,
    db: Session = Depends(get_db),
):
    """保存草稿"""
    draft_id = DraftService.save(db, request.invoice_ids)

    return ApiResponse(
        code=0,
        message="草稿保存成功",
        data=DraftResponse(draftId=draft_id)
    )
