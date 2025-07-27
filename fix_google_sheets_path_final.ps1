# Google Sheets認証パスの最終修正スクリプト

Write-Host "=== Google Sheets認証パスの最終修正 ===" -ForegroundColor Cyan
Write-Host ""

$userDir = "$env:USERPROFILE\.techzip"
$configDir = "$userDir\config"
$settingsFile = "$configDir\settings.json"

# 1. 現在の設定を確認
Write-Host "1. 現在の設定を確認中..." -ForegroundColor Yellow
if (Test-Path $settingsFile) {
    $settings = Get-Content $settingsFile -Raw | ConvertFrom-Json
    $currentPath = $settings.google_sheet.credentials_path
    Write-Host "   現在のパス: $currentPath" -ForegroundColor Red
    
    # 2. 実際の認証ファイルを探す
    Write-Host ""
    Write-Host "2. 実際の認証ファイルを検索中..." -ForegroundColor Yellow
    $authFiles = Get-ChildItem $configDir -Filter "*.json" | Where-Object {
        $_.Name -match "techbook-analytics|service_account"
    }
    
    if ($authFiles.Count -gt 0) {
        $authFile = $authFiles[0]
        Write-Host "   ✓ 認証ファイル発見: $($authFile.Name)" -ForegroundColor Green
        
        # 3. 設定を修正
        Write-Host ""
        Write-Host "3. 設定を修正中..." -ForegroundColor Yellow
        
        # 相対パス形式に修正
        $newPath = "config\$($authFile.Name)"
        $settings.google_sheet.credentials_path = $newPath
        
        # 設定を保存
        $settings | ConvertTo-Json -Depth 10 | Set-Content $settingsFile -Encoding UTF8
        
        Write-Host "   ✓ 新しいパス: $newPath" -ForegroundColor Green
        
        # 4. 修正後の確認
        Write-Host ""
        Write-Host "4. 修正後の確認..." -ForegroundColor Yellow
        $verifySettings = Get-Content $settingsFile -Raw | ConvertFrom-Json
        $verifyPath = $verifySettings.google_sheet.credentials_path
        
        if ($verifyPath -eq $newPath) {
            Write-Host "   ✓ 設定の修正が完了しました！" -ForegroundColor Green
            
            # ファイルの存在確認
            $fullPath = "$configDir\$($authFile.Name)"
            if (Test-Path $fullPath) {
                Write-Host "   ✓ 認証ファイルが正しい場所に存在します" -ForegroundColor Green
                Write-Host "     $fullPath" -ForegroundColor Gray
            }
        } else {
            Write-Host "   ✗ 設定の修正に失敗しました" -ForegroundColor Red
        }
    } else {
        Write-Host "   ✗ 認証ファイルが見つかりません" -ForegroundColor Red
        Write-Host "   以下のファイルをコピーしてください:" -ForegroundColor Yellow
        Write-Host "   元: C:\Users\tky99\dev\techbookanalytics\config\techbook-analytics-aa03914c6639.json"
        Write-Host "   先: $configDir"
    }
} else {
    Write-Host "   ✗ settings.json が存在しません" -ForegroundColor Red
}

Write-Host ""
Write-Host "スクリプトが完了しました。" -ForegroundColor Cyan
Write-Host "アプリケーションを再起動してください。" -ForegroundColor Yellow
pause