# PowerShellスクリプト - 技術の泉シリーズ制作支援ツール起動

# スクリプトのディレクトリに移動
Set-Location $PSScriptRoot

Write-Host "技術の泉シリーズ制作支援ツールを起動しています..." -ForegroundColor Green

# 仮想環境のチェック
if (Test-Path ".\venv_windows") {
    # 仮想環境を有効化
    & ".\venv_windows\Scripts\Activate.ps1"
    
    # アプリケーションを起動
    python main.py
} else {
    Write-Host "エラー: 仮想環境が見つかりません" -ForegroundColor Red
    Write-Host "setup_windows.ps1を先に実行してください" -ForegroundColor Yellow
}

Write-Host "終了するには任意のキーを押してください..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")