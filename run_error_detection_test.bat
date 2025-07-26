@echo off
chcp 65001 >nul
echo ================================================================
echo   TechZip エラーファイル検知機能 テスト
echo ================================================================
echo.

REM PowerShellスクリプトを実行
powershell -ExecutionPolicy Bypass -File test_error_detection.ps1

pause