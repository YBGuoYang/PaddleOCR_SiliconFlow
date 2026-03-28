"""Selection overlay used for region capture."""

from __future__ import annotations

import tkinter as tk
from typing import Callable

from .logging_utils import log_debug


def normalize_region(start_x: int, start_y: int, end_x: int, end_y: int) -> tuple[int, int, int, int]:
    return (
        min(start_x, end_x),
        min(start_y, end_y),
        max(start_x, end_x),
        max(start_y, end_y),
    )


class RegionSelector:
    """Manage a fullscreen selection overlay and report the chosen region."""

    def __init__(
        self,
        *,
        on_region_selected: Callable[[tuple[int, int, int, int]], None],
        on_cancel: Callable[[], None] | None = None,
    ):
        self.on_region_selected = on_region_selected
        self.on_cancel = on_cancel
        self.selecting = False
        self.select_window: tk.Toplevel | None = None
        self.canvas: tk.Canvas | None = None
        self.rect_id: int | None = None
        self.start_x: int | None = None
        self.start_y: int | None = None
        self.start_x_win: int | None = None
        self.start_y_win: int | None = None

    def open(self, root: tk.Misc) -> bool:
        if self.selecting:
            log_debug("已有选择窗口，跳过")
            return False

        self.selecting = True
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        log_debug(f"屏幕尺寸: {screen_width}x{screen_height}")

        self.select_window = tk.Toplevel(root)
        self.select_window.overrideredirect(True)
        self.select_window.geometry(f"{screen_width}x{screen_height}+0+0")
        self.select_window.attributes("-topmost", True)
        self.select_window.attributes("-alpha", 0.3)

        self.canvas = tk.Canvas(self.select_window, cursor="crosshair", bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.start_x = None
        self.start_y = None
        self.rect_id = None

        self.select_window.bind("<ButtonPress-1>", self.on_mouse_press)
        self.select_window.bind("<B1-Motion>", self.on_mouse_drag)
        self.select_window.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.select_window.bind("<Escape>", self.cancel)
        self.select_window.protocol("WM_DELETE_WINDOW", self.cancel)
        return True

    def on_mouse_press(self, event: tk.Event) -> None:
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.start_x_win = event.x
        self.start_y_win = event.y

    def on_mouse_drag(self, event: tk.Event) -> None:
        if self.start_x is None or self.canvas is None:
            return
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x_win,
            self.start_y_win,
            event.x,
            event.y,
            outline="#00ff00",
            width=3,
        )

    def on_mouse_release(self, event: tk.Event) -> None:
        if self.start_x is None or self.start_y is None:
            return

        region = normalize_region(self.start_x, self.start_y, event.x_root, event.y_root)
        log_debug(f"选择区域: {region}")
        self.close()
        self.on_region_selected(region)

    def cancel(self, _event: tk.Event | None = None) -> None:
        self.close()
        if self.on_cancel is not None:
            self.on_cancel()

    def close(self) -> None:
        self.selecting = False
        if self.select_window is not None:
            try:
                self.select_window.destroy()
            except tk.TclError:
                pass
        self.select_window = None
        self.canvas = None
        self.rect_id = None
