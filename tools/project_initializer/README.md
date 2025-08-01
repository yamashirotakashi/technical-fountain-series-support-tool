# 技術の泉シリーズプロジェクト初期化ツール

技術の泉シリーズの新規プロジェクト初期化を自動化するQt6ベースのGUIアプリケーション。

## 概要

このツールは以下の処理を自動化します：

1. **Google Sheets連携**
   - 発行計画シートからプロジェクト情報を取得
   - 購入リストから書籍URLを取得
   - 手動タスク管理シートへの記録

2. **Slack連携**
   - プロジェクト専用チャンネルの作成
   - 編集者とBotの自動招待
   - 著者の招待（既存ユーザー/メール招待）

3. **GitHub連携**
   - irdtechbook組織でのリポジトリ作成
   - 著者のコラボレーター招待
   - 初期ファイル（README.md、.gitignore）の作成

## 機能

### 自動化される処理
- ✅ Nコードからプロジェクト情報の自動取得
- ✅ Slackチャンネル作成（命名規則: `zn[ncode]`）
- ✅ GitHub プライベートリポジトリ作成
- ✅ 関係者の自動招待
- ✅ Google Sheets の自動更新
- ✅ 手動タスクの管理シートへの記録

### 手動対応が必要な場合
- 新規著者のワークスペース招待
- GitHub アカウントが不明な場合のコラボレーター招待
- メールアドレスでのSlack招待

## セットアップ

### 必要な環境
- Python 3.12+
- Qt6 (Windows環境で実行時)
- Google Sheets API アクセス
- Slack Bot Token
- GitHub Organization Token

### インストール

1. **仮想環境の作成**
```bash
python -m venv venv
source venv/bin/activate  # Linux/WSL
# または
.\venv\Scripts\activate   # Windows
```

2. **依存関係のインストール**
```bash
pip install -r requirements.txt
```

3. **設定ファイルの配置**
- `config/service_account.json` - Google Sheets API サービスアカウント
- `.env` - API トークン設定

### 環境変数設定（.env）

```env
# Slack Bot Token
SLACK_BOT_TOKEN=xoxb-...

# GitHub Organization Token
GITHUB_ORG_TOKEN=ghp_...

# Google Sheets IDs
PLANNING_SHEET_ID=17DKsMGQ6krbhY7GIcX0iaeN-y8HcGGVkXt3d4oOckyQ
PURCHASE_SHEET_ID=1JJ_C3z0txlJWiyEDl0c6OoVD5Ym_IoZJMMf5o76oV4c
```

## 使用方法

### GUI版
```bash
python run.py
```

### バックエンドテスト
```bash
python test_backend.py
```

### 基本的な使用手順

1. **Nコード入力**: 処理したいNコード（例: N09999）を入力
2. **情報確認**: 「情報確認」ボタンでGoogle Sheetsからデータを取得
3. **オプション選択**: 
   - Slackチャンネル作成
   - GitHubリポジトリ作成  
   - Google Sheets更新
4. **実行**: 「プロジェクト初期化実行」ボタンで処理開始

## 技術仕様

### アーキテクチャ
- **フロントエンド**: PyQt6 (タブベースUI)
- **バックエンド**: 非同期処理 (asyncio + asyncqt)
- **API連携**: aiohttp ベースの非同期クライアント

### 主要コンポーネント
- `main_window.py` - Qt6 GUI メインウィンドウ
- `google_sheets.py` - Google Sheets API クライアント
- `slack_client.py` - Slack Web API クライアント  
- `github_client.py` - GitHub API クライアント
- `test_backend.py` - バックエンド機能テスト

### データフロー
```
Nコード入力 → Google Sheets検索 → プロジェクト情報取得
                     ↓
        並行実行: Slack + GitHub + Sheets更新
                     ↓
            結果表示 + 手動タスク通知
```

## 設定

### Bot/API 設定情報

#### Slack Bot 設定
- **Bot名**: TechZip PDF Bot
- **Bot ID**: U098ADT46E4
- **ワークスペース**: 技術の泉シリーズ (irdtechbooks)
- **必要スコープ**: 
  - `channels:write`
  - `channels:read` 
  - `users:read`
  - `users:read.email`

#### GitHub 設定
- **組織**: irdtechbook
- **必要権限**: リポジトリ作成、コラボレーター管理

#### Google Sheets 設定
- **発行計画シート**: 17DKsMGQ6krbhY7GIcX0iaeN-y8HcGGVkXt3d4oOckyQ
- **購入リストシート**: 1JJ_C3z0txlJWiyEDl0c6OoVD5Ym_IoZJMMf5o76oV4c
- **サービスアカウント**: techbook-analyzer-local-dev@techbook-analytics.iam.gserviceaccount.com

### 固定設定値
- **管理チャンネル**: C0980EXAZD1
- **デフォルト編集者**: U7V83BLLB (山城敬)
- **GitHub組織**: irdtechbook

## EXE化 (Windows用)

```bash
pyinstaller --onefile --windowed --add-data "config;config" run.py
```

## トラブルシューティング

### よくある問題

1. **Qt6が見つからない (WSL環境)**
   - WSLではGUIテストが困難
   - `test_backend.py` でバックエンド機能を確認

2. **Google Sheets権限エラー**
   - サービスアカウントにシート共有権限を確認
   - Google Sheets API有効化を確認

3. **Slack Bot権限不足**
   - Bot Token の有効性確認
   - 必要スコープの付与確認

4. **GitHub 404エラー**
   - Organization Token の権限確認
   - irdtechbook組織へのアクセス権確認

## 開発

### テスト実行
```bash
# バックエンド機能すべてをテスト
python test_backend.py

# 個別テスト (手動)
python -c "from test_backend import test_google_sheets; import asyncio; asyncio.run(test_google_sheets())"
```

### デバッグ
- ログレベル: INFO
- エラーハンドリング: 各API クライアントで例外キャッチ
- 進捗表示: Qt Progress Bar + Status Bar

## ライセンス

内部ツールのため、ライセンス制限なし。

## 更新履歴

- **v1.0.0** (2025-07-30): 初期リリース
  - Qt6 GUI実装
  - 三大API統合 (Google Sheets, Slack, GitHub)
  - 非同期処理対応
  - 手動タスク管理機能