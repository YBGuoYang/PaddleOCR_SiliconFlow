from screenshot_ocr.config import AppConfig
from screenshot_ocr.ui_dialogs import build_current_settings_text


def test_build_current_settings_text_renders_config():
    config = AppConfig(hotkey="f8", mode="instant", long_press_time=1.2)

    text = build_current_settings_text(config)

    assert "F8" in text
    assert "即时" in text
    assert "1.2秒" in text
