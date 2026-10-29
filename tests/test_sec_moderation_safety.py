"""SEC: kiểm thử an toàn quyết định kiểm duyệt bằng điểm giả lập.

Không gọi Discord, inference service hoặc database thật. Không đo FP/FN thực tế
của mô hình. Tương thích với classify_and_moderate(session=...) dùng aiohttp.
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from bot import actions


class FakeResponse:
    def __init__(self, score):
        self.status = 200
        self.score = score

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def json(self):
        return {"score": self.score, "model_version_id": 1}


class FakeSession:
    def __init__(self, score):
        self.score = score
        self.requests = []
        self.closed = False

    def post(self, url, json=None, timeout=None):
        self.requests.append((url, json, timeout))
        return FakeResponse(self.score)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "score,expected",
    [
        (0.00, "ignore"),
        (0.29, "ignore"),
        (0.299999, "ignore"),
        (0.30, "flag"),
        (0.89, "flag"),
        (0.899999, "flag"),
        (0.90, "delete"),
        (1.00, "delete"),
    ],
)
async def test_score_routes_to_expected_action(monkeypatch, score, expected):
    """Kiểm tra điểm ranh giới: <0.30 ignore; <0.90 flag; >=0.90 delete."""
    delete = AsyncMock()
    flag = AsyncMock()
    monkeypatch.setattr(actions, "_delete_and_warn", delete)
    monkeypatch.setattr(actions, "_flag_for_review", flag)

    message = SimpleNamespace(id=98765, content="noi dung gia lap", author=None)
    config = SimpleNamespace(threshold_low=0.30, threshold_high=0.90)
    session = FakeSession(score)

    result = await actions.classify_and_moderate(
        message, config, db_session=None, session=session
    )

    assert result["action"] == expected
    assert result["score"] == score
    assert len(session.requests) == 1
    url, payload, timeout = session.requests[0]
    assert url == actions.INFERENCE_URL
    # SEC chỉ xác nhận payload phân loại không chứa ID người dùng/server/token.
    assert payload == {"text": "noi dung gia lap"}
    assert timeout.total == actions.INFERENCE_TIMEOUT_SECONDS

    if expected == "delete":
        delete.assert_awaited_once_with(message, score)
        flag.assert_not_awaited()
    elif expected == "flag":
        flag.assert_awaited_once_with(message, score)
        delete.assert_not_awaited()
    else:
        delete.assert_not_awaited()
        flag.assert_not_awaited()


@pytest.mark.asyncio
async def test_inference_timeout_does_not_trigger_delete_or_flag(monkeypatch):
    """Timeout phải bypass, không xóa hoặc đánh dấu nhầm."""
    delete = AsyncMock()
    flag = AsyncMock()
    monkeypatch.setattr(actions, "_delete_and_warn", delete)
    monkeypatch.setattr(actions, "_flag_for_review", flag)
    monkeypatch.setattr(actions.error_tracker, "record_error", lambda *_: None)

    class TimeoutResponse:
        async def __aenter__(self):
            raise asyncio.TimeoutError("SEC simulated timeout")

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class TimeoutSession:
        closed = False

        def post(self, url, json=None, timeout=None):
            return TimeoutResponse()

    message = SimpleNamespace(id=98766, content="noi dung gia lap", author=None)
    config = SimpleNamespace(threshold_low=0.30, threshold_high=0.90)
    result = await actions.classify_and_moderate(
        message, config, db_session=None, session=TimeoutSession()
    )

    assert result["action"] == "bypass"
    assert result["reason"] == "timeout"
    delete.assert_not_awaited()
    flag.assert_not_awaited()
