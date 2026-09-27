"""
inference_service/model_loader.py — load model XLM-R đã fine-tune, cache trong RAM.
Nạp lại model đang is_current từ bảng model_version (db/models.py) khi khởi động
hoặc khi được gọi reload, phục vụ cơ chế rollback ở Chương V mục IV: đổi is_current
trong DB xong, không cần sửa code hay khởi động lại toàn bộ bot.
"""


import os

import torch
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from db.models import ModelVersion

DEFAULT_MODEL_DIR = "models/xlmr-finetuned"


class ModelLoader:
    def __init__(self) -> None:
        # TODO(DEV): load tokenizer + model XLM-R fine-tune thật ở đây,
        # đọc model_version đang is_current=true từ DB (db/models.py: ModelVersion)
        self.current_model_version_id: int | None = None
        self._model = None
        self._tokenizer = None
        self._load_current()

    def _load_current(self) -> None:
        database_url = os.getenv("DATABASE_URL")
        model_path = DEFAULT_MODEL_DIR

        if database_url:
            try:
                engine = create_engine(database_url)
                with Session(engine) as session:
                    stmt = select(ModelVersion).where(ModelVersion.is_current.is_(True))
                    mv = session.scalars(stmt).first()
                    if mv:
                        self.current_model_version_id = mv.model_version_id
            except Exception:
                pass

        if self.current_model_version_id is None:
            self.current_model_version_id = 1

        if os.path.exists(model_path):
            self._tokenizer = AutoTokenizer.from_pretrained(model_path)
            self._model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self._model.eval()

    def reload(self) -> None:
        """Nạp lại model đang is_current, dùng khi rollback hoặc sau khi fine-tune tiếp (UC11)."""
        # TODO(DEV): query ModelVersion.is_current, load lại self._model/_tokenizer
        self._load_current()

    def predict(self, text: str) -> tuple[float, int]:
        """Trả (score, model_version_id). Khung này chưa gọi model thật."""
        # TODO(DEV): tokenize, forward qua model, lấy xác suất lớp toxic
        if self._model is not None and self._tokenizer is not None:
            inputs = self._tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
            with torch.no_grad():
                logits = self._model(**inputs).logits
                probs = torch.softmax(logits, dim=-1)
                score = probs[0][1].item()
        else:
            score = 0.0

        version_id = self.current_model_version_id if self.current_model_version_id is not None else 1
        return float(score), int(version_id)
