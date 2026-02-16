@echo off

echo ==========================================
echo   Smart Garden Watering - Server Start
echo ==========================================
echo.

:: Try python first
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON=python
    goto :Found
)

:: Try python3
python3 --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON=python3
    goto :Found
)

:: Try py
py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON=py
    goto :Found
)

:: Not found
echo [ERROR] Python not found!
echo.
echo Please install Python 3.10+ from https://python.org
echo Make sure to check "Add Python to PATH" during installation
echo.
pause
exit /b 1

:Found
echo [OK] Found: %PYTHON%
%PYTHON% --version
echo.

:: Create venv if not exists
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PYTHON% -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create venv
        pause
        exit /b 1
    )
    echo Installing dependencies...
    venv\Scripts\pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

:: Run migrations
echo.
echo Running migrations...
venv\Scripts\python manage.py migrate
if %errorlevel% neq 0 (
    echo [ERROR] Migration failed
    pause
    exit /b 1
)

:: Start server
echo.
echo ==========================================
echo   Starting server at http://127.0.0.1:8000/
echo ==========================================
echo.
venv\Scripts\python manage.py runserver

pause
