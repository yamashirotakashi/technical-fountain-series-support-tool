# 技術の泉シリーズ制作支援ツール

技術の泉シリーズの制作プロセスを自動化・効率化するGUIアプリケーションです。

## 概要

本ツールは、Re:VIEW形式の原稿を超原稿用紙（Word）形式に変換し、適切な場所に配置するまでの一連の作業を自動化します。

## 主な機能

- **Nコード処理**: 複数のNコードをバッチ処理
- **Googleシート連携**: Nコードからリポジトリ情報を自動取得
- **リポジトリ管理**: GitHub/ローカルリポジトリの自動検索
- **作業フォルダ選択**: ファイルマネージャー風UIで作業フォルダを確認・選択
- **自動変換**: Re:VIEWから超原稿用紙への自動変換
- **メール監視**: 変換完了メールの自動監視とダウンロード
- **Word処理**: 変換後のWordファイルの自動整形

## インストール

### 前提条件

- Python 3.10以上
- Windows環境（WSLも対応）
- Google Drive がマウントされていること
- インターネット接続

### セットアップ

1. リポジトリをクローン
```bash
git clone https://github.com/irdtechbook/technical-fountain-series-support-tool.git
cd technical-fountain-series-support-tool
```

2. 仮想環境のセットアップ

**Windows (PowerShell):**
```powershell
.\setup_windows.ps1
```

**WSL/Linux:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. 環境設定

`.env`ファイルを作成し、以下の情報を設定：
```
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
```

## 使い方

### 起動方法

**Windows (推奨):**
```powershell
.\run_windows.ps1
```

**WSL/Linux:**
```bash
source venv/bin/activate
python main.py
```

### ホットキー起動（Windows）

`Ctrl+Shift+I`でツールを起動できます。

セットアップ：
```batch
install_startup.bat
```

### 基本的な使い方

1. Nコードを入力（カンマ、タブ、スペース、改行区切りで複数可）
2. 「処理開始」ボタンをクリック
3. 作業フォルダ選択ダイアログで確認・変更
4. 自動処理の完了を待つ

## 作業フォルダ選択機能

- リポジトリ内のRe:VIEWフォルダを自動検出
- ファイルマネージャー風のツリー表示
- フォルダ内容のプレビュー機能
- 「次回からも同じフォルダで作業」オプション

## 設定ファイル

### config/settings.json
```json
{
    "google_sheet": {
        "sheet_id": "YOUR_SHEET_ID",
        "credentials_path": "path/to/credentials.json"
    },
    "paths": {
        "git_base": "G:\\マイドライブ\\[git]",
        "output_base": "G:\\.shortcut-targets-by-id\\..."
    }
}
```

### フォルダ設定の保存場所
- `~/.techzip/folder_settings.json`

## トラブルシューティング

### 依存関係エラー
```powershell
.\fix_dependencies.ps1
```

### セーフモード起動
```powershell
.\run_windows_safe.ps1
```

## 開発

### プロジェクト構造
```
technical-fountain-series-support-tool/
├── main.py                 # エントリーポイント
├── gui/                    # GUIコンポーネント
│   ├── main_window.py
│   ├── components/
│   └── dialogs/
├── core/                   # コア機能
│   ├── google_sheet.py
│   ├── file_manager.py
│   ├── web_client.py
│   └── workflow_processor.py
├── utils/                  # ユーティリティ
└── config/                 # 設定ファイル
```

## ライセンス

MIT License

## 作者

Technical Fountain Team

## 更新履歴

### 2025-01-20
- 作業フォルダ選択ダイアログを追加
- フォルダ設定の保存機能を実装
- Windows環境での起動エラーを修正