# PowerShellスクリプト - 技術の泉シリーズ制作支援ツール起動（ネイティブ版）

# スクリプトのディレクトリに移動
Set-Location $PSScriptRoot

Write-Host "技術の泉シリーズ制作支援ツールを起動しています..." -ForegroundColor Green
Write-Host "ネイティブ・グローバル環境で実行します" -ForegroundColor Cyan

# システムのPythonを直接使用（exe化対応）
try {
    # Pythonが利用可能かチェック
    $pythonVersion = python --version 2>&1
    Write-Host "Python環境: $pythonVersion" -ForegroundColor Green
    
    # アプリケーションを起動
    python main.py
    
} catch {
    # フォールバック: python.exeを試行
    try {
        $pythonVersion = python.exe --version 2>&1
        Write-Host "Python環境: $pythonVersion" -ForegroundColor Green
        python.exe main.py
    } catch {
        Write-Host "エラー: Pythonが見つかりません" -ForegroundColor Red
        Write-Host "Pythonがグローバル環境にインストールされていることを確認してください" -ForegroundColor Yellow
        Write-Host "必要なパッケージもpip install -r requirements.txtでインストールしてください" -ForegroundColor Yellow
    }
}

Write-Host "終了するには任意のキーを押してください..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")