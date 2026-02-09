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
        layout: str = "2x1",
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
                        # 从URL提取object_name（处理预签名URL的查询参数）
                        url_without_query = inv.file_url.split("?")[0]  # 去掉查询参数
                        object_name = "/".join(url_without_query.split("/")[-2:])
                        content = MinioService.download_file(object_name)
                        file_contents.append({
                            "content": content,
                            "type": inv.file_type,
                            "name": f"{inv.id}.{inv.file_type}"
                        })
                    except Exception as e:
                        print(f"下载文件失败 {inv.id}: {e}")
                        continue

            if output_type == OutputType.PDF.value:
                # 传递布局参数到PDF生成
                output_data, total_pages = MergeService._merge_to_pdf(file_contents, layout)
                object_name = f"merged/merged_{task_id}.pdf"
                content_type = "application/pdf"
            else:
                output_data, total_pages = MergeService._merge_to_zip(file_contents)
                object_name = f"merged/merged_{task_id}.zip"
                content_type = "application/zip"

            # 上传合并后的文件到 MinIO
            MinioService.upload_file(output_data, object_name, content_type)
            # 使用预签名URL（7天有效期）
            download_url = MinioService.get_file_url(object_name, expires=604800)

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
    async def merge_invoices_direct(
        db: Session,
        invoice_ids: List[str],
        layout: str = "2x1"
    ) -> Tuple[bytes, int]:
        """直接合并发票为PDF（不创建任务记录）"""
        invoices = db.query(Invoice).filter(Invoice.id.in_(invoice_ids)).all()

        # 从 MinIO 下载文件
        file_contents = []
        for inv in invoices:
            if inv.file_url:
                try:
                    # 从URL提取object_name（处理预签名URL的查询参数）
                    url_without_query = inv.file_url.split("?")[0]  # 去掉查询参数
                    object_name = "/".join(url_without_query.split("/")[-2:])
                    content = MinioService.download_file(object_name)
                    file_contents.append({
                        "content": content,
                        "type": inv.file_type,
                        "name": f"{inv.id}.{inv.file_type}"
                    })
                except Exception as e:
                    print(f"下载文件失败 {inv.id}: {e}")
                    continue

        # 合并为PDF
        pdf_bytes, page_count = MergeService._merge_with_layout(file_contents, layout)
        return pdf_bytes, page_count

    @staticmethod
    def _merge_to_pdf(file_contents: List[dict], layout: str = "2x1") -> tuple[bytes, int]:
        """合并为PDF（支持自定义布局）"""
        # 统一使用布局方式处理所有类型的发票（包括PDF和图片）
        return MergeService._merge_with_layout(file_contents, layout)

    @staticmethod
    def _merge_with_layout(file_contents: List[dict], layout: str = "2x1") -> tuple[bytes, int]:
        """统一合并所有类型发票（PDF和图片）为带布局的PDF"""
        from PIL import Image

        output = io.BytesIO()
        c = canvas.Canvas(output, pagesize=A4)
        width, height = A4

        # 根据布局计算行列
        if layout == "1x1":
            rows, cols = 1, 1
        elif layout == "2x1":
            rows, cols = 2, 1
        elif layout == "2x2":
            rows, cols = 2, 2
        else:
            rows, cols = 2, 1  # 默认2x1

        per_page = rows * cols  # 每页发票数
        margin = 10 * mm
        gap = 5 * mm

        # 计算每个发票格子的宽高
        img_width = (width - 2 * margin - gap * (cols - 1)) / cols
        img_height = (height - 2 * margin - gap * (rows - 1)) / rows

        page_count = 0

        # 处理每个发票文件
        for i, file_data in enumerate(file_contents):
            # 每页开始时（除了第一个）
            if i > 0 and i % per_page == 0:
                c.showPage()

            # 计算当前发票在页面中的位置
            position_in_page = i % per_page
            row = position_in_page // cols
            col = position_in_page % cols

            # 计算x, y坐标（注意PDF坐标系原点在左下角）
            x = margin + col * (img_width + gap)
            y = height - margin - (row + 1) * img_height - row * gap

            try:
                # 判断文件类型
                if file_data["type"] == "pdf":
                    # PDF 转为图片（使用 pypdf + reportlab）
                    img = MergeService._pdf_to_image(file_data["content"])
                else:
                    # 直接加载图片
                    img = Image.open(io.BytesIO(file_data["content"]))

                if img:
                    # 转换为临时文件供reportlab使用
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format='PNG')
                    img_buffer.seek(0)

                    from reportlab.lib.utils import ImageReader
                    img_reader = ImageReader(img_buffer)

                    c.drawImage(
                        img_reader, x, y,
                        width=img_width, height=img_height,
                        preserveAspectRatio=True, anchor='c'
                    )
                else:
                    raise Exception("图片转换失败")

            except Exception as e:
                print(f"绘制发票失败 {i}: {e}")
                # 绘制占位符
                c.setFillColorRGB(0.9, 0.9, 0.9)
                c.rect(x, y, img_width, img_height, fill=1)
                c.setFillColorRGB(0.5, 0.5, 0.5)
                c.drawCentredString(x + img_width / 2, y + img_height / 2, f"发票 {i + 1}")

            # 计算总页数
            if (i + 1) % per_page == 0 or i == len(file_contents) - 1:
                page_count += 1

        c.save()
        return output.getvalue(), page_count

    @staticmethod
    def _pdf_to_image(pdf_content: bytes):
        """将PDF第一页转换为图片（使用 pypdf 渲染）"""
        try:
            from PIL import Image
            from pypdf import PdfReader
            import fitz  # PyMuPDF

            # 使用 PyMuPDF (fitz) 渲染 PDF
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            page = pdf_document[0]  # 获取第一页

            # 渲染为图片（300 DPI 高清）
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))

            # 转换为 PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            pdf_document.close()

            return img
        except ImportError:
            # 如果没有安装 PyMuPDF，使用简化方案
            print("PyMuPDF 未安装，使用占位符")
            return None
        except Exception as e:
            print(f"PDF转图片失败: {e}")
            return None

    @staticmethod
    def _merge_pdfs(pdf_files: List[dict]) -> tuple[bytes, int]:
        """直接合并PDF文件（不使用布局，已废弃）"""
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
    def _images_to_pdf(file_contents: List[dict], layout: str = "2x1") -> tuple[bytes, int]:
        """图片合并为PDF（支持自定义行列布局）"""
        output = io.BytesIO()
        c = canvas.Canvas(output, pagesize=A4)
        width, height = A4

        # 根据布局计算行列
        if layout == "1x1":
            rows, cols = 1, 1
        elif layout == "2x1":
            rows, cols = 2, 1
        elif layout == "2x2":
            rows, cols = 2, 2
        else:
            rows, cols = 2, 1  # 默认2x1

        per_page = rows * cols  # 每页发票数
        margin = 10 * mm
        gap = 5 * mm

        # 计算每个发票格子的宽高
        img_width = (width - 2 * margin - gap * (cols - 1)) / cols
        img_height = (height - 2 * margin - gap * (rows - 1)) / rows

        page_count = 0
        for i, file_data in enumerate(file_contents):
            # 每页开始时（除了第一个）
            if i > 0 and i % per_page == 0:
                c.showPage()

            # 计算当前发票在页面中的位置
            position_in_page = i % per_page
            row = position_in_page // cols
            col = position_in_page % cols

            # 计算x, y坐标（注意PDF坐标系原点在左下角）
            x = margin + col * (img_width + gap)
            y = height - margin - (row + 1) * img_height - row * gap

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
                    img_reader, x, y,
                    width=img_width, height=img_height,
                    preserveAspectRatio=True, anchor='c'
                )
            except Exception as e:
                print(f"绘制图片失败: {e}")
                # 绘制占位符
                c.setFillColorRGB(0.9, 0.9, 0.9)
                c.rect(x, y, img_width, img_height, fill=1)
                c.setFillColorRGB(0.5, 0.5, 0.5)
                c.drawCentredString(x + img_width / 2, y + img_height / 2, f"发票 {i + 1}")

            # 计算总页数
            if (i + 1) % per_page == 0 or i == len(file_contents) - 1:
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
