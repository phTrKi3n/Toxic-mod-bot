"""
tests/test_bot.py — khớp TC04, TC05, TC06 ở Chương V mục I.2 của báo cáo.
"""

import pytest


def test_mod_can_restore_flagged_message():
    pytest.skip("TODO(OPS/DEV): cần fixture DB + bot client giả lập để chạy test này")


def test_appeal_creates_pending_record():
    pytest.skip("TODO(OPS/DEV): cần fixture DB để chạy test này")


def test_member_cannot_call_resolve_command():
    pytest.skip("TODO(SEC/OPS): cần fixture User với role='member' để chạy test này")
