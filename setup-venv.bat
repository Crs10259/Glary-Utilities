@echo off
setlocal enabledelayedexpansion

echo === Glary Utilities Build Script (Windows) ===
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://www.python.org/
    exit /b 1
)

:: Check pip installation
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not installed
    echo Installing pip...
    python -m ensurepip --default-pip
    if errorlevel 1 (
        echo Failed to install pip
        exit /b 1
    )
)

:: Create virtual environment
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        exit /b 1
    )
)

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment
    exit /b 1
)

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Warning: Failed to upgrade pip
)

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies
    exit /b 1
)

echo.
echo Build completed successfully!
echo To start the application, run: python src/main.py

endlocal