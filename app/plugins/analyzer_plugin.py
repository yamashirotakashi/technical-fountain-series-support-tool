"""
TechBook27 Analyzerプラグイン
Phase 1: TechBook27 Analyzer機能をプラグイン化
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


class AnalyzerPlugin(BasePlugin):
    """TechBook27 Analyzer プラグイン"""
    
    def __init__(self):
        super().__init__()
        self.process = None
        self.process_thread = None
        
    def _get_metadata(self) -> PluginMetadata:
        """プラグインのメタデータを返す"""
        return PluginMetadata(
            name="TechBook27 Analyzer",
            version="1.0.0",
            description="技術書の画像処理とWord文書処理を行うツール",
            icon_path="assets/icons/analyzer.png"
        )
        
    def launch(self, config: Dict[str, Any]) -> bool:
        """
        Analyzerを起動
        
        Args:
            config: 起動設定
                - mode: "standalone" or "integrated"
                - target_folder: 処理対象フォルダ（オプション）
                
        Returns:
            起動成功フラグ
        """
        try:
            mode = config.get("mode", "standalone")
            
            if mode == "standalone":
                # スタンドアロンモード：独立したAnalyzerウィンドウを起動
                analyzer_main = project_root / "app" / "modules" / "techbook27_analyzer" / "main.py"
                # パスの正規化とバリデーション
                analyzer_main = Path(os.path.normpath(str(analyzer_main)))
                
                # パスがプロジェクトルート内にあることを確認
                try:
                    analyzer_main.relative_to(project_root)
                except ValueError:
                    raise ValueError(f"Invalid path: {analyzer_main} is outside project root")
                
                if analyzer_main.exists():
                    self.process = subprocess.Popen(
                        [sys.executable, str(analyzer_main)],
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
                else:
                    # ファイルが存在しない場合は統合UIを起動
                    return self._launch_integrated_ui()
                    
            elif mode == "integrated":
                # 統合モード：統合UIのAnalyzerタブを表示
                return self._launch_integrated_ui()
                
            return True
            
        except Exception as e:
            self.handle_error(e)
            return False
            
    def _launch_integrated_ui(self) -> bool:
        """統合UIを起動してAnalyzerタブを表示"""
        try:
            # 統合UIを起動（TODO: タブ選択の実装）
            integrated_ui_path = project_root / "app" / "ui" / "main_window_integrated.py"
            if not integrated_ui_path.exists():
                raise FileNotFoundError(f"Integrated UI not found at {integrated_ui_path}")
            
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
            
            return True
        except Exception as e:
            self.handle_error(e)
            return False
            
    def stop(self) -> bool:
        """
        Analyzerを停止
        
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
                print(f"[Analyzer] {line.strip()}")
                
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
                "process_images": {
                    "type": "boolean",
                    "default": True,
                    "description": "画像処理を実行"
                },
                "process_word": {
                    "type": "boolean",
                    "default": True,
                    "description": "Word文書処理を実行"
                },
                "target_folder": {
                    "type": "string",
                    "description": "処理対象フォルダ（オプション）"
                }
            }
        }