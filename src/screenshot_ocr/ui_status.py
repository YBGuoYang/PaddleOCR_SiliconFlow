"""Transient status overlay for user-facing progress feedback."""

from __future__ import annotations

import tkinter as tk


class StatusToast:
    """Show short-lived or sticky status messages above the desktop."""

    def __init__(self, root: tk.Misc):
        self.root = root
        self.window: tk.Toplevel | None = None
        self.label: tk.Label | None = None
        self.hide_after_id: str | None = None

    def show(
        self,
        message: str,
        *,
        duration_ms: int | None = 1500,
        bg: str = "#1f2937",
        fg: str = "#ffffff",
    ) -> None:
        if not message:
            self.hide()
            return

        if self.window is None or self.label is None:
            self.window = tk.Toplevel(self.root)
            self.window.overrideredirect(True)
            self.window.attributes("-topmost", True)
            self.window.attributes("-alpha", 0.94)
            self.label = tk.Label(
                self.window,
                text=message,
                bg=bg,
                fg=fg,
                padx=18,
                pady=10,
                font=("Microsoft YaHei UI", 10, "bold"),
            )
            self.label.pack()
        else:
            self.label.configure(text=message, bg=bg, fg=fg)

        self.window.configure(bg=bg)
        self._position()
        self.window.deiconify()
        self.window.lift()

        if self.hide_after_id is not None:
            self.root.after_cancel(self.hide_after_id)
            self.hide_after_id = None

        if duration_ms is not None:
            self.hide_after_id = self.root.after(duration_ms, self.hide)

    def hide(self) -> None:
        if self.hide_after_id is not None:
            self.root.after_cancel(self.hide_after_id)
            self.hide_after_id = None
        if self.window is not None:
            self.window.withdraw()

    def _position(self) -> None:
        if self.window is None:
            return
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        screen_width = self.window.winfo_screenwidth()
        x = (screen_width - width) // 2
        y = 80
        self.window.geometry(f"{width}x{height}+{x}+{y}")
