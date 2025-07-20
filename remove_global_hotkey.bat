@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo TechZip Global Hotkey Removal
echo ========================================
echo.

:: Get startup folder path
set "startupFolder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "shortcutPath=%startupFolder%\TechZip_Hotkey.lnk"

:: Check if shortcut exists
if exist "%shortcutPath%" (
    echo Removing shortcut from startup...
    del "%shortcutPath%"
    
    if %errorlevel% equ 0 (
        echo [SUCCESS] Shortcut removed.
    ) else (
        echo [ERROR] Failed to remove shortcut.
    )
) else (
    echo [INFO] Shortcut does not exist.
)

:: Terminate running AutoHotkey processes
echo.
echo Terminating TechZip hotkey processes...
taskkill /F /IM autohotkey.exe /FI "WINDOWTITLE eq TechZip_Hotkey_v1.ahk" >nul 2>&1
taskkill /F /IM autohotkey64.exe /FI "WINDOWTITLE eq TechZip_Hotkey_v1.ahk" >nul 2>&1

echo.
echo ========================================
echo Removal Complete!
echo ========================================
echo.
echo Global hotkey has been disabled.
echo.

pause