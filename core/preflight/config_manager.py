"""Pre-flight設定管理システム"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Type
from dataclasses import dataclass, field, asdict
from datetime import datetime

from .verification_strategy import VerificationMode, VerificationConfig
from .job_state_manager import JobPriority
from utils.logger import get_logger


@dataclass
class EmailConfig:
    """メール設定"""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    imap_server: str = "imap.gmail.com"
    imap_port: int = 993
    username: str = ""
    password: str = ""
    use_ssl: bool = True
    timeout_seconds: int = 30
    
    def is_valid(self) -> bool:
        """設定が有効かどうか"""
        return bool(self.username and self.password)


@dataclass
class ServiceConfig:
    """Word2XHTML5サービス設定"""
    service_url: str = ""
    auth_username: str = ""
    auth_password: str = ""
    timeout_seconds: int = 300
    rate_limit_seconds: float = 5.0
    max_retries: int = 3
    
    # フォーム設定
    project_name: str = "山城技術の泉"
    layout_orientation: int = -10  # 横書きB5技術書
    cover_page: int = 0           # 扉なし
    crop_marks: int = 0           # トンボなし
    style_selection: int = 2      # 本文ソースコード横書き用
    index_page: int = 0           # 索引なし           # 索引なし


@dataclass
class ValidationConfig:
    """検証設定"""
    mode: VerificationMode = VerificationMode.STANDARD
    max_file_size_mb: int = 50
    min_file_size_bytes: int = 512
    allowed_extensions: List[str] = field(default_factory=lambda: ['.docx', '.doc'])
    enable_security_check: bool = True
    enable_content_analysis: bool = False
    custom_patterns: List[str] = field(default_factory=list)
    
    # 危険パターン
    dangerous_patterns: List[str] = field(default_factory=lambda: [
        '../', '..\\', '<script', 'javascript:', 'vbscript:', 'data:', 'file://', 'ftp://', 'http://', 'https://'
    ])


@dataclass
class MonitoringConfig:
    """監視設定"""
    email_check_interval_minutes: int = 5
    max_wait_minutes: int = 20
    search_hours: int = 24
    trusted_senders: List[str] = field(default_factory=lambda: [
        'nextpublishing.jp', 'trial.nextpublishing.jp', 'epub.nextpublishing.jp'
    ])
    
    # 結果パターン
    success_patterns: List[str] = field(default_factory=lambda: [
        r'.*変換.*完了.*', r'.*処理.*完了.*', r'.*conversion.*complete.*', r'.*job.*complete.*', r'.*受付番号.*'
    ])
    error_patterns: List[str] = field(default_factory=lambda: [
        r'.*エラー.*', r'.*失敗.*', r'.*error.*', r'.*failed.*', r'.*問題.*'
    ])


@dataclass
class StorageConfig:
    """ストレージ設定"""
    base_directory: str = ""
    job_states_file: str = "job_states.json"
    config_file: str = "preflight_config.json"
    log_directory: str = "logs"
    temp_directory: str = "temp"
    backup_directory: str = "backup"
    
    def __post_init__(self):
        if not self.base_directory:
            self.base_directory = str(Path.home() / ".techzip" / "preflight")


@dataclass
class PreflightConfig:
    """Pre-flight統合設定"""
    # 基本情報
    version: str = "1.0.0"
    created_at: str = ""
    updated_at: str = ""
    
    # 各種設定
    email: EmailConfig = field(default_factory=EmailConfig)
    service: ServiceConfig = field(default_factory=ServiceConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    
    # 動作設定
    default_priority: JobPriority = JobPriority.NORMAL
    auto_retry: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()


class ConfigManager:
    """設定管理システム"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = get_logger(__name__)
        
        # 設定ファイルパス
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.home() / ".techzip" / "preflight" / "config.json"
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 設定をロード
        self._config: PreflightConfig = self._load_config()
        
        # 環境変数からの設定上書き
        self._apply_environment_variables()
    
    def _load_config(self) -> PreflightConfig:
        """設定ファイルから設定をロード"""
        if not self.config_path.exists():
            self.logger.info("設定ファイルが存在しません。デフォルト設定を作成します。")
            config = PreflightConfig()
            self._save_config(config)
            return config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 各セクションを復元
            config = PreflightConfig()
            
            if 'email' in data:
                config.email = EmailConfig(**data['email'])
            if 'service' in data:
                config.service = ServiceConfig(**data['service'])
            if 'validation' in data:
                val_data = data['validation'].copy()
                if 'mode' in val_data:
                    val_data['mode'] = VerificationMode(val_data['mode'])
                config.validation = ValidationConfig(**val_data)
            if 'monitoring' in data:
                config.monitoring = MonitoringConfig(**data['monitoring'])
            if 'storage' in data:
                config.storage = StorageConfig(**data['storage'])
            
            # 基本設定
            for key in ['version', 'created_at', 'updated_at', 'auto_retry', 'enable_logging', 'log_level']:
                if key in data:
                    setattr(config, key, data[key])
            
            if 'default_priority' in data:
                config.default_priority = JobPriority(data['default_priority'])
            
            self.logger.info(f"設定ファイル読み込み成功: {self.config_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"設定ファイル読み込みエラー: {e}")
            self.logger.info("デフォルト設定を使用します。")
            return PreflightConfig()
    
    def _save_config(self, config: PreflightConfig) -> None:
        """設定をファイルに保存"""
        try:
            # 辞書に変換
            data = asdict(config)
            
            # Enumを文字列に変換
            data['validation']['mode'] = config.validation.mode.value
            data['default_priority'] = config.default_priority.value
            
            # タイムスタンプ更新
            data['updated_at'] = datetime.now().isoformat()
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"設定ファイル保存成功: {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"設定ファイル保存エラー: {e}")
    
    def _apply_environment_variables(self) -> None:
        """環境変数から設定を上書き"""
        # メール設定
        if os.getenv('GMAIL_ADDRESS'):
            self._config.email.username = os.getenv('GMAIL_ADDRESS')
        if os.getenv('GMAIL_APP_PASSWORD'):
            self._config.email.password = os.getenv('GMAIL_APP_PASSWORD')
        
        # サービス設定
        if os.getenv('WORD2XHTML_URL'):
            self._config.service.service_url = os.getenv('WORD2XHTML_URL')
        if os.getenv('WORD2XHTML_USER'):
            self._config.service.auth_username = os.getenv('WORD2XHTML_USER')
        if os.getenv('WORD2XHTML_PASSWORD'):
            self._config.service.auth_password = os.getenv('WORD2XHTML_PASSWORD')
        
        # ログレベル
        if os.getenv('LOG_LEVEL'):
            self._config.log_level = os.getenv('LOG_LEVEL')
    
    @property
    def config(self) -> PreflightConfig:
        """設定を取得"""
        return self._config
    
    def get_email_config(self) -> EmailConfig:
        """メール設定を取得"""
        return self._config.email
    
    def get_service_config(self) -> ServiceConfig:
        """サービス設定を取得"""
        return self._config.service
    
    def get_validation_config(self) -> ValidationConfig:
        """検証設定を取得"""
        return self._config.validation
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """監視設定を取得"""
        return self._config.monitoring
    
    def get_storage_config(self) -> StorageConfig:
        """ストレージ設定を取得"""
        return self._config.storage
    
    def update_email_config(self, **kwargs) -> None:
        """メール設定を更新"""
        for key, value in kwargs.items():
            if hasattr(self._config.email, key):
                setattr(self._config.email, key, value)
        self._save_config(self._config)
    
    def update_service_config(self, **kwargs) -> None:
        """サービス設定を更新"""
        for key, value in kwargs.items():
            if hasattr(self._config.service, key):
                setattr(self._config.service, key, value)
        self._save_config(self._config)
    
    def update_validation_config(self, **kwargs) -> None:
        """検証設定を更新"""
        for key, value in kwargs.items():
            if hasattr(self._config.validation, key):
                if key == 'mode' and isinstance(value, str):
                    value = VerificationMode(value)
                setattr(self._config.validation, key, value)
        self._save_config(self._config)
    
    def update_monitoring_config(self, **kwargs) -> None:
        """監視設定を更新"""
        for key, value in kwargs.items():
            if hasattr(self._config.monitoring, key):
                setattr(self._config.monitoring, key, value)
        self._save_config(self._config)
    
    def set_verification_mode(self, mode: Union[VerificationMode, str]) -> None:
        """検証モードを設定"""
        if isinstance(mode, str):
            mode = VerificationMode(mode)
        self._config.validation.mode = mode
        self._save_config(self._config)
        self.logger.info(f"検証モード変更: {mode.value}")
    
    def add_custom_pattern(self, pattern: str) -> None:
        """カスタムパターンを追加"""
        if pattern not in self._config.validation.custom_patterns:
            self._config.validation.custom_patterns.append(pattern)
            self._save_config(self._config)
            self.logger.info(f"カスタムパターン追加: {pattern}")
    
    def remove_custom_pattern(self, pattern: str) -> bool:
        """カスタムパターンを削除"""
        if pattern in self._config.validation.custom_patterns:
            self._config.validation.custom_patterns.remove(pattern)
            self._save_config(self._config)
            self.logger.info(f"カスタムパターン削除: {pattern}")
            return True
        return False
    
    def get_verification_strategy_config(self) -> VerificationConfig:
        """検証戦略用の設定を取得"""
        val_config = self._config.validation
        return VerificationConfig(
            mode=val_config.mode,
            enable_file_validation=True,
            enable_security_check=val_config.enable_security_check,
            enable_content_analysis=val_config.enable_content_analysis,
            max_file_size_mb=val_config.max_file_size_mb,
            allowed_extensions=val_config.allowed_extensions.copy(),
            custom_patterns=val_config.custom_patterns.copy()
        )
    
    def validate_config(self) -> List[str]:
        """設定の妥当性をチェック"""
        issues = []
        
        # メール設定チェック
        if not self._config.email.is_valid():
            issues.append("メール設定が不完全です（ユーザー名またはパスワードが未設定）")
        
        # ファイルサイズ設定チェック
        if self._config.validation.max_file_size_mb <= 0:
            issues.append("最大ファイルサイズが無効です")
        
        if self._config.validation.min_file_size_bytes < 0:
            issues.append("最小ファイルサイズが無効です")
        
        # 拡張子設定チェック
        if not self._config.validation.allowed_extensions:
            issues.append("許可する拡張子が設定されていません")
        
        # URL設定チェック
        if not self._config.service.service_url.startswith('http'):
            issues.append("サービスURLが無効です")
        
        return issues
    
    def export_config(self, export_path: str) -> bool:
        """設定をエクスポート"""
        try:
            export_path_obj = Path(export_path)
            export_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            data = asdict(self._config)
            data['validation']['mode'] = self._config.validation.mode.value
            data['default_priority'] = self._config.default_priority.value
            data['exported_at'] = datetime.now().isoformat()
            
            with open(export_path_obj, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"設定エクスポート成功: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"設定エクスポートエラー: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """設定をインポート"""
        try:
            import_path_obj = Path(import_path)
            if not import_path_obj.exists():
                raise FileNotFoundError(f"インポートファイルが存在しません: {import_path}")
            
            with open(import_path_obj, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # バックアップを作成
            backup_path = self.config_path.with_suffix('.backup.json')
            self.export_config(str(backup_path))
            
            # 新しい設定を適用
            self._config = PreflightConfig()
            
            if 'email' in data:
                self._config.email = EmailConfig(**data['email'])
            if 'service' in data:
                self._config.service = ServiceConfig(**data['service'])
            # 他の設定も同様に復元...
            
            self._save_config(self._config)
            self.logger.info(f"設定インポート成功: {import_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"設定インポートエラー: {e}")
            return False


# グローバルインスタンス
_config_manager_instance: Optional[ConfigManager] = None

def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """設定管理システムのグローバルインスタンスを取得"""
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager(config_path)
    return _config_manager_instance