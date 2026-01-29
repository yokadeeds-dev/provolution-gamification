@echo off
REM Provolution Gamification API - Setup Script (Windows)
REM Creates virtual environment and installs dependencies

echo.
echo ========================================
echo  Provolution Gamification API Setup
echo ========================================
echo.

REM Check Python version
python --version 2>NUL
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Initialize database if not exists
if not exist "provolution_gamification.db" (
    echo.
    echo Initializing database...
    python init_database.py
) else (
    echo Database already exists.
    echo Run 'python init_database.py' to reinitialize.
)

REM Apply schema updates
echo.
echo Applying schema updates...
python -c "import sqlite3; conn = sqlite3.connect('provolution_gamification.db'); script = open('schema_update.sql').read(); conn.executescript(script); conn.commit(); print('Schema updates applied.')" 2>NUL || echo Schema updates may have partial errors (expected on fresh install)

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo To start the server:
echo   run_server.bat
echo.
echo API will be available at:
echo   http://localhost:8000
echo   http://localhost:8000/docs (Swagger UI)
echo.

pause
