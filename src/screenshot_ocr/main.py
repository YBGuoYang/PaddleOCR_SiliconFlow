"""Package entrypoint for Screenshot OCR."""

from __future__ import annotations

from .tray_app import HotkeyOCR


def main() -> None:
    app = HotkeyOCR()
    app.run()


if __name__ == "__main__":
    main()
