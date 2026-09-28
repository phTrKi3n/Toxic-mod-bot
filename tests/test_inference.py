"""
tests/test_inference.py — khớp TC01, TC02, TC03, TC07 ở Chương V mục I.2 của báo cáo.
"""

import pytest


def test_high_toxicity_score_triggers_delete_range():
    pytest.skip("TODO(OPS/DEV): cần model hoặc mock đã fine-tune để chạy test này")


def test_normal_message_low_score():
    pytest.skip("TODO(OPS/DEV): cần model hoặc mock đã fine-tune để chạy test này")


def test_borderline_message_goes_to_queue():
    pytest.skip("TODO(OPS/DEV): cần model hoặc mock đã fine-tune để chạy test này")


def test_inference_timeout_does_not_crash_bot():
    pytest.skip("TODO(OPS): dựng mock server trễ phản hồi để test timeout")
