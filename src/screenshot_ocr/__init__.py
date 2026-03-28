"""Shared application code for Screenshot OCR."""

from .config import (
    AppConfig,
    DEFAULT_CONFIG,
    SUPPORTED_HOTKEYS,
    get_config_path,
    load_app_config,
    save_app_config,
)
from .app import OCRService
from .capture import capture_region_to_temp_file, delete_file_quietly, save_image_to_temp_file
from .hotkeys import DEFAULT_HOTKEY, HotkeyListener, SUPPORTED_HOTKEYS, normalize_hotkey
from .logging_utils import log_debug, log_error, log_info, log_ok, log_warn
from .main import main
from .notifier import (
    build_busy_message,
    build_empty_result_message,
    build_notification_preview,
    build_success_message,
    show_notification,
)
from .ocr_client import PaddleOCRVL, SiliconFlowOCR, extract_text_from_prediction
from .tray_app import HotkeyOCR
from .ui_status import StatusToast
from .ui_selection import RegionSelector, normalize_region
from .ui_tray import create_tray_icon, create_tray_icon_image

__all__ = [
    "OCRService",
    "AppConfig",
    "DEFAULT_HOTKEY",
    "DEFAULT_CONFIG",
    "HotkeyListener",
    "HotkeyOCR",
    "SUPPORTED_HOTKEYS",
    "get_config_path",
    "load_app_config",
    "save_app_config",
    "capture_region_to_temp_file",
    "delete_file_quietly",
    "save_image_to_temp_file",
    "log_debug",
    "log_error",
    "log_info",
    "log_ok",
    "log_warn",
    "main",
    "normalize_hotkey",
    "build_busy_message",
    "build_empty_result_message",
    "build_notification_preview",
    "build_success_message",
    "show_notification",
    "RegionSelector",
    "StatusToast",
    "normalize_region",
    "create_tray_icon",
    "create_tray_icon_image",
    "PaddleOCRVL",
    "SiliconFlowOCR",
    "extract_text_from_prediction",
]
