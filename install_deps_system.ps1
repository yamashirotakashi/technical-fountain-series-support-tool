# システムPython用依存関係インストールスクリプト

Write-Host "================================================================" -ForegroundColor Green
Write-Host "  TechZip Pre-flight Checker - システム依存関係インストール" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# 管理者権限チェック
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "[情報] 管理者権限で実行されていません" -ForegroundColor Yellow
    Write-Host "システム全体への依存関係インストールには管理者権限が推奨されます" -ForegroundColor Yellow
    Write-Host ""
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

# pipの確認とアップデート
Write-Host "pipの確認とアップデート..." -ForegroundColor Blue
try {
    python -m pip --version
    if ($LASTEXITCODE -eq 0) {
        Write-Host "pipをアップデート中..." -ForegroundColor Blue
        python -m pip install --upgrade pip --user
    }
}
catch {
    Write-Host "[警告] pipのアップデートに失敗しました" -ForegroundColor Yellow
}

# 必要最小限の依存関係をインストール
Write-Host ""
Write-Host "必要最小限の依存関係をインストール中..." -ForegroundColor Blue

$basicPackages = @(
    "requests",
    "psutil", 
    "python-dotenv",
    "beautifulsoup4"
)

foreach ($package in $basicPackages) {
    Write-Host "インストール中: $package" -ForegroundColor Cyan
    try {
        python -m pip install $package --user
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $package インストール完了" -ForegroundColor Green
        }
        else {
            Write-Host "  ✗ $package インストール失敗" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "  ✗ $package インストールエラー: $_" -ForegroundColor Red
    }
}

# tkinter確認
Write-Host ""
Write-Host "tkinter動作確認..." -ForegroundColor Blue
try {
    python -c "import tkinter; tkinter.Tk().destroy(); print('tkinter動作確認完了')"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ tkinter利用可能" -ForegroundColor Green
    }
    else {
        Write-Host "[警告] tkinterテストに失敗しました" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "[警告] tkinter確認中にエラーが発生しました: $_" -ForegroundColor Yellow
    Write-Host "Pythonを完全版（tcl/tk含む）で再インストールしてください" -ForegroundColor Yellow
}

# インストール確認テスト
Write-Host ""
Write-Host "インストール確認テスト実行..." -ForegroundColor Blue
try {
    python test_imports_only.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ 依存関係インストール完了！" -ForegroundColor Green
    }
    else {
        Write-Host ""
        Write-Host "[警告] 一部の依存関係で問題がある可能性があります" -ForegroundColor Yellow
    }
}
catch {
    Write-Host ""
    Write-Host "[警告] インストール確認テストでエラーが発生しました: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  インストール完了！" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "次の手順:" -ForegroundColor Cyan
Write-Host "1. .\run_gui_simple.ps1 を実行してGUIを起動" -ForegroundColor Cyan
Write-Host "2. または python main_gui.py で直接実行" -ForegroundColor Cyan
Write-Host ""

Read-Host "Enterキーで終了"