"""
inference_service/app.py — bọc model XLM-R đã fine-tune sau một API HTTP.
Khớp UC14 (Gọi model phân loại) và endpoint /health cho giám sát vận hành
(Chương V mục IV). Khung khởi điểm, phần load model thật nằm ở model_loader.py.
"""

import time

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from inference_service.model_loader import model_loader, model_manager

app = FastAPI(title="toxic-mod-bot inference service")
START_TIME = time.time()


def get_db():
    try:
        from db.session import SessionLocal

        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    except Exception:
        yield None


class ClassifyRequest(BaseModel):
    text: str = Field(..., description="Nội dung tin nhắn/bình luận cần phân loại")


class ClassifyResponse(BaseModel):
    score: float
    model_version_id: int


class HealthResponse(BaseModel):
    status: str
    current_model_version_id: int
    version_tag: str
    uptime_seconds: float
    is_current: bool = True


@app.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest) -> ClassifyResponse:
    """UC14: nhận text, trả điểm độc hại p trong [0, 1] kèm phiên bản model đã dùng."""
    if not req.text or not req.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nội dung text không được để rỗng",
        )
    score, model_version_id = model_loader.predict(req.text)
    return ClassifyResponse(score=score, model_version_id=model_version_id)


@app.get("/health", response_model=HealthResponse)
def health() -> dict:
    """Dùng cho health-check định kỳ (Chương V mục IV), không đổi hành vi bot."""
    uptime = round(time.time() - START_TIME, 2)
    return {
        "status": "healthy",
        "current_model_version_id": model_loader.model_version_id or 1,
        "version_tag": model_loader.version_tag or "v1.0.0-initial",
        "uptime_seconds": uptime,
        "is_current": True,
    }


@app.post("/ops/reload")
def trigger_reload(db: Session = Depends(get_db)) -> dict:
    """OPS endpoint phục vụ hot rollback model (Chương V mục IV)."""
    m_id, v_tag = model_loader.reload(db)
    return {
        "status": "success",
        "message": "Model reloaded successfully",
        "current_model_version_id": m_id,
        "version_tag": v_tag,
    }
