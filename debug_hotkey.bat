@echo off
echo ========================================
echo TechZip Hotkey Debug
echo ========================================
echo.

echo [1] Checking AutoHotkey installation...
where autohotkey 2>nul
if %errorlevel% equ 0 (
    echo Found: autohotkey
    where autohotkey
)

where AutoHotkey.exe 2>nul
if %errorlevel% equ 0 (
    echo Found: AutoHotkey.exe
    where AutoHotkey.exe
)

echo.
echo [2] Checking startup folder...
set "startupFolder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
echo Startup folder: %startupFolder%
echo.
dir "%startupFolder%\TechZip*" 2>nul

echo.
echo [3] Checking running AutoHotkey processes...
tasklist | findstr /i autohotkey

echo.
echo [4] Testing direct execution...
echo Running TechZip_Launcher.ahk directly...

:: Try different methods
if exist "C:\Program Files\AutoHotkey\AutoHotkey.exe" (
    echo Using: C:\Program Files\AutoHotkey\AutoHotkey.exe
    "C:\Program Files\AutoHotkey\AutoHotkey.exe" "%~dp0TechZip_Launcher.ahk"
) else if exist "C:\Program Files\AutoHotkey\v1.1\AutoHotkeyU64.exe" (
    echo Using: C:\Program Files\AutoHotkey\v1.1\AutoHotkeyU64.exe
    "C:\Program Files\AutoHotkey\v1.1\AutoHotkeyU64.exe" "%~dp0TechZip_Launcher.ahk"
) else if exist "C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe" (
    echo Using: C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe
    "C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe" "%~dp0TechZip_Launcher.ahk"
) else (
    echo No AutoHotkey found. Trying file association...
    start "" "%~dp0TechZip_Launcher.ahk"
)

echo.
echo ========================================
echo If hotkey works now, press Ctrl+Shift+I
echo ========================================
echo.
pause