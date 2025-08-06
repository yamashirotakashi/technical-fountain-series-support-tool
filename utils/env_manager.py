"""環境変数管理ユーティリティ - 開発環境とEXE環境の両対応"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv, find_dotenv

from utils.logger import get_logger
from utils.path_resolver import PathResolver


class EnvManager:
    """環境変数を統合管理するクラス"""
    
    _logger = None
    _initialized = False
    _env_loaded = False
    _env_cache: Dict[str, Any] = {}
    
    # 環境変数テンプレート
    ENV_TEMPLATE = """# TechZip環境設定ファイル
# このファイルをコピーして .env として保存し、実際の値を設定してください

# Gmail設定（IMAP/SMTP用）
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password

# GitHub設定
GITHUB_TOKEN=your-github-token

# Slack設定
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token

# Word2XHTML5サービス設定
WORD2XHTML5_USERNAME=your-username
WORD2XHTML5_PASSWORD=your-password

# NextPublishing API設定
NEXTPUBLISHING_API_KEY=your-api-key
NEXTPUBLISHING_API_SECRET=your-api-secret

# Google Sheets API設定（サービスアカウントJSON）
GOOGLE_SHEETS_CREDENTIALS_PATH=path/to/your/service-account.json
GOOGLE_SHEETS_ID=YOUR_SHEET_ID_HERE

# その他の設定
DEBUG_MODE=false
LOG_LEVEL=INFO
"""
    
    @classmethod
    def _get_logger(cls):
        """ロガーの遅延初期化"""
        if cls._logger is None:
            cls._logger = get_logger(__name__)
        return cls._logger
    
    @classmethod
    def initialize(cls, force: bool = False) -> bool:
        """
        環境変数管理システムを初期化
        
        Args:
            force: 強制的に再初期化するか
            
        Returns:
            初期化が成功したか
        """
        if cls._initialized and not force:
            return True
        
        try:
            cls._get_logger().info("環境変数管理システムを初期化中...")
            
            # .envファイルを探して読み込む
            cls._load_env_files()
            
            # 必要なディレクトリを作成
            cls._ensure_directories()
            
            # 環境変数をキャッシュ
            cls._cache_env_vars()
            
            cls._initialized = True
            cls._get_logger().info("環境変数管理システムの初期化完了")
            return True
            
        except Exception as e:
            cls._get_logger().error(f"環境変数管理システムの初期化エラー: {e}")
            return False
    
    @classmethod
    def _load_env_files(cls):
        """適切な.envファイルを読み込む"""
        env_loaded = False
        
        if PathResolver.is_exe_environment():
            # EXE環境: 複数の場所を確認
            search_paths = [
                PathResolver.get_user_dir() / '.env',  # ユーザーディレクトリ
                PathResolver.get_base_path() / '.env',  # EXEと同じディレクトリ
                PathResolver.get_config_path() / '.env'  # configディレクトリ
            ]
            
            for env_path in search_paths:
                if env_path.exists():
                    load_dotenv(env_path)
                    cls._get_logger().info(f"環境変数ファイルを読み込み: {env_path}")
                    env_loaded = True
                    break
            
            if not env_loaded:
                # .envが見つからない場合、テンプレートを作成
                cls._create_env_template()
        else:
            # 開発環境: 通常の方法で.envを探す
            dotenv_path = find_dotenv()
            if dotenv_path:
                load_dotenv(dotenv_path)
                cls._get_logger().info(f"環境変数ファイルを読み込み: {dotenv_path}")
                env_loaded = True
            else:
                cls._get_logger().warning(".envファイルが見つかりません")
        
        cls._env_loaded = env_loaded
    
    @classmethod
    def _create_env_template(cls):
        """環境変数テンプレートファイルを作成"""
        try:
            if PathResolver.is_exe_environment():
                template_path = PathResolver.get_user_dir() / '.env.template'
            else:
                template_path = PathResolver.get_base_path() / '.env.template'
            
            if not template_path.exists():
                template_path.write_text(cls.ENV_TEMPLATE, encoding='utf-8')
                cls._get_logger().info(f"環境変数テンプレートを作成: {template_path}")
                
                # ユーザーへの案内
                if PathResolver.is_exe_environment():
                    cls._get_logger().warning(
                        f"環境変数ファイルが見つかりません。\n"
                        f"{template_path} をコピーして .env として保存し、"
                        f"必要な設定を行ってください。"
                    )
        except Exception as e:
            cls._get_logger().error(f"環境変数テンプレートの作成エラー: {e}")
    
    @classmethod
    def _ensure_directories(cls):
        """必要なディレクトリを確認・作成"""
        directories = [
            PathResolver.get_logs_path(),
            PathResolver.get_temp_path(),
            PathResolver.get_config_path()
        ]
        
        for directory in directories:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                cls._get_logger().debug(f"ディレクトリを作成: {directory}")
    
    @classmethod
    def _cache_env_vars(cls):
        """重要な環境変数をキャッシュ"""
        # 環境変数のリスト
        env_vars = [
            'GMAIL_ADDRESS',
            'GMAIL_APP_PASSWORD',
            'GITHUB_TOKEN',
            'SLACK_BOT_TOKEN',
            'WORD2XHTML5_USERNAME',
            'WORD2XHTML5_PASSWORD',
            'NEXTPUBLISHING_API_KEY',
            'NEXTPUBLISHING_API_SECRET',
            'GOOGLE_SHEETS_CREDENTIALS_PATH',
            'GOOGLE_SHEETS_ID',
            'DEBUG_MODE',
            'LOG_LEVEL'
        ]
        
        cls._env_cache.clear()
        for var in env_vars:
            value = os.getenv(var)
            if value:
                cls._env_cache[var] = value
    
    @classmethod
    def get(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        環境変数を取得
        
        Args:
            key: 環境変数名
            default: デフォルト値
            
        Returns:
            環境変数の値
        """
        if not cls._initialized:
            cls.initialize()
        
        # キャッシュから取得
        if key in cls._env_cache:
            return cls._env_cache[key]
        
        # 環境変数から直接取得
        value = os.getenv(key, default)
        if value:
            cls._env_cache[key] = value
        
        return value
    
    @classmethod
    def set(cls, key: str, value: str):
        """
        環境変数を設定（一時的）
        
        Args:
            key: 環境変数名
            value: 値
        """
        os.environ[key] = value
        cls._env_cache[key] = value
    
    @classmethod
    def get_bool(cls, key: str, default: bool = False) -> bool:
        """
        環境変数をbool値として取得
        
        Args:
            key: 環境変数名
            default: デフォルト値
            
        Returns:
            bool値
        """
        value = cls.get(key)
        if value is None:
            return default
        
        return value.lower() in ('true', '1', 'yes', 'on')
    
    @classmethod
    def get_int(cls, key: str, default: int = 0) -> int:
        """
        環境変数をint値として取得
        
        Args:
            key: 環境変数名
            default: デフォルト値
            
        Returns:
            int値
        """
        value = cls.get(key)
        if value is None:
            return default
        
        try:
            return int(value)
        except ValueError:
            cls._get_logger().warning(f"環境変数 {key} の値 '{value}' を整数に変換できません")
            return default
    
    @classmethod
    def get_path(cls, key: str, default: Optional[Path] = None) -> Optional[Path]:
        """
        環境変数をPathオブジェクトとして取得
        
        Args:
            key: 環境変数名
            default: デフォルト値
            
        Returns:
            Pathオブジェクト
        """
        value = cls.get(key)
        if value is None:
            return default
        
        # WSL環境でWindowsパス（C:\...）を適切に変換
        if os.name != 'nt' and value.startswith(('C:\\', 'c:\\', 'C:/', 'c:/')):
            # WindowsパスをWSLパスに変換
            windows_path = value.replace('\\', '/')
            if windows_path.lower().startswith('c:'):
                wsl_path = '/mnt/c' + windows_path[2:]
                path = Path(wsl_path)
            else:
                path = Path(value)
        else:
            path = Path(value)
        
        # 相対パスの場合、適切なベースパスからの相対パスとして解決
        if not path.is_absolute():
            if PathResolver.is_exe_environment():
                # EXE環境: ユーザーディレクトリからの相対パス
                path = PathResolver.get_user_dir() / path
            else:
                # 開発環境: プロジェクトルートからの相対パス
                path = PathResolver.get_base_path() / path
        
        return path
    
    @classmethod
    def validate_required_vars(cls, required_vars: list) -> tuple[bool, list]:
        """
        必須環境変数が設定されているか検証
        
        Args:
            required_vars: 必須環境変数のリスト
            
        Returns:
            (すべて設定されているか, 未設定の変数リスト)
        """
        if not cls._initialized:
            cls.initialize()
        
        missing_vars = []
        for var in required_vars:
            if not cls.get(var):
                missing_vars.append(var)
        
        return len(missing_vars) == 0, missing_vars
    
    @classmethod
    def get_credentials_info(cls) -> Dict[str, bool]:
        """
        各種認証情報の設定状況を取得
        
        Returns:
            認証情報の設定状況
        """
        return {
            'gmail': bool(cls.get('GMAIL_ADDRESS') and cls.get('GMAIL_APP_PASSWORD')),
            'gmail_oauth': bool(PathResolver.resolve_config_file('gmail_oauth_credentials.json')),
            'github': bool(cls.get('GITHUB_TOKEN')),
            'slack': bool(cls.get('SLACK_BOT_TOKEN')),
            'google_sheets': bool(cls.get('GOOGLE_SHEETS_CREDENTIALS_PATH') and cls.get('GOOGLE_SHEETS_ID')),
            'nextpublishing': bool(cls.get('WORD2XHTML5_USERNAME') and cls.get('WORD2XHTML5_PASSWORD')),
            'word2xhtml5': bool(cls.get('WORD2XHTML5_USERNAME') and cls.get('WORD2XHTML5_PASSWORD'))
        }