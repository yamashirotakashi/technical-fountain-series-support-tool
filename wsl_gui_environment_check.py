#!/usr/bin/env python3
"""
WSL GUI環境調査スクリプト
PyQt6動作環境の詳細チェックとGUI環境構築支援

使用方法:
    python wsl_gui_environment_check.py

ログファイル出力: wsl_gui_check_YYYYMMDD_HHMMSS.log
"""

import sys
import os
import subprocess
import platform
import socket
from datetime import datetime
from pathlib import Path

class WSLEnvironmentChecker:
    def __init__(self):
        self.log_entries = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"wsl_gui_check_{self.timestamp}.log"
    
    def log(self, message, level="INFO"):
        """ログエントリを追加"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [{level}] {message}"
        self.log_entries.append(entry)
        print(entry)
    
    def run_command(self, command, description=""):
        """コマンド実行とログ記録"""
        self.log(f"実行中: {command}", "CMD")
        if description:
            self.log(f"目的: {description}")
        
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.log(f"成功: {result.stdout.strip()}", "OK")
                return result.stdout.strip()
            else:
                self.log(f"エラー (コード {result.returncode}): {result.stderr.strip()}", "ERROR")
                return None
                
        except subprocess.TimeoutExpired:
            self.log("タイムアウト (30秒)", "TIMEOUT")
            return None
        except FileNotFoundError:
            self.log("コマンドが見つかりません", "ERROR")
            return None
        except Exception as e:
            self.log(f"例外: {str(e)}", "ERROR")
            return None
    
    def check_basic_environment(self):
        """基本環境情報チェック"""
        self.log("=== 基本環境情報 ===")
        
        # プラットフォーム情報
        self.log(f"プラットフォーム: {platform.platform()}")
        self.log(f"アーキテクチャ: {platform.architecture()}")
        self.log(f"プロセッサ: {platform.processor()}")
        
        # WSL情報
        if Path("/proc/version").exists():
            with open("/proc/version", "r") as f:
                version_info = f.read().strip()
                self.log(f"カーネル: {version_info}")
                
                # WSL2判定
                if "microsoft" in version_info.lower():
                    if "WSL2" in version_info:
                        self.log("WSL2環境を検出", "OK")
                    else:
                        self.log("WSL1環境を検出", "INFO")
                else:
                    self.log("ネイティブLinux環境", "INFO")
        
        # Python環境
        self.log(f"Python版: {sys.version}")
        self.log(f"Python実行パス: {sys.executable}")
    
    def check_display_environment(self):
        """ディスプレイ環境チェック"""
        self.log("=== ディスプレイ環境チェック ===")
        
        # DISPLAY環境変数
        display = os.getenv("DISPLAY")
        if display:
            self.log(f"DISPLAY環境変数: {display}", "OK")
        else:
            self.log("DISPLAY環境変数が設定されていません", "WARN")
        
        # WAYLAND環境変数
        wayland_display = os.getenv("WAYLAND_DISPLAY")
        if wayland_display:
            self.log(f"WAYLAND_DISPLAY: {wayland_display}", "OK")
        else:
            self.log("WAYLAND_DISPLAY未設定（X11モード想定）", "INFO")
        
        # WSLg関連環境変数
        wslg_vars = ["PULSE_RUNTIME_PATH", "XDG_RUNTIME_DIR", "WSLENV"]
        for var in wslg_vars:
            value = os.getenv(var)
            if value:
                self.log(f"{var}: {value}", "INFO")
            else:
                self.log(f"{var}: 未設定", "INFO")
    
    def check_x11_connectivity(self):
        """X11サーバー接続テスト"""
        self.log("=== X11サーバー接続テスト ===")
        
        display = os.getenv("DISPLAY", ":0")
        
        # xdpyinfoでX11サーバー情報取得
        self.run_command("xdpyinfo", "X11サーバー情報取得")
        
        # xeyes簡易テスト（GUIアプリ起動テスト）
        self.run_command("which xeyes", "xeyesコマンド存在確認")
        
        # xclock簡易テスト
        self.run_command("which xclock", "xclockコマンド存在確認")
    
    def check_python_gui_packages(self):
        """Python GUI関連パッケージチェック"""
        self.log("=== Python GUIパッケージチェック ===")
        
        # 重要パッケージのインポートテスト
        packages_to_check = [
            ("tkinter", "標準GUIライブラリ"),
            ("PyQt6.QtCore", "PyQt6コア"),
            ("PyQt6.QtWidgets", "PyQt6ウィジェット"),
            ("PyQt6.QtGui", "PyQt6 GUI"),
            ("PySide6.QtCore", "PySide6コア"),
            ("matplotlib", "matplotlib"),
            ("PIL", "Pillow/PIL")
        ]
        
        for package, description in packages_to_check:
            try:
                __import__(package)
                self.log(f"{package}: インポート成功 - {description}", "OK")
            except ImportError as e:
                self.log(f"{package}: インポート失敗 - {str(e)}", "WARN")
    
    def check_system_packages(self):
        """システムパッケージチェック"""
        self.log("=== システムパッケージチェック ===")
        
        # X11関連パッケージ
        x11_packages = [
            "xorg-dev",
            "libx11-dev", 
            "libxext-dev",
            "libxrender-dev",
            "libxtst6",
            "libxrandr2",
            "libxi6",
            "x11-apps",
            "x11-utils"
        ]
        
        for package in x11_packages:
            self.run_command(f"dpkg -l {package}", f"パッケージ確認: {package}")
    
    def test_simple_gui(self):
        """簡単なGUIテスト"""
        self.log("=== 簡単なGUIテスト ===")
        
        # tkinter簡易テスト
        self.log("tkinter簡易テスト実行中...")
        tkinter_test = '''
import tkinter as tk
import sys

try:
    root = tk.Tk()
    root.withdraw()  # ウィンドウを隠す
    root.quit()
    root.destroy()
    print("tkinter: GUI初期化成功")
    sys.exit(0)
except Exception as e:
    print(f"tkinter: エラー - {str(e)}")
    sys.exit(1)
'''
        
        try:
            result = subprocess.run(
                [sys.executable, "-c", tkinter_test],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.log("tkinter: GUI初期化テスト成功", "OK")
            else:
                self.log(f"tkinter: GUI初期化テスト失敗 - {result.stderr.strip()}", "ERROR")
        except Exception as e:
            self.log(f"tkinter: テスト実行エラー - {str(e)}", "ERROR")
    
    def generate_recommendations(self):
        """環境構築推奨事項生成"""
        self.log("=== 環境構築推奨事項 ===")
        
        display = os.getenv("DISPLAY")
        
        if not display:
            self.log("推奨: X11サーバー環境構築が必要", "RECOMMEND")
            self.log("方法1: WSLg利用（Windows 11推奨）")
            self.log("  - Windows 11 22H2以降でWSL2を使用")
            self.log("  - wsl --update でWSLを最新に更新")
            self.log("方法2: VcXsrv利用")
            self.log("  - VcXsrvをダウンロード・インストール")
            self.log("  - 設定: Disable access control を有効化")
            self.log("  - ~/.bashrcに以下を追加:")
            self.log('    export DISPLAY=$(awk \'/nameserver / {print $2; exit}\' /etc/resolv.conf 2>/dev/null):0')
            self.log('    export LIBGL_ALWAYS_INDIRECT=1')
        
        # PyQt6インストール推奨
        try:
            import PyQt6
            self.log("PyQt6: インストール済み", "OK")
        except ImportError:
            self.log("推奨: PyQt6インストール", "RECOMMEND")
            self.log("  pip install PyQt6")
    
    def save_log(self):
        """ログファイル保存"""
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write(f"WSL GUI環境調査レポート\n")
                f.write(f"実行日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
                f.write(f"{'='*60}\n\n")
                
                for entry in self.log_entries:
                    f.write(entry + "\n")
            
            self.log(f"ログファイル保存完了: {self.log_file}", "OK")
            return self.log_file
        except Exception as e:
            self.log(f"ログファイル保存エラー: {str(e)}", "ERROR")
            return None
    
    def run_full_check(self):
        """完全チェック実行"""
        self.log("WSL GUI環境調査を開始します", "START")
        
        try:
            self.check_basic_environment()
            self.check_display_environment()
            self.check_x11_connectivity()
            self.check_python_gui_packages()
            self.check_system_packages()
            self.test_simple_gui()
            self.generate_recommendations()
            
            self.log("WSL GUI環境調査完了", "COMPLETE")
            
        except KeyboardInterrupt:
            self.log("ユーザーによる中断", "INTERRUPT")
        except Exception as e:
            self.log(f"予期しないエラー: {str(e)}", "FATAL")
        
        finally:
            log_file = self.save_log()
            print(f"\n調査完了！ログファイル: {log_file}")
            print("このログファイルをClaude Codeに提供してください。")

def main():
    """メイン関数"""
    print("WSL GUI環境調査スクリプト")
    print("=" * 50)
    
    checker = WSLEnvironmentChecker()
    checker.run_full_check()

if __name__ == "__main__":
    main()