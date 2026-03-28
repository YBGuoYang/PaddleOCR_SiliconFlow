from screenshot_ocr.notifier import (
    build_busy_message,
    build_empty_result_message,
    build_notification_preview,
    build_success_message,
    format_elapsed_text,
    show_notification,
)


def test_build_notification_preview_truncates_long_text():
    assert build_notification_preview("abcdefghijklmnopqrstuvwxyz", limit=5) == "abcde..."


def test_show_notification_returns_false_when_disabled():
    assert show_notification("title", "message", enabled=False) is False


def test_format_elapsed_text_formats_one_decimal_place():
    assert format_elapsed_text(1.234) == "1.2 秒"


def test_build_success_message_includes_line_count_elapsed_and_preview():
    message = build_success_message("first line\nsecond line", line_count=2, elapsed_seconds=1.25)

    assert "共 2 行" in message
    assert "1.2 秒" in message
    assert "first line second line" in message


def test_build_empty_result_message_includes_elapsed():
    assert build_empty_result_message(elapsed_seconds=0.8) == "未识别到文字，耗时 0.8 秒"


def test_build_busy_message_is_user_friendly():
    assert build_busy_message() == "上一张截图仍在识别，请稍候"
