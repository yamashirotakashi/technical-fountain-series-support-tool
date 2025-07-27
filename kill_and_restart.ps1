# TECHZIPプロセスを終了して再起動するスクリプト

Write-Host "=== TECHZIP プロセス管理 ===" -ForegroundColor Cyan
Write-Host ""

# 1. 現在のプロセスを確認
Write-Host "1. 現在実行中のTECHZIPプロセス:" -ForegroundColor Yellow
$processes = Get-Process | Where-Object { $_.Name -like "*TECHZIP*" }
if ($processes) {
    foreach ($proc in $processes) {
        Write-Host "   - $($proc.Name) (PID: $($proc.Id))" -ForegroundColor Red
    }
    
    # 2. プロセスを終了
    Write-Host ""
    Write-Host "2. プロセスを終了中..." -ForegroundColor Yellow
    $processes | Stop-Process -Force
    Start-Sleep -Seconds 2
    
    # 確認
    $remaining = Get-Process | Where-Object { $_.Name -like "*TECHZIP*" }
    if ($remaining) {
        Write-Host "   ⚠️ まだプロセスが残っています" -ForegroundColor Red
    } else {
        Write-Host "   ✓ すべてのプロセスが終了しました" -ForegroundColor Green
    }
} else {
    Write-Host "   実行中のプロセスはありません" -ForegroundColor Gray
}

# 3. キャッシュをクリア
Write-Host ""
Write-Host "3. キャッシュとログをクリア中..." -ForegroundColor Yellow
$tempDir = "$env:USERPROFILE\.techzip\temp"
$logsDir = "$env:USERPROFILE\.techzip\logs"

if (Test-Path $tempDir) {
    Remove-Item "$tempDir\*" -Force -Recurse -ErrorAction SilentlyContinue
    Write-Host "   ✓ tempディレクトリをクリアしました" -ForegroundColor Green
}

if (Test-Path $logsDir) {
    # 最新のログファイルは残す
    $logFiles = Get-ChildItem $logsDir -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 1
    if ($logFiles) {
        $logFiles | Remove-Item -Force
        Write-Host "   ✓ 古いログファイルを削除しました（最新は保持）" -ForegroundColor Green
    }
}

# 4. settings.jsonの確認
Write-Host ""
Write-Host "4. 設定ファイルの確認:" -ForegroundColor Yellow
$settingsFile = "$env:USERPROFILE\.techzip\config\settings.json"
if (Test-Path $settingsFile) {
    $settings = Get-Content $settingsFile -Raw | ConvertFrom-Json
    $credsPath = $settings.google_sheet.credentials_path
    Write-Host "   Google Sheets認証パス: $credsPath" -ForegroundColor Cyan
    
    if ($credsPath -match "techbook-analytics.*\.json") {
        Write-Host "   ✓ 正しいパスが設定されています" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ 古いパスが設定されています" -ForegroundColor Red
    }
}

# 5. アプリケーション再起動の準備
Write-Host ""
Write-Host "5. アプリケーションを起動しますか？" -ForegroundColor Yellow
$response = Read-Host "   起動する場合は 'y' を入力 (y/n)"

if ($response -eq 'y') {
    $exePath = ".\dist\TECHZIP1.5.exe"
    if (Test-Path $exePath) {
        Write-Host ""
        Write-Host "   TECHZIP1.5.exeを起動中..." -ForegroundColor Cyan
        Start-Process $exePath
        Write-Host "   ✓ 起動しました" -ForegroundColor Green
    } else {
        Write-Host "   ✗ EXEファイルが見つかりません: $exePath" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "完了しました。" -ForegroundColor Cyan