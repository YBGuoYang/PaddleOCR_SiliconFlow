"""Tk dialogs used by the current tray application."""

from __future__ import annotations

import tkinter as tk
import traceback
import webbrowser
from tkinter import messagebox, ttk
from typing import Callable

from .config import AppConfig, SUPPORTED_HOTKEYS
from .logging_utils import log_debug, log_error


def _center_window(window: tk.Misc, width: int, height: int) -> None:
    window.update_idletasks()
    x = (window.winfo_screenwidth() - width) // 2
    y = (window.winfo_screenheight() - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


def build_current_settings_text(config: AppConfig) -> str:
    mode_text = "长按" if config.mode == "long_press" else "即时"
    return (
        f"快捷键: {config.hotkey.upper()}\n"
        f"模式: {mode_text}\n"
        f"长按时间: {config.long_press_time}秒"
    )


def show_api_key_dialog() -> str | None:
    """Show the first-run API key dialog."""
    dialog = tk.Tk()
    dialog.title("首次使用配置")
    dialog.resizable(False, False)
    _center_window(dialog, 500, 400)

    main_frame = tk.Frame(dialog, padx=30, pady=20)
    main_frame.pack(fill="both", expand=True)

    tk.Label(main_frame, text="欢迎使用截图 OCR 工具", font=("Microsoft YaHei", 16, "bold")).pack(pady=10)
    tk.Label(main_frame, text="请输入您的硅基流动 API Key 以开始使用", font=("Microsoft YaHei", 10)).pack(pady=5)

    frame = tk.Frame(main_frame)
    frame.pack(pady=15, fill="x")

    tk.Label(frame, text="API Key:", font=("Microsoft YaHei", 10)).pack(anchor="w")
    api_key_entry = tk.Entry(frame, width=50, font=("Consolas", 10), show="*")
    api_key_entry.pack(fill="x", pady=5)

    show_var = tk.BooleanVar(value=False)

    def toggle_show() -> None:
        api_key_entry.config(show="" if show_var.get() else "*")

    tk.Checkbutton(frame, text="显示 API Key", variable=show_var, command=toggle_show).pack(anchor="w")

    link_label = tk.Label(
        main_frame,
        text="没有 API Key? 点击这里获取",
        font=("Microsoft YaHei", 9),
        fg="blue",
        cursor="hand2",
    )
    link_label.pack(pady=10)
    link_label.bind("<Button-1>", lambda _event: webbrowser.open("https://cloud.siliconflow.cn/i/sU0OEWTy"))

    result: dict[str, str | None] = {"api_key": None}

    def on_confirm() -> None:
        api_key = api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror("错误", "请输入 API Key")
            return
        if not api_key.startswith("sk-"):
            messagebox.showwarning("警告", "API Key 格式可能不正确，通常以 'sk-' 开头")
        result["api_key"] = api_key
        dialog.destroy()

    btn_frame = tk.Frame(main_frame)
    btn_frame.pack(pady=20)
    tk.Button(btn_frame, text="确定", width=12, height=2, command=on_confirm).pack(side="left", padx=15)
    tk.Button(btn_frame, text="取消", width=12, height=2, command=dialog.destroy).pack(side="left", padx=15)

    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
    dialog.mainloop()
    return result["api_key"]


def show_settings_window(
    root: tk.Misc | None,
    config: AppConfig,
    *,
    on_save: Callable[[AppConfig, bool], None],
) -> None:
    """Create the settings window and call on_save with a new config snapshot."""
    if root is None:
        log_error("主窗口不存在")
        return

    settings_win = tk.Toplevel(root)
    settings_win.title("截图OCR 设置")
    settings_win.resizable(False, False)
    _center_window(settings_win, 500, 850)
    settings_win.attributes("-topmost", True)
    settings_win.focus_force()

    main_frame = tk.Frame(settings_win, padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)

    tk.Label(main_frame, text="⚙️ 截图OCR 设置", font=("Arial", 14, "bold")).pack(pady=(0, 15))

    api_frame = tk.LabelFrame(main_frame, text="API 设置", padx=10, pady=10)
    api_frame.pack(fill="x", pady=5)

    tk.Label(api_frame, text="硅基流动 API Key:").pack(anchor="w")
    api_key_var = tk.StringVar(value=config.api_key)
    api_key_entry = tk.Entry(api_frame, textvariable=api_key_var, width=50, show="*")
    api_key_entry.pack(fill="x", pady=5)

    show_api_var = tk.BooleanVar(value=False)

    def toggle_api_key() -> None:
        api_key_entry.config(show="" if show_api_var.get() else "*")

    tk.Checkbutton(api_frame, text="显示 API Key", variable=show_api_var, command=toggle_api_key).pack(anchor="w")

    link_label = tk.Label(api_frame, text="没有 API Key? 点击这里获取", fg="blue", cursor="hand2")
    link_label.pack(anchor="w")
    link_label.bind("<Button-1>", lambda _event: webbrowser.open("https://cloud.siliconflow.cn/i/sU0OEWTy"))

    hotkey_frame = tk.LabelFrame(main_frame, text="快捷键设置", padx=10, pady=10)
    hotkey_frame.pack(fill="x", pady=5)
    tk.Label(hotkey_frame, text="触发快捷键:").grid(row=0, column=0, sticky="w", pady=5)

    hotkey_var = tk.StringVar(value=config.hotkey)
    hotkey_combo = ttk.Combobox(hotkey_frame, textvariable=hotkey_var, width=25, state="readonly")
    hotkey_combo["values"] = SUPPORTED_HOTKEYS
    hotkey_combo.grid(row=0, column=1, padx=10, pady=5)
    hotkey_combo.set(config.hotkey)
    tk.Label(hotkey_frame, text="当前仅支持键盘快捷键", fg="gray").grid(row=1, column=0, columnspan=2, sticky="w")

    mode_frame = tk.LabelFrame(main_frame, text="触发模式", padx=10, pady=10)
    mode_frame.pack(fill="x", pady=5)

    mode_var = tk.StringVar(value=config.mode)
    tk.Radiobutton(mode_frame, text="长按触发 (按住指定时间后触发)", variable=mode_var, value="long_press").pack(anchor="w")
    tk.Radiobutton(mode_frame, text="即时触发 (按下立即触发)", variable=mode_var, value="instant").pack(anchor="w")

    time_frame = tk.Frame(mode_frame)
    time_frame.pack(fill="x", pady=10)
    tk.Label(time_frame, text="长按时间:").pack(side="left")
    long_press_var = tk.DoubleVar(value=config.long_press_time)
    tk.Scale(
        time_frame,
        from_=0.5,
        to=2.0,
        resolution=0.1,
        variable=long_press_var,
        orient="horizontal",
        length=200,
    ).pack(side="left", padx=10)

    notify_frame = tk.LabelFrame(main_frame, text="通知设置", padx=10, pady=10)
    notify_frame.pack(fill="x", pady=5)
    show_notification_var = tk.BooleanVar(value=config.show_notification)
    tk.Checkbutton(notify_frame, text="识别成功时显示系统通知", variable=show_notification_var).pack(anchor="w")

    current_frame = tk.LabelFrame(main_frame, text="当前设置", padx=10, pady=10)
    current_frame.pack(fill="x", pady=5)
    current_label = tk.Label(current_frame, text=build_current_settings_text(config), justify="left")
    current_label.pack(anchor="w")

    btn_frame = tk.Frame(main_frame)
    btn_frame.pack(pady=20, fill="x")

    save_btn = tk.Button(btn_frame, text="保存设置", width=20, height=2)
    save_btn.pack(pady=5)

    def save_settings() -> None:
        log_debug("save_settings 函数被调用")
        try:
            new_config = config.clone()
            new_config.api_key = api_key_var.get().strip()
            new_config.hotkey = hotkey_var.get().lower()
            new_config.mode = mode_var.get()
            new_config.long_press_time = long_press_var.get()
            new_config.show_notification = show_notification_var.get()
            new_config.normalize()

            log_debug(
                "保存设置: "
                f"hotkey={new_config.hotkey}, mode={new_config.mode}, "
                f"time={new_config.long_press_time}, notify={new_config.show_notification}"
            )

            api_key_changed = new_config.api_key != config.api_key
            current_label.config(text=build_current_settings_text(new_config))
            on_save(new_config, api_key_changed)

            save_btn.config(text="✓ 已保存", bg="#90EE90")
            settings_win.after(1500, lambda: save_btn.config(text="保存设置", bg="SystemButtonFace"))
        except (ValueError, RuntimeError, tk.TclError) as exc:
            log_error(f"保存设置失败: {exc}")
            traceback.print_exc()

    save_btn.config(command=save_settings)

    def on_close() -> None:
        log_debug("关闭按钮被点击")
        settings_win.destroy()

    tk.Button(btn_frame, text="关闭", command=on_close, width=20, height=2).pack(pady=5)
