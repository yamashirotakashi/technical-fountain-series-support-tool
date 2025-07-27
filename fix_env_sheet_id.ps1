# .envファイルのGoogle Sheet IDを修正

Write-Host "=== .envファイルのSheet ID修正 ===" -ForegroundColor Cyan
Write-Host ""

$envFile = "$env:USERPROFILE\.techzip\.env"
$settingsFile = "$env:USERPROFILE\.techzip\config\settings.json"

if (Test-Path $envFile) {
    # バックアップを作成
    $backupFile = "$envFile.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $envFile $backupFile
    Write-Host "✓ バックアップ作成: $backupFile" -ForegroundColor Green
    
    # settings.jsonからSheet IDを取得
    if (Test-Path $settingsFile) {
        $settings = Get-Content $settingsFile -Raw | ConvertFrom-Json
        $correctSheetId = $settings.google_sheet.sheet_id
        
        Write-Host ""
        Write-Host "設定ファイルのSheet ID: $correctSheetId" -ForegroundColor Cyan
        
        # .envファイルを読み込み
        $envContent = Get-Content $envFile
        $newContent = @()
        $updated = $false
        
        foreach ($line in $envContent) {
            if ($line -match "^GOOGLE_SHEETS_ID=") {
                $oldValue = $line -replace "GOOGLE_SHEETS_ID=", ""
                if ($oldValue -eq "your-sheet-id" -or $oldValue -eq "YOUR_SHEET_ID_HERE") {
                    $newContent += "GOOGLE_SHEETS_ID=$correctSheetId"
                    $updated = $true
                    Write-Host ""
                    Write-Host "✓ Sheet IDを更新:" -ForegroundColor Green
                    Write-Host "   旧: $oldValue" -ForegroundColor Red
                    Write-Host "   新: $correctSheetId" -ForegroundColor Green
                } else {
                    $newContent += $line
                }
            } else {
                $newContent += $line
            }
        }
        
        if ($updated) {
            # ファイルを保存
            $newContent | Set-Content $envFile -Encoding UTF8
            Write-Host ""
            Write-Host "✓ .envファイルを更新しました" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "Sheet IDは既に正しく設定されています" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "✗ .envファイルが存在しません: $envFile" -ForegroundColor Red
}

Write-Host ""
Write-Host "完了。アプリケーションを再起動してください。" -ForegroundColor Cyan
pause