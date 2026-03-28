@echo off
setlocal
chcp 65001 >nul
set "NO_PAUSE=0"
if /I "%~1"=="--no-pause" set "NO_PAUSE=1"

echo ========================================
echo   Screenshot OCR Tool - Build Script
echo ========================================
echo.

cd /d "%~dp0"

call setup_env.bat --dev
if errorlevel 1 (
    call :maybe_pause
    exit /b 1
)

echo.
echo [Building EXE...]
echo.

REM Clean previous build
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"

REM Build the EXE with hidden imports and config directory
".\.venv\Scripts\python.exe" -m PyInstaller --onefile --windowed --name "ScreenshotOCR" ^
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
    --hidden-import=plyer.platforms ^
    --hidden-import=plyer.platforms.win ^
    --hidden-import=plyer.platforms.win.notification ^
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
    call :maybe_pause
    exit /b 1
)

echo.
call :maybe_pause
exit /b 0

:maybe_pause
if "%NO_PAUSE%"=="1" exit /b 0
pause
exit /b 0
