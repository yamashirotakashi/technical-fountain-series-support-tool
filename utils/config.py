from __future__ import annotations
"""設定管理モジュール"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from utils.path_resolver import PathResolver
from utils.env_manager import EnvManager
from utils.logger import get_logger


class Config:
    """アプリケーション設定を管理するクラス"""
    
    def __init__(self, config_path: str = None):
        """
        設定を初期化
        
        Args:
            config_path: 設定ファイルのパス（省略時はデフォルトパスを使用）
        """
        self.logger = get_logger(__name__)
        
        # 環境変数管理システムを初期化
        EnvManager.initialize()
        
        if config_path is None:
            # PathResolverを使用して適切な設定ファイルパスを取得
            if PathResolver.is_exe_environment():
                # EXE環境ではユーザーディレクトリの設定を優先
                config_path = PathResolver.get_user_dir() / 'config' / 'settings.json'
                if not config_path.exists():
                    # バンドルされた設定を探す
                    config_file = PathResolver.resolve_config_file('settings.json')
                    if config_file:
                        config_path = config_file
                    else:
                        # どちらもない場合はユーザーディレクトリにデフォルトを作成
                        self._create_default_config(config_path)
            else:
                # 開発環境
                config_file = PathResolver.resolve_config_file('settings.json')
                if config_file:
                    config_path = config_file
                else:
                    config_path = PathResolver.get_config_path() / "settings.json"
                    self._create_default_config(config_path)
        
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _create_default_config(self, config_path: Path):
        """デフォルト設定ファイルを作成"""
        # EXE環境では既存の設定ファイルを上書きしない
        if PathResolver.is_exe_environment() and config_path.exists():
            self.logger.info(f"既存の設定ファイルが存在するため、デフォルト設定の作成をスキップ: {config_path}")
            return
        
        default_config = {
            "google_sheet": {
                "sheet_id": EnvManager.get("GOOGLE_SHEETS_ID", "YOUR_SHEET_ID_HERE"),
                "credentials_path": str(EnvManager.get_path("GOOGLE_SHEETS_CREDENTIALS_PATH", 
                                                           Path("config/techbook-analytics-aa03914c6639.json")))
            },
            "paths": {
                "git_base": "G:\\マイドライブ\\[git]",
                "output_base": "G:\\.shortcut-targets-by-id\\YOUR_FOLDER_ID\\NP-IRD"
            },
            "web": {
                "upload_url": "http://trial.nextpublishing.jp/reviewer/upload",
                "username": EnvManager.get("NEXTPUBLISHING_USERNAME", ""),
                "password": EnvManager.get("NEXTPUBLISHING_PASSWORD", "")
            },
            "email": {
                "gmail_credentials_path": str(PathResolver.get_config_path() / "gmail_oauth_credentials.json"),
                "gmail_address": EnvManager.get("GMAIL_ADDRESS", ""),
                "gmail_app_password": EnvManager.get("GMAIL_APP_PASSWORD", "")
            }
        }
        
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            self.logger.info(f"デフォルト設定ファイルを作成: {config_path}")
        except Exception as e:
            self.logger.error(f"デフォルト設定ファイルの作成に失敗: {e}")
    
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込む"""
        if not self.config_path.exists():
            self.logger.error(f"設定ファイルが見つかりません: {self.config_path}")
            return {}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
                # 環境変数で上書き（存在する場合）
                self._override_with_env_vars(config)
                
                return config
        except Exception as e:
            self.logger.error(f"設定ファイルの読み込みエラー: {e}")
            return {}
    
    def _override_with_env_vars(self, config: Dict[str, Any]):
        """環境変数で設定を上書き"""
        # Gmail設定
        if 'email' in config:
            if EnvManager.get('GMAIL_ADDRESS'):
                config['email']['gmail_address'] = EnvManager.get('GMAIL_ADDRESS')
            if EnvManager.get('GMAIL_APP_PASSWORD'):
                config['email']['gmail_app_password'] = EnvManager.get('GMAIL_APP_PASSWORD')
        
        # Google Sheets設定
        if 'google_sheet' in config:
            if EnvManager.get('GOOGLE_SHEETS_ID'):
                config['google_sheet']['sheet_id'] = EnvManager.get('GOOGLE_SHEETS_ID')
            if EnvManager.get('GOOGLE_SHEETS_CREDENTIALS_PATH'):
                config['google_sheet']['credentials_path'] = str(
                    EnvManager.get_path('GOOGLE_SHEETS_CREDENTIALS_PATH')
                )
        
        # NextPublishing設定
        if 'web' in config:
            if EnvManager.get('NEXTPUBLISHING_USERNAME'):
                config['web']['username'] = EnvManager.get('NEXTPUBLISHING_USERNAME')
            if EnvManager.get('NEXTPUBLISHING_PASSWORD'):
                config['web']['password'] = EnvManager.get('NEXTPUBLISHING_PASSWORD')
    
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
    
    def get_credentials_path(self) -> Optional[Path]:
        """Google認証情報ファイルのパスを取得（絶対パスに変換）"""
        # まず環境変数から取得を試みる
        env_path = EnvManager.get_path('GOOGLE_SHEETS_CREDENTIALS_PATH')
        if env_path and env_path.exists():
            self.logger.debug(f"環境変数からGoogle認証情報パスを取得: {env_path}")
            return env_path
        
        # EXE環境では設定ファイルを直接読む（キャッシュ問題を回避）
        if PathResolver.is_exe_environment():
            try:
                # 設定ファイルを直接読み込む
                import json
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    raw_config = json.load(f)
                
                if 'google_sheet' in raw_config and 'credentials_path' in raw_config['google_sheet']:
                    creds_path = raw_config['google_sheet']['credentials_path']
                    self.logger.debug(f"設定ファイルから直接読み込んだ認証パス: {creds_path}")
                else:
                    creds_path = None
            except Exception as e:
                self.logger.error(f"設定ファイルの直接読み込みエラー: {e}")
                creds_path = self.get('google_sheet.credentials_path')
        else:
            # 開発環境では通常通り
            creds_path = self.get('google_sheet.credentials_path')
        
        if creds_path:
            path = Path(creds_path)
            
            # EXE環境でのパス解決を改善
            if PathResolver.is_exe_environment():
                # 相対パスの場合の処理
                if not path.is_absolute():
                    # config/ファイル名 形式の場合
                    if str(path).startswith('config'):
                        # ユーザーディレクトリ内を確認
                        user_path = PathResolver.get_user_dir() / path
                        if user_path.exists():
                            self.logger.debug(f"ユーザーディレクトリから認証ファイルを検出: {user_path}")
                            return user_path
                    
                    # ファイル名のみでも検索
                    filename = path.name
                    # techbook-analytics-*.jsonパターンを優先
                    if 'techbook-analytics' in filename or filename == 'techbook-analytics-aa03914c6639.json':
                        user_path = PathResolver.get_user_dir() / 'config' / filename
                        if user_path.exists():
                            self.logger.debug(f"ユーザーディレクトリから認証ファイルを検出: {user_path}")
                            return user_path
                    
                    # 古い名前のファイルは無視（google_service_account.json）
                    if filename == 'google_service_account.json':
                        # 正しいファイルを探す
                        config_dir = PathResolver.get_user_dir() / 'config'
                        for json_file in config_dir.glob('techbook-analytics-*.json'):
                            self.logger.debug(f"正しい認証ファイルを発見: {json_file}")
                            return json_file
                    
                    # バンドルされたconfigディレクトリを確認
                    config_path = PathResolver.get_config_path(prefer_user_dir=False) / filename
                    if config_path.exists():
                        self.logger.debug(f"バンドルconfigから認証ファイルを検出: {config_path}")
                        return config_path
                else:
                    # 絶対パスの場合はそのまま使用
                    if path.exists():
                        return path
            else:
                # 開発環境での処理
                if not path.is_absolute():
                    # 設定ファイルからの相対パス
                    path = (self.config_path.parent / path).resolve()
                
                if path.exists():
                    return path
        
        # 見つからない場合はログ出力
        self.logger.warning(f"Google認証情報ファイルが見つかりません - 環境変数: {env_path}, 設定: {creds_path}")
        return None


# シングルトンインスタンス
_config_instance = None


def get_config() -> Config:
    """設定のシングルトンインスタンスを取得"""
    global _config_instance
    
    # EXE環境では常に新しいインスタンスを作成（キャッシュ問題を回避）
    if PathResolver.is_exe_environment() and _config_instance is None:
        _config_instance = Config()
    elif _config_instance is None:
        _config_instance = Config()
    
    return _config_instance


def reset_config():
    """設定のシングルトンインスタンスをリセット（再読み込み用）"""
    global _config_instance
    _config_instance = None
    # EnvManagerも再初期化
    EnvManager.initialize()