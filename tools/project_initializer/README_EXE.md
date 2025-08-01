# 技術の泉シリーズプロジェクト初期化ツール - EXE版

## 概要
技術の泉シリーズの編集プロジェクト初期化を自動化するWindowsネイティブアプリケーションです。

## 機能
- ✅ Google Sheetsからプロジェクト情報を自動取得
- ✅ Slackプライベートチャンネルの自動作成・メンバー招待
- ✅ GitHubリポジトリの自動作成・設定
- ✅ 原稿執筆ガイドライン準拠のREADME.md生成
- ✅ 書籍タイトルの自動設定
- ✅ 包括的エラーハンドリング

## システム要件
- Windows 10/11 (64-bit)
- インターネット接続
- 必要なAPI権限（Slack、GitHub、Google Sheets）

## EXE化手順

### 1. 依存関係のインストール
```powershell
# PowerShell実行ポリシーの設定（初回のみ）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 依存関係のインストール
.\build_exe.ps1 -InstallDeps
```

### 2. EXE化の実行
```powershell
# 通常ビルド
.\build_exe.ps1

# クリーンビルド（推奨）
.\build_exe.ps1 -Clean
```

### 3. ビルド結果
- 出力先: `dist/TechBridge_ProjectInitializer/`
- 実行ファイル: `TechBridge_ProjectInitializer.exe`
- フォルダ方式で高速起動対応

## 配布・インストール

### 配布パッケージの作成
1. `dist/TechBridge_ProjectInitializer/` フォルダ全体をZIP圧縮
2. ユーザーに配布

### エンドユーザーでのインストール
1. ZIPファイルを任意のフォルダに展開
2. 環境変数ファイルの設定:
   ```
   # .env.template を .env にリネーム
   # 必要なAPIトークンを設定
   ```
3. `TechBridge_ProjectInitializer.exe` を実行

## 設定ファイル

### 環境変数ファイル (.env)
```bash
# Slack API設定
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_USER_TOKEN=xoxp-your-user-token-here

# GitHub API設定  
GITHUB_ORG_TOKEN=ghp_your-github-token-here
```

### Google Service Account設定
- `config/service_account.json` ファイルを配置
- Google Sheets APIの認証に使用

## トラブルシューティング

### よくあるエラー

#### 1. アプリケーションが起動しない
```
原因: 必要なランタイムが不足
解決: Microsoft Visual C++ Redistributable をインストール
```

#### 2. API接続エラー
```
原因: 環境変数が設定されていない
解決: .env ファイルの設定を確認
```

#### 3. Google Sheets接続エラー
```
原因: service_account.json が見つからない
解決: config/service_account.json を配置
```

### デバッグモード
```powershell
# コンソール出力を確認してデバッグ
TechBridge_ProjectInitializer.exe
```

## 開発者向け情報

### ビルド最適化オプション
```powershell
# UPX圧縮を無効化（起動速度優先）
pyinstaller --noupx build_exe.spec

# デバッグ版ビルド
pyinstaller --debug=all build_exe.spec
```

### フォルダ構成
```
dist/TechBridge_ProjectInitializer/
├── TechBridge_ProjectInitializer.exe  # メイン実行ファイル
├── _internal/                         # PyInstallerランタイム
├── config/                           # 設定ファイル（オプション）
└── .env                             # 環境変数（ユーザー設定）
```

### カスタマイズ
- `main_exe.py`: エントリーポイント
- `build_exe.spec`: PyInstaller設定
- `build_exe.ps1`: ビルドスクリプト

## ライセンス
技術の泉シリーズプロジェクト用内部ツール

## 更新履歴
- v1.0.0: 初回リリース
  - Google Sheets連携
  - Slack自動チャンネル作成
  - GitHub自動リポジトリ作成
  - フォルダ方式EXE化対応