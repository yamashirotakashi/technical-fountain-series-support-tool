# -*- coding: utf-8 -*-
# CodeBlock Overflow Checker - セットアップ＆実行スクリプト
# 仮想環境の構築、ライブラリインストール、アプリケーション起動を自動化

# スクリプトのディレクトリに移動
Set-Location $PSScriptRoot

Write-Host "===== CodeBlock Overflow Checker セットアップ =====" -ForegroundColor Cyan

# 1. 仮想環境の確認・作成
$venvPath = ".\venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "仮想環境を作成中..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "仮想環境の作成に失敗しました。" -ForegroundColor Red
        exit 1
    }
    Write-Host "仮想環境を作成しました。" -ForegroundColor Green
} else {
    Write-Host "既存の仮想環境を使用します。" -ForegroundColor Green
}

# 2. 仮想環境のアクティベート
Write-Host "仮想環境をアクティベート中..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# 3. pipのアップグレード
Write-Host "pipをアップグレード中..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# 4. 必要なライブラリのインストール
Write-Host "必要なライブラリをインストール中..." -ForegroundColor Yellow

# 基本的な依存関係
$libraries = @(
    "PyQt6>=6.4.0",
    "PyPDF2>=3.0.1",
    "Pillow>=9.3.0",
    "PyMuPDF>=1.23.8",
    "pdfplumber>=0.9.0",
    "pytesseract>=0.3.10",
    "opencv-python>=4.6.0",
    "numpy>=1.21.0",
    "colorlog>=6.7.0"
)

# Windows環境の場合はpywin32も追加
if ($env:OS -eq "Windows_NT") {
    $libraries += "pywin32>=305"
}

foreach ($lib in $libraries) {
    Write-Host "  - $lib をインストール中..." -ForegroundColor Gray
    pip install $lib
}

# 5. Tesseract OCRの確認と環境変数設定
Write-Host "`nTesseract OCRの確認中..." -ForegroundColor Yellow

# 複数の可能なパスをチェック
$tesseractPaths = @(
    "C:\Program Files\Tesseract-OCR\tesseract.exe",
    "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    "$env:LOCALAPPDATA\Tesseract-OCR\tesseract.exe",
    "$env:LOCALAPPDATA\Programs\Tesseract-OCR\tesseract.exe"
)

$foundTesseract = $false
foreach ($path in $tesseractPaths) {
    if (Test-Path $path) {
        Write-Host "Tesseract OCRが検出されました: $path" -ForegroundColor Green
        
        # 環境変数に設定
        $env:TESSERACT_CMD = $path
        Write-Host "環境変数TESSERACT_CMDを設定しました。" -ForegroundColor Green
        
        # PATHにも追加
        $tesseractDir = Split-Path $path -Parent
        if ($env:PATH -notlike "*$tesseractDir*") {
            $env:PATH = "$tesseractDir;$env:PATH"
            Write-Host "PATHに追加しました: $tesseractDir" -ForegroundColor Green
        }
        
        $foundTesseract = $true
        break
    }
}

if (-not $foundTesseract) {
    # whereコマンドで探す
    try {
        $whereResult = where.exe tesseract 2>$null
        if ($whereResult) {
            Write-Host "システムPATHでTesseractが見つかりました: $whereResult" -ForegroundColor Green
            $env:TESSERACT_CMD = $whereResult
            $foundTesseract = $true
        }
    } catch {
        # whereコマンドが失敗した場合は無視
    }
}

if (-not $foundTesseract) {
    Write-Host "警告: Tesseract OCRが見つかりません。" -ForegroundColor Yellow
    Write-Host "以下の方法でインストールしてください:" -ForegroundColor Yellow
    Write-Host "1. https://github.com/UB-Mannheim/tesseract/wiki からダウンロード" -ForegroundColor Yellow
    Write-Host "2. インストール後、このスクリプトを再実行" -ForegroundColor Yellow
    Write-Host "" -ForegroundColor Yellow
    Write-Host "または、既にインストール済みの場合:" -ForegroundColor Yellow
    Write-Host "環境変数TESSERACT_CMDにtesseract.exeのフルパスを設定してください。" -ForegroundColor Yellow
}

# 6. インストール確認
Write-Host "`nインストールされたパッケージ:" -ForegroundColor Cyan
pip list

# 7. アプリケーション起動の確認
Write-Host "`n===== セットアップ完了 =====" -ForegroundColor Green
Write-Host "アプリケーションを起動しますか？ (Y/N): " -ForegroundColor Cyan -NoNewline
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host "`nアプリケーションを起動中..." -ForegroundColor Yellow
    python run_ultimate.py
} else {
    Write-Host "`n起動方法:" -ForegroundColor Cyan
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "  python run_ultimate.py" -ForegroundColor White
}