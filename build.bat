@echo off
chcp 65001 >nul
echo ========================================
echo   Screenshot OCR Tool - Build Script
echo ========================================
echo.

cd /d "%~dp0"

REM Check PyInstaller
pip show pyinstaller >nul 2>&1 || pip install pyinstaller

echo.
echo [Building EXE...]
echo.

REM Clean previous build
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"

REM Build the EXE with hidden imports and config directory
pyinstaller --onefile --windowed --name "ScreenshotOCR" ^
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
    --hidden-import=plyer.platforms ^
    --hidden-import=plyer.platforms.win ^
    --hidden-import=plyer.platforms.win.notification ^
    --hidden-import=mss ^
    --add-data "config;config" ^
    scripts\screenshot_ocr_hotkey.py

echo.
if exist "dist\ScreenshotOCR.exe" (
    echo [OK] Build successful!
    echo.
    echo Output: dist\ScreenshotOCR.exe
    echo.
    
    REM Create config directory in dist folder for user config
    echo [Creating config directory...]
    if not exist "dist\config" mkdir "dist\config"
    
    echo [OK] Config directory created
    echo.
    echo ========================================
    echo   Build Complete!
    echo ========================================
    echo.
    echo You can now run dist\ScreenshotOCR.exe
    echo Config files will be created in dist\config\
    echo.
    echo To distribute: Copy the entire dist folder
) else (
    echo [ERROR] Build failed!
)

echo.
pause
