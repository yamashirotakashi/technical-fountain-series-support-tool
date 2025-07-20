@echo off
echo ========================================
echo TechZip Hotkey Direct Launch
echo ========================================
echo.

echo Trying to run AutoHotkey script directly...
echo.

:: Try different AutoHotkey executable names
if exist "C:\Program Files\AutoHotkey\v2\AutoHotkey.exe" (
    echo Found AutoHotkey v2
    "C:\Program Files\AutoHotkey\v2\AutoHotkey.exe" "%~dp0TechZip_Hotkey.ahk"
    goto :success
)

if exist "C:\Program Files\AutoHotkey\AutoHotkey.exe" (
    echo Found AutoHotkey v1
    "C:\Program Files\AutoHotkey\AutoHotkey.exe" "%~dp0TechZip_Hotkey_v1.ahk"
    goto :success
)

if exist "C:\Program Files\AutoHotkey\v1.1\AutoHotkeyU64.exe" (
    echo Found AutoHotkey v1.1 64-bit
    "C:\Program Files\AutoHotkey\v1.1\AutoHotkeyU64.exe" "%~dp0TechZip_Hotkey_v1.ahk"
    goto :success
)

if exist "C:\Program Files\AutoHotkey\v1.1\AutoHotkey.exe" (
    echo Found AutoHotkey v1.1
    "C:\Program Files\AutoHotkey\v1.1\AutoHotkey.exe" "%~dp0TechZip_Hotkey_v1.ahk"
    goto :success
)

:: Try running with file association
echo Trying file association...
start "" "%~dp0TechZip_Hotkey_v1.ahk"

:success
echo.
echo ========================================
echo Hotkey Active!
echo ========================================
echo.
echo Press Ctrl+Shift+I to launch TechZip
echo.
echo Keep this window open while using the hotkey.
echo Press any key to stop the hotkey...
echo.
pause >nul