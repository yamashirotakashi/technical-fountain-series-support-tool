# EXE実行時の環境変数を確認

Write-Host "=== EXE環境変数チェック ===" -ForegroundColor Cyan
Write-Host ""

# .envファイルの確認
Write-Host "1. .envファイルの確認:" -ForegroundColor Yellow
$envFile = "$env:USERPROFILE\.techzip\.env"

if (Test-Path $envFile) {
    Write-Host "   ✓ .envファイルが存在: $envFile" -ForegroundColor Green
    Write-Host ""
    Write-Host "   内容（GOOGLE_SHEETS関連）:" -ForegroundColor Cyan
    Get-Content $envFile | Where-Object { $_ -match "GOOGLE_SHEETS" } | ForEach-Object {
        Write-Host "   $_"
    }
    
    # Sheet IDの行を特別にチェック
    $sheetIdLine = Get-Content $envFile | Where-Object { $_ -match "^GOOGLE_SHEETS_ID=" }
    if ($sheetIdLine) {
        $sheetId = $sheetIdLine -replace "GOOGLE_SHEETS_ID=", ""
        if ($sheetId -eq "your-sheet-id" -or $sheetId -eq "YOUR_SHEET_ID_HERE") {
            Write-Host ""
            Write-Host "   ⚠️ Sheet IDがプレースホルダーのままです！" -ForegroundColor Red
            Write-Host "   .envファイルを編集して正しいSheet IDを設定してください" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "   ✗ .envファイルが存在しません" -ForegroundColor Red
}

# settings.jsonの再確認
Write-Host ""
Write-Host "2. settings.jsonの確認:" -ForegroundColor Yellow
$settingsFile = "$env:USERPROFILE\.techzip\config\settings.json"

if (Test-Path $settingsFile) {
    $settings = Get-Content $settingsFile -Raw | ConvertFrom-Json
    Write-Host "   Sheet ID: $($settings.google_sheet.sheet_id)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "完了。" -ForegroundColor Cyan
pause