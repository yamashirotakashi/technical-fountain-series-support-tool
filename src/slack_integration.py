#!/usr/bin/env python3
"""
Slack統合モジュール

TechZipからSlackチャネルへのPDF投稿機能を提供
"""
import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# パス解決と環境変数管理をインポート
from utils.path_resolver import PathResolver
from utils.env_manager import EnvManager

logger = logging.getLogger(__name__)

# cryptographyは暗号化機能を使用する場合のみ必要
try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    logger.warning("cryptography module not available - token encryption disabled")


class SlackIntegration:
    """Slack統合クラス"""
    
    def __init__(self, bot_token: Optional[str] = None):
        """
        Slack統合の初期化
        
        Args:
            bot_token: Slack Bot Token（省略時は環境変数から取得）
        """
        # EnvManagerを使用してトークンを取得
        self.bot_token = bot_token or EnvManager.get('SLACK_BOT_TOKEN')
        self.client = None
        self._channel_cache = {}  # チャネル名→IDのキャッシュ
        self._load_channel_cache()
        self._init_client()
    
    def _init_client(self):
        """Slackクライアントの初期化"""
        if self.bot_token:
            self.client = WebClient(token=self.bot_token)
            logger.info("Slack client initialized")
        else:
            logger.warning("No bot token provided. Set SLACK_BOT_TOKEN in .env file or environment variables.")
    
    def _load_channel_cache(self):
        """チャネルキャッシュを読み込み"""
        cache_file = PathResolver.get_config_path() / 'slack_channel_cache.json'
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self._channel_cache = json.load(f)
                logger.debug(f"Loaded channel cache with {len(self._channel_cache)} entries")
            except Exception as e:
                logger.warning(f"Failed to load channel cache: {e}")
    
    def _save_channel_cache(self):
        """チャネルキャッシュを保存"""
        cache_file = PathResolver.get_config_path() / 'slack_channel_cache.json'
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._channel_cache, f, indent=2)
            logger.debug("Saved channel cache")
        except Exception as e:
            logger.warning(f"Failed to save channel cache: {e}")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Slack接続テスト
        
        Returns:
            接続結果の辞書
        """
        if not self.client:
            return {
                "success": False,
                "error": "Bot token not configured"
            }
        
        try:
            # 認証テスト
            response = self.client.auth_test()
            
            return {
                "success": True,
                "team": response["team"],
                "user": response["user"],
                "bot_id": response["user_id"]
            }
            
        except SlackApiError as e:
            logger.error(f"Slack connection test failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_channel_id_by_name(self, channel_name: str) -> Optional[str]:
        """
        チャネル名からチャネルIDを取得
        
        Args:
            channel_name: チャネル名（#は不要）
            
        Returns:
            チャネルID（見つからない場合はNone）
        """
        # キャッシュチェック
        if channel_name in self._channel_cache:
            return self._channel_cache[channel_name]
        
        if not self.client:
            logger.error("Slack client not initialized")
            return None
        
        try:
            # プライベートチャネル一覧を取得
            response = self.client.conversations_list(
                types="private_channel",
                limit=1000
            )
            
            # チャネル名で検索
            for channel in response.get('channels', []):
                if channel['name'] == channel_name:
                    channel_id = channel['id']
                    self._channel_cache[channel_name] = channel_id
                    self._save_channel_cache()  # キャッシュを保存
                    logger.info(f"Found channel: {channel_name} -> {channel_id}")
                    return channel_id
            
            logger.warning(f"Channel not found: {channel_name}")
            return None
            
        except SlackApiError as e:
            logger.error(f"Failed to get channel list: {e}")
            return None
    
    def post_pdf_to_channel(
        self,
        pdf_path: str,
        repo_name: str,
        message_template: Optional[str] = None,
        book_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        PDFをSlackチャネルに投稿
        
        Args:
            pdf_path: PDFファイルのパス
            repo_name: リポジトリ名（=チャネル名）
            message_template: メッセージテンプレート
            book_title: 書籍タイトル
            
        Returns:
            投稿結果の辞書
        """
        if not self.client:
            return {
                "success": False,
                "error": "Slack client not initialized",
                "action_required": "Bot Token設定が必要です"
            }
        
        # チャネルIDを取得
        channel_id = self.get_channel_id_by_name(repo_name)
        if not channel_id:
            # チャネルが見つからない = Botが参加していない
            invite_instruction = f"""
チャネル #{repo_name} が見つかりません。

【対処方法】
1. Slackで #{repo_name} チャネルを開く
2. チャネル名をクリック → 「メンバーを追加」
3. @techzip_pdf_bot を検索して追加
4. 追加完了後、もう一度PDF生成を実行

※プライベートチャネルの場合、Botを招待しないと投稿できません
"""
            return {
                "success": False,
                "error": f"Channel '{repo_name}' not found",
                "action_required": "Bot招待が必要",
                "instruction": invite_instruction
            }
        
        # PDFファイルの存在確認
        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            return {
                "success": False,
                "error": f"PDF file not found: {pdf_path}"
            }
        
        # メッセージ生成
        if not message_template:
            message_template = "📚 {book_title} のPDFが更新されました\n\n作成日時: {timestamp}\nリポジトリ: {repo_name}"
        
        message = message_template.format(
            book_title=book_title or repo_name,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            repo_name=repo_name
        )
        
        try:
            # ファイルアップロード（v2 APIを使用）
            response = self.client.files_upload_v2(
                channel=channel_id,
                file=pdf_path,
                filename=pdf_path_obj.name,
                initial_comment=message
            )
            
            logger.info(f"PDF posted successfully to {repo_name}")
            
            # v2 APIのレスポンス構造に対応
            file_info = response.get('files', [{}])[0] if response.get('files') else response.get('file', {})
            return {
                "success": True,
                "channel": repo_name,
                "file_id": file_info.get('id', 'unknown'),
                "permalink": file_info.get('permalink', 'unknown')
            }
            
        except SlackApiError as e:
            error_msg = str(e)
            logger.error(f"Failed to post PDF: {error_msg}")
            
            # エラーの詳細な分析
            if "not_in_channel" in error_msg:
                invite_instruction = f"""
Botがチャネルに参加していません。

【対処方法】
1. Slackで #{repo_name} チャネルを開く
2. チャネル名をクリック → 「メンバーを追加」
3. @techzip_pdf_bot を検索して追加
4. 追加完了後、もう一度PDF生成を実行
"""
                return {
                    "success": False,
                    "error": f"Bot is not in channel '{repo_name}'",
                    "action_required": "Bot招待が必要",
                    "instruction": invite_instruction
                }
            elif "file_upload_disabled" in error_msg:
                return {
                    "success": False,
                    "error": "File upload is disabled in this workspace"
                }
            else:
                return {
                    "success": False,
                    "error": error_msg
                }
    
    def get_bot_channels(self) -> List[Dict[str, str]]:
        """
        Botが参加しているチャネル一覧を取得
        
        Returns:
            チャネル情報のリスト
        """
        if not self.client:
            return []
        
        try:
            response = self.client.conversations_list(
                types="private_channel",
                limit=1000
            )
            
            channels = []
            for channel in response.get('channels', []):
                if channel.get('is_member', False):
                    channels.append({
                        "id": channel['id'],
                        "name": channel['name'],
                        "is_private": channel.get('is_private', True)
                    })
            
            return channels
            
        except SlackApiError as e:
            logger.error(f"Failed to get bot channels: {e}")
            return []
    
    @staticmethod
    def encrypt_token(token: str) -> str:
        """
        トークンを暗号化
        
        Args:
            token: 平文のトークン
            
        Returns:
            暗号化されたトークン
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            logger.warning("Cryptography not available - returning token as-is")
            return token
            
        # 固定キーを使用（本番環境では環境変数等から取得すべき）
        key = b'TechZip-Slack-Integration-Key-32bytes-long!!!'[:32].ljust(32, b'0')
        fernet = Fernet(Fernet.generate_key())  # 実際の実装では固定キーを使用
        return fernet.encrypt(token.encode()).decode()
    
    @staticmethod
    def decrypt_token(encrypted_token: str) -> str:
        """
        トークンを復号化
        
        Args:
            encrypted_token: 暗号化されたトークン
            
        Returns:
            平文のトークン
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            logger.warning("Cryptography not available - returning token as-is")
            return encrypted_token
            
        # 固定キーを使用（本番環境では環境変数等から取得すべき）
        key = b'TechZip-Slack-Integration-Key-32bytes-long!!!'[:32].ljust(32, b'0')
        fernet = Fernet(Fernet.generate_key())  # 実際の実装では固定キーを使用
        return fernet.decrypt(encrypted_token.encode()).decode()


class SlackConfig:
    """Slack設定管理クラス"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        設定管理の初期化
        
        Args:
            config_path: 設定ファイルのパス
        """
        # PathResolverを使用して適切な設定ファイルパスを取得
        if config_path:
            self.config_path = Path(config_path)
        else:
            config_file = PathResolver.resolve_config_file('settings.json')
            self.config_path = config_file if config_file else PathResolver.get_config_path() / 'settings.json'
        
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        config_path = self.config_path
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        
        # デフォルト設定（環境変数から取得）
        return {
            "slack": {
                "enabled": bool(EnvManager.get('SLACK_BOT_TOKEN')),
                "bot_token": EnvManager.get('SLACK_BOT_TOKEN', ''),
                "default_message_template": "📚 {book_title} のPDFが更新されました\n\n作成日時: {timestamp}\nリポジトリ: {repo_name}",
                "auto_post": True,
                "last_channel_cache": {}
            }
        }
    
    def save_config(self):
        """設定をファイルに保存"""
        config_path = self.config_path
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info("Config saved successfully")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def get_slack_config(self) -> Dict[str, Any]:
        """Slack設定を取得"""
        return self.config.get("slack", {})
    
    def update_slack_config(self, **kwargs):
        """Slack設定を更新"""
        if "slack" not in self.config:
            self.config["slack"] = {}
        
        self.config["slack"].update(kwargs)
        self.save_config()
    
    def is_slack_enabled(self) -> bool:
        """Slack統合が有効かどうか"""
        return self.config.get("slack", {}).get("enabled", False)
    
    def get_bot_token(self) -> Optional[str]:
        """Bot Tokenを取得（環境変数優先）"""
        # 環境変数優先
        env_token = os.environ.get('SLACK_BOT_TOKEN')
        if env_token:
            return env_token
        
        # 設定ファイルから取得
        encrypted_token = self.config.get("slack", {}).get("bot_token", "")
        if encrypted_token:
            try:
                # 暗号化されている場合は復号化
                if CRYPTOGRAPHY_AVAILABLE and encrypted_token.startswith("gAAAAA"):  # Fernetの暗号化プレフィックス
                    return SlackIntegration.decrypt_token(encrypted_token)
                else:
                    # 平文の場合またはcryptography未インストールの場合はそのまま返す
                    return encrypted_token
            except:
                return encrypted_token
        
        return None


# テスト用のメイン関数
if __name__ == "__main__":
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 設定ファイルの確認
    config = SlackConfig()
    print(f"Slack enabled: {config.is_slack_enabled()}")
    
    # 接続テスト
    slack = SlackIntegration()
    result = slack.test_connection()
    print(f"Connection test: {result}")
    
    # Bot参加チャネル一覧
    if result.get("success"):
        channels = slack.get_bot_channels()
        print(f"\nBot is in {len(channels)} channels:")
        for ch in channels[:5]:
            print(f"  - {ch['name']}")
        if len(channels) > 5:
            print(f"  ... and {len(channels) - 5} more")