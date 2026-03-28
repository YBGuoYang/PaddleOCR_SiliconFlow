@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0"

set "REQ_FILE=requirements.txt"
if /I "%~1"=="--dev" set "REQ_FILE=requirements-dev.txt"

if not exist ".venv\Scripts\python.exe" (
    call :detect_python
    if not defined PYTHON_BOOTSTRAP (
        echo [ERROR] Python 3.10-3.13 not found. Install a supported version first.
        exit /b 1
    )

    echo [INFO] Creating .venv with %PYTHON_BOOTSTRAP%
    %PYTHON_BOOTSTRAP% -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create .venv
        exit /b 1
    )
)

set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"

%PYTHON_EXE% -c "import sys; raise SystemExit(0 if (3, 10) <= sys.version_info[:2] < (3, 14) else 1)"
if errorlevel 1 (
    echo [ERROR] .venv uses an unsupported Python version. Recreate it with Python 3.10-3.13.
    exit /b 1
)

echo [INFO] Installing dependencies from %REQ_FILE%
%PYTHON_EXE% -m pip install -r "%REQ_FILE%"
if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    exit /b 1
)

echo [OK] Environment ready: %PYTHON_EXE%
exit /b 0

:detect_python
set "PYTHON_BOOTSTRAP="

py -3.13 --version >nul 2>&1
if not errorlevel 1 set "PYTHON_BOOTSTRAP=py -3.13"

if not defined PYTHON_BOOTSTRAP (
    py -3.12 --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_BOOTSTRAP=py -3.12"
)

if not defined PYTHON_BOOTSTRAP (
    py -3.11 --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_BOOTSTRAP=py -3.11"
)

if not defined PYTHON_BOOTSTRAP (
    py -3.10 --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_BOOTSTRAP=py -3.10"
)

if not defined PYTHON_BOOTSTRAP (
    python -c "import sys; raise SystemExit(0 if (3, 10) <= sys.version_info[:2] < (3, 14) else 1)" >nul 2>&1
    if not errorlevel 1 set "PYTHON_BOOTSTRAP=python"
)

exit /b 0
