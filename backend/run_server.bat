@echo off
REM Provolution Gamification API - Windows Run Script
REM Usage: run_server.bat [port]

set PORT=%1
if "%PORT%"=="" set PORT=8000

echo.
echo ========================================
echo  Provolution Gamification API
echo  Starting on http://localhost:%PORT%
echo ========================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found. Using system Python.
    echo Tip: Create venv with: python -m venv venv
)

echo.
echo Starting server...
echo Docs available at: http://localhost:%PORT%/docs
echo.

uvicorn app.main:app --reload --port %PORT%
