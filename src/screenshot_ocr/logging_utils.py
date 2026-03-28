"""Small logging helpers for consistent terminal output."""

from __future__ import annotations

import traceback


def _log(level: str, message: str) -> None:
    print(f"[{level}] {message}")


def log_debug(message: str) -> None:
    _log("DEBUG", message)


def log_info(message: str) -> None:
    _log("INFO", message)


def log_ok(message: str) -> None:
    _log("OK", message)


def log_warn(message: str) -> None:
    _log("WARN", message)


def log_error(message: str, exc: Exception | None = None) -> None:
    _log("ERROR", message)
    if exc is not None:
        traceback.print_exc()
