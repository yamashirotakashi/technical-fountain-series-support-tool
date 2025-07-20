@echo off
echo ========================================
echo TechZip Hotkey Quick Test
echo ========================================
echo.

:: Check if AutoHotkey is installed
where autohotkey >nul 2>&1
if %errorlevel% neq 0 (
    where autohotkey64 >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] AutoHotkey is not installed.
        echo.
        echo Opening AutoHotkey download page...
        start https://www.autohotkey.com/
        echo.
        pause
        exit /b 1
    )
)

echo Starting AutoHotkey script...
echo.

:: Run the AutoHotkey script
start "" "%~dp0TechZip_Hotkey_v1.ahk"

echo ========================================
echo Ready to test!
echo ========================================
echo.
echo Press Ctrl+Shift+I to launch TechZip
echo.
echo The hotkey is now active in this session.
echo To stop, close this window.
echo.
pause