@echo off
echo ========================================
echo AutoHotkey Installation Check
echo ========================================
echo.

echo Checking common AutoHotkey locations...
echo.

echo [1] Program Files locations:
dir "C:\Program Files\AutoHotkey\" /b 2>nul
echo.

echo [2] Program Files (x86) locations:
dir "C:\Program Files (x86)\AutoHotkey\" /b 2>nul
echo.

echo [3] PATH environment:
where autohotkey 2>nul
where AutoHotkey 2>nul
where autohotkey.exe 2>nul
where AutoHotkey.exe 2>nul
where ahk 2>nul
echo.

echo [4] Registry check:
reg query "HKLM\SOFTWARE\AutoHotkey" 2>nul
reg query "HKCU\SOFTWARE\AutoHotkey" 2>nul
echo.

echo [5] File associations:
assoc .ahk 2>nul
ftype AutoHotkeyScript 2>nul
echo.

pause