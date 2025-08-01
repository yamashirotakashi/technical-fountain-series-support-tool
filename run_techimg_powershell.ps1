# TechImgFile PowerShell起動スクリプト
# Qt6ベースの画像・文書処理ツール

Write-Host "=== TechImgFile (Qt6) 起動中 ===" -ForegroundColor Green

# プロジェクトディレクトリに移動
$ProjectRoot = "C:\Users\tky99\DEV\technical-fountain-series-support-tool"
Set-Location $ProjectRoot

Write-Host "プロジェクトディレクトリ: $ProjectRoot" -ForegroundColor Yellow

# 仮想環境の確認と有効化
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "仮想環境を有効化中..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "警告: 仮想環境が見つかりません" -ForegroundColor Red
    Write-Host "venv\Scripts\Activate.ps1 が存在しません"
    exit 1
}

# Qt6アプリケーション起動
Write-Host "TechImgFile (Qt6) を起動します..." -ForegroundColor Green
python app\modules\techbook27_analyzer\main.py

Write-Host "アプリケーションが終了しました" -ForegroundColor Yellow