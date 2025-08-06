# TechZip 完全自動化スクリプト - 仮想環境セットアップ & GUI実行
# 作成日: 2025-08-04
# 機能: 仮想環境作成/確認 → GUI実行 → 環境クリーンアップ

param(
    [switch]$ForceRecreate = $false  # 仮想環境を強制再作成
)

Write-Host "================================================================" -ForegroundColor Green
Write-Host "  TechZip 完全自動化ランチャー" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# プロジェクトルートディレクトリに移動
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
Write-Host "✓ プロジェクトディレクトリ: $scriptDir" -ForegroundColor Green
Write-Host ""

# Python環境確認
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
}
catch {
    Write-Host "[エラー] Python確認中にエラーが発生しました: $_" -ForegroundColor Red
    Read-Host "Enterキーで終了"
    exit 1
}

# 仮想環境管理
$venvPath = "venv"
$activateScript = "$venvPath\Scripts\Activate.ps1"

if ($ForceRecreate -and (Test-Path $venvPath)) {
    Write-Host "仮想環境を強制再作成中..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $venvPath
}

if (-not (Test-Path $venvPath) -or -not (Test-Path $activateScript)) {
    Write-Host "仮想環境を作成中..." -ForegroundColor Blue
    try {
        python -m venv $venvPath
        if ($LASTEXITCODE -ne 0) {
            throw "仮想環境の作成に失敗しました"
        }
        Write-Host "✓ 仮想環境作成完了" -ForegroundColor Green
    }
    catch {
        Write-Host "[エラー] 仮想環境作成エラー: $_" -ForegroundColor Red
        Read-Host "Enterキーで終了"
        exit 1
    }
}
else {
    Write-Host "✓ 既存の仮想環境を検出" -ForegroundColor Green
}

# 仮想環境アクティベート
Write-Host "仮想環境をアクティベート中..." -ForegroundColor Blue
try {
    & $activateScript
    if ($LASTEXITCODE -ne 0) {
        throw "仮想環境のアクティベートに失敗しました"
    }
    Write-Host "✓ 仮想環境アクティベート完了" -ForegroundColor Green
}
catch {
    Write-Host "[エラー] 仮想環境アクティベートエラー: $_" -ForegroundColor Red
    Read-Host "Enterキーで終了"
    exit 1
}

# 依存関係チェック・インストール
Write-Host ""
Write-Host "依存関係をチェック中..." -ForegroundColor Blue
try {
    python -c "import tkinter; import psutil; import dotenv; import requests" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "依存関係をインストール中..." -ForegroundColor Yellow
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            throw "依存関係のインストールに失敗しました"
        }
        Write-Host "✓ 依存関係インストール完了" -ForegroundColor Green
    }
    else {
        Write-Host "✓ 依存関係確認済み" -ForegroundColor Green
    }
}
catch {
    Write-Host "[警告] 依存関係チェック中にエラーが発生しました: $_" -ForegroundColor Yellow
}

# GUI起動前の最終確認
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  GUI起動準備完了" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  使用方法:" -ForegroundColor Cyan
Write-Host "  1. 環境チェック - システム環境と依存関係を確認" -ForegroundColor Cyan
Write-Host "  2. ファイル選択 - テスト対象のDOCXファイルを選択" -ForegroundColor Cyan
Write-Host "  3. 設定調整 - 検証モードとメール設定を確認" -ForegroundColor Cyan
Write-Host "  4. テスト実行 - 完全テストスイートを実行" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# GUI起動
Write-Host "TechZip GUI を起動中..." -ForegroundColor Blue
Write-Host "GUI終了まで待機します..." -ForegroundColor Gray
Write-Host ""

try {
    # main_gui.pyが存在するかチェック
    if (-not (Test-Path "main_gui.py")) {
        throw "main_gui.pyが見つかりません"
    }
    
    # GUI実行（同期実行、終了まで待機）
    python main_gui.py
    $guiExitCode = $LASTEXITCODE
    
    Write-Host ""
    if ($guiExitCode -eq 0) {
        Write-Host "✓ GUI正常終了" -ForegroundColor Green
    }
    else {
        Write-Host "[警告] GUI終了コード: $guiExitCode" -ForegroundColor Yellow
    }
}
catch {
    Write-Host ""
    Write-Host "[エラー] GUI実行中にエラーが発生しました: $_" -ForegroundColor Red
    Write-Host "エラー詳細を確認して、必要に応じて依存関係を再インストールしてください" -ForegroundColor Red
}

# 仮想環境からの退出
Write-Host ""
Write-Host "仮想環境から退出中..." -ForegroundColor Blue
try {
    # PowerShellの仮想環境デアクティベート
    if (Get-Command deactivate -ErrorAction SilentlyContinue) {
        deactivate
    }
    Write-Host "✓ 仮想環境から退出完了" -ForegroundColor Green
}
catch {
    Write-Host "[警告] 仮想環境退出時に警告: $_" -ForegroundColor Yellow
}

# 完了メッセージ
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  TechZip セッション完了" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host "仮想環境: $venvPath" -ForegroundColor Gray
Write-Host "プロジェクト: $scriptDir" -ForegroundColor Gray
Write-Host ""
Write-Host "次回実行コマンド:" -ForegroundColor Cyan
Write-Host "  .\setup_and_run_techwf.ps1" -ForegroundColor White
Write-Host "  .\setup_and_run_techwf.ps1 -ForceRecreate  # 仮想環境再作成" -ForegroundColor White
Write-Host ""

# 使用統計表示（オプション）
if (Test-Path $venvPath) {
    $venvSize = (Get-ChildItem $venvPath -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "仮想環境サイズ: $([math]::Round($venvSize, 1)) MB" -ForegroundColor Gray
}

Read-Host "Enterキーで終了"