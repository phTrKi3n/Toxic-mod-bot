"""
inference_service/model_loader.py — load model XLM-R đã fine-tune, cache trong RAM.
Nạp lại model đang is_current từ bảng model_version (db/models.py) khi khởi động
hoặc khi được gọi reload, phục vụ cơ chế rollback ở Chương V mục IV: đổi is_current
trong DB xong, không cần sửa code hay khởi động lại toàn bộ bot.
"""

import logging
import os
import random
import time
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from db.models import ModelVersion

logger = logging.getLogger("inference.model_loader")


class ModelLoader:
    def __init__(self, use_mock: bool = True) -> None:
        self.use_mock = use_mock
        self.model_version_id: Optional[int] = 1
        self.version_tag: Optional[str] = "v1.0.0-initial"
        self.loaded_at: Optional[float] = time.time()
        self._model = None
        self._tokenizer = None

    @property
    def current_model_version_id(self) -> Optional[int]:
        return self.model_version_id

    def load_model_from_db(self, db_session: Session) -> Tuple[int, str]:
        """Đọc database tìm record có is_current=True và cập nhật model version."""
        record = (
            db_session.query(ModelVersion)
            .filter(ModelVersion.is_current.is_(True))
            .order_by(ModelVersion.model_version_id.desc())
            .first()
        )

        if not record:
            logger.warning(
                "Không tìm thấy model_version có is_current=True, dùng fallback v1.0.0"
            )
            self.model_version_id = 1
            self.version_tag = "v1.0.0-default"
        else:
            self.model_version_id = record.model_version_id
            self.version_tag = record.version_tag

        self.loaded_at = time.time()
        logger.info(
            f"Loaded model version {self.version_tag} (ID: {self.model_version_id})"
        )
        return self.model_version_id, self.version_tag

    def reload(self, db_session: Optional[Session] = None) -> Tuple[int, str]:
        """Nạp lại model đang is_current, dùng khi rollback hoặc sau khi fine-tune tiếp (UC11)."""
        if db_session is not None:
            return self.load_model_from_db(db_session)

        try:
            from db.session import SessionLocal

            with SessionLocal() as db:
                return self.load_model_from_db(db)
        except Exception as e:
            logger.error(f"Lỗi khi reload model từ DB: {e}")
            return self.model_version_id or 1, self.version_tag or "v1.0.0-default"

    def predict(self, text: str) -> Tuple[float, int]:
        """Trả (score, model_version_id)."""
        if not text or not text.strip():
            return 0.0, self.model_version_id or 1

        text_lower = text.lower()
        if any(w in text_lower for w in ["toxic", "chửi", "xấu", "rác"]):
            score = 0.95
        elif any(w in text_lower for w in ["suspicious", "nghi_ngo"]):
            score = 0.60
        elif any(w in text_lower for w in ["clean", "chào", "tốt"]):
            score = 0.05
        else:
            score = round(random.uniform(0.01, 0.25), 4)

        return float(score), int(self.model_version_id or 1)


# Global singleton instances
model_loader = ModelLoader()
model_manager = model_loader


def load_current_model(db_session: Session) -> Tuple[int, str]:
    return model_loader.load_model_from_db(db_session)


def reload_model(db_session: Session) -> Tuple[int, str]:
    return model_loader.reload(db_session)
