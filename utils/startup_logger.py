"""起動時ログ収集ユーティリティ"""

import logging
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

from utils.path_resolver import PathResolver
from utils.env_manager import EnvManager


class StartupLogger:
    """起動時の情報を収集してGUIに渡すためのクラス"""
    
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
        
    def add_log(self, message: str, level: str = "INFO"):
        """ログエントリを追加"""
        entry = {
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'level': level,
            'message': message
        }
        self.logs.append(entry)
        
        # 通常のログにも出力
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def collect_startup_info(self):
        """起動時の情報を収集"""
        self.add_log("アプリケーションを起動します")
        
        # 実行環境
        if PathResolver.is_exe_environment():
            self.add_log("EXE環境で実行中")
            self.add_log(f"ベースパス: {PathResolver.get_base_path()}")
            self.add_log(f"ユーザーディレクトリ: {PathResolver.get_user_dir()}")
            self.add_log(f"設定パス: {PathResolver.get_config_path()}")
        else:
            self.add_log("開発環境で実行中")
            self.add_log(f"プロジェクトルート: {PathResolver.get_base_path()}")
        
        # 初回実行チェック
        if EnvManager.get('TECHZIP_FIRST_RUN') == '1':
            self.add_log("初回実行を検出しました", "WARNING")
            self.add_log(f"設定ファイルは {PathResolver.get_user_dir()} に作成されます")
        
        # 認証情報の設定状況
        self.add_log("認証情報の設定状況:")
        creds_info = EnvManager.get_credentials_info()
        for key, value in creds_info.items():
            status = "✓" if value else "✗"
            level = "INFO" if value else "WARNING"
            self.add_log(f"  {status} {key}", level)
        
        # 設定ファイルの存在確認
        config_path = PathResolver.get_config_path()
        settings_file = config_path / 'settings.json'
        if settings_file.exists():
            self.add_log(f"設定ファイル確認: {settings_file}")
            
            # Google Sheets認証ファイルの確認（詳細版）
            from utils.config import get_config
            
            # 設定ファイルの内容を直接確認（キャッシュを回避）
            import json
            with open(settings_file, 'r', encoding='utf-8') as f:
                raw_settings = json.load(f)
            
            if 'google_sheet' in raw_settings and 'credentials_path' in raw_settings['google_sheet']:
                raw_creds_path = raw_settings['google_sheet']['credentials_path']
                self.add_log(f"設定ファイル内の認証パス: {raw_creds_path}")
            
            # Configクラス経由での確認
            config = get_config()
            sheets_creds_path = config.get_credentials_path()
            if sheets_creds_path and sheets_creds_path.exists():
                self.add_log(f"Google Sheets認証ファイル: {sheets_creds_path}")
            else:
                self.add_log("Google Sheets認証ファイルが設定されていません", "WARNING")
                sheets_config = config.get('google_sheet.credentials_path')
                if sheets_config:
                    self.add_log(f"  設定値: {sheets_config}", "WARNING")
                else:
                    self.add_log("  設定値が取得できません（キャッシュ問題の可能性）", "WARNING")
                self.add_log("  ファイルが存在しないか、パスが無効です", "WARNING")
        else:
            self.add_log(f"設定ファイルが見つかりません: {settings_file}", "WARNING")
        
        # .envファイルの確認
        if PathResolver.is_exe_environment():
            env_file = PathResolver.get_user_dir() / '.env'
        else:
            env_file = Path('.env')
        
        if env_file.exists():
            self.add_log(f"環境変数ファイル確認: {env_file}")
        else:
            self.add_log(f"環境変数ファイルが見つかりません: {env_file}", "WARNING")
            self.add_log("メニュー > ツール > 設定 から認証情報を設定してください", "WARNING")
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """収集したログを取得"""
        return self.logs
    
    def format_logs_for_display(self) -> str:
        """ログを表示用にフォーマット"""
        lines = []
        for log in self.logs:
            level_emoji = {
                "INFO": "ℹ️",
                "WARNING": "⚠️",
                "ERROR": "❌"
            }.get(log['level'], "")
            
            lines.append(f"[{log['timestamp']}] {level_emoji} {log['message']}")
        
        return "\n".join(lines)