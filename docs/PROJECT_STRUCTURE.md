# 项目结构说明

本文档用于说明仓库中各目录的职责，便于 GitHub 维护与发布。

## 顶层目录

- `src/screenshot_ocr/`：核心业务代码（截图、OCR 请求、托盘、热键、配置模型）。
- `scripts/`：Python 启动壳（对外入口脚本）。
- `config/`：默认配置模板与兼容层。
- `installer/`：Inno Setup 脚本，用于生成单文件安装包。
- `tests/`：测试用例与测试素材。
- `docs/`：项目文档（结构说明、发布流程、历史计划）。
- `release/`：本地发布产物目录，仅保留说明文件，不提交二进制。

## 顶层脚本

- `run.bat`：正式运行入口（托盘 + 热键）。
- `run_hotkey.bat`：兼容别名入口。
- `run_hotkey_silent.vbs`：静默启动入口。
- `setup_env.bat`：创建/修复 `.venv` 并安装依赖。
- `build.bat`：构建正式 EXE。
- `build_debug.bat`：构建调试 EXE。
- `package_source.bat`：打包源码分发 zip（仅必要源码内容）。
- `package_release.bat`：打包 Release 单文件（安装包优先，便携版回退）。
- `package_all.bat`：一键产出源码包和 Release 包。

## GitHub 提交建议

建议只提交以下类型内容：

- 源代码与配置模板：`src/`、`scripts/`、`config/`
- 文档：`README.md`、`DEVELOPMENT.md`、`docs/`
- 测试：`tests/`
- 构建与运行脚本：`*.bat`、`*.vbs`、`installer/*.iss`

不要提交：

- `dist/`、`build/`、`release/*.zip`、`release/*.exe`
- `__pycache__/`、`.pytest_cache/`、`.venv/`
