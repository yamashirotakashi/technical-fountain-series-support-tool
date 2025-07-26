# 依存関係の修正スクリプト

Write-Host "依存関係を修正しています..." -ForegroundColor Yellow

# 仮想環境を有効化
if (Test-Path ".\venv_windows") {
    & ".\venv_windows\Scripts\Activate.ps1"
    
    # urllib3をダウングレード
    Write-Host "urllib3をダウングレードしています..." -ForegroundColor Cyan
    pip uninstall urllib3 -y
    pip install "urllib3<2.0"
    
    # 依存関係を再インストール
    Write-Host "依存関係を再インストールしています..." -ForegroundColor Cyan
    pip install -r requirements.txt --upgrade
    
    Write-Host "完了しました！" -ForegroundColor Green
} else {
    Write-Host "エラー: 仮想環境が見つかりません" -ForegroundColor Red
}

Write-Host "終了するには任意のキーを押してください..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")