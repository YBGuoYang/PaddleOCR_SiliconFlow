from screenshot_ocr.config import AppConfig, load_app_config, save_app_config


def test_config_normalizes_values(tmp_path):
    config = AppConfig(hotkey=" mouse4 ", long_press_time=9, mode="bad", api_key=" sk-test ")
    save_path = tmp_path / "hotkey_config.json"

    save_app_config(config, str(save_path))
    loaded = load_app_config(str(save_path))

    assert loaded.hotkey == "f9"
    assert loaded.long_press_time == 2.0
    assert loaded.mode == "long_press"
    assert loaded.api_key == "sk-test"


def test_load_invalid_file_falls_back_to_defaults(tmp_path):
    broken = tmp_path / "broken.json"
    broken.write_text("{not-json", encoding="utf-8")

    loaded = load_app_config(str(broken))

    assert loaded == AppConfig()
