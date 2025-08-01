"""
TECHZIPプラグイン
Phase 1: 既存のTECHZIP機能をプラグイン化
"""
from typing import Dict, Any
import subprocess
import sys
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
        
    def _get_metadata(self) -> PluginMetadata:
        """プラグインのメタデータを返す"""
        return PluginMetadata(
            name="TECHZIP",
            version="1.0.0",
            description="Re:VIEWから超原稿用紙（Word）形式への自動変換",
            icon_path="assets/icons/techzip.png"
        )
        
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
            mode = config.get("mode", "standalone")
            
            if mode == "standalone":
                # スタンドアロンモード：既存のmain.pyを起動
                self.process = subprocess.Popen(
                    [sys.executable, "main.py"],
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
                self.process = subprocess.Popen(
                    [sys.executable, "app/ui/main_window_integrated.py"],
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
                self.process.wait(timeout=5)
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