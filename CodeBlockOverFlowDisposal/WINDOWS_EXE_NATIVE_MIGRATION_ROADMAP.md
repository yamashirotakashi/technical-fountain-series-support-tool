# Windows EXE化によるネイティブ実行移行ロードマップ

最終更新: 2025-01-29

## 🎯 基本方針

TECHZIPと同様のアプローチで、PyInstallerを使用してWindows実行ファイル（.exe）として配布する。これにより、Pythonインストールが不要な完全なスタンドアロンアプリケーションを実現する。

## 📋 現状分析

### TECHZIPのEXE化実装
- **ビルドツール**: PyInstaller
- **配布形式**: 単一フォルダ形式（--onedir）
- **GUI**: PyQt6ベース
- **起動方法**: techzip.exe直接実行

### 溢れチェッカーの要件
- **GUI**: PyQt6（TECHZIPと共通）
- **外部依存**: Tesseract OCR
- **データファイル**: 学習データベース（SQLite）
- **画像処理**: OpenCV, Pillow

## 🚀 Phase 1: スタンドアロンEXE化（2週間）

### Step 1.1: PyInstallerスペックファイル作成（2日）

```python
# overflow_checker.spec
# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None

# アプリケーションのルートディレクトリ
ROOT_DIR = Path(__file__).parent

a = Analysis(
    ['overflow_checker_standalone/run_ultimate.py'],
    pathex=[str(ROOT_DIR)],
    binaries=[
        # Tesseract実行ファイル（オプション）
        # ('C:/Program Files/Tesseract-OCR/tesseract.exe', 'tesseract'),
    ],
    datas=[
        # 設定ファイル
        ('overflow_checker_standalone/config', 'config'),
        # アセット
        ('overflow_checker_standalone/assets', 'assets'),
        # 初期データベース
        ('overflow_checker_standalone/data/learning.db', 'data'),
    ],
    hiddenimports=[
        'pdfplumber',
        'PyPDF2',
        'pytesseract',
        'PIL',
        'cv2',
        'numpy',
        'sqlite3',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # 不要な大型ライブラリを除外
        'scipy',
        'pandas',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OverflowChecker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX圧縮は使用しない（起動速度優先）
    console=False,  # コンソールウィンドウを表示しない
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='overflow_checker_standalone/assets/overflow_checker.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='OverflowChecker',
)
```

### Step 1.2: ビルド環境の整備（3日）

#### ビルドスクリプト作成
```powershell
# build_exe.ps1
param(
    [string]$Version = "1.0.0",
    [switch]$Clean = $false
)

Write-Host "=== 溢れチェッカー EXEビルド ===" -ForegroundColor Cyan
Write-Host "バージョン: $Version" -ForegroundColor Yellow

# クリーンビルド
if ($Clean) {
    Write-Host "既存のビルドを削除中..." -ForegroundColor Yellow
    Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
}

# バージョン情報の更新
$versionFile = "overflow_checker_standalone/version.py"
@"
VERSION = '$Version'
BUILD_DATE = '$(Get-Date -Format "yyyy-MM-dd")'
"@ | Set-Content $versionFile

# PyInstallerでビルド
Write-Host "EXEをビルド中..." -ForegroundColor Yellow
pyinstaller overflow_checker.spec --clean

# ビルド成功確認
if (Test-Path "dist/OverflowChecker/OverflowChecker.exe") {
    Write-Host "✅ ビルド成功！" -ForegroundColor Green
    Write-Host "出力先: dist/OverflowChecker/" -ForegroundColor Cyan
} else {
    Write-Host "❌ ビルド失敗" -ForegroundColor Red
    exit 1
}
```

#### アイコン作成
```python
# scripts/create_icon.py
from PIL import Image, ImageDraw, ImageFont

def create_overflow_icon():
    """溢れチェッカーのアイコン作成"""
    # 256x256のアイコン作成
    img = Image.new('RGBA', (256, 256), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 背景（グラデーション風）
    for i in range(256):
        color = (50, 100 + i//2, 200, 255)
        draw.rectangle([0, i, 256, i+1], fill=color)
    
    # "OC"の文字
    try:
        font = ImageFont.truetype("arial.ttf", 120)
    except:
        font = ImageFont.load_default()
    
    draw.text((40, 60), "OC", fill=(255, 255, 255, 255), font=font)
    
    # 溢れを示す赤い線
    draw.rectangle([200, 100, 256, 120], fill=(255, 0, 0, 255))
    
    # 複数サイズのアイコンを含むICOファイル作成
    img.save("overflow_checker.ico", sizes=[(16,16), (32,32), (48,48), (256,256)])
```

### Step 1.3: Tesseract OCR対応（4日）

#### オプション1: Tesseractバンドル版
```python
# utils/tesseract_bundle.py
import os
import sys
import urllib.request
import zipfile
from pathlib import Path

class TesseractBundleManager:
    """EXEにバンドルされたTesseract管理"""
    
    def __init__(self):
        if getattr(sys, 'frozen', False):
            # EXE実行時
            self.app_dir = Path(sys._MEIPASS)
        else:
            # 開発環境
            self.app_dir = Path(__file__).parent.parent
        
        self.tesseract_dir = self.app_dir / "tesseract"
        
    def setup_tesseract(self):
        """Tesseractのパスを設定"""
        if self.tesseract_dir.exists():
            # バンドル版を使用
            tesseract_exe = self.tesseract_dir / "tesseract.exe"
            os.environ['TESSERACT_CMD'] = str(tesseract_exe)
            return True
        else:
            # システムのTesseractを検索
            return self.find_system_tesseract()
    
    def find_system_tesseract(self):
        """システムインストールのTesseractを検索"""
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Tesseract-OCR\tesseract.exe",
        ]
        
        for path in common_paths:
            if Path(path).exists():
                os.environ['TESSERACT_CMD'] = path
                return True
        
        return False
```

#### オプション2: Tesseractダウンローダー
```python
# gui/tesseract_installer_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QProgressBar
from PyQt6.QtCore import QThread, pyqtSignal
import urllib.request

class TesseractDownloader(QThread):
    """バックグラウンドでTesseractをダウンロード"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    TESSERACT_URL = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.0/tesseract-portable.zip"
    
    def run(self):
        try:
            # ダウンロード処理
            def download_callback(block_num, block_size, total_size):
                downloaded = block_num * block_size
                percent = min(int(downloaded * 100 / total_size), 100)
                self.progress.emit(percent)
            
            urllib.request.urlretrieve(
                self.TESSERACT_URL,
                "tesseract-portable.zip",
                reporthook=download_callback
            )
            
            # 解凍処理
            # ...
            
            self.finished.emit(True, "インストール完了")
        except Exception as e:
            self.finished.emit(False, str(e))

class TesseractInstallerDialog(QDialog):
    """Tesseractインストーラーダイアログ"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Tesseract OCRセットアップ")
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # 説明
        label = QLabel(
            "Tesseract OCRが見つかりません。\n"
            "今すぐダウンロードしてインストールしますか？"
        )
        layout.addWidget(label)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # ボタン
        self.install_btn = QPushButton("インストール")
        self.install_btn.clicked.connect(self.start_install)
        layout.addWidget(self.install_btn)
```

### Step 1.4: 実行時の初期設定（3日）

```python
# overflow_checker_standalone/run_ultimate.py の更新
import sys
import os
from pathlib import Path

def setup_exe_environment():
    """EXE実行環境のセットアップ"""
    
    # 実行環境の判定
    if getattr(sys, 'frozen', False):
        # EXEとして実行中
        app_dir = Path(sys.executable).parent
        
        # 作業ディレクトリを設定
        os.chdir(app_dir)
        
        # データディレクトリの確認/作成
        data_dir = app_dir / "data"
        data_dir.mkdir(exist_ok=True)
        
        # ログディレクトリ
        log_dir = app_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # 設定ファイルのパス修正
        os.environ['OVERFLOW_CHECKER_HOME'] = str(app_dir)
    else:
        # 開発環境
        os.environ['OVERFLOW_CHECKER_HOME'] = str(Path(__file__).parent)

def main():
    """メインエントリポイント"""
    # 環境セットアップ
    setup_exe_environment()
    
    # Tesseractセットアップ
    from utils.tesseract_bundle import TesseractBundleManager
    tesseract_manager = TesseractBundleManager()
    
    if not tesseract_manager.setup_tesseract():
        # Tesseractが見つからない場合
        from PyQt6.QtWidgets import QApplication
        from gui.tesseract_installer_dialog import TesseractInstallerDialog
        
        app = QApplication(sys.argv)
        dialog = TesseractInstallerDialog()
        if dialog.exec() != QDialog.DialogCode.Accepted:
            sys.exit(1)
    
    # メインアプリケーション起動
    from gui.main_application import OverflowCheckerApp
    app = OverflowCheckerApp()
    sys.exit(app.run())

if __name__ == "__main__":
    main()
```

### Step 1.5: 配布パッケージ作成（2日）

#### フォルダ構成
```
OverflowChecker_v1.0.0/
├── OverflowChecker.exe      # メイン実行ファイル
├── config/
│   └── settings.json        # 設定ファイル
├── data/
│   └── learning.db          # 初期学習データベース
├── tesseract/               # Tesseractポータブル版（オプション）
│   ├── tesseract.exe
│   └── tessdata/
├── logs/                    # ログファイル出力先
├── README.txt               # 使用説明書
└── LICENSE.txt             # ライセンス
```

#### インストーラー作成（NSIS使用）
```nsis
; overflow_checker_installer.nsi
!include "MUI2.nsh"

Name "溢れチェッカー"
OutFile "OverflowChecker_Setup_v1.0.0.exe"
InstallDir "$PROGRAMFILES\OverflowChecker"

; ページ設定
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; 言語設定
!insertmacro MUI_LANGUAGE "Japanese"

Section "メインプログラム"
    SetOutPath "$INSTDIR"
    
    ; ファイルコピー
    File /r "dist\OverflowChecker\*.*"
    
    ; スタートメニューショートカット
    CreateDirectory "$SMPROGRAMS\溢れチェッカー"
    CreateShortcut "$SMPROGRAMS\溢れチェッカー\溢れチェッカー.lnk" "$INSTDIR\OverflowChecker.exe"
    CreateShortcut "$SMPROGRAMS\溢れチェッカー\アンインストール.lnk" "$INSTDIR\uninstall.exe"
    
    ; デスクトップショートカット（オプション）
    CreateShortcut "$DESKTOP\溢れチェッカー.lnk" "$INSTDIR\OverflowChecker.exe"
    
    ; アンインストーラー作成
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; レジストリ登録
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OverflowChecker" \
                     "DisplayName" "溢れチェッカー"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OverflowChecker" \
                     "UninstallString" "$INSTDIR\uninstall.exe"
SectionEnd

Section "Tesseract OCR" SEC_TESSERACT
    ; Tesseractのインストール（オプション）
    SetOutPath "$INSTDIR\tesseract"
    File /r "tesseract-portable\*.*"
SectionEnd
```

## 🚀 Phase 2: 自動更新機能（1週間）

### Step 2.1: 更新チェック機能（2日）

```python
# utils/auto_updater.py
import requests
from packaging import version
import json

class AutoUpdater:
    """GitHub Releasesを使用した自動更新"""
    
    GITHUB_API = "https://api.github.com/repos/YOUR_REPO/overflow-checker/releases/latest"
    
    def __init__(self, current_version):
        self.current_version = current_version
        self.update_info = None
        
    def check_for_updates(self):
        """更新チェック"""
        try:
            response = requests.get(self.GITHUB_API)
            if response.status_code == 200:
                latest_release = response.json()
                latest_version = latest_release['tag_name'].lstrip('v')
                
                if version.parse(latest_version) > version.parse(self.current_version):
                    self.update_info = {
                        'version': latest_version,
                        'download_url': self._find_exe_asset(latest_release),
                        'release_notes': latest_release['body']
                    }
                    return True
        except Exception as e:
            print(f"更新チェックエラー: {e}")
        
        return False
    
    def _find_exe_asset(self, release):
        """EXEファイルのダウンロードURLを取得"""
        for asset in release['assets']:
            if asset['name'].endswith('.exe'):
                return asset['browser_download_url']
        return None
```

### Step 2.2: 更新ダイアログ（2日）

```python
# gui/update_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextBrowser
from PyQt6.QtCore import Qt

class UpdateDialog(QDialog):
    """更新通知ダイアログ"""
    
    def __init__(self, update_info, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("アップデート利用可能")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # バージョン情報
        version_label = QLabel(
            f"新しいバージョン {self.update_info['version']} が利用可能です"
        )
        version_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(version_label)
        
        # リリースノート
        release_notes = QTextBrowser()
        release_notes.setMarkdown(self.update_info['release_notes'])
        layout.addWidget(release_notes)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        update_btn = QPushButton("今すぐ更新")
        update_btn.clicked.connect(self.accept)
        
        later_btn = QPushButton("後で")
        later_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(update_btn)
        button_layout.addWidget(later_btn)
        layout.addLayout(button_layout)
```

### Step 2.3: バックグラウンド更新（3日）

```python
# utils/update_installer.py
import subprocess
import tempfile
from pathlib import Path

class UpdateInstaller:
    """更新のダウンロードとインストール"""
    
    def download_and_install(self, download_url, progress_callback=None):
        """更新をダウンロードして実行"""
        
        # 一時ファイルにダウンロード
        temp_dir = Path(tempfile.gettempdir())
        update_exe = temp_dir / "OverflowChecker_Update.exe"
        
        # ダウンロード処理
        response = requests.get(download_url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(update_exe, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if progress_callback:
                    progress_callback(downloaded, total_size)
        
        # 更新スクリプト作成（現在のプロセス終了後に実行）
        update_script = temp_dir / "update.bat"
        with open(update_script, 'w') as f:
            f.write(f"""
@echo off
timeout /t 2 /nobreak > nul
"{update_exe}" /S
del "{update_exe}"
del "%~f0"
""")
        
        # 更新スクリプトを起動して終了
        subprocess.Popen(str(update_script), shell=True)
        sys.exit(0)
```

## 📊 Phase 3: パフォーマンス最適化（1週間）

### Step 3.1: 起動時間の最適化（2日）

```python
# core/lazy_loader.py
class LazyLoader:
    """重いモジュールの遅延読み込み"""
    
    _modules = {}
    
    @classmethod
    def load(cls, module_name):
        """必要になったときに読み込み"""
        if module_name not in cls._modules:
            if module_name == 'pdfplumber':
                import pdfplumber
                cls._modules['pdfplumber'] = pdfplumber
            elif module_name == 'cv2':
                import cv2
                cls._modules['cv2'] = cv2
            # 他のモジュール...
        
        return cls._modules[module_name]
```

### Step 3.2: リソース管理（3日）

```python
# utils/resource_manager.py
import psutil
import gc

class ResourceManager:
    """メモリとリソースの管理"""
    
    def __init__(self):
        self.max_memory_mb = 500  # 最大500MB
        
    def check_memory(self):
        """メモリ使用量チェック"""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        if memory_mb > self.max_memory_mb:
            # ガベージコレクション実行
            gc.collect()
            
            # キャッシュクリア
            self.clear_caches()
    
    def clear_caches(self):
        """各種キャッシュをクリア"""
        # PDFキャッシュ、画像キャッシュなど
        pass
```

### Step 3.3: 並列処理の最適化（2日）

```python
# core/parallel_processor.py
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

class ParallelPDFProcessor:
    """並列PDF処理"""
    
    def __init__(self):
        # CPU数に基づいてワーカー数を決定
        self.max_workers = min(multiprocessing.cpu_count() - 1, 4)
        
    def process_pages_parallel(self, pages):
        """ページを並列処理"""
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for page in pages:
                future = executor.submit(self.process_single_page, page)
                futures.append(future)
            
            results = []
            for future in futures:
                results.append(future.result())
            
        return results
```

## 📅 実装スケジュール

### Week 1-2: Phase 1（EXE化基本実装）
- Day 1-2: PyInstallerスペックファイル作成
- Day 3-5: ビルド環境整備
- Day 6-9: Tesseract対応
- Day 10-12: 実行時初期設定
- Day 13-14: 配布パッケージ作成

### Week 3: Phase 2（自動更新）
- Day 15-16: 更新チェック機能
- Day 17-18: 更新ダイアログ
- Day 19-21: バックグラウンド更新

### Week 4: Phase 3（最適化）
- Day 22-23: 起動時間最適化
- Day 24-26: リソース管理
- Day 27-28: 並列処理最適化

## ✅ 成功指標

### 基本要件
- ✅ Python未インストール環境での動作
- ✅ ダブルクリックで起動
- ✅ 起動時間: 3秒以内
- ✅ メモリ使用量: 200MB以内

### 配布要件
- ✅ 単一EXEファイル or インストーラー
- ✅ ファイルサイズ: 50MB以内（Tesseract除く）
- ✅ Windows 10/11対応
- ✅ 32bit/64bit両対応

### ユーザビリティ
- ✅ 初回起動時の自動セットアップ
- ✅ エラー時の分かりやすいメッセージ
- ✅ 自動更新通知
- ✅ 日本語UI完全対応

## 🚀 次のステップ

1. **即座に開始**
   - overflow_checker.specファイルの作成
   - アイコンデザイン
   - ビルドスクリプトの作成

2. **並行作業**
   - Tesseractポータブル版の調査
   - 更新サーバー（GitHub Releases）の準備
   - ドキュメント作成

3. **テスト準備**
   - クリーンなWindows環境でのテスト
   - 各種Windowsバージョンでの動作確認
   - ウイルス対策ソフトとの互換性確認