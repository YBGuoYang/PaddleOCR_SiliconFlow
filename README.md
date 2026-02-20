# 📷 截图 OCR 工具

<div align="center">

![Windows](https://img.shields.io/badge/Windows-0078D6?logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

一个简单易用的截图文字识别工具，支持快捷键触发、长按检测和后台托盘运行。

[🚀 下载最新版](#-下载) | [📖 使用说明](#-使用说明) | [⚙️ 配置指南](#️-配置说明)

</div>

## ✨ 功能特性

- 🖼️ **全屏/区域截图** - 支持框选任意区域进行 OCR 识别
- ⌨️ **自定义快捷键** - 支持 F1-F12、组合键（如 Ctrl+E）
- ⏱️ **长按触发** - 可配置 0.5-2 秒长按时间
- 📋 **自动复制** - 识别结果自动复制到剪贴板
- 🔔 **系统通知** - 识别成功后显示通知预览
- 🎯 **后台运行** - 最小化到系统托盘，不占用任务栏
- 🔑 **API Key 配置** - 首次运行引导配置，支持在设置中修改

## 📥 下载

### Windows 开箱即用版（推荐）

<details>
<summary>📦 点击展开下载选项</summary>

#### 方式一：直接下载 EXE

从 [Releases](https://github.com/YBGuoYang/PaddleOCR_SiliconFlow/releases) 页面下载最新的 `ScreenshotOCR.zip`

#### 方式二：克隆仓库

```bash
git clone https://github.com/YBGuoYang/PaddleOCR_SiliconFlow.git
cd PaddleOCR_SiliconFlow/dist
双击 ScreenshotOCR.exe 运行
```

</details>

**使用步骤：**
1. 下载并解压 `ScreenshotOCR.zip`
2. 双击 `ScreenshotOCR.exe` 运行
3. 首次运行会弹出配置窗口，输入您的硅基流动 API Key
4. 程序将在后台运行，按 F9 触发截图

> 💡 **获取 API Key**：访问 [SiliconFlow](https://cloud.siliconflow.cn/i/sU0OEWTy) 注册账号并创建 API Key

---

## 🚀 快速开始

### 方式一：直接运行 EXE（推荐）

### 方式二：Python 源码运行

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 运行程序

**基础版（窗口界面）：**
```bash
run.bat
```

**快捷键版（托盘运行）：**
```bash
run_hotkey.bat
```

**静默启动（无终端窗口）：**
```bash
run_hotkey_silent.vbs
```

首次运行会提示输入 API Key。

## 📖 使用说明

### 基础版

1. 运行 `run.bat` 启动程序
2. 点击「选择区域截图」按钮
3. 框选需要识别的区域
4. 等待识别完成，结果自动复制到剪贴板

### 快捷键版

1. 运行 `run_hotkey.bat` 启动程序
2. 程序最小化到系统托盘
3. 按住快捷键（默认 F9）指定时间触发截图
4. 框选区域后自动识别并复制

**修改设置：**
- 右键托盘图标 → 设置
- 可修改 API Key、快捷键、触发模式、长按时间

## ⚙️ 配置说明

### 配置文件

配置文件：`config/hotkey_config.json`

```json
{
  "api_key": "sk-xxxxxxxx",
  "hotkey": "f9",
  "long_press_time": 1.0,
  "mode": "long_press",
  "show_notification": true
}
```

| 参数 | 说明 | 可选值 |
|------|------|--------|
| api_key | 硅基流动 API Key | sk-xxx 格式 |
| hotkey | 触发快捷键 | f1-f12, ctrl+a-z, ctrl+shift+a-z |
| long_press_time | 长按时间（秒） | 0.5 - 2.0 |
| mode | 触发模式 | long_press（长按）, instant（即时） |
| show_notification | 显示通知 | true, false |

### 支持的快捷键

- **单键**：F1-F12、Insert、Delete、Home、End 等
- **组合键**：Ctrl+A-Z、Ctrl+Shift+A-Z、Alt+A-Z

> 注意：组合键只支持即时触发模式

## 📁 项目结构

```
paddleocr/
├── run.bat                    # 基础版启动脚本
├── run_hotkey.bat             # 快捷键版启动脚本
├── run_hotkey_silent.vbs      # 静默启动（无终端窗口）
├── build.bat                  # 打包 EXE 脚本
├── requirements.txt           # Python 依赖
├── README.md                  # 项目说明
├── config/
│   ├── ocr_config.py         # OCR 配置
│   ├── siliconflow_ocr.py    # OCR API 客户端
│   └── hotkey_config.json    # 用户配置（API Key、快捷键等）
└── scripts/
    ├── screenshot_ocr_simple.py   # 基础版主程序
    └── screenshot_ocr_hotkey.py   # 快捷键版主程序
```

## 📦 打包 EXE

运行 `build.bat` 将程序打包为独立的 EXE 文件：

```bash
build.bat
```

打包完成后，`dist` 文件夹包含：
- `ScreenshotOCR.exe` - 主程序
- `config/` - 配置文件目录（首次运行时自动创建配置文件）

**分发方式**：将整个 `dist` 文件夹打包发送给用户即可。

## 🔧 依赖说明

| 库 | 用途 |
|---|------|
| Pillow | 图像处理 |
| pyperclip | 剪贴板操作 |
| keyboard | 全局热键监听 |
| pystray | 系统托盘 |
| plyer | 系统通知 |
| requests | API 请求 |

## 🌟 系统要求

- **操作系统**：Windows 10/11（64位）
- **内存**：建议 4GB 以上
- **网络**：需要连接互联网（调用 OCR API）
- **权限**：建议以管理员权限运行（避免截图偏移问题）

## ❓ 常见问题

### Q: 截图区域偏移？

确保程序以管理员权限运行，或检查显示器的 DPI 缩放设置。

### Q: 快捷键不生效？

1. 检查快捷键是否被其他程序占用
2. 尝试使用其他快捷键
3. 确保程序正在运行（检查托盘图标）

### Q: API 请求超时？

检查网络连接，或稍后重试。API 服务可能暂时不可用。

### Q: 如何修改 API Key？

右键托盘图标 → 设置 → 在 API 设置区域修改

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 强大的 OCR 工具包
- [SiliconFlow](https://siliconflow.cn) - 提供 OCR API 服务

## 📮 联系方式

如有问题或建议，欢迎提交 [Issue](https://github.com/YBGuoYang/PaddleOCR_SiliconFlow/issues)

---

<div align="center">

**如果这个项目对你有帮助，请给它一个 ⭐️**

Made with ❤️ by [YBGuoYang](https://github.com/YBGuoYang)

</div>
