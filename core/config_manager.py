"""
ConfigManager独立モジュール
統一設定管理システム
.env、YAML、環境変数を統合管理

分離元: src/slack_pdf_poster.py
作成日: 2025-08-03
"""
from __future__ import annotations

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv


class ConfigManager:
    """
    統一設定管理システム
    .env、YAML、環境変数を統合管理
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        初期化
        
        Args:
            config_dir: 設定ディレクトリ（省略時は./config）
        """
        self.config_dir = config_dir or Path("config")
        self.config_dir.mkdir(exist_ok=True)
        
        # .env ファイル読み込み
        env_file = self.config_dir / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        
        # メイン設定ファイル
        self.main_config_file = self.config_dir / "techzip_config.yaml"
        self._config_cache = None
        self._load_config()
    
    def _load_config(self):
        """設定ファイルを読み込み"""
        try:
            if self.main_config_file.exists():
                with open(self.main_config_file, 'r', encoding='utf-8') as f:
                    self._config_cache = yaml.safe_load(f)
            else:
                # デフォルト設定を作成
                self._config_cache = self._create_default_config()
                self._save_config()
        except Exception as e:
            print(f"設定読み込みエラー: {e}")
            self._config_cache = self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """デフォルト設定を作成"""
        return {
            "paths": {
                "base_repository_path": os.getenv("TECHZIP_BASE_PATH", "G:/.shortcut-targets-by-id/0B6euJ_grVeOeMnJLU1IyUWgxeWM/NP-IRD"),
                "temp_directory": os.getenv("TECHZIP_TEMP_DIR", "/tmp/techzip"),
                "output_directory": os.getenv("TECHZIP_OUTPUT_DIR", "./output"),
                "log_directory": os.getenv("TECHZIP_LOG_DIR", "./logs")
            },
            "api": {
                "nextpublishing": {
                    "base_url": os.getenv("NEXTPUB_BASE_URL", "http://sd001.nextpublishing.jp/rapture"),
                    "download_endpoint": os.getenv("NEXTPUB_DOWNLOAD_ENDPOINT", "do_download_pdf"),
                    "username": os.getenv("NEXTPUB_USERNAME", "ep_user"),
                    "password": os.getenv("NEXTPUB_PASSWORD", "Nn7eUTX5"),
                    "timeout": int(os.getenv("NEXTPUB_TIMEOUT", "30")),
                    "retry_count": int(os.getenv("NEXTPUB_RETRY_COUNT", "3"))
                },
                "slack": {
                    "bot_token": os.getenv("SLACK_BOT_TOKEN"),
                    "api_base_url": os.getenv("SLACK_API_URL", "https://slack.com/api/"),
                    "timeout": int(os.getenv("SLACK_TIMEOUT", "30")),
                    "rate_limit_delay": float(os.getenv("SLACK_RATE_DELAY", "1.0"))
                }
            },
            "oauth": {
                "redirect_uri": os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8888/callback"),
                "server_host": os.getenv("OAUTH_SERVER_HOST", "localhost"),
                "server_port": int(os.getenv("OAUTH_SERVER_PORT", "8888"))
            },
            "processing": {
                "batch_size": int(os.getenv("TECHZIP_BATCH_SIZE", "10")),
                "delay_between_batches": float(os.getenv("TECHZIP_BATCH_DELAY", "1.0")),
                "max_concurrent": int(os.getenv("TECHZIP_MAX_CONCURRENT", "3")),
                "default_timeout": int(os.getenv("TECHZIP_DEFAULT_TIMEOUT", "300")),
                "auto_cleanup": os.getenv("TECHZIP_AUTO_CLEANUP", "true").lower() == "true"
            },
            "logging": {
                "level": os.getenv("TECHZIP_LOG_LEVEL", "INFO"),
                "file_rotation": os.getenv("TECHZIP_LOG_ROTATION", "daily"),
                "max_file_size": os.getenv("TECHZIP_LOG_MAX_SIZE", "10MB"),
                "retention_days": int(os.getenv("TECHZIP_LOG_RETENTION", "30"))
            }
        }
    
    def _save_config(self):
        """設定をファイルに保存"""
        try:
            with open(self.main_config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self._config_cache, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"設定保存エラー: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        設定値を取得（ドット記法対応）
        
        Args:
            key_path: 設定キーのパス（例: "api.slack.bot_token"）
            default: デフォルト値
            
        Returns:
            設定値
        """
        try:
            keys = key_path.split('.')
            value = self._config_cache
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
                    
            return value
        except Exception:
            return default
    
    def set(self, key_path: str, value: Any):
        """
        設定値を更新
        
        Args:
            key_path: 設定キーのパス
            value: 設定値
        """
        try:
            keys = key_path.split('.')
            config = self._config_cache
            
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            config[keys[-1]] = value
            self._save_config()
        except Exception as e:
            print(f"設定更新エラー: {e}")
    
    def get_api_config(self, service: str) -> Dict[str, Any]:
        """
        API設定を取得
        
        Args:
            service: サービス名（nextpublishing, slack）
            
        Returns:
            API設定辞書
        """
        return self.get(f"api.{service}", {})
    
    def get_path_config(self) -> Dict[str, str]:
        """パス設定を取得"""
        return self.get("paths", {})
    
    def validate_config(self) -> Dict[str, list]:
        """
        設定の妥当性チェック
        
        Returns:
            {
                "errors": ["エラーメッセージ"],
                "warnings": ["警告メッセージ"],
                "missing_env_vars": ["不足環境変数"]
            }
        """
        errors = []
        warnings = []
        missing_env_vars = []
        
        # 必須設定のチェック
        required_configs = [
            "paths.base_repository_path",
            "api.nextpublishing.base_url",
            "api.slack.bot_token"
        ]
        
        for config_path in required_configs:
            value = self.get(config_path)
            if not value:
                errors.append(f"必須設定が不足: {config_path}")
        
        # 環境変数のチェック
        required_env_vars = [
            "SLACK_BOT_TOKEN",
            "NEXTPUB_USERNAME",
            "NEXTPUB_PASSWORD"
        ]
        
        for env_var in required_env_vars:
            if not os.getenv(env_var):
                missing_env_vars.append(env_var)
        
        # パス存在チェック
        base_path = Path(self.get("paths.base_repository_path", ""))
        if not base_path.exists():
            warnings.append(f"ベースパスが存在しません: {base_path}")
        
        return {
            "errors": errors,
            "warnings": warnings,
            "missing_env_vars": missing_env_vars
        }


# シングルトンインスタンス
_config_manager = None


def get_config_manager() -> ConfigManager:
    """ConfigManagerのシングルトンインスタンスを取得"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager