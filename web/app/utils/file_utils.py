"""
文件处理工具
"""
from app.models.invoice import FileType


def get_file_type_from_name(filename: str) -> str:
    """根据文件名获取文件类型"""
    ext = filename.lower().split(".")[-1]
    mapping = {
        "pdf": FileType.PDF.value,
        "jpg": FileType.JPG.value,
        "jpeg": FileType.JPG.value,
        "png": FileType.PNG.value,
        "ofd": FileType.OFD.value,
    }
    return mapping.get(ext, FileType.PDF.value)


def validate_file_type(content_type: str) -> bool:
    """验证文件MIME类型"""
    allowed_types = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/jpg",
    ]
    return content_type in allowed_types


def validate_file_size(size: int, max_size_mb: int = 10) -> bool:
    """验证文件大小"""
    return size <= max_size_mb * 1024 * 1024
