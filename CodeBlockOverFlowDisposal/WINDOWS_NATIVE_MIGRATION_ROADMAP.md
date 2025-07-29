# Windowsネイティブ実行への移行ロードマップ

最終更新: 2025-01-29

## 🎯 現状分析

### 現在の環境
- **実行環境**: 仮想環境（venv）内での独立実行
- **依存関係**: 
  - PyQt6（TECHZIPと共通）
  - pdfplumber, PyPDF2（PDF処理）
  - pytesseract（OCR）
  - Pillow, opencv-python（画像処理）
  - numpy（数値計算）

### TECHZIPの環境
- **実行環境**: Windows PowerShell直接実行
- **Pythonバージョン**: システムPython
- **主要ライブラリ**: PyQt6, requests, google-api-python-client等

## 📋 移行戦略

### Phase 1: 依存関係の統合（1週間）

#### 1.1 依存関係の調査と整理（2日）
```powershell
# 現在の依存関係を確認
cd overflow_checker_standalone
pip freeze > current_requirements.txt

# TECHZIPの依存関係と比較
cd ../..
pip freeze > techzip_requirements.txt

# 差分を確認
Compare-Object (Get-Content current_requirements.txt) (Get-Content techzip_requirements.txt)
```

#### 1.2 統合requirements.txtの作成（1日）
```txt
# requirements_addon.txt - 溢れチェック機能の追加依存関係
pdfplumber>=0.9.0
PyPDF2>=3.0.1
pytesseract>=0.3.10
opencv-python>=4.6.0
numpy>=1.21.0
Pillow>=9.3.0
colorlog>=6.7.0
```

#### 1.3 TECHZIPのrequirements.txt更新（1日）
```python
# install_overflow_deps.py - 追加依存関係のインストールスクリプト
import subprocess
import sys

def install_overflow_dependencies():
    """溢れチェック機能の依存関係をインストール"""
    deps = [
        'pdfplumber>=0.9.0',
        'pytesseract>=0.3.10',
        # Tesseract OCRは別途インストールが必要
    ]
    
    for dep in deps:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
```

#### 1.4 Tesseract OCRの自動セットアップ（3日）
```python
# utils/tesseract_installer.py
import os
import urllib.request
import zipfile
from pathlib import Path

class TesseractInstaller:
    """Windows用Tesseract OCR自動インストーラー"""
    
    def check_tesseract(self):
        """Tesseractがインストールされているか確認"""
        # 環境変数チェック
        # レジストリチェック
        # 一般的なパスチェック
    
    def download_and_install(self):
        """Tesseractを自動ダウンロード・インストール"""
        # GitHubからダウンロード
        # サイレントインストール
        # 環境変数設定
```

### Phase 2: コードベースの統合（2週間）

#### 2.1 モジュール構造の再編成（3日）
```
technical-fountain-series-support-tool/
├── core/
│   ├── workflow_processor.py
│   └── overflow_detector/  # 新規追加
│       ├── __init__.py
│       ├── detector.py
│       ├── learning_manager.py
│       └── pattern_analyzer.py
├── gui/
│   ├── main_window.py
│   └── dialogs/
│       └── overflow_result_dialog.py  # 新規追加
└── utils/
    └── tesseract_config.py  # 新規追加
```

#### 2.2 溢れチェック機能のライブラリ化（4日）
```python
# core/overflow_detector/__init__.py
from .detector import OverflowDetector
from .learning_manager import LearningManager

class OverflowChecker:
    """TECHZIPから使用するための統一インターフェース"""
    
    def __init__(self, config=None):
        self.detector = OverflowDetector(config)
        self.learning_manager = LearningManager()
    
    def check_pdf(self, pdf_path, callback=None):
        """PDFの溢れチェックを実行"""
        result = self.detector.process_pdf(pdf_path, callback)
        return result
    
    def show_result_dialog(self, result, parent_window):
        """結果ダイアログを表示（Qt統合）"""
        from gui.dialogs.overflow_result_dialog import OverflowResultDialog
        dialog = OverflowResultDialog(result, parent_window)
        return dialog.exec()
```

#### 2.3 メインウィンドウへの統合（4日）
```python
# gui/main_window.py への追加
from core.overflow_detector import OverflowChecker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.overflow_checker = OverflowChecker()
        # ... 既存のコード
    
    def setup_overflow_button(self):
        """溢れチェックボタンの追加"""
        self.overflow_check_button = QPushButton("リスト溢れチェック")
        self.overflow_check_button.clicked.connect(self.on_overflow_check)
        # InputPanelに追加
    
    def on_overflow_check(self):
        """溢れチェック実行"""
        n_code = self.get_selected_ncode()
        pdf_path = self.find_pdf_for_ncode(n_code)
        
        if pdf_path:
            result = self.overflow_checker.check_pdf(pdf_path)
            self.overflow_checker.show_result_dialog(result, self)
```

#### 2.4 設定ファイルの統合（3日）
```json
// config/settings.json への追加
{
    "overflow_checker": {
        "enabled": true,
        "tesseract_path": "auto",  // 自動検出
        "detection_sensitivity": "medium",
        "use_learning": true,
        "learning_db_path": "./data/overflow_learning.db"
    }
}
```

### Phase 3: デプロイメントの簡素化（1週間）

#### 3.1 ワンクリックセットアップ（3日）
```powershell
# setup_overflow_checker.ps1
Write-Host "=== 溢れチェック機能セットアップ ===" -ForegroundColor Cyan

# 1. Python依存関係インストール
Write-Host "依存関係をインストール中..." -ForegroundColor Yellow
pip install -r requirements_addon.txt

# 2. Tesseract OCRチェック
Write-Host "Tesseract OCRを確認中..." -ForegroundColor Yellow
python -c "from utils.tesseract_installer import TesseractInstaller; TesseractInstaller().setup()"

# 3. 初期データベース作成
Write-Host "学習データベースを初期化中..." -ForegroundColor Yellow
python -c "from core.overflow_detector.learning_manager import LearningManager; LearningManager().init_database()"

Write-Host "✅ セットアップ完了！" -ForegroundColor Green
```

#### 3.2 統合版run_windows.ps1の更新（2日）
```powershell
# run_windows.ps1 の更新
param(
    [switch]$NoOverflowChecker = $false
)

# ... 既存のセットアップコード

# 溢れチェック機能の確認
if (-not $NoOverflowChecker) {
    # Tesseractの確認
    $tesseractOK = Test-Path $env:TESSERACT_CMD
    if (-not $tesseractOK) {
        Write-Host "⚠️ Tesseract OCRが見つかりません。溢れチェック機能は制限されます。" -ForegroundColor Yellow
    }
}

# メインアプリケーション起動
python main.py
```

#### 3.3 インストーラーの作成（2日）
```python
# build_installer.py
import PyInstaller.__main__
import shutil
from pathlib import Path

def build_techzip_with_overflow():
    """溢れチェック機能統合版のインストーラー作成"""
    
    PyInstaller.__main__.run([
        'main.py',
        '--name=TECHZIP',
        '--windowed',
        '--icon=assets/icon.ico',
        '--add-data=config;config',
        '--add-data=core/overflow_detector;core/overflow_detector',
        '--hidden-import=pdfplumber',
        '--hidden-import=pytesseract',
        '--collect-all=pdfplumber',
        '--onedir'
    ])
```

## 🎯 移行後の実行方法

### 開発環境
```powershell
# 統合版TECHZIP起動（溢れチェック機能付き）
cd C:\Users\tky99\DEV\technical-fountain-series-support-tool
.\run_windows.ps1
```

### 本番環境
```powershell
# インストーラーでインストール後
# スタートメニューから「TECHZIP」を起動
# または
C:\Program Files\TECHZIP\TECHZIP.exe
```

## 📊 移行スケジュール

### Week 1: Phase 1（依存関係統合）
- Day 1-2: 依存関係調査
- Day 3: 統合requirements作成
- Day 4: Tesseractインストーラー開発
- Day 5: テストとドキュメント

### Week 2-3: Phase 2（コード統合）
- Week 2: モジュール再編成とライブラリ化
- Week 3前半: GUI統合
- Week 3後半: 設定ファイル統合とテスト

### Week 4: Phase 3（デプロイメント）
- Day 1-2: セットアップスクリプト
- Day 3: run_windows.ps1更新
- Day 4-5: インストーラー作成とテスト

## ✅ 成功基準

1. **シームレスな統合**
   - TECHZIPのメインウィンドウに「リスト溢れチェック」ボタンが表示
   - ワンクリックで溢れチェック実行
   - 学習データの保存と活用

2. **簡単なセットアップ**
   - 単一のPowerShellコマンドで全機能セットアップ
   - Tesseract OCRの自動インストール（または明確な手順）
   - エラーの自動回復

3. **パフォーマンス**
   - 起動時間の増加: 1秒以内
   - メモリ使用量の増加: 50MB以内
   - レスポンシブなUI

## 🚀 次のステップ

1. **即座に開始可能**:
   - 依存関係の詳細調査
   - requirements_addon.txtの作成
   - Tesseractインストーラーのプロトタイプ

2. **並行作業可能**:
   - 溢れチェック機能のライブラリ化
   - 学習機能の改善（別ロードマップ参照）

3. **統合テスト準備**:
   - テストPDFの準備
   - ベンチマーク設定
   - ユーザー受け入れテスト計画