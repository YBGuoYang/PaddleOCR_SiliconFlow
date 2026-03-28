import queue

from screenshot_ocr.tray_app import HotkeyOCR


def test_queue_status_adds_status_task():
    app = object.__new__(HotkeyOCR)
    app.ui_queue = queue.Queue()

    app.queue_status("正在识别...", duration_ms=None, level="info")
    task, data = app.ui_queue.get_nowait()

    assert task == "status"
    assert data["message"] == "正在识别..."
    assert data["duration_ms"] is None
    assert data["level"] == "info"
