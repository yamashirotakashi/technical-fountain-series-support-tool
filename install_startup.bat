@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo TechZip Startup Installation
echo ========================================
echo.

:: Get startup folder path
set "startupFolder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "ahkFile=%~dp0TechZip_Launcher.ahk"
set "targetFile=%startupFolder%\TechZip_Launcher.ahk"

:: Copy AHK file to startup folder
echo Copying AutoHotkey script to startup folder...
copy /Y "%ahkFile%" "%targetFile%" >nul

if %errorlevel% equ 0 (
    echo [SUCCESS] AutoHotkey script copied to startup folder.
    echo.
    
    :: Check if AutoHotkey is installed
    where autohotkey >nul 2>&1
    if %errorlevel% neq 0 (
        echo.
        echo [WARNING] AutoHotkey is not installed!
        echo.
        echo Please install AutoHotkey first:
        echo 1. Run: download_autohotkey.ps1
        echo 2. Install AutoHotkey
        echo 3. Run this script again
        echo.
    ) else (
        :: Try to run the script immediately
        echo Starting TechZip hotkey listener...
        start "" "%targetFile%"
    )
    
    echo.
    echo ========================================
    echo Installation Complete!
    echo ========================================
    echo.
    echo ✅ TechZip hotkey (Ctrl+Shift+I) is now active.
    echo ✅ Will automatically start when Windows starts.
    echo.
    echo 📌 To test now: Press Ctrl+Shift+I
    echo.
) else (
    echo [ERROR] Failed to copy AutoHotkey script.
    echo Please run as administrator if needed.
    echo.
)

pause