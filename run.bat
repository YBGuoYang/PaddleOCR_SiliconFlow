@echo off
chcp 65001 >nul
echo ========================================
echo   Screenshot OCR Tool
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
pip show mss >nul 2>&1 || pip install mss
pip show Pillow >nul 2>&1 || pip install Pillow
pip show pyperclip >nul 2>&1 || pip install pyperclip
pip show requests >nul 2>&1 || pip install requests

echo.
echo [Starting...]
python scripts\screenshot_ocr_simple.py

pause
