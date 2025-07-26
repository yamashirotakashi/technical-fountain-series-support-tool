# Windows環境完全修復スクリプト

param(
    [switch]$Force
)

Write-Host "================================================================" -ForegroundColor Red
Write-Host "  TechZip Pre-flight Checker - Windows環境完全修復" -ForegroundColor Red
Write-Host "================================================================" -ForegroundColor Red
Write-Host ""

Write-Host "【警告】このスクリプトは以下を実行します:" -ForegroundColor Yellow
Write-Host "- WSL用仮想環境を完全削除" -ForegroundColor Yellow
Write-Host "- Windows用仮想環境を新規作成" -ForegroundColor Yellow
Write-Host "- 依存関係を再インストール" -ForegroundColor Yellow
Write-Host ""

if (-not $Force) {
    $confirm = Read-Host "続行しますか？ (y/N)"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "中止しました。" -ForegroundColor Gray
        exit 0
    }
}

Write-Host ""
Write-Host "=== STEP 1: 環境クリーンアップ ===" -ForegroundColor Cyan

# 既存仮想環境を強制削除
if (Test-Path "venv") {
    Write-Host "WSL用仮想環境を削除中..." -ForegroundColor Blue
    try {
        # 仮想環境が有効な場合は無効化
        if ($env:VIRTUAL_ENV) {
            Write-Host "仮想環境を無効化中..." -ForegroundColor Gray
            & deactivate 2>$null
        }
        
        # ファイルとディレクトリを強制削除
        Remove-Item -Path "venv" -Recurse -Force -ErrorAction Stop
        Write-Host "✓ WSL用仮想環境削除完了" -ForegroundColor Green
    }
    catch {
        Write-Host "[警告] 仮想環境削除エラー: $_" -ForegroundColor Yellow
        Write-Host "手動で削除してください: Remove-Item -Path venv -Recurse -Force" -ForegroundColor Yellow
        
        # 強制的に削除を試行
        try {
            Get-ChildItem -Path "venv" -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
            Remove-Item -Path "venv" -Force -ErrorAction SilentlyContinue
            Write-Host "✓ 強制削除完了" -ForegroundColor Green
        }
        catch {
            Write-Host "[エラー] 仮想環境削除に失敗しました" -ForegroundColor Red
            Write-Host "Explorerで手動削除するか、PCを再起動してから再実行してください" -ForegroundColor Red
            Read-Host "Enterキーで続行（削除をスキップ）"
        }
    }
}
else {
    Write-Host "既存の仮想環境なし" -ForegroundColor Gray
}

# Python環境確認
Write-Host ""
Write-Host "=== STEP 2: Python環境確認 ===" -ForegroundColor Cyan

try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[エラー] Pythonがインストールされていません" -ForegroundColor Red
        Write-Host "https://python.org からPython 3.8以降をインストールしてください" -ForegroundColor Red
        Read-Host "Enterキーで終了"
        exit 1
    }
    Write-Host "✓ Python確認: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "[エラー] Python確認中にエラー: $_" -ForegroundColor Red
    exit 1
}

# Windows用仮想環境作成
Write-Host ""
Write-Host "=== STEP 3: Windows用仮想環境作成 ===" -ForegroundColor Cyan

try {
    Write-Host "Windows用仮想環境を作成中..." -ForegroundColor Blue
    python -m venv venv --clear
    if ($LASTEXITCODE -ne 0) {
        throw "仮想環境作成に失敗"
    }
    Write-Host "✓ Windows用仮想環境作成完了" -ForegroundColor Green
}
catch {
    Write-Host "[エラー] 仮想環境作成失敗: $_" -ForegroundColor Red
    Write-Host "システムPythonで続行します..." -ForegroundColor Yellow
    $useSystemPython = $true
}

# 仮想環境有効化（作成成功時のみ）
if (-not $useSystemPython -and (Test-Path "venv\Scripts\Activate.ps1")) {
    try {
        Write-Host "仮想環境を有効化中..." -ForegroundColor Blue
        & "venv\Scripts\Activate.ps1"
        Write-Host "✓ 仮想環境有効化完了" -ForegroundColor Green
    }
    catch {
        Write-Host "[警告] 仮想環境有効化失敗: $_" -ForegroundColor Yellow
        Write-Host "ExecutionPolicyの設定が必要な可能性があります" -ForegroundColor Yellow
        Write-Host "システムPythonで続行します..." -ForegroundColor Yellow
        $useSystemPython = $true
    }
}

# 依存関係インストール
Write-Host ""
Write-Host "=== STEP 4: 依存関係インストール ===" -ForegroundColor Cyan

Write-Host "pipをアップデート中..." -ForegroundColor Blue
python -m pip install --upgrade pip --quiet

$packages = @(
    "requests",
    "psutil", 
    "python-dotenv",
    "beautifulsoup4"
)

Write-Host "必要な依存関係をインストール中..." -ForegroundColor Blue
foreach ($package in $packages) {
    try {
        Write-Host "  $package をインストール中..." -ForegroundColor Gray
        
        if ($useSystemPython) {
            python -m pip install $package --user --quiet
        }
        else {
            python -m pip install $package --quiet
        }
        
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

# 動作確認テスト
Write-Host ""
Write-Host "=== STEP 5: 動作確認 ===" -ForegroundColor Cyan

Write-Host "インポートテストを実行中..." -ForegroundColor Blue
try {
    python test_imports_only.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 修復完了！すべてのテストが成功しました！" -ForegroundColor Green
    }
    else {
        Write-Host ""
        Write-Host "[警告] 一部のテストが失敗しました" -ForegroundColor Yellow
    }
}
catch {
    Write-Host ""
    Write-Host "[警告] テスト実行エラー: $_" -ForegroundColor Yellow
}

# 最終確認
Write-Host ""
Write-Host "=== 修復完了 ===" -ForegroundColor Green
Write-Host ""
Write-Host "次の手順でGUIを起動してください:" -ForegroundColor Cyan
Write-Host ""

if ($useSystemPython) {
    Write-Host "【システムPython環境】" -ForegroundColor Yellow
    Write-Host "python main_gui.py" -ForegroundColor White
}
else {
    Write-Host "【仮想環境】" -ForegroundColor Yellow
    Write-Host "1. 新しいPowerShellを開く" -ForegroundColor White
    Write-Host "2. プロジェクトディレクトリに移動" -ForegroundColor White
    Write-Host "3. venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "4. python main_gui.py" -ForegroundColor White
}

Write-Host ""
Write-Host "または以下のスクリプトを使用:" -ForegroundColor Cyan
Write-Host ".\run_gui_clean.ps1" -ForegroundColor White

Write-Host ""
Read-Host "Enterキーで終了"