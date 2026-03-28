@echo off
chcp 65001 >nul
echo ========================================
echo   Screenshot OCR Tool
echo ========================================
echo.

cd /d "%~dp0"

echo [INFO] run.bat now launches the official tray + hotkey version.
echo.
call run_hotkey.bat
