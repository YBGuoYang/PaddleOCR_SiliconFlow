#!/usr/bin/env python3
"""Legacy compatibility launcher for the retired simple entry."""

from __future__ import annotations

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_ROOT = os.path.join(PROJECT_ROOT, "src")
if SRC_ROOT not in sys.path:
    sys.path.insert(0, SRC_ROOT)

from screenshot_ocr.main import main as hotkey_main


def main() -> None:
    print("[INFO] 简版窗口入口已下线，正在切换到托盘 + 快捷键版本。")
    hotkey_main()


if __name__ == "__main__":
    main()
