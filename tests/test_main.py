import screenshot_ocr


def test_package_main_module_exports_main():
    assert callable(screenshot_ocr.main)
