@echo off
echo ========================================
echo   TechZip Single File EXE Build
echo ========================================
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_windows_exe_fixed.ps1" -OneFile

pause