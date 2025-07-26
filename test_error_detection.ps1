# エラーファイル検知機能テスト用スクリプト
# TechZip Pre-flight Checker - Error File Detection Test

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  TechZip エラーファイル検知機能 テスト" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# プロジェクトディレクトリ確認
$projectDir = Get-Location
Write-Host "プロジェクトディレクトリ: $projectDir" -ForegroundColor Green

# Python環境確認
Write-Host ""
Write-Host "=== Python環境確認 ===" -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
    }
    else {
        throw "Pythonが見つかりません"
    }
}
catch {
    Write-Host "[エラー] Python確認失敗: $_" -ForegroundColor Red
    Write-Host "Pythonをインストールしてください" -ForegroundColor Red
    Read-Host "Enterキーで終了"
    exit 1
}

# 仮想環境の確認と有効化
Write-Host ""
Write-Host "=== 仮想環境確認 ===" -ForegroundColor Yellow
$useVenv = $false

if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "仮想環境が見つかりました" -ForegroundColor Green
    try {
        & "venv\Scripts\Activate.ps1"
        Write-Host "✓ 仮想環境を有効化しました" -ForegroundColor Green
        $useVenv = $true
    }
    catch {
        Write-Host "[警告] 仮想環境の有効化に失敗: $_" -ForegroundColor Yellow
        Write-Host "システムPythonを使用します" -ForegroundColor Yellow
    }
}
else {
    Write-Host "仮想環境なし - システムPythonを使用" -ForegroundColor Yellow
}

# 依存関係確認
Write-Host ""
Write-Host "=== 依存関係確認 ===" -ForegroundColor Yellow

$requiredModules = @(
    "PyQt6",
    "requests", 
    "beautifulsoup4",
    "python-dotenv",
    "psutil"
)

$missingModules = @()

foreach ($module in $requiredModules) {
    Write-Host -NoNewline "  $module ... " -ForegroundColor Gray
    
    $importName = $module
    if ($module -eq "beautifulsoup4") {
        $importName = "bs4"
    }
    elseif ($module -eq "python-dotenv") {
        $importName = "dotenv"
    }
    
    python -c "import $importName" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK" -ForegroundColor Green
    }
    else {
        Write-Host "見つかりません" -ForegroundColor Red
        $missingModules += $module
    }
}

if ($missingModules.Count -gt 0) {
    Write-Host ""
    Write-Host "[エラー] 以下のモジュールが不足しています:" -ForegroundColor Red
    $missingModules | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    
    Write-Host ""
    Write-Host "インストールコマンド:" -ForegroundColor Yellow
    if ($useVenv) {
        Write-Host "  pip install $($missingModules -join ' ')" -ForegroundColor White
    }
    else {
        Write-Host "  pip install --user $($missingModules -join ' ')" -ForegroundColor White
    }
    
    $install = Read-Host "今すぐインストールしますか？ (Y/N)"
    if ($install -eq "Y" -or $install -eq "y") {
        if ($useVenv) {
            pip install $missingModules
        }
        else {
            pip install --user $missingModules
        }
    }
    else {
        Read-Host "Enterキーで終了"
        exit 1
    }
}

# エラーファイル検知機能のテスト
Write-Host ""
Write-Host "=== エラーファイル検知機能テスト ===" -ForegroundColor Yellow

# テストモード選択
Write-Host ""
Write-Host "テストモードを選択してください:" -ForegroundColor Cyan
Write-Host "1. インポートテストのみ（GUI起動なし）" -ForegroundColor White
Write-Host "2. 完全なGUI起動テスト" -ForegroundColor White
Write-Host "3. NextPublishingサービステスト（アップロードなし）" -ForegroundColor White
Write-Host ""

$mode = Read-Host "選択 (1-3)"

switch ($mode) {
    "1" {
        Write-Host ""
        Write-Host "インポートテストを実行中..." -ForegroundColor Blue
        
        # インポートテストスクリプト
        $importTest = @"
import sys
print('Python Path:', sys.executable)
print('Module Import Test:')

try:
    print('  - PyQt6...', end=' ')
    from PyQt6.QtWidgets import QApplication, QPushButton
    print('OK')
except Exception as e:
    print(f'FAILED: {e}')

try:
    print('  - services.nextpublishing_service...', end=' ')
    from services.nextpublishing_service import NextPublishingService
    print('OK')
except Exception as e:
    print(f'FAILED: {e}')

try:
    print('  - services.error_file_detector...', end=' ')
    from services.error_file_detector import ErrorFileDetectorWorker
    print('OK')
except Exception as e:
    print(f'FAILED: {e}')

try:
    print('  - gui.components.input_panel_qt6...', end=' ')
    from gui.components.input_panel_qt6 import InputPanel
    print('OK')
except Exception as e:
    print(f'FAILED: {e}')

print('\n✓ インポートテスト完了')
"@
        
        python -c $importTest
    }
    
    "2" {
        Write-Host ""
        Write-Host "GUIアプリケーションを起動中..." -ForegroundColor Blue
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Cyan
        Write-Host "  エラーファイル検知機能の使い方:" -ForegroundColor Cyan
        Write-Host "  1. Nコードを入力（組版エラーが発生したもの）" -ForegroundColor White
        Write-Host "  2. 「エラーファイル検知」ボタンをクリック（赤いボタン）" -ForegroundColor White
        Write-Host "  3. メール監視の設定を選択" -ForegroundColor White
        Write-Host "  4. 処理完了を待つ（20-40分程度）" -ForegroundColor White
        Write-Host "================================================================" -ForegroundColor Cyan
        Write-Host ""
        
        python main.py
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host ""
            Write-Host "[エラー] アプリケーション起動失敗" -ForegroundColor Red
            Write-Host "エラーコード: $LASTEXITCODE" -ForegroundColor Red
        }
    }
    
    "3" {
        Write-Host ""
        Write-Host "NextPublishingサービステストを実行中..." -ForegroundColor Blue
        
        python tests/test_nextpublishing_upload.py
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host ""
            Write-Host "[エラー] テスト実行失敗" -ForegroundColor Red
        }
    }
    
    default {
        Write-Host "無効な選択です" -ForegroundColor Red
    }
}

Write-Host ""
Read-Host "Enterキーで終了"