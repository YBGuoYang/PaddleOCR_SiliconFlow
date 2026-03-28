"""Hotkey registration and press-duration handling."""

from __future__ import annotations

import time
from typing import Any, Callable

from .logging_utils import log_debug, log_ok

SUPPORTED_HOTKEYS = [
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
    "insert", "delete", "home", "end", "page up", "page down",
    "scroll lock", "pause", "print screen",
    "ctrl+a", "ctrl+b", "ctrl+c", "ctrl+d", "ctrl+e", "ctrl+f",
    "ctrl+shift+a", "ctrl+shift+s", "ctrl+shift+d",
    "alt+a", "alt+s", "alt+d", "alt+f",
    "ctrl+alt+a", "ctrl+alt+s",
]

UNSUPPORTED_HOTKEYS = {"mouse4", "mouse5"}
DEFAULT_HOTKEY = "f9"


def normalize_hotkey(hotkey: str | None) -> str:
    candidate = str(hotkey or "").lower().strip() or DEFAULT_HOTKEY
    if candidate in SUPPORTED_HOTKEYS:
        return candidate
    return DEFAULT_HOTKEY


class HotkeyListener:
    """Manage keyboard listeners and long-press behavior."""

    def __init__(
        self,
        *,
        hotkey: str,
        mode: str,
        long_press_time: float,
        on_trigger: Callable[[], None],
        keyboard_module: Any | None = None,
        time_module: Any | None = None,
    ):
        self.hotkey = normalize_hotkey(hotkey)
        self.mode = mode
        self.long_press_time = long_press_time
        self.on_trigger = on_trigger
        self.keyboard_module = keyboard_module
        self.time_module = time_module or time
        self.key_pressed = False
        self.key_press_time = 0.0

    def _keyboard(self):
        if self.keyboard_module is not None:
            return self.keyboard_module
        import keyboard

        self.keyboard_module = keyboard
        return keyboard

    def start(self) -> None:
        keyboard = self._keyboard()
        log_ok(f"热键监听已启动: {self.hotkey}")
        if "+" in self.hotkey:
            keyboard.add_hotkey(self.hotkey, self.on_trigger)
            log_ok(f"组合键热键已注册: {self.hotkey}")
        else:
            keyboard.on_press_key(self.hotkey, self.on_key_press)
            keyboard.on_release_key(self.hotkey, self.on_key_release)
            log_ok(f"单键热键已注册: {self.hotkey}")

    def stop(self) -> None:
        keyboard = self._keyboard()
        keyboard.unhook_all()
        keyboard.clear_hotkeys()

    def on_key_press(self, _event: Any) -> None:
        if self.key_pressed:
            return
        self.key_pressed = True
        self.key_press_time = self.time_module.time()
        log_debug("按键按下")
        if self.mode == "instant":
            self.on_trigger()

    def on_key_release(self, _event: Any) -> None:
        if not self.key_pressed:
            return
        self.key_pressed = False
        press_duration = self.time_module.time() - self.key_press_time
        log_debug(f"按键释放，持续时间: {press_duration:.2f}s")
        if self.mode != "long_press":
            return
        if press_duration >= self.long_press_time:
            log_ok(f"长按触发 (>= {self.long_press_time}s)")
            self.on_trigger()
        else:
            log_debug(f"按键时间不足 ({press_duration:.2f}s < {self.long_press_time}s)")
