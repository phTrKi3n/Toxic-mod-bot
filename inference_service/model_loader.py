import logging
import os
import random
import time
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from db.models import ModelVersion

logger = logging.getLogger("inference.model_loader")


class ModelManager:
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        self.model_version_id: Optional[int] = None
        self.version_tag: Optional[str] = None
        self.pipeline = None
        self.loaded_at: Optional[float] = None

    def load_model_from_db(self, db_session: Session) -> Tuple[int, str]:
        """Reads database for record with is_current=True and sets up model instance."""
        record = (
            db_session.query(ModelVersion)
            .filter(ModelVersion.is_current == True)  # noqa: E712
            .order_by(ModelVersion.model_version_id.desc())
            .first()
        )

        if not record:
            logger.warning(
                "No active model_version record found with is_current=True. Fallback to default v1.0.0"
            )
            self.model_version_id = 1
            self.version_tag = "v1.0.0-default"
        else:
            self.model_version_id = record.model_version_id
            self.version_tag = record.version_tag

        if self.use_mock:
            logger.info(
                f"[MOCK] Loaded model version {self.version_tag} (ID: {self.model_version_id})"
            )
            self.pipeline = "mock_xlm_roberta_pipeline"
        else:
            try:
                from transformers import pipeline

                model_name = os.getenv("MODEL_PATH", "xlm-roberta-base")
                self.pipeline = pipeline("text-classification", model=model_name)
                logger.info(
                    f"Loaded real HuggingFace model '{model_name}' for version {self.version_tag}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to load HuggingFace pipeline: {e}. Falling back to mock."
                )
                self.use_mock = True
                self.pipeline = "mock_xlm_roberta_pipeline"

        self.loaded_at = time.time()
        return self.model_version_id, self.version_tag

    def predict(self, text: str) -> float:
        """Performs classification on text, returning toxic probability score [0.0, 1.0]."""
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")

        if self.use_mock or self.pipeline == "mock_xlm_roberta_pipeline":
            text_lower = text.lower()
            if any(k in text_lower for k in ["toxic", "chửi", "xấu", "rác"]):
                return 0.95
            elif any(k in text_lower for k in ["suspicious", "nghi_ngov"]):
                return 0.60
            elif any(k in text_lower for k in ["clean", "chào", "tốt"]):
                return 0.05
            else:
                return round(random.uniform(0.01, 0.25), 4)
        else:
            result = self.pipeline(text)
            score = result[0]["score"]
            label = result[0]["label"]
            if label.upper() in ["LABEL_1", "TOXIC", "BAD"]:
                return float(score)
            else:
                return float(1.0 - score)


USE_MOCK_ENV = os.getenv("MOCK_MODEL", "true").lower() in ("true", "1", "yes")
model_manager = ModelManager(use_mock=USE_MOCK_ENV)


def load_current_model(db_session: Session) -> Tuple[int, str]:
    return model_manager.load_model_from_db(db_session)


def reload_model(db_session: Session) -> Tuple[int, str]:
    logger.info("Executing Hot-Reload/Rollback of model from Database...")
    return model_manager.load_model_from_db(db_session)
