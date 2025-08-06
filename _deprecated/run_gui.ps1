# TechZip Pre-flight Checker - 統合テストGUI起動 (PowerShell版)

Write-Host "================================================================" -ForegroundColor Green
Write-Host "  TechZip Pre-flight Checker - 統合テストGUI起動" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# Pythonインストール確認
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[エラー] Pythonがインストールされていません" -ForegroundColor Red
        Write-Host "Python 3.8以降をインストールしてください" -ForegroundColor Red
        Read-Host "Enterキーで終了"
        exit 1
    }
    Write-Host "✓ Python環境確認済み" -ForegroundColor Green
    Write-Host "  $pythonVersion" -ForegroundColor Gray
    Write-Host ""
}
catch {
    Write-Host "[エラー] Python確認中にエラーが発生しました: $_" -ForegroundColor Red
    Read-Host "Enterキーで終了"
    exit 1
}

# 作業ディレクトリの確認
if (-not (Test-Path "main_gui.py")) {
    Write-Host "[エラー] main_gui.pyが見つかりません" -ForegroundColor Red
    Write-Host "プロジェクトルートディレクトリで実行してください" -ForegroundColor Red
    Read-Host "Enterキーで終了"
    exit 1
}

Write-Host "✓ プロジェクトルート確認済み" -ForegroundColor Green
Write-Host ""

# 仮想環境の確認と有効化（オプション）
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "仮想環境を検出しました。" -ForegroundColor Yellow
    $useVenv = Read-Host "仮想環境を使用しますか？ (y/N)"
    if ($useVenv -eq "y" -or $useVenv -eq "Y") {
        Write-Host "仮想環境を有効化中..." -ForegroundColor Blue
        try {
            & "venv\Scripts\Activate.ps1"
            Write-Host "✓ 仮想環境有効化完了" -ForegroundColor Green
        }
        catch {
            Write-Host "[警告] 仮想環境の有効化に失敗しました: $_" -ForegroundColor Yellow
            Write-Host "システムPythonを使用します" -ForegroundColor Yellow
        }
    }
}
else {
    Write-Host "仮想環境が見つかりません。システムPythonを使用します。" -ForegroundColor Yellow
}
Write-Host ""

# 依存関係の確認
Write-Host "依存関係チェック中..." -ForegroundColor Blue
try {
    python -c "import tkinter; import psutil; import dotenv; import requests" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[警告] 一部の依存関係が不足している可能性があります" -ForegroundColor Yellow
        $installDeps = Read-Host "依存関係をインストールしますか？ (y/N)"
        if ($installDeps -eq "y" -or $installDeps -eq "Y") {
            Write-Host "依存関係をインストール中..." -ForegroundColor Blue
            pip install -r requirements.txt
            if ($LASTEXITCODE -ne 0) {
                Write-Host "[エラー] 依存関係のインストールに失敗しました" -ForegroundColor Red
                Read-Host "Enterキーで終了"
                exit 1
            }
            Write-Host "✓ 依存関係インストール完了" -ForegroundColor Green
        }
    }
    else {
        Write-Host "✓ 依存関係確認済み" -ForegroundColor Green
    }
}
catch {
    Write-Host "[警告] 依存関係チェック中にエラーが発生しました: $_" -ForegroundColor Yellow
}
Write-Host ""

# GUI起動
Write-Host "統合テストGUIを起動中..." -ForegroundColor Blue
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  使用方法:" -ForegroundColor Cyan
Write-Host "  1. 環境チェック - システム環境と依存関係を確認" -ForegroundColor Cyan
Write-Host "  2. ファイル選択 - テスト対象のDOCXファイルを選択" -ForegroundColor Cyan
Write-Host "  3. 設定調整 - 検証モードとメール設定を確認" -ForegroundColor Cyan
Write-Host "  4. テスト実行 - 完全テストスイートを実行" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

try {
    python main_gui.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "[エラー] GUIアプリケーションの起動に失敗しました" -ForegroundColor Red
        Write-Host "エラー詳細を確認して、必要に応じて依存関係を再インストールしてください" -ForegroundColor Red
        Read-Host "Enterキーで終了"
        exit 1
    }
}
catch {
    Write-Host ""
    Write-Host "[エラー] GUI起動中にエラーが発生しました: $_" -ForegroundColor Red
    Read-Host "Enterキーで終了"
    exit 1
}

Write-Host ""
Write-Host "GUI起動完了" -ForegroundColor Green
Read-Host "Enterキーで終了"