# TechZip E2E Test - Debug Mode
# エラー検知機能の詳細テスト用

param(
    [string]$TestFile = "04_powershell_sample_advanced.docx",
    [switch]$SkipUpload,
    [switch]$EmailOnly
)

# PowerShell 7のチェック
if ($PSVersionTable.PSVersion.Major -lt 7) {
    Write-Host "PowerShell 7 が必要です。" -ForegroundColor Red
    exit 1
}

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "=== TechZip E2E Test - Debug Mode ===" -ForegroundColor Cyan
Write-Host "Test Target: $TestFile" -ForegroundColor Yellow
Write-Host "Skip Upload: $SkipUpload" -ForegroundColor Yellow
Write-Host "Email Only: $EmailOnly" -ForegroundColor Yellow
Write-Host ""

# 仮想環境の確認
$PythonExe = Join-Path $ProjectRoot "venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    Write-Host "Python実行ファイルが見つかりません: $PythonExe" -ForegroundColor Red
    exit 1
}

# 環境変数の設定
$env:PYTHONPATH = $ProjectRoot
$env:TECHZIP_TEST_MODE = "1"
$env:TECHZIP_DEBUG_MODE = "1"
$env:TECHZIP_LOG_LEVEL = "DEBUG"

if ($EmailOnly) {
    Write-Host "=== Gmail API Email Test ===" -ForegroundColor Cyan
    Write-Host "最新の統合テストを実行します..." -ForegroundColor Green
    
    & $PythonExe "final_integration_test_simple.py"
    
} elseif ($SkipUpload) {
    Write-Host "=== Error Detection Test (No Upload) ===" -ForegroundColor Cyan
    Write-Host "アップロードをスキップして、既存メールでエラー検知をテストします..." -ForegroundColor Green
    
    & $PythonExe "verify_error_file_url.py"
    
} else {
    Write-Host "=== Full E2E Test ===" -ForegroundColor Cyan
    Write-Host "完全なE2Eテストを実行します..." -ForegroundColor Green
    Write-Host "注意: 実際のファイルアップロードとメール監視が実行されます" -ForegroundColor Yellow
    Write-Host ""
    
    $confirmation = Read-Host "続行しますか? (y/N)"
    if ($confirmation -ne "y" -and $confirmation -ne "Y") {
        Write-Host "テストをキャンセルしました。" -ForegroundColor Yellow
        exit 0
    }
    
    Write-Host "GUIアプリケーションを起動します..." -ForegroundColor Cyan
    Write-Host "テスト手順:" -ForegroundColor Green
    Write-Host "1. エラー検知フローを選択" -ForegroundColor White
    Write-Host "2. テストファイル ($TestFile) を含むNコードを入力" -ForegroundColor White
    Write-Host "3. 実行してエラー検知が正しく動作するか確認" -ForegroundColor White
    Write-Host ""
    
    & $PythonExe "main.py"
}

$ExitCode = $LASTEXITCODE

Write-Host ""
Write-Host "=== Debug Test Complete ===" -ForegroundColor Cyan
Write-Host "Exit Code: $ExitCode" -ForegroundColor $(if ($ExitCode -eq 0) { "Green" } else { "Red" })
Write-Host "Test Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Green

exit $ExitCode