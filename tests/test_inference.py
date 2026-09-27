"""
tests/test_inference.py — khớp TC01, TC02, TC03, TC07 ở Chương V mục I.2 của
báo cáo. Khung khởi điểm, cần model thật hoặc mock trước khi chạy được.
"""

import pytest


def test_high_toxicity_score_triggers_delete_range():
    # TC01: tin nhắn độc hại rõ ràng, điểm dự kiến >= threshold_high
    pytest.skip("TODO(OPS/DEV): cần model hoặc mock đã fine-tune để chạy test này")


def test_normal_message_low_score():
    # TC02: tin nhắn bình thường, điểm dự kiến < threshold_low
    pytest.skip("TODO(OPS/DEV): cần model hoặc mock đã fine-tune để chạy test này")


def test_borderline_message_goes_to_queue():
    # TC03: điểm ở vùng giữa 2 ngưỡng, kỳ vọng tạo HardCase status=pending
    pytest.skip("TODO(OPS/DEV): cần model hoặc mock đã fine-tune để chạy test này")


def test_inference_timeout_does_not_crash_bot():
    # TC07: Inference Service không phản hồi > 2 giây, bot phải bỏ qua tin nhắn
    # và ghi log lỗi timeout, không được raise ra ngoài làm crash bot.
    pytest.skip("TODO(OPS): dựng mock server trễ phản hồi để test timeout")
