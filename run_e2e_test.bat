@echo off
REM TechZip E2E Test Launcher - Simple Batch Version
REM PowerShell 7で起動スクリプトを実行

echo ====================================
echo TechZip E2E Test Launcher
echo ====================================

REM PowerShell 7の確認と実行
where pwsh >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo PowerShell 7 found: pwsh
    pwsh -ExecutionPolicy Bypass -File "%~dp0run_e2e_test.ps1" %*
) else (
    REM PowerShell 7が見つからない場合、Windows PowerShellを試行
    echo PowerShell 7 not found, trying Windows PowerShell...
    powershell -ExecutionPolicy Bypass -File "%~dp0run_e2e_test.ps1" %*
)

pause