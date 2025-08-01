"""
Slack API連携モジュール
チャンネル作成、メンバー招待、メッセージ投稿機能
"""

import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SlackClient:
    """Slack API クライアント"""
    
    # Bot IDs
    TECHZIP_PDF_BOT_ID = "U098ADT46E4"  # TechZip PDF Bot（このBot自身）
    GITHUB_APP_ID = "UA8BZ8ENT"         # GitHub App (注意: cant_inviteエラーが発生中 - 要手動確認)
    
    # 技術の泉シリーズ招待Bot（TechZip Botとは別のBot）
    # 環境変数 SLACK_INVITATION_BOT_TOKEN から取得
    INVITATION_BOT_TOKEN = os.getenv("SLACK_INVITATION_BOT_TOKEN")  # "xoxb-..." 形式のBot Token
    
    # 管理チャンネル（-管理channel）
    ADMIN_CHANNEL_ID = "C0980EXAZD1"  # https://irdtechbooks.slack.com/archives/C0980EXAZD1
    
    def __init__(self, bot_token: str, user_token: str = None):
        """
        Args:
            bot_token: Slack Bot User OAuth Token (メッセージ投稿等用)
            user_token: Slack User OAuth Token (チャンネル作成用)
        """
        self.client = AsyncWebClient(token=bot_token)
        self.bot_token = bot_token
        
        # チャンネル作成用のユーザートークンクライアント
        self.user_token = user_token or os.getenv("SLACK_USER_TOKEN")
        if self.user_token:
            self.user_client = AsyncWebClient(token=self.user_token)
        else:
            self.user_client = self.client
    
    async def create_channel(self, channel_name: str, book_title: str = None) -> Optional[str]:
        """
        プライベートチャンネルを作成し、トピックと説明を設定
        
        Args:
            channel_name: チャンネル名（例: zn9999）
            book_title: 書籍名（トピックに設定）
            
        Returns:
            作成されたチャンネルのID、失敗時はNone
        """
        try:
            # チャンネル名の正規化（Slack制約: 小文字、21文字以内、特殊文字不可）
            channel_name = channel_name.lower().replace("_", "-")[:21]
            
            # プライベートチャンネルとして作成（User Tokenを使用）
            response = await self.user_client.conversations_create(
                name=channel_name,
                is_private=True  # プライベートチャンネル（必須要件）
            )
            
            channel_id = response["channel"]["id"]
            logger.info(f"Created private channel: {channel_name} ({channel_id})")
            
            # チャンネルのトピックと説明を設定
            await self._set_channel_topic_and_purpose(channel_id, book_title)
            
            return channel_id
            
        except SlackApiError as e:
            if e.response["error"] == "name_taken":
                # チャンネルが既に存在する場合
                logger.warning(f"Channel {channel_name} already exists")
                # 既存チャンネルのIDを取得
                existing_channel = await self._find_channel_by_name(channel_name)
                if existing_channel:
                    return existing_channel["id"]
            else:
                logger.error(f"Failed to create channel: {e.response['error']} - {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating channel: {e}")
            return None
    
    async def _set_channel_topic_and_purpose(self, channel_id: str, book_title: str = None):
        """
        チャンネルのトピックと説明を設定
        
        Args:
            channel_id: チャンネルID
            book_title: 書籍名（トピックに設定）
        """
        try:
            # トピックを設定（書籍名）
            if book_title:
                await self.user_client.conversations_setTopic(
                    channel=channel_id,
                    topic=book_title
                )
                logger.info(f"Set channel topic: {book_title}")
            
            # 説明（Purpose）を設定
            purpose_text = """入稿メモURL：入稿関係の注意点です。
https://docs.google.com/document/d/1WptR3TC-HRDoGf6brCTVLllj4WshzuzNC01f_xVPeQo/edit?usp=sharing"""
            
            await self.user_client.conversations_setPurpose(
                channel=channel_id,
                purpose=purpose_text
            )
            logger.info("Set channel purpose with 入稿メモURL")
            
        except SlackApiError as e:
            logger.warning(f"Failed to set channel topic/purpose: {e.response['error']} - {e}")
        except Exception as e:
            logger.warning(f"Unexpected error setting channel topic/purpose: {e}")
    
    async def post_workflow_guidance(self, channel_id: str, project_info: dict, manual_tasks: list = None, execution_summary: dict = None, sheet_id: str = None):
        """
        ワークフロー管理チャンネルに手動タスクとガイダンスを投稿
        
        Args:
            channel_id: 投稿先チャンネルID
            project_info: プロジェクト情報
            manual_tasks: 手動タスクリスト
            execution_summary: 実行結果サマリー
            sheet_id: 発行計画シートID（リンク生成用）
        """
        try:
            # 基本プロジェクト情報
            book_title = project_info.get("book_title", "不明")
            n_code = project_info.get("n_code", "不明")
            author_email = project_info.get("author_email", "不明")
            repository_name = project_info.get("repository_name", "不明")
            row_number = project_info.get("row_number", None)  # プロジェクトの行番号
            
            # 実行結果の詳細
            slack_created = execution_summary.get("slack_channel") is not None if execution_summary else False
            github_created = execution_summary.get("github_repo") is not None if execution_summary else False
            
            # メッセージ作成（山城敬へのメンション付き）
            message = f"""<@U7V83BLLB> 🚀 **プロジェクト初期化実行結果**: {book_title}

📋 **プロジェクト情報**
• Nコード: {n_code}
• 書籍名: {book_title}
• リポジトリ: {repository_name}
• 著者メール: {author_email}

⚙️ **実行結果サマリー**"""

            # 実行されたタスクの詳細表示
            if slack_created:
                slack_channel_name = execution_summary["slack_channel"]["name"]
                slack_channel_id = execution_summary["slack_channel"]["id"]
                message += f"\n✅ Slackチャンネル作成: <#{slack_channel_id}|{slack_channel_name}>"
                message += f"\n   └─ トピック: {book_title}" if book_title != "不明" else ""
                message += f"\n   └─ 説明: 入稿メモURL設定済み"
            else:
                message += "\n❌ Slackチャンネル作成: スキップ"
            
            if github_created:
                github_url = execution_summary["github_repo"]["html_url"]
                message += f"\n✅ GitHubリポジトリ作成: {github_url}"
                message += f"\n   └─ README.md生成済み"
            else:
                message += "\n❌ GitHubリポジトリ作成: スキップ"
            
            # Google Sheets更新
            if execution_summary and execution_summary.get("book_url_from_purchase"):
                message += f"\n✅ Google Sheets更新: 書籍URL転記完了"
            else:
                message += f"\n⚪ Google Sheets更新: 更新データなし"

            message += f"\n\n📝 **手動タスク**"
            if manual_tasks and len(manual_tasks) > 0:
                for task in manual_tasks:
                    if task["type"] == "slack_invitation":
                        if "user_id" in task:
                            # 既存ユーザーだが招待失敗
                            message += f"\n• [ ] 🔴 **重要**: {task['email']} (ID: {task['user_id']}) をSlackチャンネルに招待"
                        else:
                            # ユーザーが見つからない（新規招待必要）
                            message += f"\n• [ ] 🔴 **重要**: {task['email']} をSlackワークスペースに招待（新規ユーザー）"
                    elif task["type"] == "github_invitation":
                        # GitHubリポジトリへの招待失敗
                        message += f"\n• [ ] 🔴 **重要**: {task.get('github_username', task.get('email', '著者'))} をGitHubリポジトリに招待"
                    elif task["type"] == "github_app_invitation":
                        # GitHub App招待失敗 - 具体的なコマンド表示
                        channel_name = execution_summary.get("slack_channel", {}).get("name", "チャンネル") if execution_summary else "チャンネル"
                        repo_name = task.get("repository_name", "リポジトリ")
                        github_repo_url = execution_summary.get("github_repo", {}).get("html_url", "リポジトリURL") if execution_summary else "リポジトリURL"
                        author_email = project_info.get("author_email", "著者メール") if project_info else "著者メール"
                        message += f"\n• [ ] 🔴 **GitHub App設定が必要** (順番に実行):"
                        message += f"\n  **Step 1**: 📧 {author_email} でGitHub招待メールを確認・承認"
                        message += f"\n  **Step 2**: <#{execution_summary.get('slack_channel', {}).get('id', '')}|#{channel_name}> で実行:"
                        message += f"\n  ```/invite @GitHub```"
                        message += f"\n  **Step 3**: 同じチャンネルでリポジトリを購読:"
                        message += f"\n  ```/github subscribe irdtechbook/{repo_name}```"
                        message += f"\n  📋 リポジトリ: {github_repo_url}"
                    elif task["type"] == "sheet_update":
                        message += f"\n• [ ] {task['description']}"
                    else:
                        message += f"\n• [ ] {task.get('description', '手動タスク')}"
            else:
                # デバッグ用の詳細情報を追加
                logger.info(f"Manual tasks debug: manual_tasks={manual_tasks}, type={type(manual_tasks)}, len={len(manual_tasks) if manual_tasks else 'None'}")
                message += "\n• すべて自動完了しました ✨"
            
            message += f"""

🔗 **関連リンク**"""
            
            # 手動タスク管理シートリンク（最優先）
            if sheet_id:
                message += f"\n• 手動タスク管理シート: https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=1736405482"
                # 発行計画シートの該当行（Nコードセル）にリンク
                if row_number:
                    message += f"\n• 発行計画シート ({n_code}): https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=1669653070&range=A{row_number}"
                else:
                    message += f"\n• 発行計画シート: https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=1669653070"
            else:
                # デフォルトシートID
                message += f"\n• 手動タスク管理シート: https://docs.google.com/spreadsheets/d/17DKsMGQ6krbhY7GIcX0iaeN-y8HcGGVkXt3d4oOckyQ/edit#gid=1736405482"
                if row_number:
                    message += f"\n• 発行計画シート ({n_code}): https://docs.google.com/spreadsheets/d/17DKsMGQ6krbhY7GIcX0iaeN-y8HcGGVkXt3d4oOckyQ/edit#gid=1669653070&range=A{row_number}"
                else:
                    message += f"\n• 発行計画シート: https://docs.google.com/spreadsheets/d/17DKsMGQ6krbhY7GIcX0iaeN-y8HcGGVkXt3d4oOckyQ/edit#gid=1669653070"
            
            if slack_created:
                message += f"\n• プロジェクトチャンネル: <#{execution_summary['slack_channel']['id']}|{slack_channel_name}>"
            
            message += f"\n\n⏰ 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            # メッセージ投稿
            await self.client.chat_postMessage(
                channel=channel_id,
                text=message,
                unfurl_links=False
            )
            
            logger.info(f"Posted workflow guidance to channel {channel_id}")
            
        except SlackApiError as e:
            logger.error(f"Failed to post workflow guidance: {e.response['error']} - {e}")
        except Exception as e:
            logger.error(f"Unexpected error posting workflow guidance: {e}")
    
    async def find_workflow_channel(self) -> Optional[str]:
        """
        ワークフロー管理チャンネルを検索
        
        Returns:
            チャンネルID、見つからない場合はADMIN_CHANNEL_ID
        """
        workflow_channel_names = [
            "-管理channel",           # 指定された管理チャンネル
            "techzip-workflow",
            "workflow-management", 
            "project-management",
            "techbridge-workflow"
        ]
        
        try:
            response = await self.client.conversations_list(
                types="public_channel,private_channel",
                limit=1000
            )
            
            for channel in response["channels"]:
                if channel["name"] in workflow_channel_names:
                    logger.info(f"Found workflow channel: {channel['name']} ({channel['id']})")
                    return channel["id"]
            
            # 検索で見つからない場合は、指定された管理チャンネルIDを返す
            logger.info(f"Using default admin channel: {self.ADMIN_CHANNEL_ID}")
            return self.ADMIN_CHANNEL_ID
            
        except SlackApiError as e:
            logger.warning(f"Failed to find workflow channel: {e}")
            # エラーの場合も管理チャンネルIDを返す
            return self.ADMIN_CHANNEL_ID
    
    async def _find_channel_by_name(self, channel_name: str) -> Optional[Dict]:
        """
        チャンネル名でチャンネルを検索
        
        Args:
            channel_name: チャンネル名
            
        Returns:
            チャンネル情報、見つからない場合はNone
        """
        try:
            # プライベートチャンネルも含めて検索
            response = await self.client.conversations_list(
                types="public_channel,private_channel",
                limit=1000
            )
            
            for channel in response["channels"]:
                if channel["name"] == channel_name:
                    return channel
            
            return None
            
        except SlackApiError as e:
            logger.error(f"Failed to list channels: {e}")
            return None
    
    async def invite_github_app_with_bot_token(
        self, 
        channel_id: str,
        github_app_id: str = None,
        bot_token: str = None
    ) -> bool:
        """
        Bot Token を使用してGitHub Appを招待
        ChatGPTの推奨アプローチに基づく実装
        
        Args:
            channel_id: チャンネルID
            github_app_id: GitHub App ID（デフォルトはself.GITHUB_APP_ID）
            bot_token: 使用するBot Token（デフォルトは現在のbot_token）
            
        Returns:
            成功時True
        """
        github_app_id = github_app_id or self.GITHUB_APP_ID
        bot_token = bot_token or self.bot_token
        
        if not bot_token:
            logger.warning("Bot token not available for GitHub App invitation")
            return False
        
        try:
            # Bot Tokenクライアントでの招待（ChatGPT推奨方式）
            bot_client = AsyncWebClient(token=bot_token)
            
            # Bot自身の情報を取得（デバッグ用）
            try:
                auth_info = await bot_client.auth_test()
                logger.info(f"Bot invitation using: {auth_info.get('user')} (ID: {auth_info.get('user_id')})")
            except:
                pass
            
            await bot_client.conversations_invite(
                channel=channel_id,
                users=github_app_id
            )
            
            logger.info(f"Successfully invited GitHub App {github_app_id} using bot token")
            return True
            
        except SlackApiError as e:
            error_code = e.response.get('error', 'Unknown')
            logger.error(f"Bot token invitation failed: {error_code} - {e}")
            
            # ChatGPTの指摘に基づくエラー分析
            if error_code == "cant_invite":
                logger.info("cant_invite error - Bot may need to be a member of the private channel first")
            elif error_code == "not_in_channel":
                logger.info("not_in_channel error - Bot is not a member of the channel")
            
            return False
        except Exception as e:
            logger.error(f"Bot token invitation error: {e}")
            return False

    async def invite_github_app_with_alternative_bot(
        self, 
        channel_id: str,
        github_app_id: str = None
    ) -> bool:
        """
        別Bot（技術の泉シリーズ招待Bot）を使用してGitHub Appを招待
        
        Args:
            channel_id: チャンネルID
            github_app_id: GitHub App ID（デフォルトはself.GITHUB_APP_ID）
            
        Returns:
            成功時True
        """
        if not self.INVITATION_BOT_TOKEN:
            logger.warning("Alternative invitation bot token not available")
            return False
            
        # Bot Token方式での招待を試行
        return await self.invite_github_app_with_bot_token(
            channel_id=channel_id,
            github_app_id=github_app_id,
            bot_token=self.INVITATION_BOT_TOKEN
        )

    async def invite_user_to_channel(
        self, 
        channel_id: str, 
        user_id: str,
        use_user_token: bool = False
    ) -> bool:
        """
        ユーザーをチャンネルに招待
        
        Args:
            channel_id: チャンネルID
            user_id: ユーザーID（メンバーまたはBot）
            use_user_token: User Tokenを使用するかどうか（プライベートチャンネル招待時）
            
        Returns:
            成功時True
        """
        try:
            # プライベートチャンネルの場合はUser Tokenを使用
            client = self.user_client if use_user_token and self.user_client else self.client
            
            await client.conversations_invite(
                channel=channel_id,
                users=user_id
            )
            
            logger.info(f"Invited user {user_id} to channel {channel_id}")
            return True
            
        except SlackApiError as e:
            if e.response["error"] == "already_in_channel":
                logger.info(f"User {user_id} is already in channel {channel_id}")
                return True
            elif e.response["error"] == "cant_invite_self":
                logger.info(f"Cannot invite self (user {user_id}) - user is already channel creator")
                return True  # チャンネル作成者は既にメンバーなので成功とみなす
            elif e.response["error"] == "channel_not_found":
                logger.error(f"Channel {channel_id} not found when inviting user {user_id}")
                return False
            else:
                logger.error(f"Failed to invite user {user_id} to channel {channel_id}: {e.response['error']} - {e}")
                return False
    
    async def find_user_by_email(self, email: str) -> Optional[str]:
        """
        メールアドレスからユーザーIDを検索
        
        Args:
            email: メールアドレス
            
        Returns:
            ユーザーID、見つからない場合はNone
        """
        try:
            # users.lookupByEmailを使用（要users:read.emailスコープ）
            response = await self.client.users_lookupByEmail(email=email)
            
            if response["ok"]:
                user_id = response["user"]["id"]
                logger.info(f"Found user {user_id} for email {email}")
                return user_id
            
            return None
            
        except SlackApiError as e:
            if e.response["error"] == "users_not_found":
                logger.info(f"No user found for email: {email}")
            else:
                logger.error(f"Failed to lookup user by email: {e}")
            return None
    
    async def post_message(
        self, 
        channel_id: str, 
        text: str,
        thread_ts: Optional[str] = None,
        blocks: Optional[List[Dict]] = None
    ) -> Optional[str]:
        """
        メッセージを投稿
        
        Args:
            channel_id: チャンネルID
            text: メッセージテキスト
            thread_ts: スレッドのタイムスタンプ（スレッド返信の場合）
            blocks: Block Kit形式のリッチメッセージ
            
        Returns:
            投稿されたメッセージのタイムスタンプ、失敗時はNone
        """
        try:
            kwargs = {
                "channel": channel_id,
                "text": text
            }
            
            if thread_ts:
                kwargs["thread_ts"] = thread_ts
            
            if blocks:
                kwargs["blocks"] = blocks
            
            response = await self.client.chat_postMessage(**kwargs)
            
            timestamp = response["ts"]
            logger.info(f"Posted message to {channel_id}")
            
            return timestamp
            
        except SlackApiError as e:
            logger.error(f"Failed to post message: {e}")
            return None
    
    async def post_manual_task_notification(
        self,
        n_code: str,
        channel_name: str,
        task_type: str,
        details: str,
        task_id: str
    ) -> bool:
        """
        管理チャンネルに手動タスク通知を投稿
        
        Args:
            n_code: Nコード
            channel_name: 対象チャンネル名
            task_type: タスクタイプ（例: slack_invitation）
            details: タスクの詳細
            task_id: タスクID
            
        Returns:
            成功時True
        """
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🔔 手動タスクが必要です"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Nコード:*\n{n_code}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*チャンネル:*\n#{channel_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*タスク:*\n{task_type}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*タスクID:*\n{task_id}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*詳細:*\n{details}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ]
        
        text = f"手動タスク: {n_code} - {task_type}"
        
        ts = await self.post_message(
            self.ADMIN_CHANNEL_ID,
            text=text,
            blocks=blocks
        )
        
        return ts is not None
    
    async def setup_channel_with_members(
        self,
        channel_name: str,
        members: List[str],
        bots: List[str] = None
    ) -> Optional[str]:
        """
        チャンネルを作成してメンバーとBotを招待
        
        Args:
            channel_name: チャンネル名
            members: 招待するメンバーのユーザーID
            bots: 招待するBotのID（デフォルトでTechZip PDF Botを含む）
            
        Returns:
            作成されたチャンネルのID、失敗時はNone
        """
        # チャンネル作成
        channel_id = await self.create_channel(channel_name)
        if not channel_id:
            return None
        
        # デフォルトのBot
        if bots is None:
            bots = [self.TECHZIP_PDF_BOT_ID]
        
        # メンバー招待
        success_count = 0
        total_count = len(members) + len(bots)
        
        # 通常メンバーの招待
        for member_id in members:
            if await self.invite_user_to_channel(channel_id, member_id):
                success_count += 1
            else:
                logger.warning(f"Failed to invite member {member_id}")
        
        # Botの招待
        for bot_id in bots:
            if await self.invite_user_to_channel(channel_id, bot_id):
                success_count += 1
            else:
                logger.warning(f"Failed to invite bot {bot_id}")
        
        logger.info(f"Invited {success_count}/{total_count} users to channel {channel_name}")
        
        return channel_id
    
    async def _get_channel_info(self, channel_name: str) -> Optional[Dict[str, Any]]:
        """
        チャンネル情報を取得（存在確認用）
        
        Args:
            channel_name: チャンネル名（#なし）
            
        Returns:
            チャンネル情報辞書、見つからない場合はNone
        """
        try:
            # チャンネル一覧から検索
            response = await self.client.conversations_list(
                exclude_archived=True,
                types="private_channel,public_channel"
            )
            
            if response["ok"]:
                for channel in response["channels"]:
                    if channel["name"] == channel_name:
                        return channel
            
            return None
            
        except SlackApiError as e:
            logger.error(f"Failed to get channel info: {e}")
            return None
    
    def format_channel_name(self, n_code: str) -> str:
        """
        NコードからSlackチャンネル名を生成
        
        Args:
            n_code: Nコード（例: N09999）
            
        Returns:
            チャンネル名（例: zn9999）
        """
        # N09999 -> zn9999
        if n_code.upper().startswith("N"):
            number_part = n_code[1:].lstrip("0")
            return f"zn{number_part}"
        
        return n_code.lower()