"""
統一設定管理システム
Phase 1-3: プラグインとアプリケーション共通の設定管理
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import threading
from datetime import datetime


class SettingsManager:
    """統一された設定管理クラス"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """シングルトンパターンの実装"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初期化"""
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.project_root = Path(__file__).parent.parent.parent
        self.settings_dir = self.project_root / "config"
        self.settings_file = self.settings_dir / "techgate_settings.json"
        self.plugin_settings_dir = self.settings_dir / "plugins"
        
        # ディレクトリの作成
        self.settings_dir.mkdir(exist_ok=True)
        self.plugin_settings_dir.mkdir(exist_ok=True)
        
        # 設定の読み込み
        self.settings = self._load_settings()
        
    def _load_settings(self) -> Dict[str, Any]:
        """設定ファイルの読み込み"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"設定ファイル読み込みエラー: {e}")
                return self._get_default_settings()
        else:
            return self._get_default_settings()
            
    def _get_default_settings(self) -> Dict[str, Any]:
        """デフォルト設定の取得"""
        return {
            "version": "1.0.0",
            "app": {
                "theme": "dark",
                "language": "ja",
                "auto_update": True,
                "log_level": "INFO"
            },
            "paths": {
                "git_base": "G:\\マイドライブ\\[git]",
                "output_base": "G:\\.shortcut-targets-by-id\\0B6euJ_grVeOeMnJLU1IyUWgxeWM\\NP-IRD",
                "cache_dir": str(self.project_root / "cache"),
                "log_dir": str(self.project_root / "logs")
            },
            "google": {
                "sheet_id": "17DKsMGQ6krbhY7GIcX0iaeN-y8HcGGVkXt3d4oOckyQ",
                "credentials_path": "C:\\Users\\tky99\\dev\\techbookanalytics\\config\\techbook-analytics-aa03914c6639.json"
            },
            "email": {
                "enable_monitoring": True,
                "check_interval": 60  # seconds
            },
            "plugins": {
                "enabled": ["TechZipPlugin", "AnalyzerPlugin"],
                "auto_start": []
            },
            "last_updated": datetime.now().isoformat()
        }
        
    def save_settings(self) -> bool:
        """設定の保存"""
        try:
            # 最終更新日時を更新
            self.settings["last_updated"] = datetime.now().isoformat()
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"設定保存エラー: {e}")
            return False
            
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        ドット記法で設定値を取得
        
        Args:
            key_path: "app.theme" のようなドット区切りのキーパス
            default: キーが存在しない場合のデフォルト値
            
        Returns:
            設定値またはデフォルト値
        """
        keys = key_path.split('.')
        value = self.settings
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
        
    def set(self, key_path: str, value: Any) -> bool:
        """
        ドット記法で設定値を更新
        
        Args:
            key_path: "app.theme" のようなドット区切りのキーパス
            value: 設定する値
            
        Returns:
            成功フラグ
        """
        keys = key_path.split('.')
        target = self.settings
        
        # 最後のキーを除いて辿る
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
            
        # 値を設定
        target[keys[-1]] = value
        
        # 保存
        return self.save_settings()
        
    def get_plugin_settings(self, plugin_name: str) -> Dict[str, Any]:
        """
        プラグイン固有の設定を取得
        
        Args:
            plugin_name: プラグイン名
            
        Returns:
            プラグイン設定の辞書
        """
        plugin_file = self.plugin_settings_dir / f"{plugin_name}.json"
        
        if plugin_file.exists():
            try:
                with open(plugin_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"プラグイン設定読み込みエラー ({plugin_name}): {e}")
                
        return {}
        
    def save_plugin_settings(self, plugin_name: str, settings: Dict[str, Any]) -> bool:
        """
        プラグイン固有の設定を保存
        
        Args:
            plugin_name: プラグイン名
            settings: 保存する設定
            
        Returns:
            成功フラグ
        """
        plugin_file = self.plugin_settings_dir / f"{plugin_name}.json"
        
        try:
            with open(plugin_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"プラグイン設定保存エラー ({plugin_name}): {e}")
            return False
            
    def reset_to_default(self) -> bool:
        """設定をデフォルトにリセット"""
        self.settings = self._get_default_settings()
        return self.save_settings()
        
    def export_settings(self, export_path: Path) -> bool:
        """
        設定をエクスポート
        
        Args:
            export_path: エクスポート先のパス
            
        Returns:
            成功フラグ
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"設定エクスポートエラー: {e}")
            return False
            
    def import_settings(self, import_path: Path) -> bool:
        """
        設定をインポート
        
        Args:
            import_path: インポート元のパス
            
        Returns:
            成功フラグ
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported = json.load(f)
                
            # バリデーション（最小限のチェック）
            if not isinstance(imported, dict):
                raise ValueError("Invalid settings format")
                
            self.settings = imported
            return self.save_settings()
            
        except Exception as e:
            print(f"設定インポートエラー: {e}")
            return False
            
    def get_all_plugin_names(self) -> List[str]:
        """すべてのプラグイン設定ファイル名を取得"""
        plugin_files = self.plugin_settings_dir.glob("*.json")
        return [f.stem for f in plugin_files]


# グローバルインスタンス
settings_manager = SettingsManager()


# 使用例
if __name__ == "__main__":
    # 設定の取得
    theme = settings_manager.get("app.theme")
    print(f"現在のテーマ: {theme}")
    
    # 設定の更新
    settings_manager.set("app.theme", "light")
    print(f"更新後のテーマ: {settings_manager.get('app.theme')}")
    
    # プラグイン設定
    plugin_settings = {
        "auto_start": True,
        "window_size": [800, 600]
    }
    settings_manager.save_plugin_settings("TechZipPlugin", plugin_settings)
    
    # プラグイン設定の取得
    loaded = settings_manager.get_plugin_settings("TechZipPlugin")
    print(f"プラグイン設定: {loaded}")