"""
发票视图
"""
from typing import Optional, List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.invoice import Invoice
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


@router.delete("", response_model=ApiResponse[None])
async def delete_all_invoices(db: Session = Depends(get_db)):
    """删除所有发票（清空数据库）"""
    try:
        from app.models.invoice import Invoice
        # 删除所有发票记录
        deleted_count = db.query(Invoice).delete()
        db.commit()
        print(f"✅ 已清空所有发票，共删除 {deleted_count} 条记录")
        return ApiResponse(code=0, message=f"成功清空 {deleted_count} 条发票记录", data=None)
    except Exception as e:
        db.rollback()
        print(f"❌ 清空发票失败: {e}")
        raise HTTPException(status_code=500, detail="清空失败")


@router.post("/upload-and-merge", response_model=ApiResponse[dict])
async def upload_and_merge(
    files: List[UploadFile] = File(...),
    layout: str = Query("2x1", description="布局方式: 1x1, 2x1, 2x2"),
    db: Session = Depends(get_db),
):
    """批量上传发票并自动合并为PDF"""
    if not files:
        raise HTTPException(status_code=400, detail="请选择要上传的文件")

    print(f"📤 开始上传并合并 {len(files)} 个发票文件，布局: {layout}")

    # 1. 上传并识别所有发票
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
        invoices.append(invoice)

    if not invoices:
        raise HTTPException(status_code=400, detail="没有有效的发票文件")

    print(f"✅ 成功识别 {len(invoices)} 个发票")

    # 2. 获取数据库中所有发票（包括之前的和新上传的）
    all_invoices = db.query(Invoice).order_by(Invoice.created_at.asc()).all()
    all_invoice_ids = [inv.id for inv in all_invoices]

    print(f"📋 数据库中总发票数: {len(all_invoices)}")
    print(f"📋 本次新增: {len(invoices)}, 总计: {len(all_invoices)}")

    # 3. 自动调用合并服务生成2x1布局PDF（合并所有发票）
    try:
        from app.services.merge_service import MergeService
        from app.services.minio_service import MinioService

        print(f"🔄 开始合并所有发票，布局: {layout}")

        # 调用合并服务（合并所有发票，不仅仅是新上传的）
        pdf_bytes, page_count = await MergeService.merge_invoices_direct(
            db=db,
            invoice_ids=all_invoice_ids,  # 使用所有发票ID
            layout=layout
        )

        # 上传合并后的PDF到MinIO
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        merged_filename = f"merged_{timestamp}.pdf"
        object_name = MinioService.generate_object_name(merged_filename, prefix="merged")

        MinioService.upload_file(pdf_bytes, object_name, "application/pdf")
        merged_pdf_url = MinioService.get_file_url(object_name, expires=604800)

        print(f"✅ 合并完成，共 {page_count} 页，URL: {merged_pdf_url}")

        # 3. 返回所有发票列表（包括之前的和新上传的）和合并后的PDF URL
        all_invoice_responses = [InvoiceService.to_response(inv) for inv in all_invoices]

        return ApiResponse(
            code=0,
            message=f"成功上传 {len(invoices)} 个新发票，当前共 {len(all_invoices)} 个",
            data={
                "invoices": all_invoice_responses,  # ✅ 返回所有发票
                "mergedPdfUrl": merged_pdf_url,
                "totalPages": page_count,
                "layout": layout
            }
        )

    except Exception as e:
        print(f"❌ 合并失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"合并失败: {str(e)}")
