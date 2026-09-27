"""
tests/test_bot.py — khớp TC04, TC05, TC06 ở Chương V mục I.2 của báo cáo,
chủ yếu kiểm tra RBAC (SEC) và luồng /resolve, /appeal.
"""

import pytest


def test_mod_can_restore_flagged_message():
    # TC04: Mod chạy /resolve restore trên ca đã bị xoá oan
    pytest.skip("TODO(OPS/DEV): cần fixture DB + bot client giả lập để chạy test này")


def test_appeal_creates_pending_record():
    # TC05: người dùng gửi /appeal sau khi bị xoá tin
    pytest.skip("TODO(OPS/DEV): cần fixture DB để chạy test này")


def test_member_cannot_call_resolve_command():
    # TC06: RBAC, thành viên thường gọi /resolve phải bị từ chối
    pytest.skip("TODO(SEC/OPS): cần fixture User với role='member' để chạy test này")
