# セーフモード起動スクリプト

# スクリプトのディレクトリに移動
Set-Location $PSScriptRoot

Write-Host "技術の泉シリーズ制作支援ツール（セーフモード）" -ForegroundColor Yellow
Write-Host "依存関係の問題を確認しています..." -ForegroundColor Cyan

# 仮想環境のチェック
if (Test-Path ".\venv_windows") {
    # 仮想環境を有効化
    & ".\venv_windows\Scripts\Activate.ps1"
    
    # テストスクリプトを実行
    Write-Host "`nテストを実行中..." -ForegroundColor Cyan
    python test_launch.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nアプリケーションを起動します..." -ForegroundColor Green
        python main.py
    } else {
        Write-Host "`nエラーが発生しました。" -ForegroundColor Red
        Write-Host "fix_dependencies.ps1を実行して依存関係を修正してください。" -ForegroundColor Yellow
    }
} else {
    Write-Host "エラー: 仮想環境が見つかりません" -ForegroundColor Red
    Write-Host "setup_windows.ps1を先に実行してください" -ForegroundColor Yellow
}

Write-Host "`n終了するには任意のキーを押してください..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")