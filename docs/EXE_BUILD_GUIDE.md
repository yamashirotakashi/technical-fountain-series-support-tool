# exe化ビルドガイド

## 概要
技術の泉シリーズ制作支援ツールをWindows実行可能ファイル（.exe）として配布するためのガイドです。

## 前提条件

### Pythonのグローバルインストール
- **Python 3.9+** をシステム全体にインストール
- **仮想環境は使わない**（exe化のため）
- PATHにPythonが含まれていること

```cmd
python --version
pip --version
```

### 必要パッケージのインストール
```cmd
cd C:\Users\tky99\DEV\technical-fountain-series-support-tool
pip install -r requirements.txt
pip install pyinstaller
```

## ビルド手順

### 1. 起動テスト（ネイティブ環境）
```powershell
# 詳細診断付きで起動テスト
.\run_native_exe.ps1

# シンプル起動テスト
.\run_windows.ps1
```

### 2. PyInstaller設定ファイル作成
```cmd
# 設定ファイルを生成
pyi-makespec --windowed --onefile --name TechZip main.py
```

### 3. specファイルの編集
`TechZip.spec` を以下のように編集：

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('gui', 'gui'),
        ('core', 'core'),
        ('utils', 'utils'),
        ('resources', 'resources'),  # アイコンなど
    ],
    hiddenimports=[
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'selenium',
        'google.oauth2',
        'googleapiclient',
        'openpyxl',
        'imaplib',
        'email',
        'core.preflight',  # Pre-flight Check関連
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TechZip',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico'  # アイコンファイル（オプション）
)
```

### 4. ビルド実行
```cmd
# specファイルを使用してビルド
pyinstaller TechZip.spec

# または直接コマンドでビルド
pyinstaller --windowed --onefile --name TechZip main.py
```

### 5. 動作確認
```cmd
# 生成されたexeファイルをテスト
dist\TechZip.exe
```

## トラブルシューティング

### よくある問題

#### 1. モジュールが見つからないエラー
```
ModuleNotFoundError: No module named 'XXX'
```
**解決法**: `hiddenimports` に該当モジュールを追加

#### 2. ファイルが見つからないエラー
```
FileNotFoundError: config/settings.json
```
**解決法**: `datas` に必要なファイル・ディレクトリを追加

#### 3. PyQt6関連エラー
```
ImportError: cannot import name 'XXX' from 'PyQt6'
```
**解決法**: PyQt6の全サブモジュールを `hiddenimports` に追加

#### 4. Selenium WebDriverエラー
```
WebDriverException: 'chromedriver' executable needs to be in PATH
```
**解決法**: ChromeDriverを含むか、実行時にダウンロードする仕組みを実装済み

### デバッグ方法

#### コンソール付きでビルド
```cmd
# デバッグ用（コンソール表示）
pyinstaller --onefile --name TechZip-Debug main.py
```

#### 詳細ログを有効化
```python
# main.pyの先頭に追加
import sys
if hasattr(sys, '_MEIPASS'):
    # PyInstallerで実行中の場合
    import logging
    logging.basicConfig(level=logging.DEBUG)
```

## 配布準備

### ファイル構成
```
TechZip-v1.0/
├── TechZip.exe              # メイン実行ファイル
├── README.txt               # 使用方法
├── config/
│   └── settings.json.example  # 設定ファイルの例
└── docs/
    └── USER_GUIDE.md        # ユーザーガイド
```

### 設定ファイルの準備
- `config/settings.json.example` を配布
- ユーザーが `.example` を削除して設定を入力
- 初回起動時に設定ファイルの存在チェック

### 必要な外部ファイル
- Google Cloud サービスアカウントキー
- ChromeDriver（自動ダウンロード機能実装済み）

## Pre-flight Check機能の対応

Pre-flight Check機能は以下のコンポーネントを含みます：
- Seleniumベースのスクレイピング
- メール監視機能
- バッチ処理
- 状態管理
- API移行準備（将来対応）

exe化時の注意点：
- ChromeDriverの自動ダウンロード機能が有効
- メール設定は環境変数または設定ファイルから読み込み
- 状態ファイルは `%USERPROFILE%\.techzip` に保存

## 最終チェックリスト

- [ ] ネイティブ環境での動作確認
- [ ] 全機能のテスト（通常処理、Pre-flight Check）
- [ ] exe化後の動作確認
- [ ] 設定ファイルの準備
- [ ] ドキュメントの作成（README.txt）
- [ ] インストーラーの作成（オプション）