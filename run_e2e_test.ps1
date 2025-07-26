# TechZip E2E Test Launcher for PowerShell 7
# 仮想環境でアプリケーションを起動してE2Eテストを実行

param(
    [switch]$TestMode,
    [string]$LogLevel = "INFO"
)

# PowerShell 7のチェック
if ($PSVersionTable.PSVersion.Major -lt 7) {
    Write-Host "PowerShell 7 が必要です。現在のバージョン: $($PSVersionTable.PSVersion)" -ForegroundColor Red
    Write-Host "PowerShell 7をインストールしてから再実行してください。" -ForegroundColor Yellow
    exit 1
}

# プロジェクトディレクトリに移動
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "=== TechZip E2E Test Launcher ===" -ForegroundColor Cyan
Write-Host "Project Root: $ProjectRoot" -ForegroundColor Green
Write-Host "PowerShell Version: $($PSVersionTable.PSVersion)" -ForegroundColor Green
Write-Host "Execution Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Green
Write-Host ""

# 仮想環境の確認
$VenvPath = Join-Path $ProjectRoot "venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"

if (-not (Test-Path $VenvPath)) {
    Write-Host "仮想環境が見つかりません: $VenvPath" -ForegroundColor Red
    Write-Host "仮想環境を作成してから再実行してください。" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $PythonExe)) {
    Write-Host "Python実行ファイルが見つかりません: $PythonExe" -ForegroundColor Red
    exit 1
}

Write-Host "仮想環境確認: OK" -ForegroundColor Green
Write-Host "Python Path: $PythonExe" -ForegroundColor Cyan

# 必要なファイルの確認
$RequiredFiles = @(
    "main.py",
    "config\settings.json",
    "config\gmail_oauth_credentials.json"
)

$MissingFiles = @()
foreach ($file in $RequiredFiles) {
    $FilePath = Join-Path $ProjectRoot $file
    if (-not (Test-Path $FilePath)) {
        $MissingFiles += $file
    }
}

if ($MissingFiles.Count -gt 0) {
    Write-Host "必要なファイルが見つかりません:" -ForegroundColor Red
    foreach ($file in $MissingFiles) {
        Write-Host "  - $file" -ForegroundColor Yellow
    }
    exit 1
}

Write-Host "必要なファイル確認: OK" -ForegroundColor Green

# 環境変数の設定
$env:PYTHONPATH = $ProjectRoot
$env:TECHZIP_LOG_LEVEL = $LogLevel

# テストモードの場合は環境変数を設定
if ($TestMode) {
    $env:TECHZIP_TEST_MODE = "1"
    Write-Host "テストモード: 有効" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== アプリケーション起動 ===" -ForegroundColor Cyan

# Gmail APIの認証状態をチェック
$TokenPath = Join-Path $ProjectRoot "config\gmail_token.pickle"
if (Test-Path $TokenPath) {
    Write-Host "Gmail API認証: 既存トークン使用" -ForegroundColor Green
} else {
    Write-Host "Gmail API認証: 初回認証が必要です" -ForegroundColor Yellow
    Write-Host "ブラウザで認証画面が開きます..." -ForegroundColor Cyan
}

Write-Host ""
Write-Host "アプリケーションを起動しています..." -ForegroundColor Cyan
Write-Host "終了するには Ctrl+C を押してください" -ForegroundColor Yellow
Write-Host ""

try {
    # アプリケーション起動
    & $PythonExe "main.py"
    
    $ExitCode = $LASTEXITCODE
    
    if ($ExitCode -eq 0) {
        Write-Host ""
        Write-Host "アプリケーションが正常に終了しました" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "アプリケーションがエラーで終了しました (Exit Code: $ExitCode)" -ForegroundColor Red
    }
    
} catch {
    Write-Host ""
    Write-Host "アプリケーション実行中にエラーが発生しました:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    $ExitCode = 1
}

Write-Host ""
Write-Host "=== E2E Test Complete ===" -ForegroundColor Cyan
Write-Host "終了時刻: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Green

exit $ExitCode