@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo TechZip Startup Uninstallation
echo ========================================
echo.

:: Get startup folder path
set "startupFolder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "targetFile=%startupFolder%\TechZip_Launcher.ahk"

:: Check if file exists
if exist "%targetFile%" (
    echo Removing TechZip from startup...
    del /F "%targetFile%"
    
    if %errorlevel% equ 0 (
        echo [SUCCESS] TechZip removed from startup.
    ) else (
        echo [ERROR] Failed to remove file.
        echo Please run as administrator if needed.
    )
) else (
    echo [INFO] TechZip is not in startup folder.
)

:: Try to terminate running process
echo.
echo Stopping TechZip hotkey listener...
taskkill /F /IM autohotkey.exe /FI "WINDOWTITLE eq TechZip_Launcher.ahk*" >nul 2>&1
taskkill /F /IM autohotkey64.exe /FI "WINDOWTITLE eq TechZip_Launcher.ahk*" >nul 2>&1

echo.
echo ========================================
echo Uninstallation Complete!
echo ========================================
echo.
echo TechZip hotkey has been disabled.
echo.

pause