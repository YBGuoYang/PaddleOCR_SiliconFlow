"""Path helpers shared by runtime scripts and packaged builds."""

from __future__ import annotations

import os
import sys


def get_project_root() -> str:
    """Return the writable application root."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_resource_root() -> str:
    """Return the resource root used by PyInstaller and source runs."""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS  # type: ignore[attr-defined]
    return get_project_root()


def get_config_dir() -> str:
    return os.path.join(get_project_root(), "config")


def get_resource_path(relative_path: str) -> str:
    return os.path.join(get_resource_root(), relative_path)
