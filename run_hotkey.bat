@echo off
chcp 65001 >nul
echo ========================================
echo   Screenshot OCR Tool (Hotkey Version)
echo ========================================
echo.

cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found, please install Python 3.8+
    pause
    exit /b 1
)

REM Check dependencies
echo [Checking dependencies...]
pip show keyboard >nul 2>&1 || pip install keyboard
pip show pystray >nul 2>&1 || pip install pystray
pip show plyer >nul 2>&1 || pip install plyer
pip show mss >nul 2>&1 || pip install mss
pip show Pillow >nul 2>&1 || pip install Pillow
pip show pyperclip >nul 2>&1 || pip install pyperclip
pip show requests >nul 2>&1 || pip install requests

echo.
echo [Starting...]
echo Press F9 (or configured hotkey) to trigger screenshot OCR
echo.

python scripts\screenshot_ocr_hotkey.py

pause
