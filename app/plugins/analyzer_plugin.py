"""
TechBook27 Analyzerプラグイン
Phase 2: 完全統合されたTechBook27 Analyzer機能
- 共通機能との統合（設定管理、認証、ログ）
- 画像処理・Word処理の完全実装
- 統合UIとスタンドアロンUIの両対応
"""
from typing import Dict, Any, Optional
import subprocess
import sys
import os
from pathlib import Path
import threading
import customtkinter as ctk
import tkinter as tk

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
        self.analyzer_window = None
        self.logger.info("Analyzer Plugin (Phase 2) 初期化完了")
        
    def _get_metadata(self) -> PluginMetadata:
        """プラグインのメタデータを返す"""
        return PluginMetadata(
            name="TechBook27 Analyzer",
            version="2.0.0",
            description="統合された技術書画像・文書処理ツール（共通機能統合版）",
            icon_path="assets/icons/analyzer.png"
        )
        
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            "auto_start": False,
            "window_size": [1000, 800],
            "default_mode": "integrated",
            "processing_threads": 4,
            "image_processing": {
                "max_pixels": "400",
                "resolution": 100,
                "remove_profile": False,
                "grayscale": False,
                "change_resolution": True,
                "resize": True,
                "backup": True,
                "png_to_jpg": True
            },
            "word_processing": {
                "backup_original": True,
                "delete_first_line": True
            }
        }
        
    def launch(self, config: Dict[str, Any]) -> bool:
        """
        TechBook27 Analyzerを起動
        
        Args:
            config: 起動設定
                - mode: "standalone" or "integrated" (default: integrated)
                - target_folder: 処理対象フォルダ（オプション）
                
        Returns:
            起動成功フラグ
        """
        try:
            mode = config.get("mode", self.config.get("default_mode", "integrated"))
            self.logger.info(f"TechBook27 Analyzer起動: mode={mode}")
            
            if mode == "standalone":
                return self._launch_standalone_analyzer()
            else:
                return self._launch_integrated_analyzer()
                
        except Exception as e:
            self.handle_error(e)
            return False
            
    def _launch_standalone_analyzer(self) -> bool:
        """スタンドアロンAnalyzerを起動"""
        try:
            self.logger.info("Standalone Analyzer起動")
            
            # TechBook27 Analyzerメインファイルパス
            analyzer_main = project_root / "app" / "modules" / "techbook27_analyzer" / "main.py"
            analyzer_main = Path(os.path.normpath(str(analyzer_main)))
            
            # セキュリティ: パスがプロジェクトルート内にあることを確認
            try:
                analyzer_main.relative_to(project_root)
            except ValueError:
                raise ValueError(f"Security violation: {analyzer_main} outside project root")
            
            if not analyzer_main.exists():
                raise FileNotFoundError(f"Analyzer main not found: {analyzer_main}")
            
            self.process = subprocess.Popen(
                [sys.executable, str(analyzer_main)],
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.is_running = True
            
            # プロセス監視スレッド開始
            self.process_thread = threading.Thread(
                target=self._monitor_process,
                daemon=True
            )
            self.process_thread.start()
            
            self.logger.info("Standalone Analyzer起動完了")
            return True
            
        except Exception as e:
            self.logger.error(f"Standalone Analyzer起動失敗: {e}")
            return False
    
    def _launch_integrated_analyzer(self) -> bool:
        """統合Analyzerウィンドウを起動"""
        try:
            self.logger.info("Integrated Analyzer起動")
            
            # TechBook27 Analyzerウィンドウをインポート
            from app.modules.techbook27_analyzer.ui.analyzer_window import TechBook27AnalyzerWindow
            
            # 新しいスレッドでAnalyzerウィンドウを起動
            def run_analyzer():
                try:
                    self.analyzer_window = TechBook27AnalyzerWindow()
                    self.analyzer_window.mainloop()
                    self.is_running = False
                except Exception as e:
                    self.logger.error(f"Analyzer window error: {e}")
                    self.handle_error(e)
                    self.is_running = False
            
            self.process_thread = threading.Thread(target=run_analyzer, daemon=False)
            self.process_thread.start()
            self.is_running = True
            
            self.logger.info("Integrated Analyzer起動完了")
            return True
            
        except Exception as e:
            self.logger.error(f"Integrated Analyzer起動失敗: {e}")
            return False
            
    def stop(self) -> bool:
        """
        Analyzerを停止
        
        Returns:
            停止成功フラグ
        """
        try:
            self.logger.info("Analyzer停止中...")
            
            # 統合モードの場合はウィンドウを閉じる
            if self.analyzer_window:
                try:
                    self.analyzer_window.destroy()
                    self.analyzer_window = None
                except Exception as e:
                    self.logger.warning(f"Analyzer window close error: {e}")
            
            # スタンドアロンモードの場合はプロセスを終了
            if self.process:
                try:
                    self.process.terminate()
                    self.process.wait(timeout=5)
                    self.process = None
                except Exception as e:
                    # 強制終了を試みる
                    try:
                        self.process.kill()
                        self.process = None
                    except:
                        pass
            
            self.is_running = False
            self.logger.info("Analyzer停止完了")
            return True
            
        except Exception as e:
            self.handle_error(e)
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
            "version": self.metadata.version,
            "mode": "integrated" if self.analyzer_window else "standalone",
            "features": {
                "image_processing": True,
                "word_processing": True,
                "common_features": True
            }
        }
        
        if self.process:
            status["pid"] = self.process.pid
            status["returncode"] = self.process.returncode
            
        if self.analyzer_window:
            status["window_active"] = True
        
        # プラグイン固有の設定情報
        if hasattr(self, 'config'):
            status["config"] = {
                "default_mode": self.config.get("default_mode", "integrated"),
                "image_processing_enabled": bool(self.config.get("image_processing")),
                "word_processing_enabled": bool(self.config.get("word_processing"))
            }
            
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
                    "default": "integrated",
                    "description": "起動モード（統合UIまたはスタンドアロン）"
                },
                "window_size": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "default": [1000, 800],
                    "description": "ウィンドウサイズ [幅, 高さ]"
                },
                "processing_threads": {
                    "type": "integer",
                    "default": 4,
                    "minimum": 1,
                    "maximum": 16,
                    "description": "処理スレッド数"
                },
                "image_processing": {
                    "type": "object",
                    "properties": {
                        "max_pixels": {
                            "type": "string",
                            "default": "400",
                            "description": "最大画素数（万画素単位）"
                        },
                        "resolution": {
                            "type": "integer",
                            "default": 100,
                            "minimum": 1,
                            "maximum": 600,
                            "description": "解像度（DPI）"
                        },
                        "remove_profile": {
                            "type": "boolean",
                            "default": False,
                            "description": "カラープロファイル除去"
                        },
                        "grayscale": {
                            "type": "boolean",
                            "default": False,
                            "description": "グレースケール変換"
                        },
                        "change_resolution": {
                            "type": "boolean",
                            "default": True,
                            "description": "解像度変更を実行"
                        },
                        "resize": {
                            "type": "boolean",
                            "default": True,
                            "description": "最大画素数でリサイズ"
                        },
                        "backup": {
                            "type": "boolean",
                            "default": True,
                            "description": "処理前バックアップ作成"
                        },
                        "png_to_jpg": {
                            "type": "boolean",
                            "default": True,
                            "description": "PNG→JPG変換"
                        }
                    }
                },
                "word_processing": {
                    "type": "object",
                    "properties": {
                        "backup_original": {
                            "type": "boolean",
                            "default": True,
                            "description": "元ファイルのバックアップ作成"
                        },
                        "delete_first_line": {
                            "type": "boolean",
                            "default": True,
                            "description": "先頭行の削除を実行"
                        }
                    }
                },
                "target_folder": {
                    "type": "string",
                    "description": "デフォルト処理対象フォルダ（オプション）"
                }
            }
        }