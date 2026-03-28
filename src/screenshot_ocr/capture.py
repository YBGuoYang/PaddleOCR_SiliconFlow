"""Screen capture and temp file helpers."""

from __future__ import annotations

import os
import tempfile
from typing import Protocol

from PIL import ImageGrab


class SavableImage(Protocol):
    def save(self, fp: str) -> None:
        ...


def save_image_to_temp_file(image: SavableImage, suffix: str = ".png") -> str:
    """Persist an in-memory image into a temp file and return its path."""
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    temp_path = temp_file.name
    temp_file.close()
    image.save(temp_path)
    return temp_path


def capture_region_to_temp_file(x1: int, y1: int, x2: int, y2: int) -> tuple[str, tuple[int, int]]:
    """Capture a screen region and store it as a temp file."""
    screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    temp_path = save_image_to_temp_file(screenshot)
    return temp_path, screenshot.size


def delete_file_quietly(path: str | None) -> None:
    """Delete a file if it exists and ignore cleanup failures."""
    if not path:
        return
    try:
        if os.path.exists(path):
            os.unlink(path)
    except OSError:
        pass
