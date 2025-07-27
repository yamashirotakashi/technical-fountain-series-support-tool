# プロジェクト初期化自動化 - 事前研究ドキュメント

最終更新: 2025-01-27

## 概要

技術の泉シリーズの新規プロジェクト開始時に必要なSlackチャネルとGitHubリポジトリの作成、設定、著者招待までの一連の作業を自動化する機能の実現可能性調査。

## 現在の手動作業フロー

1. **Slack/GitHub同名リソース作成**
   - プライベートSlackチャネル作成
   - GitHubリポジトリ作成（同じ名前）

2. **Slack設定**
   - チャネルトピック設定（定型文）
   - チャネル説明設定（定型文）
   - スター付きセクション指定
   - @github Bot招待
   - `/github subscribe owner/repo` コマンド実行

3. **GitHub設定**
   - Description: 書籍名を設定
   - README.md: 定型内容で自動生成

4. **著者招待**
   - Slack: メールアドレスで招待
   - GitHub: GitHubアカウントまたはメールで招待

## 自動化可能性の分析

### Slack側の自動化

| タスク | 自動化可否 | 使用API/方法 | 備考 |
|--------|------------|--------------|------|
| チャネル作成 | ✅ 可能 | `conversations.create` | is_private=true |
| トピック設定 | ✅ 可能 | `conversations.setTopic` | |
| 説明設定 | ✅ 可能 | `conversations.setPurpose` | |
| スター付きセクション | ❌ 不可 | API未提供 | ピン留めで代替可 |
| GitHub Bot招待 | ✅ 可能 | `conversations.invite` | Bot IDが必要 |
| /github subscribe | ⚠️ 制限付き | 以下参照 | |
| メール招待 | ⚠️ 制限付き | 以下参照 | |

#### /github subscribeの実行方法

1. **Webhook経由（推奨）**
   ```python
   # Incoming Webhookではなく、GitHub側でWebhook設定
   github_client.create_webhook(
       repo=repo_name,
       config={"url": slack_webhook_url}
   )
   ```

2. **Bot経由でコマンド送信**
   ```python
   # chat.postMessageでコマンドを送信（動作保証なし）
   slack_client.chat_postMessage(
       channel=channel_id,
       text="/github subscribe owner/repo"
   )
   ```

#### メール招待（無料プラン）

```python
# 招待リンク生成
response = slack_client.conversations_inviteShared(
    channel=channel_id,
    emails=["author@example.com"]
)
invite_link = response['invite_link']
# メール送信は別途実装
```

### GitHub側の自動化

| タスク | 自動化可否 | 使用API | 備考 |
|--------|------------|---------|------|
| リポジトリ作成 | ✅ 可能 | `POST /user/repos` | |
| Description設定 | ✅ 可能 | 作成時パラメータ | |
| README生成 | ✅ 可能 | `PUT /repos/{owner}/{repo}/contents/README.md` | |
| ユーザー招待 | ✅ 可能 | `PUT /repos/{owner}/{repo}/collaborators/{username}` | |
| メール招待 | ❌ 不可 | GitHubユーザー名必須 | 事前マッピング必要 |

### 実装例

```python
import os
from slack_sdk import WebClient
from github import Github
import base64

class ProjectInitializer:
    def __init__(self, slack_token, github_token):
        self.slack = WebClient(token=slack_token)
        self.github = Github(github_token)
        
    def create_project(self, project_config):
        """
        project_config = {
            "name": "N12345-book-title",
            "book_title": "素晴らしい技術書",
            "authors": [
                {"email": "author@example.com", "github": "author_username"}
            ],
            "topic_template": "📚 {book_title} の編集チャネル",
            "purpose_template": "執筆・編集・校正の作業場所"
        }
        """
        # 1. Slackチャネル作成
        channel = self._create_slack_channel(project_config)
        
        # 2. GitHubリポジトリ作成
        repo = self._create_github_repo(project_config)
        
        # 3. 連携設定
        self._setup_integration(channel, repo)
        
        # 4. 著者招待
        self._invite_authors(channel, repo, project_config["authors"])
        
    def _create_slack_channel(self, config):
        # チャネル作成
        response = self.slack.conversations_create(
            name=config["name"],
            is_private=True
        )
        channel_id = response["channel"]["id"]
        
        # トピック・説明設定
        self.slack.conversations_setTopic(
            channel=channel_id,
            topic=config["topic_template"].format(book_title=config["book_title"])
        )
        self.slack.conversations_setPurpose(
            channel=channel_id,
            purpose=config["purpose_template"]
        )
        
        # 初回メッセージ（スター付きセクションの代替）
        message = self.slack.chat_postMessage(
            channel=channel_id,
            text="📌 重要情報\n• GitHub: https://github.com/owner/{}\n• 書籍名: {}".format(
                config["name"], config["book_title"]
            )
        )
        # ピン留め
        self.slack.pins_add(
            channel=channel_id,
            timestamp=message["ts"]
        )
        
        return channel_id
        
    def _create_github_repo(self, config):
        # リポジトリ作成
        user = self.github.get_user()
        repo = user.create_repo(
            name=config["name"],
            description=config["book_title"],
            private=True,
            auto_init=False
        )
        
        # README作成
        readme_content = f"""# {config["book_title"]}

技術の泉シリーズ 執筆プロジェクト

## 概要
{config["book_title"]}の原稿管理リポジトリです。

## ディレクトリ構成
```
├── manuscripts/    # 原稿ファイル
├── images/        # 画像ファイル
├── reviews/       # レビューコメント
└── outputs/       # 組版結果
```

## 執筆ルール
1. ファイル形式: Markdown (.md)
2. 文字コード: UTF-8
3. 改行コード: LF

## Slack連携
Slackチャネル: #{config["name"]}
"""
        repo.create_file(
            "README.md",
            "Initial commit: プロジェクト開始",
            readme_content
        )
        
        return repo
```

## 自動化の制約と解決策

### 制約事項

1. **スター付きセクション**
   - Slack APIで未対応
   - 解決策: 重要メッセージのピン留めで代替

2. **Slashコマンド実行**
   - Bot経由での実行は不確実
   - 解決策: GitHub Webhookを直接設定

3. **メールアドレスからの招待**
   - Slack無料プラン: 招待リンク生成＋メール送信
   - GitHub: ユーザー名が必須（メールマッピング管理必要）

4. **権限要件**
   - Slack: 管理者権限のUser Token
   - GitHub: Personal Access Token (repo, admin:org権限)

### 推奨アーキテクチャ

```
TechZip GUI
    ↓
Project Initializer
    ├── Slack Manager
    │   ├── Channel Creator
    │   ├── Settings Configurator
    │   └── Invitation Handler
    ├── GitHub Manager
    │   ├── Repository Creator
    │   ├── README Generator
    │   └── Collaborator Manager
    └── Integration Manager
        ├── GitHub App Setup
        └── Webhook Configurator
```

## 実装ロードマップ

### Phase 1: 基本機能（1-2週間）
- Slack/GitHubリポジトリ作成
- 基本設定（トピック、説明、README）
- 手動確認ポイントの明確化

### Phase 2: 連携機能（1週間）
- GitHub Bot招待
- Webhook設定
- 招待リンク生成

### Phase 3: 完全自動化（1週間）
- 著者情報管理システム
- メール送信統合
- エラーハンドリング強化

## 期待される効果

- **作業時間**: 30分 → 2-3分（93%削減）
- **自動化率**: 約85%（スター付きセクション以外）
- **ヒューマンエラー**: 大幅削減
- **標準化**: 全プロジェクトで統一された構成

## セキュリティ考慮事項

1. **トークン管理**
   - 環境変数または暗号化設定
   - 最小権限の原則

2. **アクセス制御**
   - プライベートチャネル/リポジトリ
   - 招待者の検証

3. **ログ記録**
   - 全操作の監査ログ
   - エラー時の詳細記録

## 次のステップ

1. プロトタイプ実装（Slack/GitHub個別）
2. 統合テスト環境構築
3. UI設計（プロジェクト設定画面）
4. 本番環境での試験運用