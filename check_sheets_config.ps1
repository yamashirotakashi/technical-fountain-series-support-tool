# Google Sheets設定を確認するスクリプト

Write-Host "=== Google Sheets設定確認 ===" -ForegroundColor Cyan
Write-Host ""

$settingsFile = "$env:USERPROFILE\.techzip\config\settings.json"

if (Test-Path $settingsFile) {
    $settings = Get-Content $settingsFile -Raw | ConvertFrom-Json
    
    Write-Host "1. 現在の設定:" -ForegroundColor Yellow
    Write-Host "   Sheet ID: $($settings.google_sheet.sheet_id)" -ForegroundColor Cyan
    Write-Host "   認証ファイル: $($settings.google_sheet.credentials_path)" -ForegroundColor Green
    
    # Sheet IDの検証
    Write-Host ""
    Write-Host "2. Sheet ID検証:" -ForegroundColor Yellow
    $sheetId = $settings.google_sheet.sheet_id
    
    if ($sheetId -eq "YOUR_SHEET_ID_HERE" -or $sheetId -eq "your-sheet-id") {
        Write-Host "   ⚠️ Sheet IDがプレースホルダーのままです！" -ForegroundColor Red
        Write-Host ""
        Write-Host "   正しいSheet IDに更新してください:" -ForegroundColor Yellow
        Write-Host "   1. Google Sheetsを開く" -ForegroundColor White
        Write-Host "   2. URLから以下の部分をコピー:" -ForegroundColor White
        Write-Host "      https://docs.google.com/spreadsheets/d/[ここの部分]/edit" -ForegroundColor Gray
        Write-Host ""
        Write-Host "   例: https://docs.google.com/spreadsheets/d/17DKsMGQ6krbhY7GIcX0iaeN-y8HcGGVkXt3d4oOckyQ/edit" -ForegroundColor Gray
        Write-Host "       → Sheet ID: 17DKsMGQ6krbhY7GIcX0iaeN-y8HcGGVkXt3d4oOckyQ" -ForegroundColor Cyan
    } else {
        Write-Host "   ✓ Sheet IDが設定されています: $sheetId" -ForegroundColor Green
        
        # URLを構築して表示
        $sheetUrl = "https://docs.google.com/spreadsheets/d/$sheetId/edit"
        Write-Host "   Google Sheets URL: $sheetUrl" -ForegroundColor Gray
    }
    
    # 開発環境の設定ファイルも確認
    Write-Host ""
    Write-Host "3. 開発環境の設定:" -ForegroundColor Yellow
    $devSettingsFile = ".\config\settings.json"
    if (Test-Path $devSettingsFile) {
        $devSettings = Get-Content $devSettingsFile -Raw | ConvertFrom-Json
        Write-Host "   開発環境のSheet ID: $($devSettings.google_sheet.sheet_id)" -ForegroundColor Cyan
        
        if ($devSettings.google_sheet.sheet_id -ne $settings.google_sheet.sheet_id) {
            Write-Host "   ⚠️ 開発環境とEXE環境で異なるSheet IDが設定されています" -ForegroundColor Yellow
        }
    }
    
    # 修正方法の提示
    if ($sheetId -eq "YOUR_SHEET_ID_HERE" -or $sheetId -eq "your-sheet-id") {
        Write-Host ""
        Write-Host "4. 修正方法:" -ForegroundColor Yellow
        Write-Host "   以下のコマンドを実行してSheet IDを更新:" -ForegroundColor White
        Write-Host ""
        Write-Host '   $settings = Get-Content "' + $settingsFile + '" -Raw | ConvertFrom-Json' -ForegroundColor Cyan
        Write-Host '   $settings.google_sheet.sheet_id = "17DKsMGQ6krbhY7GIcX0iaeN-y8HcGGVkXt3d4oOckyQ"' -ForegroundColor Cyan
        Write-Host '   $settings | ConvertTo-Json -Depth 10 | Set-Content "' + $settingsFile + '" -Encoding UTF8' -ForegroundColor Cyan
        Write-Host ""
        Write-Host "   または、メニューから「ツール」→「設定」で変更可能" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "確認完了。" -ForegroundColor Cyan
pause