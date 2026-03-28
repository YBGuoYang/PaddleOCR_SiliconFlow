"""Configuration loading and persistence."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Any

from .hotkeys import SUPPORTED_HOTKEYS, UNSUPPORTED_HOTKEYS, normalize_hotkey
from .logging_utils import log_warn
from .paths import get_config_dir


@dataclass
class AppConfig:
    hotkey: str = "f9"
    long_press_time: float = 1.0
    mode: str = "long_press"
    auto_start: bool = False
    show_notification: bool = True
    api_key: str = ""

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def clone(self) -> "AppConfig":
        return AppConfig.from_dict(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppConfig":
        config = cls()
        for field_name in config.to_dict():
            if field_name in data:
                setattr(config, field_name, data[field_name])
        config.normalize()
        return config

    def normalize(self) -> None:
        original_hotkey = str(self.hotkey).lower().strip() or "f9"
        self.hotkey = normalize_hotkey(original_hotkey)
        if original_hotkey in UNSUPPORTED_HOTKEYS:
            log_warn(f"快捷键 {original_hotkey} 当前未实现，已回退到 {self.hotkey}")
        elif original_hotkey != self.hotkey:
            log_warn(f"快捷键 {original_hotkey} 不受支持，已回退到 {self.hotkey}")
        self.mode = str(self.mode).strip() or "long_press"
        if self.mode not in {"long_press", "instant"}:
            self.mode = "long_press"

        try:
            self.long_press_time = float(self.long_press_time)
        except (TypeError, ValueError):
            self.long_press_time = 1.0
        self.long_press_time = min(2.0, max(0.5, self.long_press_time))

        self.auto_start = bool(self.auto_start)
        self.show_notification = bool(self.show_notification)
        self.api_key = str(self.api_key).strip()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


DEFAULT_CONFIG = AppConfig()


def get_config_path() -> str:
    return os.path.join(get_config_dir(), "hotkey_config.json")


def load_app_config(config_path: str | None = None) -> AppConfig:
    config_path = config_path or get_config_path()
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            raw_config = json.load(file)
        if not isinstance(raw_config, dict):
            raise ValueError("Config root must be an object")
        return AppConfig.from_dict(raw_config)
    except FileNotFoundError:
        return AppConfig()
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        log_warn(f"加载配置失败: {exc}")
        return AppConfig()


def save_app_config(config: AppConfig, config_path: str | None = None) -> str:
    config_path = config_path or get_config_path()
    config.normalize()
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(config.to_dict(), file, indent=2, ensure_ascii=False)
    return config_path
