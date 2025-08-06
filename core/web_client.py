from __future__ import annotations
"""Web連携モジュール - Refactored with Authentication Abstraction"""
import os
from pathlib import Path
from typing import Optional, Tuple
import requests

from utils.logger import get_logger
from core.configuration_provider import get_unified_config
from core.authentication import (
    AuthenticationProvider, 
    create_config_adapter,
    create_nextpublishing_auth
)


class WebClient:
    """Web連携クライアント - Refactored with proper authentication architecture"""
    
    def __init__(self, auth_provider: Optional[AuthenticationProvider] = None):
        """WebClient初期化
        
        Args:
            auth_provider: Optional authentication provider. If None, creates default.
        """
        self.logger = get_logger(__name__)
        self.config = get_unified_config()
        
        # Initialize authentication provider
        if auth_provider:
            self._auth_provider = auth_provider
            self.logger.debug("Using provided authentication provider")
        else:
            # Create authentication provider using the unified config
            from core.configuration_provider import get_config_provider
            try:
                config_provider = get_config_provider()
                self.logger.debug(f"Got config provider: {type(config_provider).__name__}")
                
                config_adapter = create_config_adapter(config_provider)
                self.logger.debug(f"Created config adapter: {type(config_adapter).__name__}")
                
                self._auth_provider = create_nextpublishing_auth(config_adapter)
                self.logger.debug("Created default NextPublishing authentication provider")
            except Exception as e:
                self.logger.error(f"Failed to create authentication provider: {str(e)}")
                import traceback
                self.logger.error(f"Stack trace: {traceback.format_exc()}")
                raise
    
    def upload_file(self, file_path: Path, email_address: str, process_mode: str = "api") -> bool:
        """
        ファイルをアップロード
        
        Args:
            file_path: アップロードするファイルのパス
            email_address: 送信先メールアドレス
            process_mode: 処理方式 ("api", "traditional", "gmail_api")
            
        Returns:
            アップロード成功フラグ
        """
        try:
            # NextPublishingServiceを使用してアップロード実行
            from services.nextpublishing_service import NextPublishingService, UploadSettings
            
            # メール設定を適用
            settings = UploadSettings()
            settings.email = email_address
            
            # サービスを初期化してアップロード実行（処理方式を渡す）
            service = NextPublishingService(settings, process_mode=process_mode)
            success, message, control_number = service.upload_single_file(file_path)
            
            if success:
                self.logger.info(f"NextPublishingアップロード成功: {message}")
                if control_number:
                    self.logger.info(f"管理番号: {control_number}")
                return True
            else:
                self.logger.error(f"NextPublishingアップロード失敗: {message}")
                return False
                
        except Exception as e:
            self.logger.error(f"WebClient.upload_file エラー: {str(e)}")
            import traceback
            self.logger.error(f"スタックトレース: {traceback.format_exc()}")
            return False
    
    def check_email_status(self) -> Tuple[bool, Optional[str]]:
        """
        メールステータスチェック
        
        Returns:
            (成功フラグ, ダウンロードURL)
        """
        try:
            # Gmail API監視を使用してメールチェック
            from core.gmail_api_monitor import GmailApiMonitor
            
            # Gmail API監視を初期化
            monitor = GmailApiMonitor()
            
            # 最新の変換完了メールを確認
            success, download_url = monitor.check_latest_conversion_email()
            
            if success and download_url:
                self.logger.info(f"メールから変換完了を確認: {download_url}")
                return True, download_url
            else:
                self.logger.info("変換完了メールが見つかりません")
                return False, None
                
        except Exception as e:
            self.logger.error(f"WebClient.check_email_status エラー: {str(e)}")
            self.logger.warning("WebClient.check_email_status: メール監視エラーのため未実装扱い")
            return False, None
    
    def download_file(self, download_url: str, output_path: Path) -> bool:
        """
        ダウンロードURLからファイルをダウンロード
        
        Args:
            download_url: ダウンロードURL
            output_path: 保存先パス
            
        Returns:
            ダウンロード成功フラグ
        """
        try:
            self.logger.info(f"ファイルダウンロード開始: {download_url}")
            
            # Use authentication provider instead of hardcoded credentials
            auth_obj = self._auth_provider.create_auth_object()
            self.logger.debug(f"認証情報を取得: {type(auth_obj).__name__}")
            
            # Execute download request with proper authentication
            response = requests.get(
                download_url, 
                stream=True, 
                timeout=300,
                auth=auth_obj
            )
            response.raise_for_status()
            
            # ファイルサイズを取得（可能であれば）
            total_size = int(response.headers.get('content-length', 0))
            if total_size > 0:
                self.logger.info(f"ダウンロードサイズ: {total_size:,} bytes ({total_size / 1024 / 1024:.1f} MB)")
            
            # ダウンロード実行
            downloaded = 0
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # 進捗ログ（1MBごと）
                        if downloaded % (1024 * 1024) == 0:
                            mb_downloaded = downloaded / 1024 / 1024
                            self.logger.info(f"ダウンロード進捗: {mb_downloaded:.1f} MB")
            
            self.logger.info(f"ダウンロード完了: {output_path} ({downloaded:,} bytes)")
            
            # ファイルサイズの検証
            if output_path.stat().st_size != downloaded:
                self.logger.warning("ダウンロードサイズが一致しません")
                return False
                
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"ダウンロードリクエストエラー: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"WebClient.download_file エラー: {str(e)}")
            import traceback
            self.logger.error(f"スタックトレース: {traceback.format_exc()}")
            return False
    
    def close(self):
        """リソースのクリーンアップ"""
        # WebClientは特にクリーンアップするリソースがないため、パススルー
        pass


# ===== ConfigManager独立ファイル作成 =====
# このコンテンツを core/config_manager.py として作成

CONFIG_MANAGER_FILE_CONTENT = '''"""
ConfigManager独立モジュール
統一設定管理システム
.env、YAML、環境変数を統合管理

分離元: src/slack_pdf_poster.py
作成日: 2025-08-03
"""

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
                    "base_url": os.getenv("NEXTPUB_BASE_URL", "http://trial.nextpublishing.jp/rapture/"),
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
'''

# 上記内容を core/config_manager.py として作成
# ===== ConfigManager独立ファイル作成終了 =====

# CONFIG_MANAGER_PY と HARDCODING_DETECTOR_PY のコンテンツ
# ここに分離すべきクラスの内容を記載

HARDCODING_DETECTOR_CONTENT = '''"""
HardcodingDetector独立モジュール
ハードコーディング検知システム
リファクタリング時に設定すべき値をスキャンして検出

分離元: src/slack_pdf_poster.py
作成日: 2025-08-03
"""

import re
from pathlib import Path
from typing import Dict, List, Optional


class HardcodingDetector:
    """
    ハードコーディング検知システム
    リファクタリング時に設定すべき値をスキャンして検出
    """
    
    HARDCODE_PATTERNS = {
        "file_paths": [
            r"G:\\.*",
            r"G:/.*",
            r"C:\\.*",
            r"C:/.*",
            r"/mnt/.*",
            r"Path\\(\\\\\\\".*\\\\\\\"\\),",
        ],
        "urls": [
            r"https?://[^\\s\\\"\\\']+",
            r"localhost:\\d+",
            r"127\\.0\\.0\\.1:\\d+",
        ],
        "credentials": [
            r"ep_user",
            r"Nn7eUTX5",
            r"password\\s*=\\s*[\\\"\\'][^\\\"\\'][\\\"\\']",
            r"username\\s*=\\s*[\\\"\\'][^\\\"\\'][\\\"\\']",
        ],
        "api_endpoints": [
            r"trial\\.nextpublishing\\.jp",
            r"upload_46tate",
            r"do_download_pdf",
            r"api\\.slack\\.com",
        ],
        "magic_numbers": [
            r":\\d{4,5}",  # ポート番号
            r"timeout\\s*=\\s*\\d+",
            r"sleep\\(\\d+\\)",
        ]
    }
    
    def __init__(self, config_provider=None):
        """HardcodingDetectorを初期化"""
        # 循環インポートを避けるため、config_providerは任意
        self.config_provider = config_provider
    
    def scan_file(self, file_path: Path) -> Dict[str, list]:
        """
        ファイル内のハードコーディングをスキャン
        
        Args:
            file_path: スキャン対象ファイル
            
        Returns:
            検出されたハードコーディングの分類別リスト
        """
        return self.scan_hardcoding(str(file_path))
    
    def scan_multiple_files(self, file_paths: list) -> Dict[str, Dict[str, list]]:
        """
        複数ファイルの一括スキャン
        
        Args:
            file_paths: スキャン対象ファイルのリスト
            
        Returns:
            ファイル別の検出結果
        """
        results = {}
        for file_path in file_paths:
            results[str(file_path)] = self.scan_file(Path(file_path))
        return results
    
    def suggest_remediation(self, scan_results: Dict[str, list]) -> list:
        """
        修正提案を生成
        
        Args:
            scan_results: スキャン結果
            
        Returns:
            修正提案のリスト
        """
        suggestions = []
        
        for category, detections in scan_results.items():
            if not detections:
                continue
                
            if category == "file_paths":
                suggestions.append("ファイルパスを設定ファイル（config.yaml）に外部化してください")
            elif category == "urls":
                suggestions.append("URLを環境変数（.env）または設定ファイルに移動してください")
            elif category == "credentials":
                suggestions.append("認証情報を環境変数（.env）に移動し、コードから削除してください")
            elif category == "api_endpoints":
                suggestions.append("APIエンドポイントを設定ファイルに外部化してください")
            elif category == "magic_numbers":
                suggestions.append("数値設定を設定ファイルの定数として定義してください")
                
        return suggestions
    
    @classmethod
    def scan_hardcoding(cls, file_path: str) -> Dict[str, list]:
        """
        ファイル内のハードコーディングをスキャン
        
        Args:
            file_path: スキャン対象ファイル
            
        Returns:
            検出されたハードコーディングの分類別リスト
        """
        detected = {category: [] for category in cls.HARDCODE_PATTERNS.keys()}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for category, patterns in cls.HARDCODE_PATTERNS.items():
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        detected[category].extend(matches)
                        
        except Exception as e:
            print(f"ハードコーディングスキャンエラー: {e}")
            
        return detected
'''

# 上記内容を core/hardcoding_detector.py として作成
