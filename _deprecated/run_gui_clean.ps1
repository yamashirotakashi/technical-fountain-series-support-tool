# TechZip Pre-flight Checker - クリーンGUI起動スクリプト
# 修復後の環境で確実に動作する版

Write-Host "================================================================" -ForegroundColor Green
Write-Host "  TechZip Pre-flight Checker - クリーンGUI起動" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# Python環境確認
Write-Host "Python環境確認中..." -ForegroundColor Blue
try {
    $pythonInfo = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Pythonが見つかりません"
    }
    Write-Host "✓ $pythonInfo" -ForegroundColor Green
}
catch {
    Write-Host "[エラー] Python確認失敗: $_" -ForegroundColor Red
    Write-Host "https://python.org からPythonをインストールしてください" -ForegroundColor Red
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

# 仮想環境確認（オプション）
$useVenv = $false
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Windows用仮想環境が利用可能です" -ForegroundColor Green
    
    # 自動的に仮想環境を有効化
    try {
        & "venv\Scripts\Activate.ps1"
        Write-Host "✓ 仮想環境有効化完了" -ForegroundColor Green
        $useVenv = $true
    }
    catch {
        Write-Host "[警告] 仮想環境有効化失敗" -ForegroundColor Yellow
        Write-Host "システムPythonを使用します" -ForegroundColor Yellow
    }
}
else {
    Write-Host "仮想環境なし - システムPythonを使用" -ForegroundColor Gray
}

# 重要な依存関係の簡易チェック
Write-Host "依存関係簡易チェック..." -ForegroundColor Blue
$criticalModules = @("tkinter", "threading", "json")
$missingCritical = @()

foreach ($module in $criticalModules) {
    python -c "import $module" 2>$null
    if ($LASTEXITCODE -ne 0) {
        $missingCritical += $module
    }
}

if ($missingCritical.Count -gt 0) {
    Write-Host "[エラー] 重要なモジュールが不足: $($missingCritical -join ', ')" -ForegroundColor Red
    Write-Host "Pythonを完全版で再インストールしてください" -ForegroundColor Red
    Read-Host "Enterキーで終了"
    exit 1
}
Write-Host "✓ 重要な依存関係確認済み" -ForegroundColor Green

Write-Host ""
Write-Host "=== GUI起動準備完了 ===" -ForegroundColor Cyan
Write-Host ""

if ($useVenv) {
    Write-Host "環境: Windows仮想環境" -ForegroundColor Green
}
else {
    Write-Host "環境: システムPython" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "GUI使用方法:" -ForegroundColor Cyan
Write-Host "1. 環境チェック - システム環境確認" -ForegroundColor White
Write-Host "2. ファイル選択 - DOCXファイル選択" -ForegroundColor White
Write-Host "3. テスト実行 - 完全テスト実行" -ForegroundColor White
Write-Host ""

# GUI起動
Write-Host "GUIアプリケーションを起動中..." -ForegroundColor Blue
Write-Host ""

try {
    # 現在の環境でPythonスクリプト実行
    python main_gui.py
    
    $exitCode = $LASTEXITCODE
    Write-Host ""
    
    if ($exitCode -eq 0) {
        Write-Host "✓ GUI正常終了" -ForegroundColor Green
    }
    elseif ($exitCode -eq 103) {
        Write-Host "[エラー] 仮想環境エラー（コード103）" -ForegroundColor Red
        Write-Host "修復スクリプトを再実行してください: .\fix_windows_environment.ps1" -ForegroundColor Yellow
    }
    else {
        Write-Host "[エラー] GUI終了（コード: $exitCode）" -ForegroundColor Red
        Write-Host "詳細はGUI内のログを確認してください" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "[エラー] GUI起動エラー: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "対処方法:" -ForegroundColor Yellow
    Write-Host "1. 修復スクリプト実行: .\fix_windows_environment.ps1" -ForegroundColor White
    Write-Host "2. 依存関係確認: python test_imports_only.py" -ForegroundColor White
    Write-Host "3. Python再インストール" -ForegroundColor White
}

Write-Host ""
Read-Host "Enterキーで終了"