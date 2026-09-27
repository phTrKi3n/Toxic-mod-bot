"""
inference_service/model_loader.py — load model XLM-R đã fine-tune, cache trong RAM.
Nạp lại model đang is_current từ bảng model_version (db/models.py) khi khởi động
hoặc khi được gọi reload, phục vụ cơ chế rollback ở Chương V mục IV: đổi is_current
trong DB xong, không cần sửa code hay khởi động lại toàn bộ bot.
"""


class ModelLoader:
    def __init__(self) -> None:
        # TODO(DEV): load tokenizer + model XLM-R fine-tune thật ở đây,
        # đọc model_version đang is_current=true từ DB (db/models.py: ModelVersion)
        self.current_model_version_id: int | None = None
        self._model = None
        self._tokenizer = None

    def reload(self) -> None:
        """Nạp lại model đang is_current, dùng khi rollback hoặc sau khi fine-tune tiếp (UC11)."""
        # TODO(DEV): query ModelVersion.is_current, load lại self._model/_tokenizer
        raise NotImplementedError

    def predict(self, text: str) -> tuple[float, int]:
        """Trả (score, model_version_id). Khung này chưa gọi model thật."""
        # TODO(DEV): tokenize, forward qua model, lấy xác suất lớp toxic
        raise NotImplementedError
