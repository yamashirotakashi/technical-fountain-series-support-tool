# 溢れチェッカー - Windows EXE化ガイド

## 🚀 高速起動フォルダ構成について

このプロジェクトは **フォルダ構成** でのEXE化を採用しています。

### フォルダ構成の利点
- ✅ **高速起動**: 単一EXEより大幅に起動時間短縮
- ✅ **安定性**: 依存関係の分離でクラッシュリスク低減
- ✅ **メンテナンス性**: 個別ファイルの更新が容易
- ✅ **デバッグ**: ログファイルやデータの確認が簡単

### 単一EXEとの比較
| 項目 | フォルダ構成 | 単一EXE |
|------|-------------|---------|
| 起動速度 | ⚡ 高速 | 🐌 遅い |
| ファイルサイズ | 📁 分散 | 📦 単一 |
| 配布性 | ZIP圧縮 | そのまま |
| 実行安定性 | ✅ 高い | ⚠️ 中程度 |

## 📦 ビルド手順

### 1. 環境セットアップ
```powershell
# Windows環境の初期化
.\setup_windows.ps1

# 必要に応じてクリーンインストール
.\setup_windows.ps1 -Clean
```

### 2. EXE化実行
```powershell
# 標準ビルド（フォルダ構成・高速起動）
.\build_exe.ps1

# バージョン指定
.\build_exe.ps1 -Version "1.1.0"

# クリーンビルド
.\build_exe.ps1 -Clean

# デバッグビルド
.\build_exe.ps1 -Debug
```

### 3. 生成物の確認
```
dist/
└── OverflowChecker/          # 実行フォルダ
    ├── OverflowChecker.exe   # メイン実行ファイル
    ├── _internal/            # 依存関係
    └── assets/               # リソースファイル
```

## 🛡️ 安全性について

### 他プログラムファイルの保護
ビルドスクリプトは以下の安全対策を実装しています：

```powershell
# 削除対象を限定（他のプログラムを保護）
$cleanTargets = @(
    "dist\OverflowChecker",      # 本プロジェクトのみ
    "build",                     # PyInstallerの一時ファイル
    "*.spec.bak"                 # specファイルのバックアップ
)
```

- ❌ `dist`フォルダ全体の削除 → ✅ `dist\OverflowChecker`のみ削除
- ❌ システムファイルへの影響 → ✅ プロジェクト内ファイルのみ対象
- ❌ 他のプログラムの削除 → ✅ 完全に保護

## 🎯 配布方法

### ZIP配布（推奨）
```powershell
# 自動的にZIP配布パッケージを作成
.\build_exe.ps1

# 生成物:
# - dist/OverflowChecker_v1.0.0.zip  # 配布用アーカイブ
```

### エンドユーザーでの使用
1. ZIPファイルを任意のフォルダに展開
2. `OverflowChecker.exe`を実行
3. Pythonインストール不要

## ⚙️ 高速起動の技術詳細

### PyInstallerの最適化設定
```python
# EXE設定
exe = EXE(
    exclude_binaries=True,      # フォルダ構成
    upx=False,                  # 圧縮無効（速度優先）
    runtime_tmpdir=None,        # 一時ディレクトリなし
)

# 配布フォルダ設定
coll = COLLECT(
    strip=False,    # 高速起動を優先
    upx=False,      # 圧縮無効（起動速度最優先）
)
```

### 起動時間の目安
- **フォルダ構成**: 約2-5秒
- **単一EXE**: 約10-30秒

## 🔧 トラブルシューティング

### WSL PATH汚染問題（Windows環境）

#### 症状
```
pipをアップグレード中...
did not find executable at '/usr/bin\python.exe': ????????????????
❌ セットアップ中にエラーが発生しました: pipアップグレードに失敗しました
```

#### 原因
WSL（Windows Subsystem for Linux）環境のPATHが Windows Python仮想環境に混入し、Linuxパス（/usr/bin）がWindows環境で参照されることが原因です。

#### 根本的解決方法（推奨）
```batch
# 1. コマンドプロンプトを管理者権限で起動
# 2. プロジェクトディレクトリに移動
cd C:\Users\[ユーザー名]\DEV\technical-fountain-series-support-tool\CodeBlockOverFlowDisposal\overflow_checker_standalone

# 3. WSL汚染解決スクリプト実行
fix_contamination.bat

# または PowerShell で直接実行
powershell -ExecutionPolicy Bypass -File fix_wsl_contamination.ps1
```

#### 解決スクリプトの動作
1. **WSL環境変数の完全クリア** - Linux関連の環境変数を除去
2. **汚染された仮想環境の削除** - 既存のvenvフォルダを完全削除
3. **純粋なWindows Python検出** - WSL汚染のないPythonを特定
4. **クリーンな仮想環境作成** - 分離されたプロセスで新規作成
5. **依存関係の再インストール** - 純粋なWindows環境で実行
6. **汚染チェック** - 新環境にLinuxパスが含まれていないことを確認

### よくある問題

#### 1. Tesseract OCRが見つからない
```
⚠️ Tesseract OCRが見つかりません
```
**解決方法**:
```powershell
# Chocolateyでインストール
choco install tesseract

# または手動インストール
# https://github.com/UB-Mannheim/tesseract/wiki
```

#### 2. PyInstaller実行エラー
```
❌ PyInstaller実行に失敗しました
```
**解決方法**:
```powershell
# 依存関係の再インストール
.\setup_windows.ps1 -Clean

# デバッグモードで詳細確認
.\build_exe.ps1 -Debug
```

#### 3. 実行時DLLエラー
```
❌ DLLが見つかりません
```
**解決方法**:
- Visual C++ Redistributableのインストール
- Windows Updateの実行
- 依存関係の再ビルド

## 📝 開発者向け情報

### ビルドスクリプトの機能
- ✅ 前提条件の自動チェック
- ✅ バージョン情報の自動生成
- ✅ 事前・事後テストの実行
- ✅ 配布パッケージの自動作成
- ✅ 安全なクリーンアップ処理

### カスタマイズポイント
1. **アイコン**: `assets/overflow_checker.ico`
2. **バージョン情報**: `version_info.txt`（自動生成）
3. **依存関係**: `overflow_checker.spec`
4. **配布設定**: `build_exe.ps1`の配布関数

## 🎉 次のステップ

EXE化が完了したら：
1. 実際のPDFでテスト実行
2. 人間判定UIの動作確認  
3. 学習データの蓄積開始
4. Phase1 MLモデルの開発準備

詳細は **[技術仕様書](../PHASE1_COMPLETION_REPORT.md)** を参照してください。