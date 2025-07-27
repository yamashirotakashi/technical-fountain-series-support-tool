# EXE環境の設定状況を確認

Write-Host "=== TECHZIP EXE環境 設定確認 ===" -ForegroundColor Cyan
Write-Host ""

# ユーザーディレクトリの確認
$userDir = "$env:USERPROFILE\.techzip"
$configDir = "$userDir\config"

Write-Host "1. ディレクトリ構造:" -ForegroundColor Yellow
if (Test-Path $userDir) {
    Write-Host "   ✓ $userDir" -ForegroundColor Green
    Get-ChildItem $userDir -Recurse | ForEach-Object {
        $indent = "   " * ($_.FullName.Split('\').Count - $userDir.Split('\').Count)
        Write-Host "$indent└─ $($_.Name)"
    }
} else {
    Write-Host "   ✗ $userDir が存在しません" -ForegroundColor Red
}

Write-Host ""
Write-Host "2. settings.json の内容:" -ForegroundColor Yellow
$settingsFile = "$configDir\settings.json"
if (Test-Path $settingsFile) {
    $settings = Get-Content $settingsFile -Raw | ConvertFrom-Json
    Write-Host "   Google Sheets設定:" -ForegroundColor Cyan
    Write-Host "   - sheet_id: $($settings.google_sheet.sheet_id)"
    Write-Host "   - credentials_path: $($settings.google_sheet.credentials_path)" -ForegroundColor Red
} else {
    Write-Host "   ✗ settings.json が存在しません" -ForegroundColor Red
}

Write-Host ""
Write-Host "3. Google Sheets認証ファイル:" -ForegroundColor Yellow
$possibleFiles = @(
    "$configDir\google_service_account.json",
    "$configDir\techbook-analytics-aa03914c6639.json"
)

foreach ($file in $possibleFiles) {
    if (Test-Path $file) {
        Write-Host "   ✓ $file ($(Get-Item $file).Length bytes)" -ForegroundColor Green
    } else {
        Write-Host "   ✗ $file" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "4. 修正方法:" -ForegroundColor Yellow
Write-Host "   settings.json の google_sheet.credentials_path を以下に変更してください:"
Write-Host '   "credentials_path": "config\\techbook-analytics-aa03914c6639.json"' -ForegroundColor Cyan
Write-Host ""
pause