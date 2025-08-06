# Slack統合機能 - 事前研究ドキュメント

最終更新: 2025-01-27

## 概要

技術の泉シリーズ制作支援ツール（TechZip）において、Nフォルダに生成された組版PDFを編集環境であるSlackチャネルに自動投稿する機能の実装に向けた事前研究。

## 要件定義

### 基本要件
- **目的**: Nフォルダの組版済みPDFをSlackチャネルに定型文と共に自動投稿
- **チャネル命名規則**: チャネル名 = リポジトリ名
- **チャネル種別**: 全てプライベートチャネル
- **環境**: Slack無料プラン（ワークスペース管理者権限あり）

## 技術調査結果

### 1. チャネル名からチャネルIDの逆引き

**結論: 可能**

Slack Web APIの`conversations.list`を使用してチャネル名からチャネルIDを取得可能。

```python
def get_channel_id_by_name(channel_name):
    response = slack_client.conversations_list(types="private_channel")
    for channel in response['channels']:
        if channel['name'] == channel_name:
            return channel['id']
    return None
```

### 2. Bot設定と権限要件

**必要な手順:**

1. **Slack App作成**
   - https://api.slack.com/apps でアプリ作成
   - Bot User OAuth Tokenの取得

2. **必要なOAuth Scopes**
   - `groups:read` - プライベートチャネル一覧取得
   - `groups:write` - プライベートチャネルへの投稿
   - `chat:write` - メッセージ投稿
   - `files:write` - PDFファイルアップロード
   - `users:read` - ユーザー情報取得（Bot ID確認用）

3. **制約事項**
   - Botは各プライベートチャネルに招待される必要がある
   - ファイルサイズ制限: 1GB
   - Rate Limit: Tier 3（50+ requests/minute）

### 3. Botの一括チャネル登録方法

**管理者権限を活用した効率的な方法:**

#### 方法1: Slack CLI使用（推奨）

```bash
# Slack CLI インストール
curl -fsSL https://downloads.slack-edge.com/slack-cli/install.sh | bash

# 認証
slack login

# Bot ID確認
slack users list | grep "bot-name"

# 一括招待（PowerShell）
$bot_id = "U1234567890"
slack conversations list --types private_channel | ForEach-Object {
    slack conversations invite --channel $_.id --users $bot_id
}
```

#### 方法2: Python + 管理者トークン

```python
from slack_sdk import WebClient
import time

USER_TOKEN = "xoxp-admin-token"  # 管理者のUser OAuth Token
BOT_USER_ID = "U1234567890"      # Bot User ID

client = WebClient(token=USER_TOKEN)

# プライベートチャネル一覧取得
channels = client.conversations_list(types="private_channel", limit=1000)

# 各チャネルにBotを招待
for channel in channels['channels']:
    try:
        client.conversations_invite(
            channel=channel['id'],
            users=BOT_USER_ID
        )
        print(f"✓ Added to: {channel['name']}")
        time.sleep(1)  # Rate limit対策
    except Exception as e:
        print(f"✗ Failed for {channel['name']}: {e}")
```

### 4. Bot招待の仕様

**重要な確認事項:**
- Bot招待 = 即座に参加完了（承認プロセスなし）
- `conversations.invite` API実行後、すぐにメッセージ投稿可能
- 既にメンバーの場合は`already_in_channel`エラー

## 実装設計案

### アーキテクチャ

```
TechZip GUI
    ↓
Slack Integration Module
    ├── Channel Resolver (チャネル名→ID変換)
    ├── File Uploader (PDF投稿)
    └── Message Composer (定型文生成)
```

### 実装フロー

1. **初期設定フェーズ**
   - Slack App作成・トークン取得
   - 管理者権限でBotを全チャネルに一括登録
   - 設定ファイルにトークン保存

2. **運用フェーズ**
   ```python
   def post_to_slack(repo_name, pdf_path, message_template):
       # 1. チャネル名からID取得
       channel_id = get_channel_id_by_name(repo_name)
       
       # 2. PDFアップロード
       response = slack_client.files_upload(
           channels=channel_id,
           file=pdf_path,
           initial_comment=message_template
       )
       
       return response
   ```

### セキュリティ考慮事項

1. **トークン管理**
   - Bot Token: 環境変数または暗号化設定ファイル
   - User Token: 初期設定時のみ使用、保存しない

2. **エラーハンドリング**
   - チャネル不在
   - Bot未参加
   - ファイルサイズ超過
   - Rate Limit

### 次のステップ

1. Slack App作成とトークン取得
2. Bot一括登録スクリプトの実行
3. TechZipへのSlack統合モジュール実装
4. 設定UIの追加
5. テストとエラーハンドリング強化

## 参考資料

- [Slack Web API Documentation](https://api.slack.com/web)
- [Slack App OAuth Scopes](https://api.slack.com/scopes)
- [Slack CLI Documentation](https://api.slack.com/automation/cli)
- [slack-sdk Python Library](https://slack.dev/python-slack-sdk/)