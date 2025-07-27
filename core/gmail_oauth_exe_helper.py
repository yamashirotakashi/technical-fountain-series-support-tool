"""Gmail OAuth認証のEXE環境対応ヘルパーモジュール"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Tuple

from utils.logger import get_logger
from utils.path_resolver import PathResolver


class GmailOAuthExeHelper:
    """EXE環境でのGmail OAuth認証を支援するクラス"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.is_exe = PathResolver.is_exe_environment()
        
    def get_credentials_path(self) -> Tuple[str, str]:
        """
        認証ファイルのパスを取得（EXE環境対応）
        
        Returns:
            (credentials_path, token_path) のタプル
        """
        # PathResolverを使用して適切なパスを取得
        config_path = PathResolver.get_config_path(prefer_user_dir=True)
        
        # 認証ファイルのパス
        credentials_filename = 'gmail_oauth_credentials.json'
        token_filename = 'gmail_token.pickle'
        
        # 既存のファイルを探す
        credentials_path = PathResolver.resolve_config_file(credentials_filename)
        
        if credentials_path:
            # 認証ファイルが見つかった場合、同じディレクトリにトークンファイルを配置
            token_path = credentials_path.parent / token_filename
        else:
            # 見つからない場合は、適切な場所に新規作成
            credentials_path = config_path / credentials_filename
            token_path = config_path / token_filename
            
            # EXE環境で初期ファイルをコピー
            if self.is_exe:
                exe_creds = PathResolver.get_base_path() / 'config' / credentials_filename
                if exe_creds.exists() and not credentials_path.exists():
                    import shutil
                    try:
                        shutil.copy2(exe_creds, credentials_path)
                        self.logger.info(f"認証ファイルをユーザーディレクトリにコピー: {credentials_path}")
                    except Exception as e:
                        self.logger.warning(f"認証ファイルのコピーに失敗: {e}")
        
        return str(credentials_path), str(token_path)
    
    def check_credentials_exist(self) -> bool:
        """認証ファイルが存在するかチェック"""
        credentials_path, _ = self.get_credentials_path()
        exists = Path(credentials_path).exists()
        
        if not exists:
            self.logger.warning(f"Gmail OAuth認証ファイルが見つかりません: {credentials_path}")
            if self.is_exe:
                self.show_setup_instructions()
        
        return exists
    
    def show_setup_instructions(self):
        """セットアップ手順を表示"""
        credentials_path, _ = self.get_credentials_path()
        instructions = f"""
================================================================================
Gmail API OAuth2.0 認証セットアップが必要です
================================================================================

1. Google Cloud Console にアクセス:
   https://console.cloud.google.com/

2. APIs & Services > Credentials

3. 「+ CREATE CREDENTIALS」> OAuth client ID

4. Application type: Desktop application
   Name: TechZip Gmail Monitor

5. ダウンロードしたJSONファイルを以下に保存:
   {credentials_path}

詳細な手順は以下を参照:
https://developers.google.com/gmail/api/quickstart/python

================================================================================
"""
        self.logger.info(instructions)
        
        # GUIモードの場合はメッセージボックスも表示
        if not sys.stdout.isatty():  # コンソールがない場合
            try:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(
                    None,
                    "Gmail API認証セットアップ",
                    f"Gmail API認証ファイルが必要です。\n\n"
                    f"以下の場所に認証ファイルを配置してください:\n"
                    f"{credentials_path}\n\n"
                    f"詳細はログを確認してください。"
                )
            except ImportError:
                pass
    
    def get_oauth_port(self) -> int:
        """
        OAuth認証用のポート番号を取得（EXE環境での競合回避）
        
        Returns:
            使用可能なポート番号
        """
        if self.is_exe:
            # EXE環境では動的にポートを選択
            import socket
            sock = socket.socket()
            sock.bind(('', 0))
            port = sock.getsockname()[1]
            sock.close()
            self.logger.debug(f"OAuth認証用ポート: {port}")
            return port
        else:
            # 開発環境ではデフォルトポート
            return 0
    
    def handle_oauth_error(self, error: Exception) -> Optional[str]:
        """
        OAuth認証エラーを処理
        
        Args:
            error: 発生したエラー
            
        Returns:
            ユーザー向けのエラーメッセージ
        """
        error_msg = str(error)
        
        if "credentials" in error_msg.lower():
            return (
                "Gmail OAuth認証ファイルが見つかりません。\n"
                "セットアップ手順に従って認証ファイルを配置してください。"
            )
        elif "token" in error_msg.lower() and "expired" in error_msg.lower():
            return (
                "Gmail認証トークンの有効期限が切れています。\n"
                "再度認証を行ってください。"
            )
        elif "browser" in error_msg.lower():
            return (
                "認証用のブラウザを開けませんでした。\n"
                "手動でURLを開いて認証を完了してください。"
            )
        else:
            return f"Gmail API認証エラー: {error_msg}"
    
    def save_config_template(self):
        """設定ファイルのテンプレートを保存（初回実行時）"""
        config_path = PathResolver.get_config_path() / 'settings.json'
        
        if not config_path.exists():
            template = {
                "google_sheet": {
                    "sheet_id": "YOUR_SHEET_ID_HERE",
                    "credentials_path": "YOUR_GOOGLE_SERVICE_ACCOUNT_JSON_PATH"
                },
                "paths": {
                    "git_base": "G:\\マイドライブ\\[git]",
                    "output_base": "G:\\.shortcut-targets-by-id\\YOUR_FOLDER_ID\\NP-IRD"
                },
                "email": {
                    "gmail_credentials_path": str(PathResolver.get_config_path() / "gmail_oauth_credentials.json")
                }
            }
            
            PathResolver.ensure_file_exists(
                config_path,
                json.dumps(template, indent=4, ensure_ascii=False)
            )
            
            self.logger.info(f"設定ファイルテンプレートを作成: {config_path}")


# グローバルインスタンス
gmail_oauth_helper = GmailOAuthExeHelper()