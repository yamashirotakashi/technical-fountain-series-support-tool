"""
Unified Configuration Provider Interface
Phase 2: Configuration Hell Resolution
統一設定インターフェース実装

Architecture Pattern: Strategy + Adapter Pattern
- ConfigurationProvider: 統一インターフェース
- ConfigManagerAdapter: 新しいConfigManagerとの統合
- LegacyConfigAdapter: 既存Configシステムとの統合
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Union
from utils.logger import get_logger


class ConfigurationProvider(ABC):
    """統一設定提供インターフェース - SOLID原則準拠"""
    
    @abstractmethod
    def get(self, key_path: str, default: Any = None) -> Any:
        """ドット記法で設定値を取得"""
        pass
    
    @abstractmethod
    def set(self, key_path: str, value: Any) -> None:
        """設定値を更新"""
        pass
    
    @abstractmethod
    def get_section(self, section: str) -> Dict[str, Any]:
        """設定セクション全体を取得"""
        pass
    
    @abstractmethod
    def validate(self) -> Dict[str, list]:
        """設定の妥当性検証"""
        pass
    
    @abstractmethod
    def reload(self) -> None:
        """設定を再読み込み"""
        pass


class ConfigManagerAdapter(ConfigurationProvider):
    """新しいConfigManagerシステムのアダプター"""
    
    def __init__(self, config_manager=None):
        self.logger = get_logger(__name__)
        
        if config_manager:
            self._config_manager = config_manager
        else:
            from core.config_manager import get_config_manager
            self._config_manager = get_config_manager()
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """ドット記法で設定値を取得"""
        return self._config_manager.get(key_path, default)
    
    def set(self, key_path: str, value: Any) -> None:
        """設定値を更新"""
        self._config_manager.set(key_path, value)
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """設定セクション全体を取得"""
        if section == "api":
            return self._config_manager.get("api", {})
        elif section == "paths":
            return self._config_manager.get_path_config()
        elif section == "web":
            # API > NextPublishing設定をWebセクションとしてマッピング
            np_config = self._config_manager.get_api_config("nextpublishing")
            return {
                "upload_url": np_config.get("base_url", ""),
                "username": np_config.get("username", ""),
                "password": np_config.get("password", "")
            }
        else:
            return self._config_manager.get(section, {})
    
    def validate(self) -> Dict[str, list]:
        """設定の妥当性検証"""
        return self._config_manager.validate_config()
    
    def reload(self) -> None:
        """設定を再読み込み"""
        self._config_manager._load_config()


class LegacyConfigAdapter(ConfigurationProvider):
    """既存のConfigシステムのアダプター - 後方互換性確保"""
    
    def __init__(self, config=None):
        self.logger = get_logger(__name__)
        
        if config:
            self._config = config
        else:
            from utils.config import get_config
            self._config = get_config()
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """ドット記法で設定値を取得"""
        return self._config.get(key_path, default)
    
    def set(self, key_path: str, value: Any) -> None:
        """設定値を更新"""
        self._config.update(key_path, value)
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """設定セクション全体を取得"""
        if section == "web":
            return self._config.get_web_config()
        elif section == "api":
            # Legacy系では api.nextpublishing 相当をwebとして扱う
            web_config = self._config.get_web_config()
            return {
                "nextpublishing": {
                    "base_url": web_config.get("upload_url", ""),
                    "username": web_config.get("username", ""),
                    "password": web_config.get("password", "")
                }
            }
        elif section == "paths":
            return self._config.get_paths_config()
        elif section == "email":
            return self._config.get_email_config()
        elif section == "google_sheet":
            return self._config.get_google_sheet_config()
        else:
            return self._config.get(section, {})
    
    def validate(self) -> Dict[str, list]:
        """設定の妥当性検証 - 基本的な検証のみ"""
        errors = []
        warnings = []
        missing_env_vars = []
        
        # 基本的な必須設定チェック
        web_config = self.get_section("web")
        if not web_config.get("upload_url"):
            errors.append("web.upload_url が設定されていません")
        
        paths_config = self.get_section("paths")
        if not paths_config.get("git_base"):
            warnings.append("paths.git_base が設定されていません")
        
        return {
            "errors": errors,
            "warnings": warnings,
            "missing_env_vars": missing_env_vars
        }
    
    def reload(self) -> None:
        """設定を再読み込み"""
        from utils.config import reset_config
        reset_config()
        from utils.config import get_config
        self._config = get_config()


class UnifiedConfigurationService:
    """統一設定サービス - Singleton Pattern"""
    
    _instance: Optional['UnifiedConfigurationService'] = None
    _provider: Optional[ConfigurationProvider] = None
    
    def __new__(cls) -> 'UnifiedConfigurationService':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.logger = get_logger(__name__)
        if self._provider is None:
            self._initialize_provider()
    
    def _initialize_provider(self) -> None:
        """設定プロバイダーを初期化 - 自動選択ロジック"""
        try:
            # 新しいConfigManagerが利用可能かチェック
            config_yaml_path = Path("config/techzip_config.yaml")
            
            if config_yaml_path.exists() or os.getenv("TECHZIP_USE_NEW_CONFIG"):
                # 新しいConfigManagerを使用
                self.logger.info("新しいConfigManagerシステムを使用します")
                self._provider = ConfigManagerAdapter()
                self._config_type = "ConfigManager"
            else:
                # 既存のConfigシステムを使用
                self.logger.info("既存のConfigシステムを使用します（後方互換性）")
                self._provider = LegacyConfigAdapter()
                self._config_type = "LegacyConfig"
                
        except Exception as e:
            self.logger.warning(f"ConfigManager初期化失敗、Legacyシステムにフォールバック: {e}")
            self._provider = LegacyConfigAdapter()
            self._config_type = "LegacyConfig"
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """統一設定値取得インターフェース"""
        return self._provider.get(key_path, default)
    
    def set(self, key_path: str, value: Any) -> None:
        """統一設定値更新インターフェース"""
        self._provider.set(key_path, value)
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """統一設定セクション取得インターフェース"""
        return self._provider.get_section(section)
    
    def validate(self) -> Dict[str, list]:
        """統一設定検証インターフェース"""
        return self._provider.validate()
    
    def reload(self) -> None:
        """統一設定再読み込みインターフェース"""
        self._provider.reload()
    
    def get_provider_info(self) -> Dict[str, str]:
        """現在の設定プロバイダー情報を取得"""
        return {
            "provider_type": self._config_type,
            "provider_class": type(self._provider).__name__
        }
    
    # 後方互換性のためのメソッド
    def get_web_config(self) -> Dict[str, Any]:
        """Web設定を取得 - 後方互換性"""
        return self.get_section("web")
    
    def get_api_config(self, service: str = None) -> Dict[str, Any]:
        """API設定を取得 - 後方互換性"""
        if service:
            return self.get(f"api.{service}", {})
        return self.get_section("api")
    
    def get_paths_config(self) -> Dict[str, Any]:
        """パス設定を取得 - 後方互換性"""
        return self.get_section("paths")


# シングルトンインスタンス取得関数
def get_unified_config() -> UnifiedConfigurationService:
    """統一設定サービスのシングルトンインスタンスを取得"""
    return UnifiedConfigurationService()


# 後方互換性のための関数群
def get_config_provider() -> ConfigurationProvider:
    """設定プロバイダーを直接取得（高度な使用例向け）"""
    service = get_unified_config()
    return service._provider


def get_web_config() -> Dict[str, Any]:
    """Web設定を取得 - 後方互換性関数"""
    return get_unified_config().get_web_config()


def get_api_config(service: str = None) -> Dict[str, Any]:
    """API設定を取得 - 後方互換性関数"""
    return get_unified_config().get_api_config(service)


def get_paths_config() -> Dict[str, Any]:
    """パス設定を取得 - 後方互換性関数"""
    return get_unified_config().get_paths_config()