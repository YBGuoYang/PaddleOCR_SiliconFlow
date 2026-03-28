# Release 流程

本项目采用双产物发布：

1. 源码包：给开发者
2. Release 单文件：给普通用户

## 1. 预检查

1. 确认代码和文档已更新（至少 `README.md`、`docs/`）。
2. 关闭正在运行的 `ScreenshotOCR.exe`（否则无法清理 `dist/`）。
3. 确认 `config/hotkey_config.json` 不包含真实密钥。

## 2. 生成源码包

```powershell
.\package_source.bat
```

产物示例：

- `release/ScreenshotOCR_Source_20260328_2100.zip`

## 3. 生成 release 单文件

```powershell
.\package_release.bat
```

脚本行为：

- 自动调用 `build.bat --no-pause` 构建 `dist/ScreenshotOCR.exe`
- 如果检测到 Inno Setup（`iscc`），生成安装包：
  - `release/ScreenshotOCR_Setup_YYYYMMDD_HHMM.exe`
- 如果未检测到 Inno Setup，则回退为便携单文件：
  - `release/ScreenshotOCR_Portable_YYYYMMDD_HHMM.exe`

## 4. 一次性生成全部产物

```powershell
.\package_all.bat
```

## 5. 发布到 GitHub

建议在 Release 页面上传以下文件：

1. `ScreenshotOCR_Setup_*.exe`（或 `ScreenshotOCR_Portable_*.exe`）
2. `ScreenshotOCR_Source_*.zip`

并在 Release Notes 标明：

- Windows 版本
- 安装包/便携版类型
- 主要更新点与已知问题
