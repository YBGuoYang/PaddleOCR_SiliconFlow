@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0"

set "SKIP_BUILD=0"
if /I "%~1"=="--skip-build" set "SKIP_BUILD=1"

if not exist "release" mkdir "release"
del /q "release\ScreenshotOCR_Setup_*.exe" >nul 2>&1
del /q "release\ScreenshotOCR_Portable_*.exe" >nul 2>&1

for /f %%i in ('powershell -NoProfile -Command "(Get-Date).ToString(\"yyyyMMdd_HHmm\")"') do set "STAMP=%%i"

if "%SKIP_BUILD%"=="0" (
    echo [INFO] Building executable...
    call build.bat --no-pause
    if errorlevel 1 (
        echo [ERROR] Build failed.
        exit /b 1
    )
)

if not exist "dist\ScreenshotOCR.exe" (
    echo [ERROR] dist\ScreenshotOCR.exe not found.
    exit /b 1
)

set "SETUP_OUT=release\ScreenshotOCR_Setup_%STAMP%.exe"
set "PORTABLE_OUT=release\ScreenshotOCR_Portable_%STAMP%.exe"

set "ISCC_EXE="
for /f "delims=" %%i in ('where iscc 2^>nul') do (
    set "ISCC_EXE=%%i"
    goto :found_iscc
)

if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC_EXE=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC_EXE if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC_EXE=%ProgramFiles%\Inno Setup 6\ISCC.exe"

:found_iscc
if defined ISCC_EXE (
    echo [INFO] Building installer with Inno Setup...
    "%ISCC_EXE%" /Qp /DSTAMP=%STAMP% "installer\ScreenshotOCR.iss"
    if errorlevel 1 (
        echo [WARN] Installer build failed. Falling back to portable EXE.
        goto :portable_fallback
    )
    if exist "%SETUP_OUT%" (
        echo [OK] Installer created:
        echo      %SETUP_OUT%
        call :cleanup_temp
        exit /b 0
    )
    echo [WARN] Setup file missing after compile. Falling back to portable EXE.
)

:portable_fallback
copy /Y "dist\ScreenshotOCR.exe" "%PORTABLE_OUT%" >nul
if errorlevel 1 (
    echo [ERROR] Failed to create portable release EXE.
    exit /b 1
)

echo [OK] Portable release created:
echo      %PORTABLE_OUT%
echo [INFO] Install package was not produced because Inno Setup was not available.
call :cleanup_temp
exit /b 0

:cleanup_temp
if exist "build" rmdir /s /q "build"
if exist "ScreenshotOCR.spec" del /q "ScreenshotOCR.spec"
if exist "ScreenshotOCR_Debug.spec" del /q "ScreenshotOCR_Debug.spec"
exit /b 0
