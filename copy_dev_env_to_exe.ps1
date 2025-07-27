# 開発環境の.envファイルをEXE環境にコピー

Write-Host "=== 開発環境 → EXE環境 .envファイルコピー ===" -ForegroundColor Cyan
Write-Host ""

# パスの定義
$devEnvFile = ".\\.env"
$exeEnvFile = "$env:USERPROFILE\.techzip\.env"
$exeConfigDir = "$env:USERPROFILE\.techzip"

# 1. 開発環境の.envファイルを確認
Write-Host "1. 開発環境の.envファイルを確認:" -ForegroundColor Yellow
if (Test-Path $devEnvFile) {
    Write-Host "   ✓ 開発環境の.envファイルが存在: $devEnvFile" -ForegroundColor Green
    
    # 内容を表示（機密情報は隠す）
    Write-Host ""
    Write-Host "   内容（一部マスク）:" -ForegroundColor Cyan
    Get-Content $devEnvFile | ForEach-Object {
        if ($_ -match "PASSWORD=|TOKEN=|SECRET=") {
            $key = ($_ -split "=")[0]
            Write-Host "   $key=***" -ForegroundColor Gray
        } else {
            Write-Host "   $_" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "   ✗ 開発環境の.envファイルが見つかりません" -ForegroundColor Red
    Write-Host "   開発環境のルートディレクトリで実行してください" -ForegroundColor Yellow
    pause
    exit
}

# 2. EXE環境のディレクトリ確認
Write-Host ""
Write-Host "2. EXE環境のディレクトリを確認:" -ForegroundColor Yellow
if (-not (Test-Path $exeConfigDir)) {
    Write-Host "   ディレクトリを作成: $exeConfigDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $exeConfigDir -Force | Out-Null
}

# 3. 既存の.envファイルのバックアップ
if (Test-Path $exeEnvFile) {
    $backupFile = "$exeEnvFile.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $exeEnvFile $backupFile
    Write-Host "   ✓ 既存ファイルをバックアップ: $backupFile" -ForegroundColor Green
}

# 4. ファイルをコピー
Write-Host ""
Write-Host "3. .envファイルをコピー:" -ForegroundColor Yellow
try {
    Copy-Item $devEnvFile $exeEnvFile -Force
    Write-Host "   ✓ コピー完了: $devEnvFile → $exeEnvFile" -ForegroundColor Green
    
    # コピー後の確認
    Write-Host ""
    Write-Host "4. コピー後の確認:" -ForegroundColor Yellow
    $copiedContent = Get-Content $exeEnvFile
    
    # 重要な設定項目をチェック
    $requiredKeys = @(
        "GMAIL_ADDRESS",
        "GMAIL_APP_PASSWORD",
        "GOOGLE_SHEETS_ID",
        "GOOGLE_SHEETS_CREDENTIALS_PATH",
        "GITHUB_TOKEN",
        "SLACK_BOT_TOKEN",
        "WORD2XHTML5_USERNAME",
        "WORD2XHTML5_PASSWORD"
    )
    
    foreach ($key in $requiredKeys) {
        $found = $copiedContent | Where-Object { $_ -match "^$key=" }
        if ($found) {
            $value = ($found -split "=", 2)[1]
            if ($value -and $value -ne "your-$($key.ToLower())" -and $value -ne "YOUR_$($key.ToUpper())_HERE") {
                Write-Host "   ✓ ${key}: 設定済み" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️ ${key}: プレースホルダーのまま" -ForegroundColor Yellow
            }
        } else {
            Write-Host "   ✗ ${key}: 未設定" -ForegroundColor Red
        }
    }
    
} catch {
    Write-Host "   ✗ コピーに失敗: $_" -ForegroundColor Red
}

# 5. アプリケーション再起動の案内
Write-Host ""
Write-Host "5. 次のステップ:" -ForegroundColor Yellow
Write-Host "   1. 実行中のTECHZIPを終了" -ForegroundColor White
Write-Host "   2. TECHZIP1.5.exeを再起動" -ForegroundColor White
Write-Host ""
Write-Host "   または、以下のコマンドを実行:" -ForegroundColor Gray
Write-Host '   Get-Process | Where-Object { $_.Name -like "*TECHZIP*" } | Stop-Process -Force' -ForegroundColor Cyan
Write-Host '   .\dist\TECHZIP1.5.exe' -ForegroundColor Cyan

Write-Host ""
Write-Host "完了。" -ForegroundColor Cyan
pause