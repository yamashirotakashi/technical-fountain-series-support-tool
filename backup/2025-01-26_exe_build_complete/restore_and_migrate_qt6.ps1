# Qt5バックアップから復元してQt6へ正しく移行するスクリプト
# UTF-8 with BOM encoding

Write-Host "=== Qt5バックアップからの復元とQt6移行 ===" -ForegroundColor Cyan
Write-Host ""

# バックアップディレクトリの確認
$backupDir = "backup_qt5_20250725_193233"
if (-not (Test-Path $backupDir)) {
    Write-Host "エラー: バックアップディレクトリが見つかりません: $backupDir" -ForegroundColor Red
    exit 1
}

# 1. 現在のファイルをバックアップ（念のため）
Write-Host "1. 現在の状態をバックアップ中..." -ForegroundColor Yellow
$currentBackup = "backup_before_restore_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $currentBackup -Force | Out-Null

# 主要ファイルのみバックアップ
Copy-Item -Path "*.py" -Destination $currentBackup -Force -ErrorAction SilentlyContinue
Copy-Item -Path "gui" -Destination $currentBackup -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item -Path "core" -Destination $currentBackup -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item -Path "utils" -Destination $currentBackup -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "  ✓ バックアップ完了: $currentBackup" -ForegroundColor Green

# 2. Qt5バックアップから復元
Write-Host ""
Write-Host "2. Qt5バックアップから復元中..." -ForegroundColor Yellow

# 復元対象のディレクトリとファイル
$restorePaths = @(
    "main.py",
    "gui/main_window.py",
    "gui/components/input_panel.py",
    "gui/components/log_panel.py",
    "gui/components/progress_bar.py",
    "gui/dialogs/*.py",
    "utils/validators.py",
    "core/*.py"
)

$restoredCount = 0
$failedCount = 0

foreach ($path in $restorePaths) {
    $sourceFiles = Get-ChildItem -Path "$backupDir/$path" -ErrorAction SilentlyContinue
    foreach ($file in $sourceFiles) {
        $relativePath = $file.FullName.Replace("$PWD\$backupDir\", "")
        $destinationPath = Join-Path $PWD $relativePath
        
        # ディレクトリが存在しない場合は作成
        $destinationDir = Split-Path $destinationPath -Parent
        if (-not (Test-Path $destinationDir)) {
            New-Item -ItemType Directory -Path $destinationDir -Force | Out-Null
        }
        
        try {
            Copy-Item -Path $file.FullName -Destination $destinationPath -Force
            Write-Host "  ✓ 復元: $relativePath" -ForegroundColor Green
            $restoredCount++
        } catch {
            Write-Host "  ✗ 復元失敗: $relativePath - $_" -ForegroundColor Red
            $failedCount++
        }
    }
}

Write-Host ""
Write-Host "復元完了: $restoredCount ファイル成功、$failedCount ファイル失敗" -ForegroundColor Cyan

# 3. Qt6移行の実行
Write-Host ""
Write-Host "3. Qt6への移行を開始..." -ForegroundColor Yellow

# Qt6移行関数
function Convert-ToQt6 {
    param($filePath)
    
    # ファイルを読み込む（UTF-8として）
    $content = Get-Content -Path $filePath -Raw -Encoding UTF8
    
    # PyQt5からPyQt6への変換
    $content = $content -replace 'from PyQt5', 'from PyQt6'
    $content = $content -replace 'import PyQt5', 'import PyQt6'
    
    # Qt6で移動したクラスの修正
    if ($content -match 'from PyQt6\.QtWidgets import.*QAction') {
        $content = $content -replace 'from PyQt6\.QtWidgets import (.*)', {
            $imports = $matches[1]
            # QActionを除外してQtWidgetsのインポート行を作成
            $widgetImports = ($imports -split ',' | Where-Object { $_ -notmatch 'QAction' }) -join ','
            $result = "from PyQt6.QtWidgets import $widgetImports"
            if ($imports -match 'QAction') {
                $result += "`nfrom PyQt6.QtGui import QAction"
            }
            $result
        }
    }
    
    # exec_() -> exec()
    $content = $content -replace '\.exec_\(\)', '.exec()'
    
    # High DPI属性の削除（Qt6では不要）
    $content = $content -replace 'QApplication\.setAttribute\(Qt\.AA_EnableHighDpiScaling.*?\)\s*\n', ''
    $content = $content -replace 'QApplication\.setAttribute\(Qt\.AA_UseHighDpiPixmaps.*?\)\s*\n', ''
    
    # StandardButtonsの更新
    $content = $content -replace 'QMessageBox\.Yes', 'QMessageBox.StandardButton.Yes'
    $content = $content -replace 'QMessageBox\.No', 'QMessageBox.StandardButton.No'
    $content = $content -replace 'QMessageBox\.Ok', 'QMessageBox.StandardButton.Ok'
    $content = $content -replace 'QMessageBox\.Cancel', 'QMessageBox.StandardButton.Cancel'
    
    # Qt.Orientationの更新
    $content = $content -replace 'Qt\.Vertical', 'Qt.Orientation.Vertical'
    $content = $content -replace 'Qt\.Horizontal', 'Qt.Orientation.Horizontal'
    
    # QLineEdit.EchoModeの更新
    $content = $content -replace 'QLineEdit\.Password', 'QLineEdit.EchoMode.Password'
    
    # ファイルを保存（UTF-8 with BOM）
    $utf8WithBom = New-Object System.Text.UTF8Encoding $true
    [System.IO.File]::WriteAllText($filePath, $content, $utf8WithBom)
}

# Pythonファイルを検索して変換
$pythonFiles = Get-ChildItem -Path . -Include *.py -Recurse | Where-Object {
    $_.FullName -notmatch '\\(venv|test_venv|\.git|backup_|__pycache__)\\' -and
    $_.Name -ne 'setup.py' -and
    $_.Name -notmatch 'test_.*\.py'
}

$convertedCount = 0
$errorCount = 0

foreach ($file in $pythonFiles) {
    try {
        Write-Host "  処理中: $($file.Name)"
        Convert-ToQt6 -filePath $file.FullName
        Write-Host "    ✓ Qt6に変換完了" -ForegroundColor Green
        $convertedCount++
    } catch {
        Write-Host "    ✗ 変換エラー: $_" -ForegroundColor Red
        $errorCount++
    }
}

Write-Host ""
Write-Host "Qt6移行完了: $convertedCount ファイル成功、$errorCount ファイル失敗" -ForegroundColor Cyan

# 4. requirements.txtの更新
Write-Host ""
Write-Host "4. requirements.txtを更新中..." -ForegroundColor Yellow

if (Test-Path "requirements.txt") {
    $requirements = Get-Content "requirements.txt"
    $requirements = $requirements -replace 'PyQt5.*', 'PyQt6>=6.5.0'
    $requirements | Set-Content "requirements.txt" -Encoding UTF8
    Write-Host "  ✓ requirements.txt更新完了" -ForegroundColor Green
}

# 5. テストスクリプトの作成
Write-Host ""
Write-Host "5. Qt6テストスクリプトを作成中..." -ForegroundColor Yellow

$testScript = @'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Qt6バージョンテストスクリプト"""
import sys
try:
    from PyQt6.QtWidgets import QApplication
    from gui.main_window import MainWindow
    
    app = QApplication(sys.argv)
    print("✓ PyQt6のインポート成功")
    
    window = MainWindow()
    print("✓ MainWindowの作成成功")
    
    window.show()
    print("✓ ウィンドウ表示成功")
    print("\nQt6移行が正常に完了しました！")
    
except Exception as e:
    print(f"✗ エラー: {e}")
    import traceback
    traceback.print_exc()
'@

$testScript | Out-File -FilePath "test_qt6_migration.py" -Encoding UTF8
Write-Host "  ✓ test_qt6_migration.py作成完了" -ForegroundColor Green

Write-Host ""
Write-Host "=== 完了 ===" -ForegroundColor Green
Write-Host ""
Write-Host "次のステップ:" -ForegroundColor Yellow
Write-Host "1. PyQt6をインストール: pip install PyQt6" -ForegroundColor White
Write-Host "2. テストを実行: python test_qt6_migration.py" -ForegroundColor White
Write-Host "3. 問題がなければメインアプリを起動: python main.py" -ForegroundColor White
Write-Host ""
Write-Host "バックアップ:" -ForegroundColor Yellow
Write-Host "- Qt5バックアップ: $backupDir" -ForegroundColor White
Write-Host "- 現在の状態のバックアップ: $currentBackup" -ForegroundColor White