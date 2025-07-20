@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo TechZip Global Hotkey Setup
echo ========================================
echo.

:: Check if AutoHotkey is installed
where autohotkey >nul 2>&1
if %errorlevel% neq 0 (
    where autohotkey64 >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] AutoHotkey is not installed.
        echo.
        echo Please download and install AutoHotkey from:
        echo https://www.autohotkey.com/
        echo.
        pause
        exit /b 1
    )
)

:: Get startup folder path
set "startupFolder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

:: Create shortcut
echo Creating shortcut in startup folder...

:: Create shortcut using PowerShell
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%startupFolder%\TechZip_Hotkey.lnk'); $Shortcut.TargetPath = '%~dp0TechZip_Hotkey_v1.ahk'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = 'powershell.exe'; $Shortcut.Description = 'TechZip - Ctrl+Shift+I to launch app'; $Shortcut.Save()"

if %errorlevel% equ 0 (
    echo [SUCCESS] Shortcut created.
    echo.
    
    :: Run AutoHotkey script
    echo Starting AutoHotkey script...
    start "" "%~dp0TechZip_Hotkey_v1.ahk"
    
    echo.
    echo ========================================
    echo Setup Complete!
    echo ========================================
    echo.
    echo Press Ctrl+Shift+I to launch TechZip app.
    echo (Available from any application)
    echo.
    echo This setting will be automatically enabled on next Windows startup.
    echo.
) else (
    echo [ERROR] Failed to create shortcut.
    echo.
)

pause