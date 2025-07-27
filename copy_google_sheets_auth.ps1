# Google Sheets認証ファイルをEXE用ディレクトリにコピー

$sourceFile = "C:\Users\tky99\dev\techbookanalytics\config\techbook-analytics-aa03914c6639.json"
$targetDir = "$env:USERPROFILE\.techzip\config"
$targetFile = "$targetDir\techbook-analytics-aa03914c6639.json"

Write-Host "Google Sheets認証ファイルのコピー" -ForegroundColor Cyan
Write-Host "元ファイル: $sourceFile" -ForegroundColor Yellow
Write-Host "コピー先: $targetFile" -ForegroundColor Yellow

# ディレクトリの作成
if (!(Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    Write-Host "ディレクトリを作成しました: $targetDir" -ForegroundColor Green
}

# ファイルのコピー
if (Test-Path $sourceFile) {
    Copy-Item -Path $sourceFile -Destination $targetFile -Force
    Write-Host "✓ 認証ファイルをコピーしました" -ForegroundColor Green
    
    # settings.jsonの更新も必要
    $settingsFile = "$targetDir\settings.json"
    if (Test-Path $settingsFile) {
        Write-Host "`nsettings.jsonを更新中..." -ForegroundColor Yellow
        $settings = Get-Content $settingsFile -Raw | ConvertFrom-Json
        
        # 相対パスに更新
        if ($settings.google_sheet -and $settings.google_sheet.credentials_path) {
            $settings.google_sheet.credentials_path = "config\techbook-analytics-aa03914c6639.json"
            $settings | ConvertTo-Json -Depth 10 | Set-Content $settingsFile -Encoding UTF8
            Write-Host "✓ settings.jsonを更新しました" -ForegroundColor Green
        }
    }
} else {
    Write-Host "✗ 元ファイルが見つかりません: $sourceFile" -ForegroundColor Red
}

Write-Host "`n完了しました。" -ForegroundColor Cyan
pause