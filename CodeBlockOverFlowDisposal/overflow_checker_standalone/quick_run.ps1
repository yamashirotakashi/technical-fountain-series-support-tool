# -*- coding: utf-8 -*-
# CodeBlock Overflow Checker - クイック起動スクリプト
# 既存の仮想環境を使用してアプリケーションを起動

# スクリプトのディレクトリに移動
Set-Location $PSScriptRoot

# 仮想環境の確認
if (-not (Test-Path ".\venv")) {
    Write-Host "仮想環境が見つかりません。setup_and_run.ps1 を実行してください。" -ForegroundColor Red
    exit 1
}

# 仮想環境のアクティベート
Write-Host "仮想環境をアクティベート中..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# PyMuPDFの確認（よくある問題なので）
Write-Host "PyMuPDFの確認中..." -ForegroundColor Yellow
python -c "import fitz; print(f'PyMuPDF OK: {fitz.version}')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "PyMuPDFが見つかりません。インストール中..." -ForegroundColor Yellow
    pip install PyMuPDF
}

# アプリケーション起動
Write-Host "CodeBlock Overflow Checkerを起動中..." -ForegroundColor Green
python run_ultimate.py