"""Legacy import shim for the shared OCR client."""

from __future__ import annotations

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_ROOT = os.path.join(PROJECT_ROOT, "src")
if SRC_ROOT not in sys.path:
    sys.path.insert(0, SRC_ROOT)

from screenshot_ocr.ocr_client import PaddleOCRVL, SiliconFlowOCR

__all__ = ["PaddleOCRVL", "SiliconFlowOCR"]
