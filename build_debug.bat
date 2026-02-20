@echo off
chcp 65001 >nul
echo ========================================
echo   Screenshot OCR Tool - Debug Build
echo ========================================
echo.

cd /d "%~dp0"

REM Check PyInstaller
pip show pyinstaller >nul 2>&1 || pip install pyinstaller

echo.
echo [Building Debug EXE...]
echo.

REM Clean previous build
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"

REM Build the EXE with console window (remove --windowed for debugging)
pyinstaller --onefile --name "ScreenshotOCR_Debug" ^
    --hidden-import=requests ^
    --hidden-import=urllib3 ^
    --hidden-import=charset_normalizer ^
    --hidden-import=idna ^
    --hidden-import=certifi ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --hidden-import=PIL.ImageDraw ^
    --hidden-import=PIL.ImageFont ^
    --hidden-import=PIL.ImageTk ^
    --hidden-import=pyperclip ^
    --hidden-import=keyboard ^
    --hidden-import=pystray ^
    --hidden-import=plyer ^
    --hidden-import=mss ^
    --add-data "config;config" ^
    scripts\screenshot_ocr_hotkey.py

echo.
if exist "dist\ScreenshotOCR_Debug.exe" (
    echo [OK] Debug build successful!
    echo.
    echo Output: dist\ScreenshotOCR_Debug.exe
    echo.
    echo Running debug version...
    echo ========================================
    start "" "dist\ScreenshotOCR_Debug.exe"
) else (
    echo [ERROR] Build failed!
)

echo.
pause
