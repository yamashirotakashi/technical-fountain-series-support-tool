# Windows環境用仮想環境セットアップスクリプト

Write-Host "================================================================" -ForegroundColor Green
Write-Host "  TechZip Pre-flight Checker - Windows環境セットアップ" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# 既存の仮想環境確認と削除
if (Test-Path "venv") {
    Write-Host "既存の仮想環境を検出しました。" -ForegroundColor Yellow
    $removeVenv = Read-Host "既存の仮想環境を削除して新しく作成しますか？ (y/N)"
    if ($removeVenv -eq "y" -or $removeVenv -eq "Y") {
        Write-Host "既存の仮想環境を削除中..." -ForegroundColor Blue
        Remove-Item -Recurse -Force "venv" -ErrorAction SilentlyContinue
        Write-Host "✓ 削除完了" -ForegroundColor Green
    }
    else {
        Write-Host "既存の仮想環境を保持します。" -ForegroundColor Yellow
        exit 0
    }
}

# Pythonバージョン確認
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[エラー] Pythonがインストールされていません" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Python確認: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "[エラー] Python確認中にエラーが発生しました: $_" -ForegroundColor Red
    exit 1
}

# Windows用仮想環境作成
Write-Host "Windows用仮想環境を作成中..." -ForegroundColor Blue
try {
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[エラー] 仮想環境の作成に失敗しました" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ 仮想環境作成完了" -ForegroundColor Green
}
catch {
    Write-Host "[エラー] 仮想環境作成中にエラーが発生しました: $_" -ForegroundColor Red
    exit 1
}

# 仮想環境有効化
Write-Host "仮想環境を有効化中..." -ForegroundColor Blue
try {
    & "venv\Scripts\Activate.ps1"
    Write-Host "✓ 仮想環境有効化完了" -ForegroundColor Green
}
catch {
    Write-Host "[エラー] 仮想環境の有効化に失敗しました: $_" -ForegroundColor Red
    Write-Host "ExecutionPolicyの設定が必要な可能性があります。" -ForegroundColor Yellow
    Write-Host "以下のコマンドを実行してください:" -ForegroundColor Yellow
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
    exit 1
}

# pipアップデート
Write-Host "pipをアップデート中..." -ForegroundColor Blue
python -m pip install --upgrade pip

# 依存関係インストール
Write-Host "依存関係をインストール中..." -ForegroundColor Blue
pip install requests psutil python-dotenv beautifulsoup4

# tkinter確認
Write-Host "tkinter動作確認中..." -ForegroundColor Blue
python -c "import tkinter; print('tkinter確認完了')"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ tkinter利用可能" -ForegroundColor Green
}
else {
    Write-Host "[警告] tkinterが利用できません" -ForegroundColor Yellow
    Write-Host "Pythonを完全版で再インストールしてください" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  セットアップ完了！" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "次の手順:" -ForegroundColor Cyan
Write-Host "1. 新しいPowerShellを開く" -ForegroundColor Cyan
Write-Host "2. プロジェクトディレクトリに移動" -ForegroundColor Cyan
Write-Host "3. .\run_gui_simple.ps1 を実行" -ForegroundColor Cyan
Write-Host ""

Read-Host "Enterキーで終了"