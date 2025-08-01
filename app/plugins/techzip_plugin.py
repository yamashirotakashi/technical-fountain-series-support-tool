"""
TECHZIPプラグイン
Phase 1: 既存のTECHZIP機能をプラグイン化
"""
from typing import Dict, Any
import subprocess
import sys
import os
from pathlib import Path
import threading

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.plugins.base_plugin import BasePlugin, PluginMetadata


class TechZipPlugin(BasePlugin):
    """TECHZIP（技術の泉シリーズ変換）プラグイン"""
    
    def __init__(self):
        super().__init__()
        self.process = None
        self.process_thread = None
        self.logger.info("TechZipプラグインが初期化されました")
        
    def _get_metadata(self) -> PluginMetadata:
        """プラグインのメタデータを返す"""
        return PluginMetadata(
            name="TECHZIP",
            version="1.0.0",
            description="Re:VIEWから超原稿用紙（Word）形式への自動変換",
            icon_path="assets/icons/techzip.png"
        )
        
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            "auto_start": False,
            "window_size": [1200, 800],
            "default_mode": "standalone"
        }
        
    def launch(self, config: Dict[str, Any]) -> bool:
        """
        TECHZIPを起動
        
        Args:
            config: 起動設定
                - mode: "integrated" or "standalone"
                - n_codes: 処理するNコードのリスト（integrated mode）
                
        Returns:
            起動成功フラグ
        """
        try:
            self.logger.info(f"TECHZIPを起動します: mode={config.get('mode', 'standalone')}")
            mode = config.get("mode", "standalone")
            
            if mode == "standalone":
                # スタンドアロンモード：既存のmain.pyを起動
                main_py_path = project_root / "main.py"
                if not main_py_path.exists():
                    raise FileNotFoundError(f"main.py not found at {main_py_path}")
                
                self.process = subprocess.Popen(
                    [sys.executable, str(main_py_path)],
                    cwd=project_root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.is_running = True
                
                # 出力監視スレッドを開始
                self.process_thread = threading.Thread(
                    target=self._monitor_process,
                    daemon=True
                )
                self.process_thread.start()
                
            elif mode == "integrated":
                # 統合モード：統合UIを起動
                integrated_ui_path = project_root / "app" / "ui" / "main_window_integrated.py"
                # パスの正規化とバリデーション
                integrated_ui_path = Path(os.path.normpath(str(integrated_ui_path)))
                
                # パスがプロジェクトルート内にあることを確認
                try:
                    integrated_ui_path.relative_to(project_root)
                except ValueError:
                    raise ValueError(f"Invalid path: {integrated_ui_path} is outside project root")
                
                if not integrated_ui_path.exists():
                    raise FileNotFoundError(f"integrated UI not found at {integrated_ui_path}")
                
                # ファイル読み取り権限の確認
                if not os.access(integrated_ui_path, os.R_OK):
                    raise PermissionError(f"Cannot read file: {integrated_ui_path}")
                
                self.process = subprocess.Popen(
                    [sys.executable, str(integrated_ui_path)],
                    cwd=project_root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.is_running = True
                
                # 出力監視スレッドを開始
                self.process_thread = threading.Thread(
                    target=self._monitor_process,
                    daemon=True
                )
                self.process_thread.start()
                
            self.logger.info("プラグインが正常に起動しました")
            return True
            
        except Exception as e:
            self.handle_error(e)
            return False
            
    def stop(self) -> bool:
        """
        TECHZIPを停止
        
        Returns:
            停止成功フラグ
        """
        try:
            if self.process:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"[{self.metadata.name}] 正常終了がタイムアウト、強制終了します")
                    self.process.kill()
                    self.process.wait()
                self.process = None
                self.is_running = False
            return True
        except Exception as e:
            self.handle_error(e)
            # 強制終了を試みる
            try:
                if self.process:
                    self.process.kill()
                    self.process = None
                    self.is_running = False
                return True
            except:
                return False
                
    def get_status(self) -> Dict[str, Any]:
        """
        プラグインの状態を取得
        
        Returns:
            状態情報の辞書
        """
        status = {
            "running": self.is_running,
            "name": self.metadata.name,
            "version": self.metadata.version
        }
        
        if self.process:
            status["pid"] = self.process.pid
            status["returncode"] = self.process.returncode
            
        return status
        
    def _monitor_process(self):
        """プロセスの出力を監視"""
        if not self.process:
            return
            
        try:
            # 標準出力を読み取り
            for line in self.process.stdout:
                print(f"[TECHZIP] {line.strip()}")
                
            # プロセス終了を待つ
            self.process.wait()
            self.is_running = False
            
        except Exception as e:
            self.handle_error(e)
            self.is_running = False
            
    def get_config_schema(self) -> Dict[str, Any]:
        """設定スキーマを取得"""
        return {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["standalone", "integrated"],
                    "default": "standalone",
                    "description": "起動モード"
                },
                "process_mode": {
                    "type": "string",
                    "enum": ["api", "traditional"],
                    "default": "api",
                    "description": "処理方式"
                }
            }
        }