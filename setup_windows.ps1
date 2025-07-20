# PowerShellスクリプト - セットアップ

# スクリプトのディレクトリに移動
Set-Location $PSScriptRoot

Write-Host "Python仮想環境をセットアップしています..." -ForegroundColor Green

# Pythonのバージョンチェック
try {
    $pythonVersion = python --version 2>&1
    Write-Host "検出されたPython: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "エラー: Pythonがインストールされていません" -ForegroundColor Red
    Write-Host "https://www.python.org/ からPythonをインストールしてください" -ForegroundColor Yellow
    exit 1
}

# 仮想環境を作成
Write-Host "仮想環境を作成しています..." -ForegroundColor Green
python -m venv venv_windows

# 仮想環境を有効化
& ".\venv_windows\Scripts\Activate.ps1"

# pipをアップグレード
Write-Host "pipをアップグレードしています..." -ForegroundColor Green
python -m pip install --upgrade pip

# 依存関係をインストール
Write-Host "依存関係をインストールしています..." -ForegroundColor Green
pip install -r requirements.txt

Write-Host "`nセットアップが完了しました！" -ForegroundColor Green
Write-Host "run_windows.ps1を実行してアプリケーションを起動してください。" -ForegroundColor Yellow

Write-Host "`n終了するには任意のキーを押してください..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")