@echo off
setlocal enabledelayedexpansion

:: Try to set UTF-8
call :SetUTF8

cls
echo ==========================================
echo   Smart Garden Watering - Server Start
echo ==========================================
echo.

:: Try to find Python
call :FindPython
if errorlevel 1 (
    echo.
    echo [ERROR] Python not found!
    echo.
    echo Please make sure Python 3.10+ is installed and added to PATH.
    echo.
    echo You can download Python from: https://python.org/downloads
    echo.
    echo During installation, check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [OK] Python found: !PYTHON_CMD!
!PYTHON_CMD! --version
echo.

:: Check if virtual environment exists
if exist "venv\Scripts\python.exe" (
    echo [OK] Virtual environment found
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo [WARNING] Failed to activate, trying to use venv Python directly...
        set PYTHON_CMD=venv\Scripts\python.exe
    )
) else (
    echo Virtual environment not found. Creating...
    echo.
    !PYTHON_CMD! -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    echo.
    echo Installing dependencies...
    venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
    set PYTHON_CMD=venv\Scripts\python.exe
)

echo.
echo ==========================================
echo   Database Migration
echo ==========================================
echo.
!PYTHON_CMD! manage.py migrate
if errorlevel 1 (
    echo [ERROR] Migration failed
    pause
    exit /b 1
)
echo [OK] Migrations applied

echo.
echo ==========================================
echo   Starting Django Server
echo ==========================================
echo.
echo Open your browser and go to:
echo   http://127.0.0.1:8000/
echo.
echo Admin panel:
echo   http://127.0.0.1:8000/admin/
echo.
echo Press Ctrl+C to stop the server
echo.

!PYTHON_CMD! manage.py runserver

if errorlevel 1 (
    echo.
    echo [ERROR] Server stopped with error
    pause
    exit /b 1
)

pause
goto :EOF

:: ==========================================
:: Function to set UTF-8 encoding
:: ==========================================
:SetUTF8
chcp 65001 >nul 2>&1
if errorlevel 1 chcp 1251 >nul 2>&1
goto :EOF

:: ==========================================
:: Function to find Python
:: Sets PYTHON_CMD variable if found
:: Returns 0 if found, 1 if not found
:: ==========================================
:FindPython
set PYTHON_CMD=

:: Try different Python commands
for %%P in (python python3 py) do (
    echo Checking for %%P...
    %%P --version >nul 2>&1
    if !errorlevel! equ 0 (
        set PYTHON_CMD=%%P
        echo Found: %%P
        goto :FoundPython
    )
)

:: Check common installation paths
for %%D in (
    "%LOCALAPPDATA%\Programs\Python\Python*"
    "%LOCALAPPDATA%\Programs\Python\Python3*"
    "C:\Python*"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python*"
) do (
    if exist "%%D\python.exe" (
        set PYTHON_CMD=%%D\python.exe
        echo Found in: %%D
        goto :FoundPython
    )
)

:: Check Windows Store Python
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
    set PYTHON_CMD=%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe
    echo Found: Windows Store Python
    goto :FoundPython
)

:: Not found
exit /b 1

:FoundPython
exit /b 0
