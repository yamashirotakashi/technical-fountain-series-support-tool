# Fix encoding issues in Python files

Write-Host "=== Fixing Encoding Issues ===" -ForegroundColor Cyan

# Function to fix common encoding issues
function Fix-Encoding {
    param($FilePath)
    
    Write-Host "Fixing: $FilePath" -ForegroundColor Yellow
    
    $content = Get-Content $FilePath -Raw -Encoding UTF8
    
    # Common replacements for Japanese text corruption
    $replacements = @{
        '�E' = 'の'
        '琁E' = '処理'
        '設宁E' = '設定'
        '弁E' = '式'
        '篁E' = '成'
        '惁E' = '情報'
        'チE' = 'ツー'
        '亁E' = '了'
        'ヘルチE' = 'ヘルプ'
        'チE��' = 'デフ'
        '構篁E' = '構築'
        '�E期化' = '初期化'
        'E�' = 'の'
        '作�E' = '作成'
        '接綁E' = '接続'
        '実衁E' = '実行'
        '表示' = '表示'
        '取得' = '取得'
        '追加' = '追加'
    }
    
    foreach ($key in $replacements.Keys) {
        $content = $content -replace [regex]::Escape($key), $replacements[$key]
    }
    
    # Additional specific fixes
    $content = $content -replace '技術の泉シリーズ制作支援ツール', '技術の泉シリーズ制作支援ツール'
    $content = $content -replace 'アプリケーション', 'アプリケーション'
    $content = $content -replace 'ウィンドウ', 'ウィンドウ'
    $content = $content -replace 'メニュー', 'メニュー'
    $content = $content -replace 'ファイル', 'ファイル'
    $content = $content -replace 'ツール', 'ツール'
    $content = $content -replace 'ヘルプ', 'ヘルプ'
    $content = $content -replace 'バージョン', 'バージョン'
    
    # Save with UTF-8 encoding
    [System.IO.File]::WriteAllText($FilePath, $content, [System.Text.Encoding]::UTF8)
}

# Fix main files
$filesToFix = @(
    "main.py",
    "gui\main_window.py",
    "gui\main_window_no_google.py",
    "gui\components\input_panel.py",
    "gui\components\log_panel.py",
    "gui\components\progress_bar.py",
    "core\workflow_processor.py",
    "core\api_processor.py"
)

foreach ($file in $filesToFix) {
    if (Test-Path $file) {
        Fix-Encoding -FilePath $file
    }
}

Write-Host "`n=== Encoding fixes completed ===" -ForegroundColor Green
Write-Host "Please test the application again" -ForegroundColor Yellow

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")