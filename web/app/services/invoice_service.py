"""
发票业务服务
"""
import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.invoice import Invoice, InvoiceStatus, InvoiceType, FileType
from app.schemas.invoice import InvoiceResponse, DashboardStats
from app.utils.file_utils import get_file_type_from_name
from app.services.minio_service import MinioService


class InvoiceService:
    """发票服务"""

    @staticmethod
    def generate_id() -> str:
        """生成唯一ID"""
        return str(uuid.uuid4())[:8]

    @staticmethod
    def get_by_id(db: Session, invoice_id: str) -> Optional[Invoice]:
        """根据ID获取发票"""
        return db.query(Invoice).filter(Invoice.id == invoice_id).first()

    @staticmethod
    def get_list(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> Tuple[List[Invoice], int]:
        """获取发票列表"""
        query = db.query(Invoice)

        if status:
            query = query.filter(Invoice.status == status)
        if keyword:
            query = query.filter(
                (Invoice.seller_name.contains(keyword)) |
                (Invoice.number.contains(keyword))
            )

        total = query.count()
        invoices = query.order_by(Invoice.created_at.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        return invoices, total

    @staticmethod
    def get_content_type(filename: str) -> str:
        """根据文件名获取MIME类型"""
        ext = filename.lower().split(".")[-1]
        content_types = {
            "pdf": "application/pdf",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
        }
        return content_types.get(ext, "application/octet-stream")

    @staticmethod
    async def create_from_file(db: Session, file_content: bytes, filename: str) -> Invoice:
        """从文件创建发票"""
        invoice_id = InvoiceService.generate_id()

        # 上传到 MinIO
        object_name = MinioService.generate_object_name(filename, prefix="invoices")
        content_type = InvoiceService.get_content_type(filename)
        MinioService.upload_file(file_content, object_name, content_type)

        # 获取访问URL
        file_url = MinioService.get_public_url(object_name)

        now = datetime.now()

        # 创建发票记录 (模拟OCR识别)
        invoice = Invoice(
            id=invoice_id,
            code=f"0440019{str(uuid.uuid4().int)[:5]}",
            number=str(uuid.uuid4().int)[:8],
            type=InvoiceType.OTHER.value,
            seller_name="待识别商户",
            buyer_name="待识别购方",
            date=now.strftime("%Y-%m-%d"),
            amount=0.0,
            tax_amount=0.0,
            total_amount=0.0,
            status=InvoiceStatus.PENDING.value,
            file_url=file_url,
            file_type=get_file_type_from_name(filename),
            created_at=now,
            updated_at=now,
        )

        db.add(invoice)
        db.commit()
        db.refresh(invoice)

        return invoice

    @staticmethod
    def delete(db: Session, invoice_id: str) -> bool:
        """删除发票"""
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if invoice:
            # 从 MinIO 删除文件
            if invoice.file_url:
                try:
                    # 从URL提取object_name
                    object_name = "/".join(invoice.file_url.split("/")[-2:])
                    MinioService.delete_file(object_name)
                except Exception:
                    pass

            db.delete(invoice)
            db.commit()
            return True
        return False

    @staticmethod
    def get_dashboard_stats(db: Session) -> DashboardStats:
        """获取仪表板统计"""
        total = db.query(Invoice).count()
        pending = db.query(Invoice).filter(
            Invoice.status == InvoiceStatus.PENDING.value
        ).count()

        # 计算总金额
        from sqlalchemy import func
        total_amount = db.query(func.sum(Invoice.total_amount)).scalar() or 0

        return DashboardStats(
            processedCount=total,
            processedChange=12.5,
            pendingCount=pending,
            pendingChange=-5.0,
            savedTax=total_amount * 0.13,
            savedChange=8.3,
        )

    @staticmethod
    def to_response(invoice: Invoice) -> InvoiceResponse:
        """转换为响应对象"""
        return InvoiceResponse(
            id=invoice.id,
            code=invoice.code,
            number=invoice.number,
            type=invoice.type,
            sellerName=invoice.seller_name,
            buyerName=invoice.buyer_name,
            date=invoice.date,
            amount=invoice.amount,
            taxAmount=invoice.tax_amount,
            totalAmount=invoice.total_amount,
            status=invoice.status,
            fileUrl=invoice.file_url,
            fileType=invoice.file_type,
            createdAt=invoice.created_at.isoformat() + "Z" if invoice.created_at else "",
            updatedAt=invoice.updated_at.isoformat() + "Z" if invoice.updated_at else "",
        )
