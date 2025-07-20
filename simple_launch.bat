@echo off
echo ========================================
echo Simple TechZip Launcher
echo ========================================
echo.

echo Testing if we can run the app directly...
echo.

cd /d "C:\Users\tky99\DEV\technical-fountain-series-support-tool"

echo Current directory: %CD%
echo.

echo Running PowerShell script...
powershell.exe -NoExit -ExecutionPolicy Bypass -File ".\run_windows.ps1"

pause