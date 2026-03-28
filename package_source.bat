@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0"

if not exist "release" mkdir "release"
del /q "release\ScreenshotOCR_Source_*.zip" >nul 2>&1

for /f %%i in ('powershell -NoProfile -Command "(Get-Date).ToString(\"yyyyMMdd_HHmm\")"') do set "STAMP=%%i"
set "STAGE_DIR=%TEMP%\ScreenshotOCR_source_%STAMP%"
set "ZIP_PATH=release\ScreenshotOCR_Source_%STAMP%.zip"

if exist "%STAGE_DIR%" rmdir /s /q "%STAGE_DIR%"
mkdir "%STAGE_DIR%"

echo [INFO] Preparing curated source package...

call :copy_dir "src"
call :copy_dir "scripts"
call :copy_dir "config"
call :copy_dir "installer"
call :copy_dir "tests"
call :copy_dir "docs"

call :copy_file "README.md"
call :copy_file "DEVELOPMENT.md"
call :copy_file "LICENSE"
call :copy_file "requirements.txt"
call :copy_file "requirements-dev.txt"
call :copy_file "setup_env.bat"
call :copy_file "run.bat"
call :copy_file "run_hotkey.bat"
call :copy_file "run_hotkey_silent.vbs"
call :copy_file "build.bat"
call :copy_file "build_debug.bat"
call :copy_file "package_source.bat"
call :copy_file "package_release.bat"
call :copy_file "package_all.bat"
call :copy_file ".gitignore"

for /d /r "%STAGE_DIR%" %%d in (__pycache__) do (
    if exist "%%d" rmdir /s /q "%%d"
)
del /s /q "%STAGE_DIR%\*.pyc" >nul 2>&1

powershell -NoProfile -Command "Compress-Archive -Path '%STAGE_DIR%\*' -DestinationPath '%ZIP_PATH%' -Force"
if errorlevel 1 (
    echo [ERROR] Failed to create source zip.
    rmdir /s /q "%STAGE_DIR%"
    exit /b 1
)

rmdir /s /q "%STAGE_DIR%"

echo [OK] Source package created:
echo      %ZIP_PATH%
exit /b 0

:copy_dir
if not exist "%~1" (
    echo [WARN] Missing directory: %~1
    exit /b 0
)
xcopy "%~1" "%STAGE_DIR%\%~1\" /E /I /Y >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy directory: %~1
    exit /b 1
)
exit /b 0

:copy_file
if not exist "%~1" (
    echo [WARN] Missing file: %~1
    exit /b 0
)
copy /Y "%~1" "%STAGE_DIR%\%~1" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy file: %~1
    exit /b 1
)
exit /b 0
