from PIL import Image

from screenshot_ocr.capture import delete_file_quietly, save_image_to_temp_file


def test_save_image_to_temp_file_creates_file():
    image = Image.new("RGB", (4, 4), color="white")

    temp_path = save_image_to_temp_file(image)

    try:
        with open(temp_path, "rb") as file:
            assert file.read(8).startswith(b"\x89PNG")
    finally:
        delete_file_quietly(temp_path)


def test_delete_file_quietly_handles_missing_paths():
    delete_file_quietly("C:/this/path/does/not/exist.png")
