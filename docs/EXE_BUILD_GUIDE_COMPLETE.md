# TechZip Windows EXE化ガイド

## 概要
本ガイドは、技術の泉シリーズ制作支援ツール（TechZip）をWindows実行可能ファイル（EXE）としてビルドする手順を説明します。

## 前提条件
- Windows 10/11
- Python 3.8以上
- Git
- PowerShell 5.0以上

## ビルド手順

### 1. 環境準備
```powershell
# プロジェクトディレクトリに移動
cd C:\Users\tky99\DEV\technical-fountain-series-support-tool

# 仮想環境の作成（初回のみ）
python -m venv venv_windows

# 仮想環境の有効化
.\venv_windows\Scripts\Activate.ps1

# 依存関係のインストール
pip install -r requirements.txt
pip install pyinstaller
```

### 2. EXEビルド

#### フォルダ形式EXE（推奨）
複数ファイルで構成される形式。起動が速く、アンチウイルスの誤検知が少ない。

```powershell
# バッチファイルを実行
.\build_exe_folder.bat

# または直接PowerShellで実行
powershell -ExecutionPolicy Bypass -File build_windows_exe.ps1
```

出力先: `dist\TechZip1.0\TechZip1.0.exe`

#### 単一ファイルEXE（ポータブル版）
すべてのファイルが1つのEXEに含まれる形式。配布が簡単。

```powershell
# バッチファイルを実行
.\build_exe_onefile.bat

# または直接PowerShellで実行
powershell -ExecutionPolicy Bypass -File build_windows_exe.ps1 -OneFile
```

出力先: `dist\TechZip1.0_portable.exe`

### 3. ビルドオプション

#### クリーンビルド
前回のビルドファイルを削除してから新規ビルド
```powershell
powershell -ExecutionPolicy Bypass -File build_windows_exe.ps1 -Clean
```

#### デバッグモード
デバッグ情報を含むビルド（問題解決用）
```powershell
powershell -ExecutionPolicy Bypass -File build_windows_exe.ps1 -DebugMode
```

## ビルド後の構成

### フォルダ形式の場合
```
dist\TechZip1.0\
├── TechZip1.0.exe          # メイン実行ファイル
├── TechZip_起動.bat        # 起動用バッチファイル
├── config\
│   └── settings.json       # 設定ファイル（編集可能）
├── README.md               # 使用説明書
└── [その他DLLファイル等]
```

### 単一ファイルの場合
```
dist\
└── TechZip1.0_portable.exe  # すべて含まれた実行ファイル
```

## Gmail OAuth認証の設定

### 初回起動時
1. EXEを実行すると、Gmail認証が必要な旨のメッセージが表示されます
2. 以下の手順でOAuth認証ファイルを取得：
   - Google Cloud Console (https://console.cloud.google.com/) にアクセス
   - APIs & Services > Credentials
   - 「+ CREATE CREDENTIALS」> OAuth client ID
   - Application type: Desktop application
   - Name: TechZip Gmail Monitor
   - JSONファイルをダウンロード

3. ダウンロードしたJSONファイルを以下の場所に配置：
   ```
   %USERPROFILE%\.techzip\config\gmail_oauth_credentials.json
   ```

4. 再度EXEを実行し、ブラウザで認証を完了

### 認証ファイルの保存場所
- 認証情報: `%USERPROFILE%\.techzip\config\gmail_oauth_credentials.json`
- トークン: `%USERPROFILE%\.techzip\config\gmail_token.pickle`
- 設定ファイル: `%USERPROFILE%\.techzip\config\settings.json`
- ログファイル: `%USERPROFILE%\.techzip\logs\`

## 配布方法

### フォルダ形式の配布
1. `dist\TechZip1.0` フォルダ全体をZIP圧縮
2. ユーザーに展開してもらい、`TechZip1.0.exe` または `TechZip_起動.bat` を実行

### 単一ファイルの配布
1. `dist\TechZip1.0_portable.exe` をそのまま配布
2. ユーザーは直接実行可能

## トラブルシューティング

### アンチウイルスの警告
- 単一ファイルEXEは誤検知されやすいため、フォルダ形式を推奨
- Windows Defenderの除外設定に追加することで回避可能

### 起動時のエラー
- `%USERPROFILE%\.techzip\logs\` のログファイルを確認
- デバッグモードでビルドして詳細情報を取得

### Gmail認証エラー
- 認証ファイルが正しい場所に配置されているか確認
- ブラウザのポップアップブロッカーを無効化
- ファイアウォールでポート番号がブロックされていないか確認

## 注意事項

1. **セキュリティ**
   - Gmail OAuth認証ファイルには機密情報が含まれるため、共有しないこと
   - EXEファイルには認証情報は含まれません

2. **互換性**
   - Windows 10/11 64bit版で動作確認済み
   - 32bit版Windowsでは動作しない可能性があります

3. **更新時の注意**
   - 新しいバージョンをビルドする際は、`APP_VERSION` を更新
   - ユーザーの設定ファイルは上書きされません

## 開発者向け情報

### カスタマイズ
- `techzip_windows.spec` でビルド設定を変更可能
- `resources/version_info.txt` でバージョン情報を更新
- アイコンを追加する場合は `resources/app_icon.ico` を配置

### ビルドスクリプトの構成
- `build_windows_exe.ps1` - メインビルドスクリプト
- `techzip_windows.spec` - PyInstaller設定ファイル
- `exe_startup_wrapper.py` - EXE起動時の初期設定
- `core/gmail_oauth_exe_helper.py` - EXE環境でのOAuth認証対応

## 更新履歴
- v1.0.0 (2025-01-27) - 初回リリース
  - Gmail API統合
  - EXE環境対応
  - ユーザー設定の外部保存