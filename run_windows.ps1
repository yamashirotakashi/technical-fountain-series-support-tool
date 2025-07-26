# PowerShellスクリプト - 技術の泉シリーズ制作支援ツール起動

# スクリプトのディレクトリに移動
Set-Location $PSScriptRoot

Write-Host "技術の泉シリーズ制作支援ツールを起動しています..." -ForegroundColor Green

# 仮想環境のチェック
if (Test-Path ".\venv_windows") {
    # 仮想環境を有効化
    & ".\venv_windows\Scripts\Activate.ps1"
    
    # Pythonの実行パスを確認
    $pythonPath = ".\venv_windows\Scripts\python.exe"
    if (Test-Path $pythonPath) {
        Write-Host "仮想環境のPythonを使用: $pythonPath" -ForegroundColor Cyan
        # 仮想環境のPythonを明示的に使用
        & $pythonPath main.py
    } else {
        Write-Host "警告: 仮想環境のPythonが見つかりません。システムのPythonを使用します。" -ForegroundColor Yellow
        # フォールバック: システムのPythonを使用
        python.exe main.py
    }
    
    # 仮想環境から抜ける
    deactivate
} else {
    Write-Host "エラー: 仮想環境が見つかりません" -ForegroundColor Red
    Write-Host "setup_windows.ps1を先に実行してください" -ForegroundColor Yellow
}

Write-Host "終了するには任意のキーを押してください..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")