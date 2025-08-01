"""
プラグイン基底クラス
Phase 1-3: 共通機能統合版
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
import json
import sys

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 共通機能のインポート
from app.common import settings_manager, auth_manager, get_logger


class PluginMetadata:
    """プラグインのメタデータ"""
    
    def __init__(self, 
                 name: str,
                 version: str,
                 description: str,
                 author: str = "TECHGATE Team",
                 icon_path: Optional[str] = None):
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.icon_path = icon_path
        
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "icon_path": self.icon_path
        }


class BasePlugin(ABC):
    """プラグインの基底クラス（共通機能統合版）"""
    
    def __init__(self):
        self.metadata = self._get_metadata()
        self.is_running = False
        self.config = {}
        
        # 共通機能の初期化
        self.logger = get_logger(
            f"plugin.{self.__class__.__name__}",
            plugin_name=self.__class__.__name__
        )
        
        # プラグイン設定の読み込み
        self.config = settings_manager.get_plugin_settings(self.__class__.__name__)
        if not self.config:
            self.config = self._get_default_config()
            settings_manager.save_plugin_settings(self.__class__.__name__, self.config)
        
    @abstractmethod
    def _get_metadata(self) -> PluginMetadata:
        """プラグインのメタデータを返す"""
        pass
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        デフォルト設定を返す（オーバーライド可能）
        
        Returns:
            デフォルト設定の辞書
        """
        return {}
        
    @abstractmethod
    def launch(self, config: Dict[str, Any]) -> bool:
        """
        プラグインを起動
        
        Args:
            config: 起動設定
            
        Returns:
            起動成功フラグ
        """
        pass
        
    @abstractmethod
    def stop(self) -> bool:
        """
        プラグインを停止
        
        Returns:
            停止成功フラグ
        """
        pass
        
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        プラグインの状態を取得
        
        Returns:
            状態情報の辞書
        """
        pass
        
    def configure(self, config: Dict[str, Any]) -> None:
        """
        プラグインを設定
        
        Args:
            config: 設定情報
        """
        self.config.update(config)
        # 設定を保存
        settings_manager.save_plugin_settings(self.__class__.__name__, self.config)
        self.logger.info(f"設定を更新しました: {config}")
        
    def get_config_schema(self) -> Dict[str, Any]:
        """
        設定スキーマを取得（オプション）
        
        Returns:
            JSON Schema形式の設定スキーマ
        """
        return {}
        
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        設定の妥当性を検証
        
        Args:
            config: 検証する設定
            
        Returns:
            妥当性フラグ
        """
        # デフォルトでは常にTrue
        return True
        
    def get_logs(self, lines: int = 100) -> str:
        """
        プラグインのログを取得（オプション）
        
        Args:
            lines: 取得する行数
            
        Returns:
            ログ文字列
        """
        return ""
        
    def handle_error(self, error: Exception) -> None:
        """
        エラーハンドリング
        
        Args:
            error: 発生したエラー
        """
        self.logger.error(f"エラーが発生しました: {error}", exc_info=True)
        
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.metadata.name} v{self.metadata.version}>"