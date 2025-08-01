"""
プラグインローダー
Phase 1: 動的プラグイン読み込みシステム
"""
import importlib
import importlib.util
import inspect
from typing import Dict, List, Type, Optional
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.plugins.base_plugin import BasePlugin


class PluginLoader:
    """プラグインを動的に読み込むクラス"""
    
    def __init__(self, plugin_dir: Path = None):
        """
        Args:
            plugin_dir: プラグインディレクトリ（デフォルト: app/plugins）
        """
        if plugin_dir is None:
            plugin_dir = project_root / "app" / "plugins"
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Type[BasePlugin]] = {}
        self.loaded_plugins: Dict[str, BasePlugin] = {}
        
    def discover_plugins(self) -> List[str]:
        """
        プラグインディレクトリからプラグインを探索
        
        Returns:
            発見したプラグイン名のリスト
        """
        discovered = []
        
        # プラグインディレクトリ内のPythonファイルを探索
        for file_path in self.plugin_dir.glob("*_plugin.py"):
            # base_plugin.pyはスキップ
            if file_path.name == "base_plugin.py":
                continue
            module_name = file_path.stem
            
            try:
                # セキュリティ: プラグインファイルの権限チェック
                # WSL環境では全てのファイルが777権限となるため、WSL環境では権限チェックをスキップ
                import stat
                import platform
                
                if platform.system() != "Windows" and not any(wsl_indicator in platform.release().lower() for wsl_indicator in ["microsoft", "wsl"]):
                    file_stat = file_path.stat()
                    # 書き込み権限を持つのは所有者のみであることを確認
                    if file_stat.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
                        print(f"セキュリティ警告: プラグインファイルに不適切な権限 ({module_name})")
                        continue
                
                # ホワイトリスト検証
                allowed_plugins = [
                    "techzip_plugin", "analyzer_plugin", "base_plugin",
                    # 将来の拡張用にプラグイン名を追加
                ]
                if module_name not in allowed_plugins:
                    print(f"未承認のプラグイン: {module_name}")
                    continue
                
                # モジュールを動的にインポート
                spec = importlib.util.spec_from_file_location(
                    f"app.plugins.{module_name}",
                    file_path
                )
                if not spec or not spec.loader:
                    print(f"プラグインスペック作成失敗: {module_name}")
                    continue
                    
                module = importlib.util.module_from_spec(spec)
                if not module:
                    print(f"プラグインモジュール作成失敗: {module_name}")
                    continue
                    
                sys.modules[f"app.plugins.{module_name}"] = module
                spec.loader.exec_module(module)
                
                # BasePluginのサブクラスを探す
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BasePlugin) and 
                        obj != BasePlugin):
                        self.plugins[name] = obj
                        discovered.append(name)
                            
            except Exception as e:
                print(f"プラグイン読み込みエラー ({module_name}): {e}")
                
        return discovered
        
    def load_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        プラグインをロード（インスタンス化）
        
        Args:
            plugin_name: プラグイン名
            
        Returns:
            プラグインインスタンス
        """
        if plugin_name in self.loaded_plugins:
            return self.loaded_plugins[plugin_name]
            
        if plugin_name not in self.plugins:
            print(f"プラグインが見つかりません: {plugin_name}")
            return None
            
        try:
            # プラグインをインスタンス化
            plugin_class = self.plugins[plugin_name]
            plugin_instance = plugin_class()
            self.loaded_plugins[plugin_name] = plugin_instance
            return plugin_instance
            
        except Exception as e:
            print(f"プラグインロードエラー ({plugin_name}): {e}")
            return None
            
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        プラグインをアンロード
        
        Args:
            plugin_name: プラグイン名
            
        Returns:
            成功フラグ
        """
        if plugin_name not in self.loaded_plugins:
            return False
            
        try:
            plugin = self.loaded_plugins[plugin_name]
            
            # 実行中の場合は停止
            if plugin.is_running:
                plugin.stop()
                
            # インスタンスを削除
            del self.loaded_plugins[plugin_name]
            return True
            
        except Exception as e:
            print(f"プラグインアンロードエラー ({plugin_name}): {e}")
            return False
            
    def get_loaded_plugins(self) -> List[BasePlugin]:
        """
        ロード済みのプラグインリストを取得
        
        Returns:
            プラグインインスタンスのリスト
        """
        return list(self.loaded_plugins.values())
        
    def get_available_plugins(self) -> List[str]:
        """
        利用可能なプラグイン名のリストを取得
        
        Returns:
            プラグイン名のリスト
        """
        return list(self.plugins.keys())
        
    def reload_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        プラグインを再読み込み
        
        Args:
            plugin_name: プラグイン名
            
        Returns:
            再読み込みされたプラグインインスタンス
        """
        # アンロード
        self.unload_plugin(plugin_name)
        
        # プラグインクラスをリロード
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            
        # 再探索
        self.discover_plugins()
        
        # 再ロード
        return self.load_plugin(plugin_name)


# 使用例
if __name__ == "__main__":
    loader = PluginLoader()
    
    # プラグインを探索
    print("プラグインを探索中...")
    plugins = loader.discover_plugins()
    print(f"発見したプラグイン: {plugins}")
    
    # プラグインをロード
    for plugin_name in plugins:
        plugin = loader.load_plugin(plugin_name)
        if plugin:
            print(f"ロード成功: {plugin.metadata.name} v{plugin.metadata.version}")