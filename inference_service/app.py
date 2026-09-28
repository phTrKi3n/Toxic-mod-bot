import logging
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from db.session import SessionLocal, init_db
from inference_service.model_loader import (
    load_current_model,
    model_manager,
    reload_model,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("inference.app")

START_TIME = time.time()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database schema...")
    init_db()
    db = SessionLocal()
    try:
        m_id, v_tag = load_current_model(db)
        logger.info(
            f"Inference Service Started. Active Model ID={m_id}, Version={v_tag}"
        )
    finally:
        db.close()
    yield
    logger.info("Shutting down Inference Service...")


app = FastAPI(
    title="Hệ thống Phát hiện Bình luận Độc hại - Inference API",
    version="1.0.0",
    lifespan=lifespan,
)


class ClassifyRequest(BaseModel):
    text: str = Field(..., description="Nội dung tin nhắn/bình luận cần phân loại")


class ClassifyResponse(BaseModel):
    score: float = Field(..., description="Xác suất độc hại từ 0.0 tới 1.0")
    model_version_id: int = Field(..., description="ID của phiên bản model đã dùng")


class HealthResponse(BaseModel):
    status: str
    current_model_version_id: int
    version_tag: str
    uptime_seconds: float


@app.post("/classify", response_model=ClassifyResponse)
def classify_text(req: ClassifyRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nội dung text không được để rỗng",
        )

    try:
        score = model_manager.predict(req.text)
        return ClassifyResponse(
            score=score, model_version_id=model_manager.model_version_id or 1
        )
    except Exception as e:
        logger.error(f"Inference error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi phân loại tin nhắn: {str(e)}",
        )


@app.get("/health", response_model=HealthResponse)
def health_check():
    uptime = round(time.time() - START_TIME, 2)
    return HealthResponse(
        status="healthy",
        current_model_version_id=model_manager.model_version_id or 1,
        version_tag=model_manager.version_tag or "v1.0.0-default",
        uptime_seconds=uptime,
    )


@app.post("/ops/reload")
def trigger_reload(db: Session = Depends(get_db)):
    m_id, v_tag = reload_model(db)
    return {
        "status": "success",
        "message": "Model reloaded successfully",
        "current_model_version_id": m_id,
        "version_tag": v_tag,
    }
