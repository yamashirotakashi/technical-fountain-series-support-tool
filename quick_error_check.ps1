# エラーファイル検知機能 - クイック起動スクリプト

Write-Host ""
Write-Host "🔍 エラーファイル検知機能を起動します..." -ForegroundColor Cyan
Write-Host ""

# 仮想環境チェック
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1" 2>$null
}

# 環境変数から必要な設定を読み込み（.envファイルがある場合）
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], [System.EnvironmentVariableTarget]::Process)
        }
    }
    Write-Host "✓ 環境設定を読み込みました" -ForegroundColor Green
}

# メインアプリケーション起動
Write-Host "アプリケーションを起動中..." -ForegroundColor Blue
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host " 使い方: " -ForegroundColor Yellow
Write-Host " 1. 組版エラーが発生したNコードを入力" -ForegroundColor White
Write-Host " 2. 赤い「エラーファイル検知」ボタンをクリック" -ForegroundColor White
Write-Host " 3. 20-40分でエラーファイルを特定します" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""

python main.py

$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    Write-Host ""
    Write-Host "⚠️  エラーが発生しました (コード: $exitCode)" -ForegroundColor Red
    Read-Host "Enterキーで終了"
}