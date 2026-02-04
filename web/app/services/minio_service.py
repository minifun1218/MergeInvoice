"""
MinIO 对象存储服务
"""
import io
import uuid
from datetime import timedelta
from typing import Optional, BinaryIO
from pathlib import Path

from minio import Minio
from minio.error import S3Error

from app.config import settings


class MinioService:
    """MinIO 存储服务"""

    _client: Optional[Minio] = None

    @classmethod
    def get_client(cls) -> Minio:
        """获取 MinIO 客户端单例"""
        if cls._client is None:
            cls._client = Minio(
                endpoint=settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=settings.minio_secure,
            )
            # 确保 bucket 存在
            cls._ensure_bucket()
        return cls._client

    @classmethod
    def _ensure_bucket(cls):
        """确保存储桶存在"""
        client = cls._client
        bucket_name = settings.minio_bucket_name
        try:
            if not client.bucket_exists(bucket_name):
                client.make_bucket(bucket_name)
                # 设置桶策略为公开读取
                policy = f'''{{
                    "Version": "2012-10-17",
                    "Statement": [
                        {{
                            "Effect": "Allow",
                            "Principal": {{"AWS": ["*"]}},
                            "Action": ["s3:GetObject"],
                            "Resource": ["arn:aws:s3:::{bucket_name}/*"]
                        }}
                    ]
                }}'''
                client.set_bucket_policy(bucket_name, policy)
        except S3Error as e:
            print(f"MinIO bucket error: {e}")

    @staticmethod
    def generate_object_name(filename: str, prefix: str = "uploads") -> str:
        """生成对象名称"""
        ext = Path(filename).suffix.lower()
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}/{unique_id}{ext}"

    @classmethod
    def upload_file(
        cls,
        file_data: bytes,
        object_name: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """上传文件到 MinIO"""
        client = cls.get_client()
        bucket_name = settings.minio_bucket_name

        try:
            client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=io.BytesIO(file_data),
                length=len(file_data),
                content_type=content_type,
            )
            return object_name
        except S3Error as e:
            raise Exception(f"上传文件失败: {e}")

    @classmethod
    def upload_file_stream(
        cls,
        file_stream: BinaryIO,
        object_name: str,
        length: int,
        content_type: str = "application/octet-stream",
    ) -> str:
        """上传文件流到 MinIO"""
        client = cls.get_client()
        bucket_name = settings.minio_bucket_name

        try:
            client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=file_stream,
                length=length,
                content_type=content_type,
            )
            return object_name
        except S3Error as e:
            raise Exception(f"上传文件失败: {e}")

    @classmethod
    def download_file(cls, object_name: str) -> bytes:
        """从 MinIO 下载文件"""
        client = cls.get_client()
        bucket_name = settings.minio_bucket_name

        try:
            response = client.get_object(bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            raise Exception(f"下载文件失败: {e}")

    @classmethod
    def get_file_url(cls, object_name: str, expires: int = 3600) -> str:
        """获取文件的预签名URL"""
        client = cls.get_client()
        bucket_name = settings.minio_bucket_name

        try:
            url = client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=object_name,
                expires=timedelta(seconds=expires),
            )
            return url
        except S3Error as e:
            raise Exception(f"获取文件URL失败: {e}")

    @classmethod
    def get_public_url(cls, object_name: str) -> str:
        """获取公开访问URL (需要桶设置为公开)"""
        protocol = "https" if settings.minio_secure else "http"
        return f"{protocol}://{settings.minio_endpoint}/{settings.minio_bucket_name}/{object_name}"

    @classmethod
    def delete_file(cls, object_name: str) -> bool:
        """删除文件"""
        client = cls.get_client()
        bucket_name = settings.minio_bucket_name

        try:
            client.remove_object(bucket_name, object_name)
            return True
        except S3Error as e:
            print(f"删除文件失败: {e}")
            return False

    @classmethod
    def file_exists(cls, object_name: str) -> bool:
        """检查文件是否存在"""
        client = cls.get_client()
        bucket_name = settings.minio_bucket_name

        try:
            client.stat_object(bucket_name, object_name)
            return True
        except S3Error:
            return False

    @classmethod
    def list_files(cls, prefix: str = "", recursive: bool = True) -> list:
        """列出文件"""
        client = cls.get_client()
        bucket_name = settings.minio_bucket_name

        try:
            objects = client.list_objects(
                bucket_name,
                prefix=prefix,
                recursive=recursive,
            )
            return [obj.object_name for obj in objects]
        except S3Error as e:
            print(f"列出文件失败: {e}")
            return []
