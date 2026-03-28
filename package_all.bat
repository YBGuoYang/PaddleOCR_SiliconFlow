@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0"

echo [INFO] Creating source package...
call package_source.bat
if errorlevel 1 exit /b 1

echo.
echo [INFO] Creating release package...
call package_release.bat
if errorlevel 1 exit /b 1

echo.
echo [OK] All artifacts are ready in the release folder.
exit /b 0
