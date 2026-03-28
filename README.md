# Screenshot OCR Tool

Windows 截图 OCR 小工具，支持托盘常驻、全局热键触发、识别后自动复制。

![Windows](https://img.shields.io/badge/Windows-0078D6?logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10--3.13-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## 两类下载方式

这个项目现在提供两种明确的分发方式：

1. 源码用户（开发/二次修改）
2. Release 用户（只想安装和使用）

### 1) 源码用户

下载源码包 `ScreenshotOCR_Source_*.zip`，或直接克隆仓库。

源码运行：

```powershell
.\setup_env.bat --dev
.\run.bat
```

### 2) Release 用户

优先下载单文件安装包 `ScreenshotOCR_Setup_*.exe`。
如果安装包不可用，则下载单文件便携版 `ScreenshotOCR_Portable_*.exe`。

## 功能概览

- 区域截图识别（OCR）
- 全局热键触发（支持长按或即时触发）
- 识别结果自动复制到剪贴板
- 托盘常驻和通知提示
- 首次运行引导配置 API Key

## 配置说明

配置文件模板：`config/hotkey_config.json`

```json
{
  "api_key": "your_api_key",
  "hotkey": "f9",
  "long_press_time": 1.0,
  "mode": "long_press",
  "auto_start": false,
  "show_notification": true
}
```

## 打包命令

```powershell
.\package_source.bat   # 生成源码包（仅必要源码内容）
.\package_release.bat  # 生成 release 单文件（安装包优先）
.\package_all.bat      # 同时生成源码包 + release 包
```

构建脚本仍可单独使用：

```powershell
.\build.bat
```

## 项目结构

```text
PaddleOCR_SiliconFlow-main/
├─ src/screenshot_ocr/         # 核心代码
├─ scripts/                    # Python 启动壳
├─ config/                     # 配置模板与兼容层
├─ installer/                  # Inno Setup 安装脚本
├─ tests/                      # 测试与测试素材
├─ docs/                       # 文档（结构/发布/计划）
├─ release/                    # 本地产物目录（不提交二进制）
├─ package_source.bat
├─ package_release.bat
├─ package_all.bat
└─ README.md
```

详细结构说明见 [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)。
完整发布流程见 [docs/RELEASE.md](docs/RELEASE.md)。

## 开发说明

- [DEVELOPMENT.md](DEVELOPMENT.md)
- 推荐 Python 版本：3.10 ~ 3.13

## 许可证

MIT，见 [LICENSE](LICENSE)。
