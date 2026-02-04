"""
发票视图
"""
from typing import Optional, List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ApiResponse, PageResponse, InvoiceResponse
from app.services import InvoiceService
from app.utils.file_utils import validate_file_type, validate_file_size

router = APIRouter(prefix="/invoices")


@router.get("", response_model=ApiResponse[PageResponse[InvoiceResponse]])
async def get_invoice_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """获取发票列表"""
    invoices, total = InvoiceService.get_list(db, page, pageSize, status, keyword)
    data = [InvoiceService.to_response(inv) for inv in invoices]

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


@router.get("/{invoice_id}", response_model=ApiResponse[InvoiceResponse])
async def get_invoice_detail(invoice_id: str, db: Session = Depends(get_db)):
    """获取发票详情"""
    invoice = InvoiceService.get_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="发票不存在")

    return ApiResponse(
        code=0,
        message="success",
        data=InvoiceService.to_response(invoice)
    )


@router.post("/upload", response_model=ApiResponse[InvoiceResponse])
async def upload_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """上传单个发票文件"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    if not validate_file_type(file.content_type or ""):
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    content = await file.read()

    if not validate_file_size(len(content)):
        raise HTTPException(status_code=400, detail="文件大小超过10MB限制")

    invoice = await InvoiceService.create_from_file(db, content, file.filename)

    return ApiResponse(
        code=0,
        message="上传成功",
        data=InvoiceService.to_response(invoice)
    )


@router.post("/batch-upload", response_model=ApiResponse[List[InvoiceResponse]])
async def batch_upload_invoices(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """批量上传发票文件"""
    if not files:
        raise HTTPException(status_code=400, detail="请选择要上传的文件")

    invoices = []
    for file in files:
        if not file.filename:
            continue

        if not validate_file_type(file.content_type or ""):
            continue

        content = await file.read()
        if not validate_file_size(len(content)):
            continue

        invoice = await InvoiceService.create_from_file(db, content, file.filename)
        invoices.append(InvoiceService.to_response(invoice))

    return ApiResponse(
        code=0,
        message=f"成功上传 {len(invoices)} 个文件",
        data=invoices
    )


@router.delete("/{invoice_id}", response_model=ApiResponse[None])
async def delete_invoice(invoice_id: str, db: Session = Depends(get_db)):
    """删除发票"""
    success = InvoiceService.delete(db, invoice_id)
    if not success:
        raise HTTPException(status_code=404, detail="发票不存在")

    return ApiResponse(code=0, message="删除成功", data=None)
