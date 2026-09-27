"""
inference_service/app.py — bọc model XLM-R đã fine-tune sau một API HTTP.
Khớp UC14 (Gọi model phân loại) và endpoint /health cho giám sát vận hành
(Chương V mục IV). Khung khởi điểm, phần load model thật nằm ở model_loader.py.
"""

from fastapi import FastAPI
from pydantic import BaseModel

from inference_service.model_loader import ModelLoader

app = FastAPI(title="toxic-mod-bot inference service")
model_loader = ModelLoader()


class ClassifyRequest(BaseModel):
    text: str


class ClassifyResponse(BaseModel):
    score: float
    model_version_id: int


@app.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest) -> ClassifyResponse:
    """UC14: nhận text, trả điểm độc hại p trong [0, 1] kèm phiên bản model đã dùng."""
    score, model_version_id = model_loader.predict(req.text)
    return ClassifyResponse(score=score, model_version_id=model_version_id)


@app.get("/health")
def health() -> dict:
    """Dùng cho health-check định kỳ (Chương V mục IV), không đổi hành vi bot."""
    return {
        "status": "ok",
        "model_version_id": model_loader.current_model_version_id,
        "is_current": True,
    }
