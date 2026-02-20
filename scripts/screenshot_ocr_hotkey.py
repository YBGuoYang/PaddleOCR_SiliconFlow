#!/usr/bin/env python3
"""
截图文字识别工具 - 快捷键版
支持自定义快捷键、长按检测、后台托盘运行
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import pyperclip
import sys
import os
import threading
import tempfile
import json
import time
import queue

# 在导入 tkinter 之前设置 DPI 感知
try:
    from ctypes import windll
    windll.user32.SetProcessDPIAware()
except:
    pass


def get_base_path():
    """获取基础路径，支持 PyInstaller 打包"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的路径
        return os.path.dirname(sys.executable)
    else:
        # 开发环境路径
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_resource_path(relative_path):
    """获取资源文件路径，支持 PyInstaller 打包"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后，资源在 _MEIPASS 目录
        base_path = sys._MEIPASS
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# 添加资源路径到 sys.path（用于导入打包的模块）
if getattr(sys, 'frozen', False):
    # 打包后，从 _MEIPASS 导入模块
    sys.path.insert(0, sys._MEIPASS)
else:
    # 开发环境
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.ocr_config import OCRConfig
from config.siliconflow_ocr import PaddleOCRVL

# 配置文件路径（打包后配置文件在 EXE 同级目录）
CONFIG_FILE = os.path.join(get_base_path(), "config", "hotkey_config.json")

# 默认配置
DEFAULT_CONFIG = {
    "hotkey": "f9",           # 默认快捷键
    "long_press_time": 1.0,   # 长按时间（秒）
    "mode": "long_press",     # 模式: "long_press" 或 "instant"
    "auto_start": False,      # 开机自启
    "show_notification": True, # 显示通知
    "api_key": ""             # API Key（用户配置）
}

# 支持的快捷键列表
SUPPORTED_HOTKEYS = [
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
    "insert", "delete", "home", "end", "page up", "page down",
    "scroll lock", "pause", "print screen",
    "mouse4", "mouse5",  # 鼠标侧键
    "ctrl+a", "ctrl+b", "ctrl+c", "ctrl+d", "ctrl+e", "ctrl+f",
    "ctrl+shift+a", "ctrl+shift+s", "ctrl+shift+d",
    "alt+a", "alt+s", "alt+d", "alt+f",
    "ctrl+alt+a", "ctrl+alt+s",
]


def show_api_key_dialog():
    """显示 API Key 配置对话框"""
    dialog = tk.Tk()
    dialog.title("首次使用配置")
    dialog.geometry("500x400")
    dialog.resizable(False, False)
    
    # 居中显示
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() - 500) // 2
    y = (dialog.winfo_screenheight() - 400) // 2
    dialog.geometry(f"500x400+{x}+{y}")
    
    # 主框架
    main_frame = tk.Frame(dialog, padx=30, pady=20)
    main_frame.pack(fill="both", expand=True)
    
    # 标题
    title_label = tk.Label(main_frame, text="欢迎使用截图 OCR 工具", font=("Microsoft YaHei", 16, "bold"))
    title_label.pack(pady=10)
    
    # 说明
    info_label = tk.Label(main_frame, text="请输入您的硅基流动 API Key 以开始使用", font=("Microsoft YaHei", 10))
    info_label.pack(pady=5)
    
    # API Key 输入框
    frame = tk.Frame(main_frame)
    frame.pack(pady=15, fill="x")
    
    tk.Label(frame, text="API Key:", font=("Microsoft YaHei", 10)).pack(anchor="w")
    api_key_entry = tk.Entry(frame, width=50, font=("Consolas", 10), show="*")
    api_key_entry.pack(fill="x", pady=5)
    
    # 显示/隐藏 API Key
    show_var = tk.BooleanVar(value=False)
    def toggle_show():
        api_key_entry.config(show="" if show_var.get() else "*")
    show_check = tk.Checkbutton(frame, text="显示 API Key", variable=show_var, command=toggle_show)
    show_check.pack(anchor="w")
    
    # 获取链接
    link_label = tk.Label(main_frame, text="没有 API Key? 点击这里获取", font=("Microsoft YaHei", 9), fg="blue", cursor="hand2")
    link_label.pack(pady=10)
    def open_link(event):
        import webbrowser
        webbrowser.open("https://cloud.siliconflow.cn/i/sU0OEWTy")
    link_label.bind("<Button-1>", open_link)
    
    # 结果
    result = {"api_key": None}
    
    def on_confirm():
        api_key = api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror("错误", "请输入 API Key")
            return
        if not api_key.startswith("sk-"):
            messagebox.showwarning("警告", "API Key 格式可能不正确，通常以 'sk-' 开头")
        result["api_key"] = api_key
        dialog.destroy()
    
    def on_cancel():
        dialog.destroy()
    
    # 按钮框架
    btn_frame = tk.Frame(main_frame)
    btn_frame.pack(pady=20)
    
    confirm_btn = tk.Button(btn_frame, text="确定", width=12, height=2, command=on_confirm)
    confirm_btn.pack(side="left", padx=15)
    
    cancel_btn = tk.Button(btn_frame, text="取消", width=12, height=2, command=on_cancel)
    cancel_btn.pack(side="left", padx=15)
    
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)
    dialog.mainloop()
    
    return result["api_key"]


class HotkeyOCR:
    """快捷键截图 OCR 工具"""

    def __init__(self):
        self.config = self.load_config()
        self.running = True
        self.key_pressed = False
        self.key_press_time = 0
        self.pipeline = None
        self.root = None
        self.tray_icon = None
        self.hotkey_hooks = []
        
        # UI 事件队列
        self.ui_queue = queue.Queue()
        
        # 选择窗口状态
        self.selecting = False
        
        # 检查 API Key
        if not self.check_api_key():
            print("[INFO] 用户取消配置，程序退出")
            sys.exit(0)
        
        # 初始化 OCR
        self.init_ocr()
        
        # 创建主窗口（隐藏）
        self.create_main_window()
        
        # 启动热键监听
        self.start_hotkey_listener()
        
        # 创建系统托盘
        self.create_tray_icon()

    def check_api_key(self):
        """检查 API Key 是否已配置"""
        api_key = self.config.get("api_key", "")
        if api_key:
            return True
        
        # 显示配置对话框
        api_key = show_api_key_dialog()
        if api_key:
            self.config["api_key"] = api_key
            self.save_config()
            return True
        return False

    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    for key, value in DEFAULT_CONFIG.items():
                        if key not in config:
                            config[key] = value
                    return config
        except Exception as e:
            print(f"[WARN] 加载配置失败: {e}")
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        """保存配置"""
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"[OK] 配置已保存到: {CONFIG_FILE}")
        except Exception as e:
            print(f"[ERROR] 保存配置失败: {e}")

    def init_ocr(self):
        """初始化 OCR"""
        print("正在初始化 PaddleOCR...")
        # 使用配置中的 API Key
        api_key = self.config.get("api_key", "")
        self.pipeline = PaddleOCRVL(
            vl_rec_backend=OCRConfig.BACKEND,
            vl_rec_server_url=OCRConfig.SERVER_URL,
            vl_rec_api_model_name=OCRConfig.MODEL_NAME,
            vl_rec_api_key=api_key,
        )
        print("[OK] OCR 初始化完成")

    def start_hotkey_listener(self):
        """启动热键监听"""
        try:
            import keyboard
            hotkey = self.config.get('hotkey', 'f9')
            print(f"[OK] 热键监听已启动: {hotkey}")
            
            # 鼠标按键映射 (keyboard 库使用不同的名称)
            mouse_keys = {
                'mouse4': None,    # 鼠标侧键需要特殊处理
                'mouse5': None,
            }
            
            # 如果是鼠标侧键，使用 mouse 模块
            if hotkey in mouse_keys:
                print(f"[WARN] 鼠标侧键 {hotkey} 暂不支持，请使用键盘快捷键")
                return
            
            # 对于组合键，使用 add_hotkey
            if '+' in hotkey:
                # 组合键使用 add_hotkey
                keyboard.add_hotkey(hotkey, self.trigger_screenshot)
                print(f"[OK] 组合键热键已注册: {hotkey}")
            else:
                # 单键使用 on_press_key/on_release_key
                keyboard.on_press_key(hotkey, self.on_key_press)
                keyboard.on_release_key(hotkey, self.on_key_release)
                print(f"[OK] 单键热键已注册: {hotkey}")
            
        except ImportError:
            print("[ERROR] 请安装 keyboard 库: pip install keyboard")
        except Exception as e:
            print(f"[ERROR] 热键监听启动失败: {e}")
            import traceback
            traceback.print_exc()

    def stop_hotkey_listener(self):
        """停止热键监听"""
        try:
            import keyboard
            keyboard.unhook_all()
            keyboard.clear_hotkeys()
            self.hotkey_hooks = []
        except:
            pass

    def on_key_press(self, event):
        """按键按下"""
        if not self.key_pressed:
            self.key_pressed = True
            self.key_press_time = time.time()
            print(f"[DEBUG] 按键按下")
            
            # 即时模式
            if self.config.get('mode') == 'instant':
                self.trigger_screenshot()

    def on_key_release(self, event):
        """按键释放"""
        if self.key_pressed:
            self.key_pressed = False
            press_duration = time.time() - self.key_press_time
            print(f"[DEBUG] 按键释放，持续时间: {press_duration:.2f}s")
            
            # 长按模式
            if self.config.get('mode') == 'long_press':
                long_press_time = self.config.get('long_press_time', 1.0)
                if press_duration >= long_press_time:
                    print(f"[OK] 长按触发 (>= {long_press_time}s)")
                    self.trigger_screenshot()
                else:
                    print(f"[DEBUG] 按键时间不足 ({press_duration:.2f}s < {long_press_time}s)")

    def trigger_screenshot(self):
        """触发截图"""
        print("[OK] 触发区域截图...")
        # 通过队列通知主线程
        self.ui_queue.put(('screenshot', None))

    def create_main_window(self):
        """创建主窗口"""
        self.root = tk.Tk()
        self.root.title("截图OCR工具")
        self.root.geometry("1x1")
        self.root.withdraw()
        
        # 启动队列处理
        self.process_queue()

    def process_queue(self):
        """处理UI队列"""
        try:
            while True:
                task, data = self.ui_queue.get_nowait()
                print(f"[DEBUG] 处理队列任务: {task}")
                if task == 'screenshot':
                    self._create_selection_ui()
                elif task == 'settings':
                    print("[DEBUG] 正在打开设置窗口...")
                    self._show_settings_window()
                    print("[DEBUG] 设置窗口已创建")
                elif task == 'notification':
                    title, message = data
                    self._show_notification(title, message)
        except queue.Empty:
            pass
        
        # 继续轮询
        if self.running:
            self.root.after(100, self.process_queue)

    def do_screenshot(self):
        """执行截图"""
        self.ui_queue.put(('screenshot', None))

    def _create_selection_ui(self):
        """创建选择界面"""
        # 防止重复创建选择窗口
        if self.selecting:
            print("[DEBUG] 已有选择窗口，跳过")
            return
        
        self.selecting = True
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        print(f"[DEBUG] 屏幕尺寸: {screen_width}x{screen_height}")

        # 创建全屏选择窗口
        self.select_window = tk.Toplevel(self.root)
        self.select_window.overrideredirect(True)
        self.select_window.geometry(f"{screen_width}x{screen_height}+0+0")
        self.select_window.attributes('-topmost', True)
        self.select_window.attributes('-alpha', 0.3)

        # 设置暗色背景画布
        self.canvas = tk.Canvas(self.select_window, cursor="crosshair", bg='#1a1a1a', highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # 变量存储选择区域
        self.start_x = None
        self.start_y = None
        self.rect_id = None

        # 绑定事件
        self.select_window.bind("<ButtonPress-1>", self.on_mouse_press)
        self.select_window.bind("<B1-Motion>", self.on_mouse_drag)
        self.select_window.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.select_window.bind("<Escape>", self.cancel_selection)
        
        # 窗口关闭时重置状态
        def on_close():
            self.selecting = False
            try:
                self.select_window.destroy()
            except:
                pass
        
        self.select_window.protocol("WM_DELETE_WINDOW", on_close)

    def on_mouse_press(self, event):
        """鼠标按下"""
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.start_x_win = event.x
        self.start_y_win = event.y

    def on_mouse_drag(self, event):
        """鼠标拖动"""
        if self.start_x is None:
            return
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x_win, self.start_y_win,
            event.x, event.y,
            outline="#00ff00", width=3
        )

    def on_mouse_release(self, event):
        """鼠标释放"""
        if self.start_x is None:
            return

        x1 = min(self.start_x, event.x_root)
        y1 = min(self.start_y, event.y_root)
        x2 = max(self.start_x, event.x_root)
        y2 = max(self.start_y, event.y_root)

        print(f"[DEBUG] 选择区域: ({x1}, {y1}) -> ({x2}, {y2})")

        # 关闭选择窗口并重置状态
        self.selecting = False
        try:
            self.select_window.destroy()
        except:
            pass

        if x2 - x1 < 10 or y2 - y1 < 10:
            print("[DEBUG] 选择区域太小，已取消")
            return

        # 截图
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            print(f"[DEBUG] 截图尺寸: {screenshot.size}")

            # 保存临时文件
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            temp_path = temp_file.name
            screenshot.save(temp_path)

            # 执行 OCR
            threading.Thread(target=self.perform_ocr, args=(temp_path,), daemon=True).start()

        except Exception as e:
            print(f"[ERROR] 截图失败: {e}")

    def cancel_selection(self, event=None):
        """取消选择"""
        self.selecting = False
        if hasattr(self, 'select_window'):
            try:
                self.select_window.destroy()
            except:
                pass

    def perform_ocr(self, image_path):
        """执行 OCR"""
        print("[OK] 正在识别文字...")
        try:
            results = self.pipeline.predict(image_path)

            # 提取文字
            text_list = []
            for result in results:
                parsing_res = result.get('parsing_res_list', [])
                for item in parsing_res:
                    content = getattr(item, 'content', '')
                    if content:
                        text_list.append(content)

            if text_list:
                text = "\n".join(text_list)
                print(f"[OK] 识别结果:\n{text}")
                
                # 复制到剪贴板
                pyperclip.copy(text)
                print("[OK] 已复制到剪贴板")
                
                # 显示通知（前20个字符）
                preview = text.replace('\n', ' ')[:20]
                if len(text) > 20:
                    preview += "..."
                self.ui_queue.put(('notification', ("OCR 识别成功", preview)))
            else:
                print("[WARN] 未识别到文字")
                self.ui_queue.put(('notification', ("OCR 识别结果", "未识别到文字")))

            # 清理临时文件
            try:
                os.unlink(image_path)
            except:
                pass

        except Exception as e:
            print(f"[ERROR] OCR 识别失败: {e}")
            import traceback
            traceback.print_exc()

    def _show_notification(self, title, message):
        """显示通知"""
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name="截图OCR",
                timeout=3
            )
        except ImportError:
            print(f"[通知] {title}: {message}")
        except Exception as e:
            print(f"[WARN] 显示通知失败: {e}")

    def create_tray_icon(self):
        """创建系统托盘图标"""
        try:
            import pystray
            
            # 创建图标
            icon_image = self.create_icon_image()
            
            # 创建菜单
            menu = pystray.Menu(
                pystray.MenuItem("📷 截图 OCR", self.tray_screenshot, default=True),
                pystray.MenuItem("⚙️ 设置", self.tray_settings),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("❌ 退出", self.tray_exit)
            )
            
            self.tray_icon = pystray.Icon("screenshot_ocr", icon_image, "截图OCR工具", menu)
            
            # 在后台线程运行托盘
            tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            tray_thread.start()
            print("[OK] 系统托盘已创建")
            
        except ImportError as e:
            print(f"[WARN] 请安装 pystray 库: pip install pystray ({e})")

    def create_icon_image(self):
        """创建托盘图标 - 使用emoji风格"""
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        
        # 绘制圆角矩形背景
        def round_rectangle(draw, xy, radius, fill, outline=None, width=1):
            """绘制圆角矩形"""
            x1, y1, x2, y2 = xy
            draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
            draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
            draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=fill)
            draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=fill)
            draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=fill)
            draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=fill)
        
        # 绘制渐变蓝色背景
        round_rectangle(dc, [4, 4, 60, 60], 12, fill=(65, 105, 225))  # 皇家蓝
        
        # 绘制文字 "OCR"
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            try:
                font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 24)
            except:
                font = ImageFont.load_default()
        
        # 居中绘制文字
        text = "OCR"
        bbox = dc.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2 - 2
        
        # 绘制白色文字
        dc.text((x, y), text, fill=(255, 255, 255), font=font)
        
        # 添加一个小相机图标效果
        dc.rectangle([8, 50, 16, 54], fill=(255, 255, 255))  # 小装饰
        
        return image

    def tray_screenshot(self, icon=None, item=None):
        """托盘菜单 - 截图"""
        print("[DEBUG] 托盘菜单: 截图")
        self.trigger_screenshot()

    def tray_settings(self, icon=None, item=None):
        """托盘菜单 - 设置"""
        print("[DEBUG] 托盘菜单: 设置")
        self.ui_queue.put(('settings', None))
        print("[DEBUG] 已将设置任务放入队列")

    def tray_exit(self, icon=None, item=None):
        """托盘菜单 - 退出"""
        self.running = False
        if self.tray_icon:
            self.tray_icon.stop()
        if self.root:
            self.root.quit()

    def _show_settings_window(self):
        """显示设置窗口"""
        print("[DEBUG] _show_settings_window 被调用")
        
        try:
            # 确保主窗口存在
            if self.root is None:
                print("[ERROR] 主窗口不存在")
                return
            
            settings_win = tk.Toplevel(self.root)
            settings_win.title("截图OCR 设置")
            settings_win.geometry("500x850")
            settings_win.resizable(False, False)
            
            # 居中显示
            settings_win.update_idletasks()
            x = (settings_win.winfo_screenwidth() - 500) // 2
            y = (settings_win.winfo_screenheight() - 850) // 2
            settings_win.geometry(f"+{x}+{y}")
            
            # 确保窗口显示在最前面
            settings_win.attributes('-topmost', True)
            settings_win.focus_force()

            # 主框架
            main_frame = tk.Frame(settings_win, padx=20, pady=20)
            main_frame.pack(fill="both", expand=True)

            # 标题
            title_label = tk.Label(main_frame, text="⚙️ 截图OCR 设置", font=("Arial", 14, "bold"))
            title_label.pack(pady=(0, 15))

            # API Key 设置
            api_frame = tk.LabelFrame(main_frame, text="API 设置", padx=10, pady=10)
            api_frame.pack(fill="x", pady=5)

            tk.Label(api_frame, text="硅基流动 API Key:").pack(anchor="w")
            api_key_var = tk.StringVar(value=self.config.get('api_key', ''))
            api_key_entry = tk.Entry(api_frame, textvariable=api_key_var, width=50, show="*")
            api_key_entry.pack(fill="x", pady=5)
            
            # 显示/隐藏 API Key
            show_api_var = tk.BooleanVar(value=False)
            def toggle_api_key():
                api_key_entry.config(show="" if show_api_var.get() else "*")
            tk.Checkbutton(api_frame, text="显示 API Key", variable=show_api_var, command=toggle_api_key).pack(anchor="w")
            
            # 获取链接
            link_label = tk.Label(api_frame, text="没有 API Key? 点击这里获取", fg="blue", cursor="hand2")
            link_label.pack(anchor="w")
            def open_link(event):
                import webbrowser
                webbrowser.open("https://cloud.siliconflow.cn/i/sU0OEWTy")
            link_label.bind("<Button-1>", open_link)

            # 快捷键设置
            hotkey_frame = tk.LabelFrame(main_frame, text="快捷键设置", padx=10, pady=10)
            hotkey_frame.pack(fill="x", pady=5)

            tk.Label(hotkey_frame, text="触发快捷键:").grid(row=0, column=0, sticky="w", pady=5)
            
            hotkey_var = tk.StringVar(value=self.config.get('hotkey', 'f9'))
            hotkey_combo = ttk.Combobox(hotkey_frame, textvariable=hotkey_var, width=25, state="readonly")
            hotkey_combo['values'] = SUPPORTED_HOTKEYS
            hotkey_combo.grid(row=0, column=1, padx=10, pady=5)
            hotkey_combo.set(self.config.get('hotkey', 'f9'))  # 确保显示当前值
            
            tk.Label(hotkey_frame, text="支持鼠标侧键(mouse4/mouse5)", fg="gray").grid(row=1, column=0, columnspan=2, sticky="w")

            # 触发模式设置
            mode_frame = tk.LabelFrame(main_frame, text="触发模式", padx=10, pady=10)
            mode_frame.pack(fill="x", pady=5)

            mode_var = tk.StringVar(value=self.config.get('mode', 'long_press'))
            tk.Radiobutton(mode_frame, text="长按触发 (按住指定时间后触发)", variable=mode_var, value="long_press").pack(anchor="w")
            tk.Radiobutton(mode_frame, text="即时触发 (按下立即触发)", variable=mode_var, value="instant").pack(anchor="w")

            # 长按时间设置
            time_frame = tk.Frame(mode_frame)
            time_frame.pack(fill="x", pady=10)
            
            tk.Label(time_frame, text="长按时间:").pack(side="left")
            long_press_var = tk.DoubleVar(value=self.config.get('long_press_time', 1.0))
            
            time_scale = tk.Scale(time_frame, from_=0.5, to=2.0, resolution=0.1,
                                  variable=long_press_var, orient="horizontal", length=200)
            time_scale.pack(side="left", padx=10)

            # 通知设置
            notify_frame = tk.LabelFrame(main_frame, text="通知设置", padx=10, pady=10)
            notify_frame.pack(fill="x", pady=5)

            show_notification_var = tk.BooleanVar(value=self.config.get('show_notification', True))
            tk.Checkbutton(notify_frame, text="识别成功时显示系统通知", variable=show_notification_var).pack(anchor="w")

            # 当前设置显示
            current_frame = tk.LabelFrame(main_frame, text="当前设置", padx=10, pady=10)
            current_frame.pack(fill="x", pady=5)
            
            current_text = f"快捷键: {self.config.get('hotkey', 'f9').upper()}\n"
            current_text += f"模式: {'长按' if self.config.get('mode') == 'long_press' else '即时'}\n"
            current_text += f"长按时间: {self.config.get('long_press_time', 1.0)}秒"
            current_label = tk.Label(current_frame, text=current_text, justify="left")
            current_label.pack(anchor="w")

            # 按钮框架 - 使用 pack 而不是 side
            btn_frame = tk.Frame(main_frame)
            btn_frame.pack(pady=20, fill="x")

            def save_settings():
                print("[DEBUG] save_settings 函数被调用")
                try:
                    new_api_key = api_key_var.get().strip()
                    new_hotkey = hotkey_var.get().lower()
                    new_mode = mode_var.get()
                    new_time = long_press_var.get()
                    new_notify = show_notification_var.get()
                    
                    print(f"[DEBUG] 保存设置: hotkey={new_hotkey}, mode={new_mode}, time={new_time}, notify={new_notify}")
                    
                    # 检查 API Key 是否变更
                    old_api_key = self.config.get('api_key', '')
                    api_key_changed = new_api_key != old_api_key
                    
                    self.config['api_key'] = new_api_key
                    self.config['hotkey'] = new_hotkey
                    self.config['mode'] = new_mode
                    self.config['long_press_time'] = new_time
                    self.config['show_notification'] = new_notify
                    self.save_config()
                    
                    # 更新当前设置显示
                    current_text = f"快捷键: {new_hotkey.upper()}\n"
                    current_text += f"模式: {'长按' if new_mode == 'long_press' else '即时'}\n"
                    current_text += f"长按时间: {new_time}秒"
                    current_label.config(text=current_text)
                    
                    # 重新注册热键
                    self.stop_hotkey_listener()
                    self.start_hotkey_listener()
                    
                    # 如果 API Key 变更，重新初始化 OCR
                    if api_key_changed and new_api_key:
                        print("[INFO] API Key 已变更，重新初始化 OCR...")
                        self.init_ocr()
                    
                    # 显示保存成功提示
                    save_btn.config(text="✓ 已保存", bg="#90EE90")
                    settings_win.after(1500, lambda: save_btn.config(text="保存设置", bg="SystemButtonFace"))
                    
                    print(f"[OK] 设置已更新: 快捷键={self.config['hotkey']}, 模式={self.config['mode']}")
                except Exception as e:
                    print(f"[ERROR] 保存设置失败: {e}")
                    import traceback
                    traceback.print_exc()

            # 保存按钮
            save_btn = tk.Button(btn_frame, text="保存设置", command=save_settings, width=20, height=2)
            save_btn.pack(pady=5)
            print(f"[DEBUG] 保存按钮已创建")
            
            # 关闭按钮
            def on_close():
                print("[DEBUG] 关闭按钮被点击")
                settings_win.destroy()
            
            close_btn = tk.Button(btn_frame, text="关闭", command=on_close, width=20, height=2)
            close_btn.pack(pady=5)
            
            print("[DEBUG] 设置窗口创建完成")
            
        except Exception as e:
            print(f"[ERROR] 创建设置窗口失败: {e}")
            import traceback
            traceback.print_exc()

    def run(self):
        """运行程序"""
        print(f"\n{'='*50}")
        print("📷 截图OCR工具已启动")
        print(f"⌨️ 快捷键: {self.config.get('hotkey', 'f9').upper()}")
        mode = self.config.get('mode', 'long_press')
        if mode == 'long_press':
            print(f"⏱️ 模式: 长按触发 (按住 {self.config.get('long_press_time', 1.0)} 秒)")
        else:
            print("⚡ 模式: 即时触发")
        print(f"{'='*50}\n")
        
        # 运行主循环
        self.root.mainloop()


if __name__ == "__main__":
    app = HotkeyOCR()
    app.run()
