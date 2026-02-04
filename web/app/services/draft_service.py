"""
草稿业务服务
"""
import json
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.draft import Draft


class DraftService:
    """草稿服务"""

    @staticmethod
    def generate_id() -> str:
        """生成唯一ID"""
        return str(uuid.uuid4())[:8]

    @staticmethod
    def save(db: Session, invoice_ids: list) -> str:
        """保存草稿"""
        draft_id = DraftService.generate_id()

        draft = Draft(
            id=draft_id,
            invoice_ids=json.dumps(invoice_ids),
            created_at=datetime.now(),
        )

        db.add(draft)
        db.commit()

        return draft_id

    @staticmethod
    def get_by_id(db: Session, draft_id: str) -> Optional[Draft]:
        """根据ID获取草稿"""
        return db.query(Draft).filter(Draft.id == draft_id).first()
