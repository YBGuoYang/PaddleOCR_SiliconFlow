"""Notification helpers."""

from __future__ import annotations

from .logging_utils import log_warn


def build_notification_preview(text: str, limit: int = 20) -> str:
    normalized = text.replace("\n", " ").strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit] + "..."


def format_elapsed_text(elapsed_seconds: float) -> str:
    elapsed_seconds = max(0.0, elapsed_seconds)
    return f"{elapsed_seconds:.1f} 秒"


def build_busy_message() -> str:
    return "上一张截图仍在识别，请稍候"


def build_success_message(text: str, *, line_count: int, elapsed_seconds: float) -> str:
    preview = build_notification_preview(text, limit=36)
    return f"共 {line_count} 行，耗时 {format_elapsed_text(elapsed_seconds)}\n{preview}"


def build_empty_result_message(*, elapsed_seconds: float) -> str:
    return f"未识别到文字，耗时 {format_elapsed_text(elapsed_seconds)}"


def show_notification(title: str, message: str, *, enabled: bool = True, app_name: str = "截图OCR", timeout: int = 3) -> bool:
    """Display a desktop notification when enabled."""
    if not enabled:
        return False

    try:
        from plyer import notification

        notification.notify(
            title=title,
            message=message,
            app_name=app_name,
            timeout=timeout,
        )
        return True
    except ImportError:
        print(f"[通知] {title}: {message}")
        return False
    except (RuntimeError, OSError) as exc:
        log_warn(f"显示通知失败: {exc}")
        return False
