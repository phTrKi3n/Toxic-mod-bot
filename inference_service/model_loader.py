import logging
import os
import random
import re
import time
import unicodedata
from typing import Optional, Tuple

import torch
from sqlalchemy.orm import Session

from db.models import ModelVersion

logger = logging.getLogger("inference.model_loader")

DEFAULT_VI_MODEL = "thong7d/vihsd-xlmr-base-hate-speech"
DEFAULT_EN_MODEL = "EIStakovskii/xlm_roberta_base_multilingual_toxicity_classifier_plus"

_VI_CHARS = set("àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ")
_VI_SLANG_MAP = {
    "đm": "địt mẹ",
    "dm": "địt mẹ",
    "đkm": "địt con mẹ",
    "dkm": "địt con mẹ",
    "vcl": "vãi cả lồn",
    "vl": "vãi lồn",
    "vãi": "vãi",
    "cc": "con cặc",
    "cl": "cái lồn",
}
_VI_WORDS = {
    "mày",
    "tao",
    "thằng",
    "đồ",
    "ngu",
    "cút",
    "chó",
    "lợn",
    "rác",
    "chửi",
    "xấu",
    "nhảm",
    "tào",
    "bạn",
    "mình",
    "không",
    "được",
    "chào",
    "tốt",
}


def preprocess_text(text: str) -> str:
    """UC13: Normalize Unicode, strip evasion separators between letters, expand common teencode."""
    if not text:
        return ""
    cleaned = unicodedata.normalize("NFC", text)
    # Remove zero-width characters
    cleaned = re.sub(r"[\u200b-\u200f\ufeff]", "", cleaned)
    # Collapse obfuscated dots/dashes/underscores placed between word characters (e.g., Đ.ồ n.g.u -> Đồ ngu)
    prev = None
    while prev != cleaned:
        prev = cleaned
        cleaned = re.sub(r"(?<=\w)[\.\-_∗*]+(?=\w)", "", cleaned, flags=re.UNICODE)
    # Collapse spaced single-letter evasion when 4+ single letters appear in a row (e.g., "n g u v l")
    cleaned = re.sub(
        r"\b(?:[a-zA-ZÀ-ỹ]\s+){3,}[a-zA-ZÀ-ỹ]\b",
        lambda m: m.group(0).replace(" ", ""),
        cleaned,
    )
    # Expand standalone Vietnamese vulgar abbreviations so the model sees full semantics
    tokens = cleaned.split()
    expanded = [_VI_SLANG_MAP.get(tok.lower(), tok) for tok in tokens]
    cleaned = " ".join(expanded)
    return re.sub(r"\s+", " ", cleaned).strip()


def is_vietnamese_or_mixed(text: str) -> bool:
    lower = text.lower()
    if any(ch in _VI_CHARS for ch in lower):
        return True
    words = set(re.findall(r"\w+", lower))
    return bool(words & (_VI_WORDS | set(_VI_SLANG_MAP.keys())))


class ModelManager:
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        self.model_version_id: Optional[int] = None
        self.version_tag: Optional[str] = None
        self.pipeline = None
        self._vi_bundle = None
        self._en_bundle = None
        self.loaded_at: Optional[float] = None

    @property
    def current_model_version_id(self) -> Optional[int]:
        return self.model_version_id

    @staticmethod
    def _load_hf_classifier(model_id: str):
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        tok = AutoTokenizer.from_pretrained(model_id)
        mod = AutoModelForSequenceClassification.from_pretrained(model_id)
        mod.eval()
        return tok, mod

    @staticmethod
    def _score_from_bundle(bundle, text: str) -> float:
        tok, mod = bundle
        inputs = tok(text, return_tensors="pt", truncation=True, max_length=128)
        with torch.no_grad():
            logits = mod(**inputs).logits
            probs = torch.softmax(logits, dim=-1)[0].tolist()
        if len(probs) == 3:
            # ViHSD 3-class: 0=CLEAN, 1=OFFENSIVE (borderline ~0.65), 2=HATE (severe ~1.0)
            score = 0.65 * probs[1] + 1.0 * probs[2]
            return float(min(max(score, 0.0), 1.0))
        if len(probs) >= 2:
            return float(probs[1])
        return float(torch.sigmoid(logits)[0][0].item())

    def load_model_from_db(self, db_session: Session) -> Tuple[int, str]:
        """Reads database for record with is_current=True and sets up model instance."""
        record = (
            db_session.query(ModelVersion)
            .filter(ModelVersion.is_current.is_(True))
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
                custom_path = os.getenv("MODEL_PATH")
                if custom_path and os.path.exists(custom_path):
                    self._vi_bundle = self._load_hf_classifier(custom_path)
                    self._en_bundle = self._vi_bundle
                    self.pipeline = "xlm_roberta_bilingual_real"
                    logger.info(
                        f"Loaded local fine-tuned XLM-R model '{custom_path}' for {self.version_tag}"
                    )
                elif os.path.exists("models/xlmr-finetuned"):
                    self._vi_bundle = self._load_hf_classifier("models/xlmr-finetuned")
                    self._en_bundle = self._vi_bundle
                    self.pipeline = "xlm_roberta_bilingual_real"
                    logger.info(
                        f"Loaded local fine-tuned XLM-R model 'models/xlmr-finetuned' for {self.version_tag}"
                    )
                else:
                    vi_id = os.getenv("MODEL_PATH_VI", DEFAULT_VI_MODEL)
                    en_id = os.getenv("MODEL_PATH_EN", DEFAULT_EN_MODEL)
                    self._vi_bundle = self._load_hf_classifier(vi_id)
                    self._en_bundle = (
                        self._vi_bundle
                        if en_id == vi_id
                        else self._load_hf_classifier(en_id)
                    )
                    self.pipeline = "xlm_roberta_bilingual_real"
                    logger.info(
                        f"Loaded bilingual XLM-R models (VI='{vi_id}', EN='{en_id}') for {self.version_tag}"
                    )
            except Exception as e:
                logger.error(
                    f"Failed to load HuggingFace XLM-R model: {e}. Falling back to mock."
                )
                self.use_mock = True
                self.pipeline = "mock_xlm_roberta_pipeline"

        self.loaded_at = time.time()
        return self.model_version_id, self.version_tag

    def reload(self, db_session: Optional[Session] = None) -> Tuple[int, str]:
        if db_session is not None:
            return self.load_model_from_db(db_session)
        try:
            from db.session import SessionLocal

            with SessionLocal() as db:
                return self.load_model_from_db(db)
        except Exception:
            return self.model_version_id or 1, self.version_tag or "v1.0.0-default"

    def predict(self, text: str) -> float:
        """Performs classification on text, returning toxic probability score [0.0, 1.0]."""
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")

        normalized = preprocess_text(text)

        if self.use_mock or self.pipeline == "mock_xlm_roberta_pipeline":
            text_lower = normalized.lower()
            toxic_keywords = [
                "toxic",
                "chửi",
                "xấu",
                "rác",
                "ngu",
                "đồ ngu",
                "cút",
                "khốn nạn",
                "vô học",
                "mất dạy",
                "địt",
                "lồn",
                "cặc",
                "óc chó",
                "idiot",
                "stupid",
                "hate you",
                "moron",
                "trash",
                "fuck",
                "bastard",
                "scum",
                "loser",
            ]
            suspicious_keywords = [
                "suspicious",
                "nghi_ngov",
                "nghi vấn",
                "kém",
                "vớ vẩn",
                "nhảm",
                "tào lao",
                "spam",
                "annoying",
                "weird",
            ]
            clean_keywords = [
                "clean",
                "chào",
                "tốt",
                "cảm ơn",
                "sai bét",
                "không đồng ý",
                "hello",
                "thanks",
                "thank you",
                "makes no sense",
                "disagree",
            ]
            if any(k in text_lower for k in toxic_keywords):
                return 0.95
            elif any(k in text_lower for k in suspicious_keywords):
                return 0.60
            elif any(k in text_lower for k in clean_keywords):
                return 0.05
            else:
                return round(random.uniform(0.01, 0.25), 4)

        if self._vi_bundle is not None and self._en_bundle is not None:
            if is_vietnamese_or_mixed(normalized):
                vi_score = self._score_from_bundle(self._vi_bundle, normalized)
                en_score = self._score_from_bundle(self._en_bundle, normalized)
                # Combine ViHSD XLM-R and multilingual XLM-R for code-switched/mixed chat
                return round(max(vi_score, 0.85 * en_score), 4)
            return round(self._score_from_bundle(self._en_bundle, normalized), 4)

        result = self.pipeline(normalized)
        score = result[0]["score"]
        label = result[0]["label"]
        if label.upper() in ["LABEL_1", "TOXIC", "BAD", "HATE"]:
            return float(score)
        return float(1.0 - score)


USE_MOCK_ENV = os.getenv("MOCK_MODEL", "true").lower() in ("true", "1", "yes")
model_manager = ModelManager(use_mock=USE_MOCK_ENV)
ModelLoader = ModelManager
model_loader = model_manager


def load_current_model(db_session: Session) -> Tuple[int, str]:
    return model_manager.load_model_from_db(db_session)


def reload_model(db_session: Session) -> Tuple[int, str]:
    logger.info("Executing Hot-Reload/Rollback of model from Database...")
    return model_manager.load_model_from_db(db_session)
