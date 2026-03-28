@echo off
setlocal
chcp 65001 >nul
echo ========================================
echo   Screenshot OCR Tool (Hotkey Version)
echo ========================================
echo.

cd /d "%~dp0"

call setup_env.bat
if errorlevel 1 (
    pause
    exit /b 1
)

echo.
echo [Starting...]
echo Press F9 (or configured hotkey) to trigger screenshot OCR
echo.

".\.venv\Scripts\python.exe" scripts\screenshot_ocr_hotkey.py

pause
