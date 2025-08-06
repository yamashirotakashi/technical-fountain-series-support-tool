# TechZip Pre-flight Checker - シンプルGUI起動スクリプト

Write-Host "================================================================" -ForegroundColor Green
Write-Host "  TechZip Pre-flight Checker - GUI起動" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# Pythonバージョン確認
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[エラー] Pythonがインストールされていません" -ForegroundColor Red
        Read-Host "Enterキーで終了"
        exit 1
    }
    Write-Host "✓ Python確認: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "[エラー] Python確認中にエラーが発生しました: $_" -ForegroundColor Red
    Read-Host "Enterキーで終了"
    exit 1
}

# プロジェクトファイル確認
if (-not (Test-Path "main_gui.py")) {
    Write-Host "[エラー] main_gui.pyが見つかりません" -ForegroundColor Red
    Write-Host "プロジェクトルートディレクトリで実行してください" -ForegroundColor Red
    Read-Host "Enterキーで終了"
    exit 1
}
Write-Host "✓ プロジェクトファイル確認済み" -ForegroundColor Green

# 仮想環境の確認（オプション）
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "仮想環境が利用可能です。" -ForegroundColor Green
    
    # 仮想環境有効化を試行
    try {
        & "venv\Scripts\Activate.ps1"
        Write-Host "✓ 仮想環境有効化完了" -ForegroundColor Green
    }
    catch {
        Write-Host "[警告] 仮想環境の有効化に失敗しました" -ForegroundColor Yellow
        Write-Host "システムPythonを使用します" -ForegroundColor Yellow
    }
}
else {
    Write-Host "仮想環境なし。システムPythonを使用します。" -ForegroundColor Yellow
}

Write-Host ""

# 重要な依存関係確認（標準ライブラリは除く）
Write-Host "重要な依存関係確認中..." -ForegroundColor Blue
$criticalModules = @("tkinter")  # GUIに必須のモジュールのみチェック
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
}
else {
    Write-Host "✓ 重要な依存関係確認済み" -ForegroundColor Green
}

Write-Host ""

# GUI起動
Write-Host "統合テストGUIを起動中..." -ForegroundColor Blue
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  使用方法:" -ForegroundColor Cyan
Write-Host "  1. 環境チェック - システム環境と依存関係を確認" -ForegroundColor Cyan
Write-Host "  2. ファイル選択 - テスト対象のDOCXファイルを選択" -ForegroundColor Cyan
Write-Host "  3. テスト実行 - 完全テストスイートを実行" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

try {
    python main_gui.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "[エラー] GUIアプリケーションの起動に失敗しました" -ForegroundColor Red
        Write-Host "エラーコード: $LASTEXITCODE" -ForegroundColor Red
    }
    else {
        Write-Host ""
        Write-Host "✓ GUI正常終了" -ForegroundColor Green
    }
}
catch {
    Write-Host ""
    Write-Host "[エラー] GUI起動中にエラーが発生しました: $_" -ForegroundColor Red
}

Write-Host ""
Read-Host "Enterキーで終了"