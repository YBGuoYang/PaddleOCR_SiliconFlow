#!/usr/bin/env python3
"""
截图文字识别工具 - 简化版
使用硅基流动在线 API,无需下载本地模型
功能:截图 → OCR 识别 → 复制到剪贴板
"""

import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from PIL import Image, ImageTk
import pyperclip
import sys
import os
import threading
import tempfile

# 在导入 tkinter 之前设置 DPI 感知
# 这样所有坐标都将使用物理像素
try:
    from ctypes import windll
    windll.user32.SetProcessDPIAware()
except:
    pass

# 添加项目路径到父目录
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.ocr_config import OCRConfig
from config.siliconflow_ocr import PaddleOCRVL


class ScreenshotOCR:
    """截图 OCR 工具"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("截图文字识别")
        self.root.geometry("600x500")

        # 初始化 OCR (使用在线 API,无需本地模型)
        print("正在初始化 PaddleOCR...")
        self.pipeline = PaddleOCRVL(
            vl_rec_backend=OCRConfig.BACKEND,
            vl_rec_server_url=OCRConfig.SERVER_URL,
            vl_rec_api_model_name=OCRConfig.MODEL_NAME,
            vl_rec_api_key=OCRConfig.API_KEY,
        )
        print("[OK] 初始化完成")

        # 创建界面
        self.create_ui()

    def create_ui(self):
        """创建用户界面"""

        # 标题
        title_label = tk.Label(
            self.root,
            text="🖼️ 截图文字识别",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=20)

        # 说明
        info_label = tk.Label(
            self.root,
            text="使用硅基流动在线 API (PaddleOCR-VL-1.5)",
            font=("Arial", 9),
            fg="gray"
        )
        info_label.pack(pady=5)

        # 按钮
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        # 全屏截图按钮
        full_screen_btn = ttk.Button(
            btn_frame,
            text="全屏截图",
            command=self.full_screen_capture,
            width=20
        )
        full_screen_btn.pack(pady=5)

        # 区域选择按钮
        region_btn = ttk.Button(
            btn_frame,
            text="选择区域截图",
            command=self.region_select,
            width=20
        )
        region_btn.pack(pady=5)

        # 结果显示区域
        result_frame = ttk.LabelFrame(self.root, text="识别结果")
        result_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # 尝试使用中文字体
        fonts_to_try = [
            ("Microsoft YaHei UI", 10),
            ("SimSun", 11),
            ("Microsoft YaHei", 10),
            ("Arial Unicode MS", 10),
            ("SimHei", 10),
        ]

        # 获取系统所有可用字体
        all_fonts = list(tkfont.families())
        print(f"[DEBUG] 系统可用字体数量: {len(all_fonts)}")

        selected_font = ("Arial", 10)  # 默认
        for font in fonts_to_try:
            if font[0] in all_fonts:
                selected_font = font
                print(f"[DEBUG] 选择字体: {font[0]}")
                break

        self.result_text = tk.Text(
            result_frame,
            wrap=tk.WORD,
            font=selected_font,
            height=15
        )
        self.result_text.pack(padx=10, pady=10, fill="both", expand=True)

        # 复制按钮
        copy_btn = ttk.Button(
            self.root,
            text="📋 复制到剪贴板",
            command=self.copy_to_clipboard,
            width=20
        )
        copy_btn.pack(pady=10)

        # 状态栏
        self.status_label = tk.Label(
            self.root,
            text="就绪",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def full_screen_capture(self):
        """全屏截图"""
        self.status_label.config(text="正在全屏截图...")

        # 隐藏窗口
        self.root.withdraw()

        import time
        time.sleep(0.5)  # 等待窗口消失

        # 全屏截图
        screenshot = ImageGrab.grab()

        # 显示窗口
        self.root.deiconify()

        # 执行 OCR
        self.perform_ocr(screenshot)

    def region_select(self):
        """区域选择截图"""
        self.status_label.config(text="请选择截图区域...")

        # 隐藏主窗口
        self.root.withdraw()

        # 获取屏幕尺寸 (由于设置了 DPI 感知，这里应该是物理尺寸)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        print(f"[DEBUG] 屏幕尺寸: {screen_width}x{screen_height}")

        # 创建全屏选择窗口
        select_window = tk.Toplevel(self.root)
        select_window.overrideredirect(True)
        select_window.geometry(f"{screen_width}x{screen_height}+0+0")
        select_window.attributes('-topmost', True)
        select_window.attributes('-alpha', 0.3)

        # 设置暗色背景画布
        canvas = tk.Canvas(select_window, cursor="crosshair", bg='#1a1a1a', highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        # 变量存储选择区域
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.selection_window = select_window
        self.canvas = canvas

        # 直接绑定事件到选择窗口
        select_window.bind("<ButtonPress-1>", self.on_mouse_press)
        select_window.bind("<B1-Motion>", self.on_mouse_drag)
        select_window.bind("<ButtonRelease-1>", self.on_mouse_release)
        select_window.bind("<Escape>", self.cancel_selection)

    def on_mouse_press(self, event):
        """鼠标按下"""
        # 获取鼠标的屏幕坐标(相对于屏幕左上角) - 逻辑坐标
        self.start_x = event.x_root
        self.start_y = event.y_root
        # 同时保存窗口坐标用于绘制矩形
        self.start_x_win = event.x
        self.start_y_win = event.y
        print(f"[DEBUG] 鼠标按下 - 逻辑坐标: ({self.start_x}, {self.start_y}), 窗口坐标: ({self.start_x_win}, {self.start_y_win})")

    def on_mouse_drag(self, event):
        """鼠标拖动"""
        if self.start_x is None:
            return

        # 删除旧矩形
        if self.rect_id:
            self.canvas.delete(self.rect_id)

        # 使用窗口坐标绘制矩形
        self.rect_id = self.canvas.create_rectangle(
            self.start_x_win, self.start_y_win,
            event.x, event.y,
            outline="#00ff00",
            width=3
        )

    def on_mouse_release(self, event):
        """鼠标释放"""
        if self.start_x is None:
            return

        # 计算选择区域 (由于设置了 DPI 感知，坐标应该是物理坐标)
        x1 = min(self.start_x, event.x_root)
        y1 = min(self.start_y, event.y_root)
        x2 = max(self.start_x, event.x_root)
        y2 = max(self.start_y, event.y_root)

        print(f"[DEBUG] 选择区域: ({x1}, {y1}) -> ({x2}, {y2})")

        # 关闭选择窗口
        self.close_selection_windows()

        # 避免无效选择
        if x2 - x1 < 10 or y2 - y1 < 10:
            self.status_label.config(text="选择区域太小，已取消")
            self.root.deiconify()
            return

        # 截图并保存到临时文件
        try:
            from PIL import ImageGrab
            
            print(f"[DEBUG] 使用 PIL ImageGrab 截图: ({x1}, {y1}) -> ({x2}, {y2})")
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

            print(f"[DEBUG] 截图尺寸: {screenshot.size}")

            # 保存到临时文件
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            temp_path = temp_file.name
            screenshot.save(temp_path)
            print(f"[DEBUG] 保存到临时文件: {temp_path}")
            
            # 调试：同时保存到桌面
            try:
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "debug_screenshot.png")
                screenshot.save(desktop_path)
                print(f"[DEBUG] 调试截图已保存到桌面: {desktop_path}")
            except Exception as e:
                print(f"[DEBUG] 无法保存到桌面: {e}")

        except Exception as e:
            print(f"[ERROR] 截图失败: {e}")
            import traceback
            traceback.print_exc()
            self.root.deiconify()
            self.status_label.config(text=f"截图失败: {e}")
            return

        # 显示主窗口
        self.root.deiconify()

        # 执行 OCR(传递临时文件路径)
        self.perform_ocr_from_file(temp_path)

    def perform_ocr_from_file(self, image_path):
        """从文件执行 OCR 识别"""
        self.status_label.config(text="正在识别文字...")

        # 在后台线程执行 OCR，避免阻塞 UI
        def ocr_worker():
            temp_path = image_path
            try:
                # 调用 OCR
                results = self.pipeline.predict(temp_path)

                # 提取文字 (在线 API 返回的格式)
                text_list = []
                for result in results:
                    parsing_res = result.get('parsing_res_list', [])
                    for item in parsing_res:
                        content = getattr(item, 'content', '')
                        if content:
                            text_list.append(content)

                # 在主线程更新 UI
                def update_result():
                    self._update_result(text_list, temp_path)
                self.root.after(0, update_result)

            except Exception as e:
                error_msg = str(e)
                # 清理临时文件
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass

                # 在主线程更新 UI
                def update_error():
                    self._update_error(error_msg)
                self.root.after(0, update_error)

        # 启动后台线程
        thread = threading.Thread(target=ocr_worker)
        thread.daemon = True
        thread.start()

    def cancel_selection(self, event=None):
        """取消选择"""
        self.close_selection_windows()
        self.root.deiconify()
        self.status_label.config(text="已取消")

    def close_selection_windows(self):
        """关闭选择相关窗口"""
        try:
            if hasattr(self, 'selection_window') and self.selection_window:
                self.selection_window.destroy()
                self.selection_window = None
        except:
            pass

        try:
            if hasattr(self, 'transparent_window_obj') and self.transparent_window_obj:
                self.transparent_window_obj.destroy()
                self.transparent_window_obj = None
        except:
            pass

    def perform_ocr(self, image):
        """执行 OCR 识别"""
        self.status_label.config(text="正在识别文字...")

        # 在后台线程执行 OCR，避免阻塞 UI
        def ocr_worker():
            temp_path = None
            try:
                import tempfile
                # 保存临时图片
                temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                temp_path = temp_file.name

                # 直接保存原始截图
                image.save(temp_path)

                # 调用 OCR
                results = self.pipeline.predict(temp_path)

                # 提取文字 (在线 API 返回的格式)
                text_list = []
                for result in results:
                    parsing_res = result.get('parsing_res_list', [])
                    for item in parsing_res:
                        content = getattr(item, 'content', '')
                        if content:
                            text_list.append(content)

                # 在主线程更新 UI（使用闭包捕获变量）
                def update_result():
                    self._update_result(text_list, temp_path)
                self.root.after(0, update_result)

            except Exception as e:
                error_msg = str(e)
                # 清理临时文件
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass

                # 在主线程更新 UI（使用闭包捕获 error_msg）
                def update_error():
                    self._update_error(error_msg)
                self.root.after(0, update_error)

        # 启动后台线程
        thread = threading.Thread(target=ocr_worker)
        thread.daemon = True
        thread.start()

    def _update_result(self, text_list, temp_path):
        """在主线程更新识别结果"""
        try:
            # 删除临时文件
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass

            # 显示结果
            if text_list:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "\n".join(text_list))
                self.status_label.config(
                    text=f"[OK] 识别完成，共 {len(text_list)} 行"
                )

                # 自动复制到剪贴板
                pyperclip.copy("\n".join(text_list))
                print("[OK] 已复制到剪贴板")
            else:
                self.status_label.config(text="未识别到文字")
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "未识别到文字")
        except Exception as e:
            self._update_error(str(e))

    def _update_error(self, error_msg):
        """在主线程更新错误信息"""
        self.status_label.config(text=f"识别失败: {error_msg}")
        print(f"错误: {error_msg}")
        import traceback
        traceback.print_exc()

    def copy_to_clipboard(self):
        """复制到剪贴板"""
        text = self.result_text.get(1.0, tk.END).strip()
        if text:
            pyperclip.copy(text)
            self.status_label.config(text="[OK] 已复制到剪贴板")
        else:
            self.status_label.config(text="没有内容可复制")

    def run(self):
        """运行应用"""
        self.root.mainloop()


if __name__ == "__main__":
    app = ScreenshotOCR()
    app.run()
