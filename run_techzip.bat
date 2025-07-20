@echo off
title TechZip Launcher
echo ========================================
echo TechZip Quick Launcher
echo ========================================
echo.

:: Change to the correct directory
cd /d "C:\Users\tky99\DEV\technical-fountain-series-support-tool"

:: Check if run_windows.ps1 exists
if not exist "run_windows.ps1" (
    echo ERROR: run_windows.ps1 not found!
    echo Current directory: %CD%
    echo.
    dir *.ps1
    echo.
    pause
    exit /b 1
)

:: Run the PowerShell script
echo Starting TechZip application...
echo.
powershell.exe -NoExit -ExecutionPolicy Bypass -Command "& '.\run_windows.ps1'"

:: If PowerShell fails, try python directly
if %errorlevel% neq 0 (
    echo.
    echo PowerShell failed. Trying Python directly...
    echo.
    
    :: Check for virtual environment
    if exist "venv_windows\Scripts\activate.bat" (
        call venv_windows\Scripts\activate.bat
        python main.py
    ) else (
        python main.py
    )
)

pause