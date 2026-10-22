"""
tests/test_inference.py — khớp TC01, TC02, TC03, TC07 ở Chương V mục I.2 của báo cáo.
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from bot.actions import classify_and_moderate
from db.models import Base, Classification, HardCase, Message, ModerationAction, Server
from inference_service.model_loader import ModelManager, model_manager, preprocess_text


class _MockResponse:
    def __init__(self, status: int, payload: dict):
        self.status = status
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def json(self):
        return self._payload


class _MockSession:
    def __init__(self, score: float, model_version_id: int = 1):
        self.score = score
        self.model_version_id = model_version_id
        self.closed = False

    def post(self, url, json=None, timeout=None):
        return _MockResponse(
            200, {"score": self.score, "model_version_id": self.model_version_id}
        )

    async def close(self):
        self.closed = True


@pytest.fixture()
def mem_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def _make_msg(msg_id: int, content: str):
    return SimpleNamespace(
        id=msg_id,
        content=content,
        guild=SimpleNamespace(id="100", name="Test Guild"),
        author=SimpleNamespace(
            id="10",
            name="user10",
            bot=False,
            roles=[SimpleNamespace(name="member")],
            send=AsyncMock(),
        ),
        delete=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_high_toxicity_score_triggers_delete_range(mem_db):
    """TC01: Điểm độc hại >= threshold_high (0.90) kích hoạt xoá tin nhắn và cảnh báo."""
    score = model_manager.predict("Đồ ngu, cút đi thứ rác rưởi toxic")
    assert score >= 0.90

    msg = _make_msg(1001, "Đồ ngu, cút đi thứ rác rưởi toxic")
    cfg = Server(
        guild_id="100", name="Test Guild", threshold_low=0.30, threshold_high=0.90
    )
    res = await classify_and_moderate(
        msg, cfg, db_session=mem_db, session=_MockSession(score)
    )

    assert res["action"] == "delete"
    msg.delete.assert_awaited_once()
    msg.author.send.assert_awaited_once()
    assert mem_db.get(Message, 1001) is not None
    assert (
        mem_db.scalar(
            select(ModerationAction).where(ModerationAction.message_id == 1001)
        ).action_type
        == "delete"
    )


@pytest.mark.asyncio
async def test_normal_message_low_score(mem_db):
    """TC02: Tin nhắn bình thường có điểm < threshold_low (0.30) được bỏ qua (ignore)."""
    score = model_manager.predict("Chào mọi người, chúc một ngày tốt lành")
    assert score < 0.30

    msg = _make_msg(1002, "Chào mọi người, chúc một ngày tốt lành")
    cfg = Server(
        guild_id="100", name="Test Guild", threshold_low=0.30, threshold_high=0.90
    )
    res = await classify_and_moderate(
        msg, cfg, db_session=mem_db, session=_MockSession(score)
    )

    assert res["action"] == "ignore"
    msg.delete.assert_not_awaited()
    assert (
        mem_db.scalar(select(Classification).where(Classification.message_id == 1002))
        is not None
    )


@pytest.mark.asyncio
async def test_borderline_message_goes_to_queue(mem_db):
    """TC03: Tin nhắn ở vùng nghi vấn (0.30 <= score < 0.90) được đưa vào HardCase."""
    score = model_manager.predict("Bình luận này hơi vớ vẩn và đáng nghi vấn")
    assert 0.30 <= score < 0.90

    msg = _make_msg(1003, "Bình luận này hơi vớ vẩn và đáng nghi vấn")
    cfg = Server(
        guild_id="100", name="Test Guild", threshold_low=0.30, threshold_high=0.90
    )
    res = await classify_and_moderate(
        msg, cfg, db_session=mem_db, session=_MockSession(score)
    )

    assert res["action"] == "flag"
    hc = mem_db.scalar(select(HardCase).where(HardCase.message_id == 1003))
    assert hc is not None
    assert hc.status == "pending"


@pytest.mark.asyncio
async def test_inference_timeout_does_not_crash_bot(mem_db):
    """TC07: Khi Inference Service timeout, bot không bị crash và trả về bypass."""

    class _TimeoutCtx:
        async def __aenter__(self):
            raise asyncio.TimeoutError("timeout")

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    class _TimeoutSession:
        closed = False

        def post(self, url, json=None, timeout=None):
            return _TimeoutCtx()

        async def close(self):
            self.closed = True

    msg = _make_msg(1004, "Tin nhắn kiểm tra timeout")
    cfg = Server(
        guild_id="100", name="Test Guild", threshold_low=0.30, threshold_high=0.90
    )
    res = await classify_and_moderate(
        msg, cfg, db_session=mem_db, session=_TimeoutSession()
    )
    assert res["action"] == "bypass"
    assert res["reason"] == "timeout"


def test_preprocess_text_normalizes_evasion_and_teencode():
    """Kiểm tra tiền xử lý chuẩn hoá chữ biến tấu (chèn dấu chấm/gạch/khoảng trắng) và từ lóng tiếng Việt."""
    assert preprocess_text("Đ.ồ n.g.u") == "Đồ ngu"
    assert preprocess_text("n-g-u v_l") == "ngu vãi lồn"
    assert preprocess_text("Mày đm nói chuyện vl") == "Mày địt mẹ nói chuyện vãi lồn"
    assert preprocess_text("s t u p i d") == "stupid"


def test_real_huggingface_xlmr_bilingual_classification(mem_db):
    """Kiểm thử mô hình XLM-RoBERTa song ngữ thực tế từ Hugging Face cho cả tiếng Việt, tiếng Anh và câu pha trộn."""
    import os

    use_mock_ci = os.getenv("MOCK_MODEL", "false").lower() in ("true", "1", "yes")
    real_mgr = ModelManager(use_mock=use_mock_ci)
    real_mgr.load_model_from_db(mem_db)

    # 1. Tiếng Việt & Tiếng Anh bình thường (< 0.30)
    assert real_mgr.predict("Chào mọi người, chúc một ngày làm việc tốt lành!") < 0.30
    assert real_mgr.predict("Ý kiến của bạn sai bét rồi, đừng phát biểu liều") < 0.30
    assert (
        real_mgr.predict("Hello everyone, thank you for helping me with Python!") < 0.30
    )
    assert real_mgr.predict("This argument makes no sense at all, I disagree.") < 0.30

    # 2. Tiếng Việt, Tiếng Anh, từ lóng & biến tấu độc hại nặng (>= 0.90)
    assert real_mgr.predict("Đồ ngu, cút khỏi server đi thứ rác rưởi") >= 0.90
    assert real_mgr.predict("Đ.ồ n.g.u, cút đi thứ rác rưởi") >= 0.90
    assert real_mgr.predict("Mày nói chuyện nghe ngứa đít vl") >= 0.90
    assert real_mgr.predict("You are a fucking idiot, shut up and get lost!") >= 0.90
    assert real_mgr.predict("Bro nói chuyện toxic vl, đúng là stupid idiot") >= 0.90

    # 3. Câu vùng nghi vấn (0.30 <= score < 0.90)
    borderline_score = real_mgr.predict("Bình luận này hơi vớ vẩn và tào lao quá")
    assert 0.30 <= borderline_score < 0.90
