"""Gmail OAuth認証のEXE環境対応ヘルパーモジュール"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Tuple

from utils.logger import get_logger


class GmailOAuthExeHelper:
    """EXE環境でのGmail OAuth認証を支援するクラス"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.is_exe = getattr(sys, 'frozen', False)
        
    def get_credentials_path(self) -> Tuple[str, str]:
        """
        認証ファイルのパスを取得（EXE環境対応）
        
        Returns:
            (credentials_path, token_path) のタプル
        """
        if self.is_exe:
            # EXE環境: 実行ファイルと同じディレクトリまたはユーザーディレクトリ
            exe_dir = Path(sys.executable).parent
            user_config_dir = Path.home() / '.techzip' / 'config'
            
            # ユーザーディレクトリを優先（書き込み可能）
            if not user_config_dir.exists():
                user_config_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"ユーザー設定ディレクトリを作成: {user_config_dir}")
            
            credentials_path = user_config_dir / 'gmail_oauth_credentials.json'
            token_path = user_config_dir / 'gmail_token.pickle'
            
            # EXEディレクトリから初期ファイルをコピー（存在する場合）
            exe_creds = exe_dir / 'config' / 'gmail_oauth_credentials.json'
            if exe_creds.exists() and not credentials_path.exists():
                import shutil
                shutil.copy2(exe_creds, credentials_path)
                self.logger.info(f"認証ファイルをユーザーディレクトリにコピー: {credentials_path}")
            
        else:
            # 開発環境: プロジェクトのconfigディレクトリ
            config_dir = Path(__file__).parent.parent / 'config'
            credentials_path = config_dir / 'gmail_oauth_credentials.json'
            token_path = config_dir / 'gmail_token.pickle'
        
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
        if self.is_exe:
            config_dir = Path.home() / '.techzip' / 'config'
            config_path = config_dir / 'settings.json'
            
            if not config_path.exists():
                config_dir.mkdir(parents=True, exist_ok=True)
                
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
                        "gmail_credentials_path": str(config_dir / "gmail_oauth_credentials.json")
                    }
                }
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(template, f, indent=4, ensure_ascii=False)
                
                self.logger.info(f"設定ファイルテンプレートを作成: {config_path}")


# グローバルインスタンス
gmail_oauth_helper = GmailOAuthExeHelper()