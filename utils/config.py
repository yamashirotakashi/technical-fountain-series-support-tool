"""設定管理モジュール"""
import json
import os
from pathlib import Path
from typing import Any, Dict


class Config:
    """アプリケーション設定を管理するクラス"""
    
    def __init__(self, config_path: str = None):
        """
        設定を初期化
        
        Args:
            config_path: 設定ファイルのパス（省略時はデフォルトパスを使用）
        """
        if config_path is None:
            # デフォルトの設定ファイルパスを構築
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "settings.json"
        
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込む"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"設定ファイルが見つかりません: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        ドット記法で設定値を取得
        
        Args:
            key_path: 取得するキーのパス（例: "google_sheet.sheet_id"）
            default: キーが存在しない場合のデフォルト値
        
        Returns:
            設定値
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_google_sheet_config(self) -> Dict[str, str]:
        """Google Sheet関連の設定を取得"""
        return self._config.get('google_sheet', {})
    
    def get_paths_config(self) -> Dict[str, str]:
        """パス関連の設定を取得"""
        return self._config.get('paths', {})
    
    def get_web_config(self) -> Dict[str, str]:
        """Web関連の設定を取得"""
        return self._config.get('web', {})
    
    def get_email_config(self) -> Dict[str, Any]:
        """メール関連の設定を取得"""
        return self._config.get('email', {})
    
    def get_credentials_path(self) -> Path:
        """Google認証情報ファイルのパスを取得（絶対パスに変換）"""
        creds_path = self.get('google_sheet.credentials_path')
        if creds_path:
            path = Path(creds_path)
            if not path.is_absolute():
                # 相対パスの場合は設定ファイルからの相対パスとして解決
                path = (self.config_path.parent / path).resolve()
            return path
        return None


# シングルトンインスタンス
_config_instance = None


def get_config() -> Config:
    """設定のシングルトンインスタンスを取得"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance