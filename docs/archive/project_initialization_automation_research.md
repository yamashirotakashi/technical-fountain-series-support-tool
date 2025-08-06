# プロジェクト初期化自動化 - 実装仕様書

最終更新: 2025-01-27

## 概要

技術の泉シリーズの新規プロジェクト開始時に必要なSlackチャネルとGitHubリポジトリの作成、設定、著者招待までの一連の作業を自動化する機能の実装仕様。

## 実装要件

### 必要な通知
- **GitHub → Slack**: Push と Issue のみ（PR等は不要）

### 著者管理
- GitHubアカウントが既知の場合のみ初期招待
- 不明な場合は後から手動招待（現状の運用を踏襲）

### アカウント要件
- **Slack**: 管理者権限（現在のチャネル作成者）を維持
- **GitHub**: irdtechbook組織での作成権限

## 現在の手動作業フロー

1. **Slack/GitHub同名リソース作成**
   - プライベートSlackチャネル作成（管理者が作成）
   - GitHubリポジトリ作成（irdtechbook組織、同じ名前）

2. **Slack設定**
   - チャネルトピック設定（定型文）
   - チャネル説明設定（定型文）
   - スター付きセクション指定
   - 既存のPDF投稿Bot招待
   - GitHub連携設定

3. **GitHub設定**
   - Description: 書籍名を設定
   - README.md: 定型内容で自動生成
   - Issue機能有効化

4. **著者招待**
   - Slack: メールアドレスで招待
   - GitHub: 既知のGitHubアカウントのみ招待

## 実装アーキテクチャ

### Bot統合設計
Phase 1で作成するPDF投稿Botを流用・拡張して以下の機能を追加：

```python
# 必要なOAuth Scopes
OAuth Scopes:
- files:write       # PDF投稿
- chat:write        # メッセージ投稿
- groups:read       # プライベートチャネル読取
- groups:write      # チャネル作成・設定（プロジェクト初期化用）
- incoming-webhook  # GitHub通知受信
```

### トークン管理

```python
class TokenManager:
    def __init__(self):
        # PDF投稿Botトークン（Phase 1で作成済み）
        self.bot_token = os.environ['SLACK_BOT_TOKEN']
        # 管理者User Token（チャネル作成用）
        self.admin_token = os.environ['SLACK_ADMIN_TOKEN']
        # irdtechbook組織のGitHub PAT
        self.github_pat = os.environ['GITHUB_ORG_PAT']
```

### 実装詳細

```python
from slack_sdk import WebClient
from github import Github
import os
import time

class TechZipProjectInitializer:
    def __init__(self):
        self.slack_bot = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
        self.slack_admin = WebClient(token=os.environ['SLACK_ADMIN_TOKEN'])
        self.github = Github(os.environ['GITHUB_ORG_PAT'])
        self.org = self.github.get_organization("irdtechbook")
        
    def create_project(self, config):
        """
        config = {
            "name": "N12345-book-title",
            "book_title": "素晴らしい技術書",
            "authors": [
                {"email": "author@example.com", "github": "author_username"},
                {"email": "author2@example.com", "github": None}  # GitHub不明
            ]
        }
        """
        try:
            # 1. Slackチャネル作成（管理者権限で）
            channel = self._create_slack_channel(config)
            
            # 2. GitHubリポジトリ作成（irdtechbook組織）
            repo = self._create_github_repository(config)
            
            # 3. GitHub-Slack連携設定（Push/Issueのみ）
            self._setup_github_webhook(repo, channel['id'])
            
            # 4. 既知の著者のみ招待
            self._invite_known_authors(channel, repo, config['authors'])
            
            return {
                "success": True,
                "channel_id": channel['id'],
                "repo_url": repo.html_url,
                "invited_authors": self._get_invited_count(config['authors'])
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_slack_channel(self, config):
        """管理者権限でチャネル作成"""
        # チャネル作成（管理者トークン使用）
        response = self.slack_admin.conversations_create(
            name=config["name"],
            is_private=True
        )
        channel_id = response["channel"]["id"]
        
        # トピック・説明設定
        self.slack_admin.conversations_setTopic(
            channel=channel_id,
            topic=f"📚 {config['book_title']} の編集チャネル"
        )
        self.slack_admin.conversations_setPurpose(
            channel=channel_id,
            purpose="執筆・編集・校正の作業場所"
        )
        
        # PDF投稿Botを招待
        self.slack_admin.conversations_invite(
            channel=channel_id,
            users=os.environ['SLACK_BOT_USER_ID']  # PDF投稿BotのユーザーID
        )
        
        # 重要情報をピン留め（スター付きセクションの代替）
        message = self.slack_bot.chat_postMessage(
            channel=channel_id,
            text=f"📌 重要情報\n"
                 f"• GitHub: https://github.com/irdtechbook/{config['name']}\n"
                 f"• 書籍名: {config['book_title']}\n"
                 f"• PDF投稿: Nフォルダの組版結果を自動投稿します"
        )
        self.slack_bot.pins_add(
            channel=channel_id,
            timestamp=message["ts"]
        )
        
        return response["channel"]
    
    def _create_github_repository(self, config):
        """irdtechbook組織でリポジトリ作成"""
        repo = self.org.create_repo(
            name=config["name"],
            description=config["book_title"],
            private=True,
            has_issues=True,  # Issue機能有効
            has_wiki=False,
            has_downloads=False
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

## Issue管理
バグ報告や改善提案はIssueに登録してください。
"""
        repo.create_file(
            "README.md",
            "Initial commit: プロジェクト開始",
            readme_content
        )
        
        return repo
    
    def _setup_github_webhook(self, repo, channel_id):
        """GitHub Webhook設定（Push/Issueのみ）"""
        # Slackチャネル用のWebhook URL取得
        webhook_url = self._get_or_create_webhook_url(channel_id)
        
        # GitHub Webhookを設定
        repo.create_hook(
            name="web",
            config={
                "url": webhook_url,
                "content_type": "json",
                "insecure_ssl": "0"
            },
            events=["push", "issues"],  # 必要なイベントのみ
            active=True
        )
        
    def _invite_known_authors(self, channel, repo, authors):
        """既知の著者のみ招待"""
        for author in authors:
            # Slack招待（メールアドレスは必須）
            if author.get("email"):
                try:
                    self.slack_admin.conversations_inviteShared(
                        channel=channel["id"],
                        emails=[author["email"]]
                    )
                except Exception as e:
                    print(f"Slack招待エラー ({author['email']}): {e}")
            
            # GitHub招待（ユーザー名が既知の場合のみ）
            if author.get("github"):
                try:
                    repo.add_to_collaborators(
                        author["github"],
                        permission="push"
                    )
                except Exception as e:
                    print(f"GitHub招待エラー ({author['github']}): {e}")
```

## GUI統合

TechZipのGUIに「プロジェクト初期化」メニューを追加：

```python
# main_window.py への追加
def init_project_menu(self):
    """プロジェクト初期化メニュー"""
    project_menu = self.menuBar().addMenu("プロジェクト")
    
    init_action = QAction("新規プロジェクト作成", self)
    init_action.triggered.connect(self.show_project_init_dialog)
    project_menu.addAction(init_action)

def show_project_init_dialog(self):
    """プロジェクト初期化ダイアログ表示"""
    dialog = ProjectInitDialog(self)
    if dialog.exec_():
        config = dialog.get_config()
        self.init_project(config)
```

## エラーハンドリング

```python
class ProjectInitError(Exception):
    """プロジェクト初期化エラー"""
    pass

def handle_init_error(self, error):
    """エラー処理とロールバック"""
    if isinstance(error, SlackError):
        # Slackチャネル作成失敗
        QMessageBox.critical(self, "エラー", 
            f"Slackチャネル作成に失敗しました: {error}")
    elif isinstance(error, GithubException):
        # GitHubリポジトリ作成失敗
        # 作成済みのSlackチャネルの処理を検討
        pass
```

## セキュリティ考慮事項

1. **トークン管理**
   - 環境変数でトークン管理
   - GUI設定画面でのトークン暗号化保存
   - 最小権限の原則

2. **アクセス制御**
   - プライベートチャネル/リポジトリのみ
   - 招待者の事前検証

3. **監査ログ**
   - 全操作をログファイルに記録
   - エラー発生時の詳細情報保存

## 実装ロードマップ

### Phase 1: 基本実装（1週間）
- [ ] ProjectInitializerクラス実装
- [ ] Slack/GitHub個別テスト
- [ ] エラーハンドリング基本実装

### Phase 2: GUI統合（3日）
- [ ] プロジェクト初期化ダイアログ
- [ ] 設定管理画面
- [ ] 進捗表示

### Phase 3: 本番投入（3日）
- [ ] 新規PDF投稿Botの作成と設定
- [ ] 本番環境でのテスト
- [ ] ドキュメント作成

## 期待される効果

- **作業時間**: 30分 → 2-3分（93%削減）
- **自動化率**: 約85%
- **ヒューマンエラー**: 大幅削減
- **標準化**: 全プロジェクトで統一された構成