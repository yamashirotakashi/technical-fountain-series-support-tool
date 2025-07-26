# PowerShellスクリプト - 技術の泉シリーズ制作支援ツール（exe化対応版）

# スクリプトのディレクトリに移動
Set-Location $PSScriptRoot

Write-Host "技術の泉シリーズ制作支援ツール（exe化対応版）" -ForegroundColor Green
Write-Host "ネイティブ・グローバルPython環境で実行" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

# Python環境の詳細チェック
try {
    $pythonVersion = python --version 2>&1
    $pipVersion = pip --version 2>&1
    
    Write-Host "✓ Python環境: $pythonVersion" -ForegroundColor Green
    Write-Host "✓ pip環境: $pipVersion" -ForegroundColor Green
    
    # 必要な主要パッケージの確認
    Write-Host "`n主要パッケージの確認中..." -ForegroundColor Yellow
    $packages = @("PyQt6", "selenium", "requests", "google-api-python-client", "openpyxl")
    
    foreach ($package in $packages) {
        try {
            $result = pip show $package 2>&1
            if ($LASTEXITCODE -eq 0) {
                $version = ($result | Select-String "Version:").ToString().Split(" ")[1]
                Write-Host "✓ $package ($version)" -ForegroundColor Green
            } else {
                Write-Host "✗ $package (未インストール)" -ForegroundColor Red
            }
        } catch {
            Write-Host "✗ $package (チェック失敗)" -ForegroundColor Red
        }
    }
    
    Write-Host "`nアプリケーションを起動します..." -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Gray
    
    # アプリケーションを起動
    python main.py
    
} catch {
    Write-Host "✗ Python環境エラー" -ForegroundColor Red
    Write-Host "対処法:" -ForegroundColor Yellow
    Write-Host "1. Pythonをグローバル環境にインストール" -ForegroundColor White
    Write-Host "2. pip install -r requirements.txt を実行" -ForegroundColor White
    Write-Host "3. 環境変数PATHにPythonを追加" -ForegroundColor White
}

Write-Host "`n=" * 60 -ForegroundColor Gray
Write-Host "終了するには任意のキーを押してください..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")