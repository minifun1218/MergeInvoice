"""
合并任务业务服务
"""
import io
import json
import uuid
import zipfile
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

from app.models.merge_task import MergeTask, MergeTaskStatus, OutputType
from app.models.invoice import Invoice
from app.schemas.merge_task import MergeTaskResponse
from app.services.minio_service import MinioService


class MergeService:
    """合并任务服务"""

    @staticmethod
    def generate_id() -> str:
        """生成唯一ID"""
        return str(uuid.uuid4())[:8]

    @staticmethod
    def get_by_id(db: Session, task_id: str) -> Optional[MergeTask]:
        """根据ID获取任务"""
        return db.query(MergeTask).filter(MergeTask.id == task_id).first()

    @staticmethod
    def get_list(
        db: Session,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[MergeTask], int]:
        """获取任务列表"""
        query = db.query(MergeTask)
        total = query.count()
        tasks = query.order_by(MergeTask.created_at.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()
        return tasks, total

    @staticmethod
    async def create_task(
        db: Session,
        invoice_ids: List[str],
        output_type: str,
    ) -> MergeTask:
        """创建合并任务"""
        task_id = MergeService.generate_id()
        now = datetime.now()

        task = MergeTask(
            id=task_id,
            invoice_ids=json.dumps(invoice_ids),
            status=MergeTaskStatus.PROCESSING.value,
            output_type=output_type,
            total_pages=0,
            total_amount=0.0,
            created_at=now,
        )

        db.add(task)
        db.commit()

        # 执行合并
        try:
            invoices = db.query(Invoice).filter(Invoice.id.in_(invoice_ids)).all()
            total_amount = sum(inv.total_amount for inv in invoices)

            # 从 MinIO 下载文件
            file_contents = []
            for inv in invoices:
                if inv.file_url:
                    try:
                        # 从URL提取object_name
                        object_name = "/".join(inv.file_url.split("/")[-2:])
                        content = MinioService.download_file(object_name)
                        file_contents.append({
                            "content": content,
                            "type": inv.file_type,
                            "name": f"{inv.id}.{inv.file_type}"
                        })
                    except Exception:
                        continue

            if output_type == OutputType.PDF.value:
                output_data, total_pages = MergeService._merge_to_pdf(file_contents)
                object_name = f"merged/merged_{task_id}.pdf"
                content_type = "application/pdf"
            else:
                output_data, total_pages = MergeService._merge_to_zip(file_contents)
                object_name = f"merged/merged_{task_id}.zip"
                content_type = "application/zip"

            # 上传合并后的文件到 MinIO
            MinioService.upload_file(output_data, object_name, content_type)
            download_url = MinioService.get_public_url(object_name)

            task.status = MergeTaskStatus.COMPLETED.value
            task.total_pages = total_pages
            task.total_amount = total_amount
            task.download_url = download_url

        except Exception as e:
            print(f"合并失败: {e}")
            task.status = MergeTaskStatus.FAILED.value

        db.commit()
        db.refresh(task)

        return task

    @staticmethod
    def _merge_to_pdf(file_contents: List[dict]) -> tuple[bytes, int]:
        """合并为PDF"""
        pdf_files = [f for f in file_contents if f["type"] == "pdf"]

        if pdf_files:
            return MergeService._merge_pdfs(pdf_files)
        else:
            return MergeService._images_to_pdf(file_contents)

    @staticmethod
    def _merge_pdfs(pdf_files: List[dict]) -> tuple[bytes, int]:
        """合并PDF文件"""
        writer = PdfWriter()
        total_pages = 0

        for pdf_file in pdf_files:
            try:
                reader = PdfReader(io.BytesIO(pdf_file["content"]))
                for page in reader.pages:
                    writer.add_page(page)
                    total_pages += 1
            except Exception:
                continue

        output = io.BytesIO()
        writer.write(output)
        return output.getvalue(), total_pages

    @staticmethod
    def _images_to_pdf(file_contents: List[dict]) -> tuple[bytes, int]:
        """图片合并为PDF (2合1布局)"""
        output = io.BytesIO()
        c = canvas.Canvas(output, pagesize=A4)
        width, height = A4

        margin = 10 * mm
        gap = 5 * mm
        img_width = width - 2 * margin
        img_height = (height - 2 * margin - gap) / 2

        page_count = 0
        for i, file_data in enumerate(file_contents):
            if i % 2 == 0 and i > 0:
                c.showPage()

            position = i % 2
            y = height - margin - img_height if position == 0 else margin + gap / 2

            try:
                # 从内存加载图片
                from PIL import Image
                img = Image.open(io.BytesIO(file_data["content"]))

                # 转换为临时文件供reportlab使用
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_buffer.seek(0)

                from reportlab.lib.utils import ImageReader
                img_reader = ImageReader(img_buffer)

                c.drawImage(
                    img_reader, margin, y,
                    width=img_width, height=img_height,
                    preserveAspectRatio=True, anchor='c'
                )
            except Exception:
                c.setFillColorRGB(0.9, 0.9, 0.9)
                c.rect(margin, y, img_width, img_height, fill=1)
                c.setFillColorRGB(0.5, 0.5, 0.5)
                c.drawCentredString(width / 2, y + img_height / 2, f"发票 {i + 1}")

            if position == 1 or i == len(file_contents) - 1:
                page_count += 1

        c.save()
        return output.getvalue(), page_count

    @staticmethod
    def _merge_to_zip(file_contents: List[dict]) -> tuple[bytes, int]:
        """打包为ZIP"""
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_data in file_contents:
                zf.writestr(file_data["name"], file_data["content"])
        return output.getvalue(), len(file_contents)

    @staticmethod
    def get_download_url(db: Session, task_id: str) -> Optional[str]:
        """获取下载URL"""
        task = MergeService.get_by_id(db, task_id)
        if not task or task.status != MergeTaskStatus.COMPLETED.value:
            return None
        return task.download_url

    @staticmethod
    def to_response(task: MergeTask) -> MergeTaskResponse:
        """转换为响应对象"""
        return MergeTaskResponse(
            id=task.id,
            invoiceIds=json.loads(task.invoice_ids) if task.invoice_ids else [],
            status=task.status,
            outputType=task.output_type,
            totalPages=task.total_pages,
            totalAmount=task.total_amount,
            createdAt=task.created_at.isoformat() + "Z" if task.created_at else "",
            downloadUrl=task.download_url,
        )
