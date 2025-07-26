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
    
    @property
    def data(self) -> Dict[str, Any]:
        """設定データ全体を取得"""
        return self._config
    
    def save(self, data: Dict[str, Any] = None) -> None:
        """
        設定を保存
        
        Args:
            data: 保存するデータ（省略時は現在の設定を保存）
        """
        if data is not None:
            self._config = data
        
        # 設定ファイルのディレクトリが存在しない場合は作成
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 設定を保存
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, ensure_ascii=False, indent=2)
    
    def update(self, key_path: str, value: Any) -> None:
        """
        ドット記法で設定値を更新
        
        Args:
            key_path: 更新するキーのパス（例: "google_sheet.sheet_id"）
            value: 設定する値
        """
        keys = key_path.split('.')
        current = self._config
        
        # 最後のキーまで辿る（必要に応じて辞書を作成）
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # 値を設定
        current[keys[-1]] = value
    
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