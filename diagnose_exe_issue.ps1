# EXE環境のGoogle Sheets認証問題を詳細診断

Write-Host "=== TECHZIP EXE環境 詳細診断 ===" -ForegroundColor Cyan
Write-Host ""

$userDir = "$env:USERPROFILE\.techzip"
$configDir = "$userDir\config"
$settingsFile = "$configDir\settings.json"

# 1. ディレクトリとファイルの確認
Write-Host "1. ディレクトリ構造の確認:" -ForegroundColor Yellow
if (Test-Path $userDir) {
    Write-Host "   ✓ ユーザーディレクトリ: $userDir" -ForegroundColor Green
    
    # configディレクトリの中身を表示
    if (Test-Path $configDir) {
        Write-Host "   ✓ configディレクトリ:" -ForegroundColor Green
        Get-ChildItem $configDir | ForEach-Object {
            $size = if ($_.PSIsContainer) { "<DIR>" } else { "$($_.Length) bytes" }
            Write-Host "      - $($_.Name) ($size)"
        }
    }
} else {
    Write-Host "   ✗ ユーザーディレクトリが存在しません" -ForegroundColor Red
}

# 2. settings.jsonの内容確認
Write-Host ""
Write-Host "2. settings.json の詳細確認:" -ForegroundColor Yellow
if (Test-Path $settingsFile) {
    $content = Get-Content $settingsFile -Raw
    $settings = $content | ConvertFrom-Json
    
    Write-Host "   ファイルサイズ: $((Get-Item $settingsFile).Length) bytes" -ForegroundColor Cyan
    Write-Host "   最終更新: $((Get-Item $settingsFile).LastWriteTime)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Google Sheets設定:" -ForegroundColor Cyan
    Write-Host "   - sheet_id: $($settings.google_sheet.sheet_id)"
    Write-Host "   - credentials_path: $($settings.google_sheet.credentials_path)" -ForegroundColor Yellow
    
    # 生のJSONも表示
    Write-Host ""
    Write-Host "   生のJSON (google_sheet部分):" -ForegroundColor Cyan
    $googleSheetJson = $settings.google_sheet | ConvertTo-Json -Compress
    Write-Host "   $googleSheetJson" -ForegroundColor Gray
} else {
    Write-Host "   ✗ settings.jsonが存在しません" -ForegroundColor Red
}

# 3. 認証ファイルの確認
Write-Host ""
Write-Host "3. Google Sheets認証ファイルの確認:" -ForegroundColor Yellow
$expectedFiles = @(
    "$configDir\google_service_account.json",
    "$configDir\techbook-analytics-aa03914c6639.json"
)

$foundAuth = $false
foreach ($file in $expectedFiles) {
    if (Test-Path $file) {
        Write-Host "   ✓ $file" -ForegroundColor Green
        Write-Host "     サイズ: $((Get-Item $file).Length) bytes"
        Write-Host "     更新日: $((Get-Item $file).LastWriteTime)"
        $foundAuth = $true
    } else {
        Write-Host "   ✗ $file (存在しない)" -ForegroundColor Gray
    }
}

if (-not $foundAuth) {
    Write-Host ""
    Write-Host "   ⚠️ 認証ファイルが見つかりません！" -ForegroundColor Red
}

# 4. プロセスの確認
Write-Host ""
Write-Host "4. 実行中のTECHZIPプロセス:" -ForegroundColor Yellow
$processes = Get-Process | Where-Object { $_.Name -like "*TECHZIP*" }
if ($processes) {
    foreach ($proc in $processes) {
        Write-Host "   - $($proc.Name) (PID: $($proc.Id))"
    }
} else {
    Write-Host "   実行中のプロセスなし" -ForegroundColor Gray
}

# 5. 修正提案
Write-Host ""
Write-Host "5. 修正提案:" -ForegroundColor Yellow

if (Test-Path $settingsFile) {
    $settings = Get-Content $settingsFile -Raw | ConvertFrom-Json
    $currentPath = $settings.google_sheet.credentials_path
    
    if ($currentPath -eq "google_service_account.json" -or $currentPath -eq "config/google_service_account.json") {
        Write-Host "   ⚠️ 古いパス形式が使用されています" -ForegroundColor Red
        Write-Host "   以下のコマンドで修正してください:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host '   $settings = Get-Content "' + $settingsFile + '" -Raw | ConvertFrom-Json' -ForegroundColor Cyan
        Write-Host '   $settings.google_sheet.credentials_path = "config\techbook-analytics-aa03914c6639.json"' -ForegroundColor Cyan
        Write-Host '   $settings | ConvertTo-Json -Depth 10 | Set-Content "' + $settingsFile + '" -Encoding UTF8' -ForegroundColor Cyan
    } elseif ($currentPath -match "techbook-analytics") {
        Write-Host "   ✓ 正しいファイル名が設定されています" -ForegroundColor Green
        
        # パス形式の確認
        if ($currentPath -match "^config[/\\]") {
            Write-Host "   ✓ 相対パス形式が使用されています" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ 絶対パスが使用されています。相対パスに変更を推奨" -ForegroundColor Yellow
        }
    }
}

# 6. 環境変数の確認
Write-Host ""
Write-Host "6. 関連する環境変数:" -ForegroundColor Yellow
$envVars = @("TECHZIP_IS_EXE", "GOOGLE_SHEETS_CREDENTIALS_PATH", "GOOGLE_SHEETS_ID")
foreach ($var in $envVars) {
    $value = [Environment]::GetEnvironmentVariable($var)
    if ($value) {
        Write-Host "   $var = $value" -ForegroundColor Green
    } else {
        Write-Host "   $var = (未設定)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "診断完了。" -ForegroundColor Cyan
pause