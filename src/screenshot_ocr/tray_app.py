"""Tray application shell for Screenshot OCR."""

from __future__ import annotations

import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk

import pyperclip

from config.ocr_config import OCRConfig
from .app import OCRService
from .capture import capture_region_to_temp_file, delete_file_quietly
from .config import load_app_config, save_app_config
from .hotkeys import HotkeyListener
from .logging_utils import log_debug, log_error, log_info, log_ok, log_warn
from .notifier import (
    build_busy_message,
    build_empty_result_message,
    build_success_message,
    show_notification,
)
from .ui_dialogs import show_api_key_dialog, show_settings_window
from .ui_selection import RegionSelector
from .ui_tray import create_tray_icon

# Set DPI awareness before creating Tk windows on Windows.
try:
    from ctypes import windll

    windll.user32.SetProcessDPIAware()
except (ImportError, AttributeError, OSError):
    pass


class HotkeyOCR:
    """Hotkey-driven tray OCR application."""

    def __init__(self):
        self.config = load_app_config()
        self.running = True
        self.root: tk.Tk | None = None
        self.tray_icon = None
        self.hotkey_listener = None
        self.ocr_service = OCRService(
            self.config,
            server_url=OCRConfig.SERVER_URL,
            model_name=OCRConfig.MODEL_NAME,
            backend=OCRConfig.BACKEND,
        )

        self.ui_queue: queue.Queue[tuple[str, object | None]] = queue.Queue()
        self.state_lock = threading.Lock()
        self.selection_requested = False
        self.ocr_in_progress = False
        self.ocr_started_at: float | None = None

        self.status_window: tk.Toplevel | None = None
        self.status_title_label: tk.Label | None = None
        self.status_detail_label: tk.Label | None = None
        self.status_progress: ttk.Progressbar | None = None

        self.region_selector = RegionSelector(
            on_region_selected=self._handle_selected_region,
            on_cancel=self._handle_selection_cancel,
        )

        if not self.check_api_key():
            log_info("用户取消配置，程序退出")
            sys.exit(0)

        self.init_ocr()
        self.create_main_window()
        self.start_hotkey_listener()
        self.create_tray_icon()

    def _request_selection(self) -> tuple[bool, str | None]:
        with self.state_lock:
            if self.selection_requested or self.region_selector.selecting:
                return False, "请先完成当前截图框选"
            if self.ocr_in_progress:
                return False, build_busy_message()
            self.selection_requested = True
            return True, None

    def _clear_selection_request(self) -> None:
        with self.state_lock:
            self.selection_requested = False

    def _begin_ocr_job(self) -> bool:
        with self.state_lock:
            if self.ocr_in_progress:
                return False
            self.ocr_in_progress = True
            self.ocr_started_at = time.perf_counter()
            return True

    def _current_ocr_elapsed(self) -> float:
        with self.state_lock:
            started_at = self.ocr_started_at
        if started_at is None:
            return 0.0
        return max(0.0, time.perf_counter() - started_at)

    def _end_ocr_job(self) -> None:
        with self.state_lock:
            self.ocr_in_progress = False
            self.ocr_started_at = None

    def check_api_key(self):
        """Check whether API key is configured."""
        api_key = self.config.get("api_key", "")
        if api_key:
            return True

        api_key = show_api_key_dialog()
        if api_key:
            self.config["api_key"] = api_key
            self.save_config()
            return True
        return False

    def save_config(self):
        """Persist current config."""
        try:
            config_path = save_app_config(self.config)
            log_ok(f"配置已保存到: {config_path}")
        except OSError as exc:
            log_error(f"保存配置失败: {exc}", exc)

    def init_ocr(self):
        """Initialize OCR service."""
        self.ocr_service.initialize()

    def start_hotkey_listener(self):
        """Start hotkey listener."""
        try:
            self.hotkey_listener = HotkeyListener(
                hotkey=self.config.hotkey,
                mode=self.config.mode,
                long_press_time=self.config.long_press_time,
                on_trigger=self.trigger_screenshot,
            )
            self.hotkey_listener.start()
        except ImportError:
            log_error("请安装 keyboard 库: pip install keyboard")
        except (RuntimeError, ValueError, OSError) as exc:
            log_error(f"热键监听启动失败: {exc}", exc)

    def stop_hotkey_listener(self):
        """Stop hotkey listener."""
        try:
            if self.hotkey_listener is not None:
                self.hotkey_listener.stop()
                self.hotkey_listener = None
        except (AttributeError, RuntimeError):
            pass

    def trigger_screenshot(self):
        """Queue a screenshot action."""
        allowed, blocked_message = self._request_selection()
        if not allowed:
            log_info(blocked_message or "当前无法开始截图")
            if blocked_message:
                self.queue_status(blocked_message, duration_ms=1400, level="warn")
            return

        log_ok("触发区域截图...")
        self.ui_queue.put(("screenshot", None))

    def create_main_window(self):
        """Create hidden Tk root."""
        self.root = tk.Tk()
        self.root.title("截图 OCR 工具")
        self.root.geometry("1x1")
        self.root.withdraw()
        self.process_queue()

    def process_queue(self):
        """Process queued UI actions."""
        if self.root is None:
            return

        try:
            while True:
                task, data = self.ui_queue.get_nowait()
                log_debug(f"处理队列任务: {task}")
                if task == "screenshot":
                    self._clear_selection_request()
                    self._open_selection_ui()
                elif task == "settings":
                    log_debug("正在打开设置窗口...")
                    self._show_settings_window()
                elif task == "notification":
                    title, message = data
                    self._show_notification(title, message)
                elif task == "status":
                    message, duration_ms, level = data
                    self._show_status_message(message, duration_ms=duration_ms, level=level)
                elif task == "status_show":
                    title, detail = data
                    self._show_status_overlay(title, detail, show_progress=True)
                elif task == "status_hide":
                    self._hide_status_overlay()
        except queue.Empty:
            pass

        if self.running:
            self.root.after(100, self.process_queue)

    def do_screenshot(self):
        """Queue screenshot action."""
        self.trigger_screenshot()

    def _open_selection_ui(self):
        """Open region selection overlay."""
        if self.root is None:
            log_error("主窗口不存在，无法打开选择界面")
            return
        if not self.region_selector.open(self.root):
            log_info("截图选择窗口已经打开")

    def _show_status_overlay(self, title: str, detail: str) -> None:
        if self.root is None:
            return

        if self.status_window is None or not self.status_window.winfo_exists():
            self.status_window = tk.Toplevel(self.root)
            self.status_window.overrideredirect(True)
            self.status_window.attributes("-topmost", True)
            try:
                self.status_window.attributes("-alpha", 0.96)
            except tk.TclError:
                pass

            container = tk.Frame(
                self.status_window,
                bg="#f8fafc",
                bd=1,
                relief="solid",
                padx=14,
                pady=12,
            )
            container.pack(fill="both", expand=True)

            self.status_title_label = tk.Label(
                container,
                text=title,
                font=("Microsoft YaHei UI", 11, "bold"),
                bg="#f8fafc",
                fg="#111827",
                anchor="w",
            )
            self.status_title_label.pack(fill="x")

            self.status_detail_label = tk.Label(
                container,
                text=detail,
                font=("Microsoft YaHei UI", 9),
                bg="#f8fafc",
                fg="#4b5563",
                justify="left",
                wraplength=280,
                anchor="w",
            )
            self.status_detail_label.pack(fill="x", pady=(6, 10))

            self.status_progress = ttk.Progressbar(container, mode="indeterminate", length=280)
            self.status_progress.pack(fill="x")
        else:
            self.status_window.deiconify()

        if self.status_title_label is not None:
            self.status_title_label.config(text=title)
        if self.status_detail_label is not None:
            self.status_detail_label.config(text=detail)
        if self.status_progress is not None:
            self.status_progress.start(12)

        self.status_window.update_idletasks()
        width = 320
        height = max(110, self.status_window.winfo_height())
        x = self.root.winfo_screenwidth() - width - 24
        y = 24
        self.status_window.geometry(f"{width}x{height}+{x}+{y}")
        self.status_window.lift()

    def _hide_status_overlay(self) -> None:
        if self.status_progress is not None:
            self.status_progress.stop()
        if self.status_window is not None:
            try:
                self.status_window.destroy()
            except tk.TclError:
                pass
        self.status_window = None
        self.status_title_label = None
        self.status_detail_label = None
        self.status_progress = None

    def _handle_selected_region(self, region):
        x1, y1, x2, y2 = region
        if x2 - x1 < 10 or y2 - y1 < 10:
            log_debug("选择区域太小，已取消")
            return

        try:
            temp_path, screenshot_size = capture_region_to_temp_file(x1, y1, x2, y2)
            log_debug(f"截图尺寸: {screenshot_size}")

            if not self._begin_ocr_job():
                delete_file_quietly(temp_path)
                message = build_busy_message()
                log_warn(message)
                if self.config.get("show_notification", True):
                    self.ui_queue.put(("notification", ("OCR 状态", message)))
                return

            width, height = screenshot_size
            self.ui_queue.put(
                (
                    "status_show",
                    ("正在识别", f"已截取 {width} x {height} 区域，正在上传并识别文字..."),
                )
            )
            threading.Thread(target=self.perform_ocr, args=(temp_path,), daemon=True).start()
        except (OSError, RuntimeError, ValueError) as exc:
            log_error(f"截图失败: {exc}", exc)

    def _handle_selection_cancel(self):
        """Handle selection cancellation."""
        log_debug("已取消区域选择")

    def perform_ocr(self, image_path):
        """Run OCR on a captured image file."""
        log_ok("正在识别文字...")
        try:
            text_list = self.ocr_service.recognize_file(image_path)
            elapsed_seconds = self._current_ocr_elapsed()

            if text_list:
                text = "\n".join(text_list)
                log_ok(f"识别结果:\n{text}")
                pyperclip.copy(text)
                log_ok("已复制到剪贴板")
                log_ok(f"识别完成，共 {len(text_list)} 行，耗时 {elapsed_seconds:.1f} 秒")

                if self.config.get("show_notification", True):
                    message = build_success_message(
                        text,
                        line_count=len(text_list),
                        elapsed_seconds=elapsed_seconds,
                    )
                    self.ui_queue.put(("notification", ("OCR 识别成功", message)))
            else:
                log_warn("未识别到文字")
                if self.config.get("show_notification", True):
                    message = build_empty_result_message(elapsed_seconds=elapsed_seconds)
                    self.ui_queue.put(("notification", ("OCR 识别结果", message)))
        except Exception as exc:
            log_error(f"OCR 识别失败: {exc}", exc)
            if self.config.get("show_notification", True):
                self.ui_queue.put(("notification", ("OCR 识别失败", str(exc))))
        finally:
            self._end_ocr_job()
            self.ui_queue.put(("status_hide", None))
            delete_file_quietly(image_path)

    def _show_notification(self, title, message):
        """Display system notification."""
        show_notification(title, message, enabled=self.config.get("show_notification", True))

    def create_tray_icon(self):
        """Create and start system tray icon."""
        try:
            self.tray_icon = create_tray_icon(
                self.tray_screenshot,
                self.tray_settings,
                self.tray_exit,
            )
            tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            tray_thread.start()
            log_ok("系统托盘已创建")
        except ImportError as exc:
            log_warn(f"请安装 pystray 库: pip install pystray ({exc})")

    def tray_screenshot(self, icon=None, item=None):
        """Tray menu callback for screenshot."""
        log_debug("托盘菜单: 截图")
        self.trigger_screenshot()

    def tray_settings(self, icon=None, item=None):
        """Tray menu callback for settings."""
        log_debug("托盘菜单: 设置")
        self.ui_queue.put(("settings", None))

    def tray_exit(self, icon=None, item=None):
        """Tray menu callback for exit."""
        self.running = False
        self.stop_hotkey_listener()
        if self.tray_icon:
            self.tray_icon.stop()
        if self.root:
            self.root.after(0, self._hide_status_overlay)
            self.root.after(0, self.root.quit)

    def _show_settings_window(self):
        """Open settings window."""
        log_debug("_show_settings_window 被调用")

        def handle_save(new_config, api_key_changed):
            self.config = new_config
            self.ocr_service.config = self.config
            self.save_config()

            self.stop_hotkey_listener()
            self.start_hotkey_listener()

            if api_key_changed and new_config.api_key:
                log_info("API Key 已变更，重新初始化 OCR...")
                self.ocr_service.update_api_key(new_config.api_key)

            log_ok(f"设置已更新: 快捷键={self.config['hotkey']}, 模式={self.config['mode']}")

        try:
            show_settings_window(self.root, self.config, on_save=handle_save)
            log_debug("设置窗口创建完成")
        except (tk.TclError, RuntimeError, ValueError) as exc:
            log_error(f"创建设置窗口失败: {exc}", exc)

    def run(self):
        """Run main event loop."""
        print(f"\n{'=' * 50}")
        print("截图 OCR 工具已启动")
        print(f"快捷键: {self.config.get('hotkey', 'f9').upper()}")
        mode = self.config.get("mode", "long_press")
        if mode == "long_press":
            print(f"模式: 长按触发 ({self.config.get('long_press_time', 1.0)} 秒)")
        else:
            print("模式: 即时触发")
        print(f"{'=' * 50}\n")
        assert self.root is not None
        self.root.mainloop()
