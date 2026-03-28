from screenshot_ocr.ui_tray import create_tray_icon_image


def test_create_tray_icon_image_returns_rgba_image():
    image = create_tray_icon_image()

    assert image.mode == "RGBA"
    assert image.size == (64, 64)
