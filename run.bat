@echo off
REM TechZip 超短縮ランチャー
REM 使用法: run.bat

echo TechZip起動中...
powershell.exe -ExecutionPolicy Bypass -File "%~dp0run.ps1" %*
pause