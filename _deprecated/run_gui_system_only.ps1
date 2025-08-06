# TechZip Pre-flight Checker - システムPython専用起動スクリプト
# 仮想環境を一切使用しない緊急用スクリプト

Write-Host "================================================================" -ForegroundColor Green
Write-Host "  TechZip Pre-flight Checker - システムPython専用起動" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

Write-Host "[情報] このスクリプトは仮想環境を使用しません" -ForegroundColor Yellow
Write-Host "[情報] システムにインストールされたPythonを直接使用します" -ForegroundColor Yellow
Write-Host ""

# 仮想環境無効化（念のため）
if ($env:VIRTUAL_ENV) {
    Write-Host "仮想環境を無効化中..." -ForegroundColor Blue
    try {
        & deactivate 2>$null
        Write-Host "✓ 仮想環境無効化完了" -ForegroundColor Green
    }
    catch {
        Write-Host "仮想環境無効化をスキップ" -ForegroundColor Gray
    }
    Write-Host ""
}

# システムPython確認
Write-Host "システムPython確認中..." -ForegroundColor Blue
try {
    $pythonInfo = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Pythonが見つかりません"
    }
    Write-Host "✓ $pythonInfo" -ForegroundColor Green
}
catch {
    Write-Host "[エラー] システムPython確認失敗: $_" -ForegroundColor Red
    Write-Host "Pythonがインストールされていない、またはPATHに設定されていません" -ForegroundColor Red
    Read-Host "Enterキーで終了"
    exit 1
}

# プロジェクトファイル確認
Write-Host "プロジェクトファイル確認中..." -ForegroundColor Blue
if (-not (Test-Path "main_gui.py")) {
    Write-Host "[エラー] main_gui.pyが見つかりません" -ForegroundColor Red
    Write-Host "プロジェクトルートディレクトリで実行してください" -ForegroundColor Red
    Read-Host "Enterキーで終了"
    exit 1
}
Write-Host "✓ プロジェクトファイル確認済み" -ForegroundColor Green

# tkinter確認（最重要）
Write-Host "tkinter確認中..." -ForegroundColor Blue
python -c "import tkinter; print('tkinter利用可能')" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ tkinter利用可能" -ForegroundColor Green
}
else {
    Write-Host "[エラー] tkinterが利用できません" -ForegroundColor Red
    Write-Host "Pythonを完全版（tcl/tk含む）で再インストールしてください" -ForegroundColor Red
    Write-Host "https://python.org からインストールして「Add to PATH」を有効にしてください" -ForegroundColor Red
    Read-Host "Enterキーで終了"
    exit 1
}

# 最小限の依存関係確認
Write-Host "最小限の依存関係確認中..." -ForegroundColor Blue
$optionalModules = @("requests", "psutil", "dotenv")
$availableModules = @()

foreach ($module in $optionalModules) {
    python -c "import $module" 2>$null
    if ($LASTEXITCODE -eq 0) {
        $availableModules += $module
    }
}

if ($availableModules.Count -gt 0) {
    Write-Host "✓ 利用可能な依存関係: $($availableModules -join ', ')" -ForegroundColor Green
}
else {
    Write-Host "[警告] オプションの依存関係が見つかりません" -ForegroundColor Yellow
    Write-Host "一部の機能が制限される可能性があります" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== システムPython環境でGUI起動 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "GUI使用方法:" -ForegroundColor White
Write-Host "1. 環境チェックボタンで詳細な依存関係を確認" -ForegroundColor White
Write-Host "2. ファイル選択で対象DOCXファイルを選択" -ForegroundColor White
Write-Host "3. テスト実行で動作確認" -ForegroundColor White
Write-Host ""

# GUI起動
Write-Host "GUIアプリケーションを起動中..." -ForegroundColor Blue
Write-Host ""

try {
    # システムPythonで直接実行
    python main_gui.py
    
    $exitCode = $LASTEXITCODE
    Write-Host ""
    
    if ($exitCode -eq 0) {
        Write-Host "✓ GUI正常終了" -ForegroundColor Green
    }
    else {
        Write-Host "[情報] GUI終了コード: $exitCode" -ForegroundColor Yellow
        if ($exitCode -eq 103) {
            Write-Host "仮想環境関連のエラーです。このスクリプトは正常に動作したはずです。" -ForegroundColor Yellow
        }
    }
}
catch {
    Write-Host "[エラー] GUI起動エラー: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "対処方法:" -ForegroundColor Yellow
    Write-Host "1. Pythonを完全版で再インストール" -ForegroundColor White
    Write-Host "2. 依存関係インストール: pip install --user requests psutil python-dotenv beautifulsoup4" -ForegroundColor White
    Write-Host "3. インポートテスト実行: python test_imports_only.py" -ForegroundColor White
}

Write-Host ""
Write-Host "=== システムPython実行完了 ===" -ForegroundColor Green
Read-Host "Enterキーで終了"