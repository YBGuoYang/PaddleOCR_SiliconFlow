#!/usr/bin/env python3
"""Thin launcher for the official tray + hotkey application."""

from __future__ import annotations

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_ROOT = os.path.join(PROJECT_ROOT, "src")

if getattr(sys, "frozen", False):
    sys.path.insert(0, sys._MEIPASS)
elif SRC_ROOT not in sys.path:
    sys.path.insert(0, SRC_ROOT)

from screenshot_ocr.main import main


if __name__ == "__main__":
    main()
