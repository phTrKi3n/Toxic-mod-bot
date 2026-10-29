"""SEC: kiểm thử nhánh quyết định kiểm duyệt bằng score giả lập.

Không gọi Discord, Inference Service hay database thật. Không đánh giá
Precision/Recall của mô hình và không xác nhận xoá tin nhắn thành công.
"""

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest


@pytest.fixture
def actions_module():
    """Nạp đúng bot/actions.py, không cần kết nối hoặc cài discord.py."""
    fake_discord = types.ModuleType("discord")
    fake_discord.Message = type("Message", (), {})
    path = Path(__file__).resolve().parents[1] / "bot" / "actions.py"
    spec = importlib.util.spec_from_file_location("sec_actions_under_test", path)
    assert spec is not None and spec.loader is not None
    actions = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"discord": fake_discord}):
        spec.loader.exec_module(actions)
    return actions


class FakeHTTPClient:
    """Trả score định sẵn, không phát sinh HTTP request thật."""

    def __init__(self, score, requests, timeout):
        self.score = score
        self.requests = requests
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, json):
        self.requests.append((url, json, self.timeout))
        return types.SimpleNamespace(json=lambda: {"score": self.score})


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
async def test_score_routes_to_expected_action(actions_module, monkeypatch, score, expected):
    """Xác nhận ngưỡng 0.30 và 0.90, không chạy handler DEV còn TODO."""
    actions = actions_module
    requests = []
    message = types.SimpleNamespace(content="noi dung gia lap")
    delete = AsyncMock()
    flag = AsyncMock()

    def make_client(*, timeout):
        return FakeHTTPClient(score, requests, timeout)

    monkeypatch.setattr(actions.httpx, "AsyncClient", make_client)
    monkeypatch.setattr(actions, "_delete_and_warn", delete)
    monkeypatch.setattr(actions, "_flag_for_review", flag)

    await actions.classify_and_act(message)

    # Gửi đúng nội dung cần phân loại, không đính kèm ID user/guild/token.
    # Đây chỉ là kiểm tra payload hiện tại, KHÔNG chứng minh bảo mật truyền tải.
    assert requests == [
        ("http://localhost:8000/classify", {"text": "noi dung gia lap"}, 2.0)
    ]
    if expected == "delete":
        delete.assert_awaited_once_with(message, score)
        flag.assert_not_awaited()
    elif expected == "flag":
        flag.assert_awaited_once_with(message, score)
        delete.assert_not_awaited()
    else:
        flag.assert_not_awaited()
        delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_inference_timeout_does_not_trigger_delete_or_flag(actions_module, monkeypatch):
    """Timeout phải bỏ qua quyết định, không gọi hành động kiểm duyệt."""
    actions = actions_module
    delete = AsyncMock()
    flag = AsyncMock()

    class TimeoutClient:
        def __init__(self, *, timeout):
            assert timeout == actions.INFERENCE_TIMEOUT_SECONDS

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, json):
            raise httpx.ReadTimeout("SEC simulated timeout")

    monkeypatch.setattr(actions.httpx, "AsyncClient", TimeoutClient)
    monkeypatch.setattr(actions, "_delete_and_warn", delete)
    monkeypatch.setattr(actions, "_flag_for_review", flag)

    message = types.SimpleNamespace(content="noi dung gia lap")
    assert await actions.classify_and_act(message) is None
    delete.assert_not_awaited()
    flag.assert_not_awaited()
