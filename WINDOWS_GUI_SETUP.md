# TechZip Pre-flight Checker - Windows GUI実行ガイド

## 🎯 概要

TechZip Pre-flight Checkerの統合テストGUIをWindows環境で実行するためのガイドです。

## 📋 必要な環境

### システム要件
- **OS**: Windows 10/11
- **Python**: 3.8以降
- **メモリ**: 2GB以上
- **ディスク**: 500MB以上の空き容量

### 事前準備
1. **Pythonインストール確認**
   ```powershell
   python --version
   ```
   ※ バージョンが表示されない場合は[Python公式サイト](https://python.org)からインストール

2. **プロジェクトディレクトリに移動**
   ```powershell
   cd C:\Users\tky99\DEV\technical-fountain-series-support-tool
   ```

## 🚀 実行方法

### 方法1: PowerShellスクリプト（推奨）
```powershell
.\run_gui.ps1
```

### 方法2: バッチファイル
```cmd
run_gui.bat
```

### 方法3: Python直接実行
```powershell
python main_gui.py
```

## 🔧 初回セットアップ

### 1. 依存関係のインストール
スクリプト実行時に自動的にインストールされますが、手動で行う場合：

```powershell
pip install -r requirements.txt
```

### 2. 環境設定ファイル
`.env`ファイルが存在することを確認してください：
```
GMAIL_ADDRESS=yamashiro.takashi@gmail.com
GMAIL_APP_PASSWORD=wmac uatf ykyh yzya
```

### 3. 仮想環境（オプション）
仮想環境を使用する場合：
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 🎨 GUI操作ガイド

### 画面構成
```
┌─────────────────────────────────────────────────────────┐
│                TechZip Pre-flight Checker               │
├─────────────────┬───────────────────────────────────────┤
│   テスト制御     │        テスト結果とログ              │
│                │                                       │
│ ○ 環境チェック  │  [テスト結果] [実行ログ]              │
│ ○ ファイル選択  │                                       │
│ ○ 検証モード    │  ○ 環境セットアップ      ✓ 成功      │
│ ○ メール設定    │  ○ マネージャー初期化    ✓ 成功      │
│                │  ○ ファイル検証          ✓ 成功      │
│ [完全テスト実行] │  ○ パフォーマンス監視    ✓ 成功      │
│ [テスト停止]    │  ○ エラー回復           ✓ 成功      │
│                │                                       │
├─────────────────┴───────────────────────────────────────┤
│ プログレス: ████████████████████████████ 100%          │
│ ステータス: テスト完了                                   │
└─────────────────────────────────────────────────────────┘
```

### 操作手順
1. **環境チェック**
   - 「システム環境確認」ボタンをクリック
   - Python環境と依存関係を確認

2. **ファイル選択**
   - 「DOCXファイル選択」でテスト対象ファイルを選択
   - 複数ファイル選択可能

3. **設定調整**
   - 検証モード選択（標準/高速/厳密）
   - メールアドレス設定確認

4. **テスト実行**
   - 「完全テスト実行」ボタンをクリック
   - リアルタイムでプログレスとログを確認

## 🛠️ トラブルシューティング

### よくある問題と解決方法

#### 1. スクリプト実行エラー
**問題**: `実行ポリシーにより...実行できません`
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. 依存関係エラー
**問題**: `ModuleNotFoundError`
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Python認識エラー
**問題**: `'python' is not recognized`
- Python環境変数の確認
- Python再インストール
- `py`コマンドを試す

#### 4. GUI起動エラー
**問題**: tkinterが利用できない
```powershell
# Pythonを完全版で再インストール
# または
pip install tk
```

### エラーログの確認
GUI内の「実行ログ」タブで詳細なエラー情報を確認できます。

## 📦 EXE版の作成と配布

### EXEファイル作成
```powershell
.\build_exe.bat
```

生成されるファイル：
- `dist\TechZipPreflightCheckerGUI.exe`

### 配布用パッケージ
以下のファイルを同じフォルダに配置：
1. `TechZipPreflightCheckerGUI.exe`
2. `.env`ファイル（メール設定）

### EXE版の実行
```
TechZipPreflightCheckerGUI.exe
```
※ダブルクリックで起動

## 🔍 デバッグモード

### ログレベル設定
環境変数でログレベルを調整：
```powershell
$env:LOG_LEVEL="DEBUG"
python main_gui.py
```

### テスト用ダミー設定
`.env`ファイルがない場合、自動的にテスト用設定が使用されます。

## 📞 サポート

### 問題報告先
- GitHub Issues
- プロジェクトドキュメント参照

### ログ情報の提供
問題報告時は以下の情報を含めてください：
1. Windowsバージョン
2. Pythonバージョン
3. エラーメッセージ（GUI内ログ）
4. 実行手順

---

## 📝 更新履歴

- **2025-07-26**: 初版作成
- WSL環境での開発、Windows環境での実行対応
- 統合テストGUI実装完了