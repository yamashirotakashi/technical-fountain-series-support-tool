# TechZip 統合ランチャー - 短縮版
# 使用法: .\run.ps1

param([switch]$Reset = $false)

Write-Host "TechZip起動中..." -ForegroundColor Green

# プロジェクトルート移動
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Python確認
try {
    python --version >$null 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Python未インストール" }
}
catch {
    Write-Host "[エラー] Pythonをインストールしてください" -ForegroundColor Red
    Read-Host "Enter"
    exit 1
}

# 仮想環境処理
$venv = "venv"
if ($Reset -and (Test-Path $venv)) { Remove-Item -Recurse -Force $venv }

if (-not (Test-Path "$venv\Scripts\Activate.ps1")) {
    Write-Host "仮想環境作成中..." -ForegroundColor Yellow
    python -m venv $venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[エラー] 仮想環境作成失敗" -ForegroundColor Red
        Read-Host "Enter"
        exit 1
    }
}

# 仮想環境アクティベート & 依存関係インストール
try {
    & "$venv\Scripts\Activate.ps1"
    pip install -r requirements.txt -q
    Write-Host "✓ 環境準備完了" -ForegroundColor Green
}
catch {
    Write-Host "[エラー] 環境準備失敗: $_" -ForegroundColor Red
    Read-Host "Enter"
    exit 1
}

# GUI起動
Write-Host "GUI起動..." -ForegroundColor Blue
try {
    python main_gui.py
    Write-Host "✓ GUI終了" -ForegroundColor Green
}
catch {
    Write-Host "[エラー] GUI起動失敗: $_" -ForegroundColor Red
}

# 仮想環境退出
if (Get-Command deactivate -ErrorAction SilentlyContinue) { deactivate }
Write-Host "完了" -ForegroundColor Green