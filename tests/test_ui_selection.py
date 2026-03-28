from screenshot_ocr.ui_selection import normalize_region


def test_normalize_region_orders_coordinates():
    assert normalize_region(9, 2, 1, 7) == (1, 2, 9, 7)
