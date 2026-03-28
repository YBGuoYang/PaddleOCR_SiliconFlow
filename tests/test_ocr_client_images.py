import os

from screenshot_ocr.ocr_client import SiliconFlowOCR


def test_encode_image_supports_added_test_images():
    client = SiliconFlowOCR(api_key="sk-test")
    base_dir = os.path.dirname(__file__)
    image_paths = [
        os.path.join(base_dir, "tset.png"),
        os.path.join(base_dir, "test2.png"),
        os.path.join(base_dir, "test3.jpg"),
    ]

    for image_path in image_paths:
        encoded = client._encode_image(image_path)
        assert encoded
        assert len(encoded) > 100
