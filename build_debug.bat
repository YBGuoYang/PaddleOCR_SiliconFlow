@echo off
setlocal
chcp 65001 >nul
echo ========================================
echo   Screenshot OCR Tool - Debug Build
echo ========================================
echo.

cd /d "%~dp0"

call setup_env.bat --dev
if errorlevel 1 (
    pause
    exit /b 1
)

echo.
echo [Building Debug EXE...]
echo.

REM Clean previous build
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"

REM Build the EXE with console window (remove --windowed for debugging)
".\.venv\Scripts\python.exe" -m PyInstaller --onefile --name "ScreenshotOCR_Debug" ^
    --paths "src" ^
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
    --hidden-import=screenshot_ocr ^
    --add-binary "D:\program\BIO\pymol\Library\bin\ffi-8.dll;." ^
    --add-binary "D:\program\BIO\pymol\Library\bin\libcrypto-3-x64.dll;." ^
    --add-binary "D:\program\BIO\pymol\Library\bin\libssl-3-x64.dll;." ^
    --add-binary "D:\program\BIO\pymol\Library\bin\libexpat.dll;." ^
    --add-binary "D:\program\BIO\pymol\Library\bin\libbz2.dll;." ^
    --add-binary "D:\program\BIO\pymol\Library\bin\liblzma.dll;." ^
    --add-binary "D:\program\BIO\pymol\Library\bin\zlib.dll;." ^
    --add-binary "D:\program\BIO\pymol\Library\bin\zlib1.dll;." ^
    --add-binary "D:\program\BIO\pymol\Library\bin\tcl86t.dll;." ^
    --add-binary "D:\program\BIO\pymol\Library\bin\tk86t.dll;." ^
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
