"""統合テストGUIアプリケーション
起動チェックと実稼働テストを統合したユーザーフレンドリーなインターフェース
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import time
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Callable
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.test_windows_powershell import WindowsPowerShellTestSuite
from core.preflight.unified_preflight_manager import create_preflight_manager
from core.preflight.verification_strategy import VerificationMode
from utils.logger import get_logger


class TestResult:
    """テスト結果データクラス"""
    def __init__(self, name: str, status: str = "pending", message: str = "", details: Dict = None):
        self.name = name
        self.status = status  # pending, running, success, failed
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()


class LogHandler:
    """ログハンドリングクラス"""
    def __init__(self, text_widget: scrolledtext.ScrolledText):
        self.text_widget = text_widget
        self.log_queue = queue.Queue()
        
    def write_log(self, message: str, level: str = "INFO"):
        """ログメッセージを追加"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        # キューに追加（スレッドセーフ）
        self.log_queue.put(formatted_message)
        
    def update_display(self):
        """ログ表示を更新（メインスレッドから呼び出し）"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.text_widget.insert(tk.END, message)
                self.text_widget.see(tk.END)
        except queue.Empty:
            pass


class IntegratedTestGUI:
    """統合テストGUIアプリケーション"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("TechZip Pre-flight Checker - 統合テストGUI")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # アプリケーション状態
        self.is_testing = False
        self.test_results: Dict[str, TestResult] = {}
        self.selected_files: List[str] = []
        
        # ログハンドラー
        self.log_handler = None
        
        # UI要素への参照
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="準備完了")
        
        self.setup_ui()
        self.setup_logger()
        
        # 定期的なログ更新
        self.root.after(100, self.update_log_display)
        
    def setup_ui(self):
        """UI要素のセットアップ"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 列の重みを設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # タイトル
        title_label = ttk.Label(
            main_frame, 
            text="TechZip Pre-flight Checker",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 左パネル：テスト制御
        self.setup_control_panel(main_frame)
        
        # 右パネル：テスト結果とログ
        self.setup_results_panel(main_frame)
        
        # 下部：プログレスバーとステータス
        self.setup_status_panel(main_frame)
        
    def setup_control_panel(self, parent):
        """制御パネルのセットアップ"""
        control_frame = ttk.LabelFrame(parent, text="テスト制御", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 環境チェックセクション
        env_frame = ttk.LabelFrame(control_frame, text="環境チェック", padding="5")
        env_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(
            env_frame,
            text="システム環境確認",
            command=self.run_environment_check
        ).grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Button(
            env_frame,
            text="依存関係チェック",
            command=self.run_dependency_check
        ).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # テストファイル選択セクション
        file_frame = ttk.LabelFrame(control_frame, text="テストファイル", padding="5")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(
            file_frame,
            text="DOCXファイル選択",
            command=self.select_test_files
        ).grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        self.file_count_label = ttk.Label(file_frame, text="選択ファイル: 0個")
        self.file_count_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # 検証モード選択
        mode_frame = ttk.LabelFrame(control_frame, text="検証モード", padding="5")
        mode_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.verification_mode = tk.StringVar(value="standard")
        ttk.Radiobutton(
            mode_frame, 
            text="標準検証", 
            variable=self.verification_mode, 
            value="standard"
        ).grid(row=0, column=0, sticky=tk.W)
        
        ttk.Radiobutton(
            mode_frame, 
            text="高速検証", 
            variable=self.verification_mode, 
            value="quick"
        ).grid(row=1, column=0, sticky=tk.W)
        
        ttk.Radiobutton(
            mode_frame, 
            text="厳密検証", 
            variable=self.verification_mode, 
            value="strict"
        ).grid(row=2, column=0, sticky=tk.W)
        
        # メール設定
        email_frame = ttk.LabelFrame(control_frame, text="メール設定", padding="5")
        email_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(email_frame, text="メールアドレス:").grid(row=0, column=0, sticky=tk.W)
        self.email_var = tk.StringVar(value="test@example.com")
        ttk.Entry(email_frame, textvariable=self.email_var, width=25).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # 実行ボタン
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.run_button = ttk.Button(
            button_frame,
            text="完全テスト実行",
            command=self.run_full_test,
            style="Accent.TButton"
        )
        self.run_button.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        self.stop_button = ttk.Button(
            button_frame,
            text="テスト停止",
            command=self.stop_test,
            state="disabled"
        )
        self.stop_button.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # 列の重みを設定
        control_frame.columnconfigure(0, weight=1)
        env_frame.columnconfigure(0, weight=1)
        file_frame.columnconfigure(0, weight=1)
        mode_frame.columnconfigure(0, weight=1)
        email_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(0, weight=1)
        
    def setup_results_panel(self, parent):
        """結果パネルのセットアップ"""
        results_frame = ttk.LabelFrame(parent, text="テスト結果とログ", padding="10")
        results_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ノートブック（タブ）
        notebook = ttk.Notebook(results_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # テスト結果タブ
        results_tab = ttk.Frame(notebook)
        notebook.add(results_tab, text="テスト結果")
        
        # ツリービューでテスト結果を表示
        self.results_tree = ttk.Treeview(
            results_tab,
            columns=("status", "message", "time"),
            show="tree headings"
        )
        self.results_tree.heading("#0", text="テスト項目")
        self.results_tree.heading("status", text="状態")
        self.results_tree.heading("message", text="メッセージ")
        self.results_tree.heading("time", text="実行時刻")
        
        # 列幅設定
        self.results_tree.column("#0", width=200)
        self.results_tree.column("status", width=80)
        self.results_tree.column("message", width=200)
        self.results_tree.column("time", width=100)
        
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # スクロールバー
        results_scrollbar = ttk.Scrollbar(results_tab, orient="vertical", command=self.results_tree.yview)
        results_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        # ログタブ
        log_tab = ttk.Frame(notebook)
        notebook.add(log_tab, text="実行ログ")
        
        self.log_text = scrolledtext.ScrolledText(
            log_tab,
            wrap=tk.WORD,
            width=60,
            height=20,
            font=("Consolas", 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ログクリアボタン
        log_clear_button = ttk.Button(log_tab, text="ログクリア", command=self.clear_log)
        log_clear_button.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # 重みを設定
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        results_tab.columnconfigure(0, weight=1)
        results_tab.rowconfigure(0, weight=1)
        log_tab.columnconfigure(0, weight=1)
        log_tab.rowconfigure(0, weight=1)
        
    def setup_status_panel(self, parent):
        """ステータスパネルのセットアップ"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # プログレスバー
        ttk.Label(status_frame, text="進行状況:").grid(row=0, column=0, sticky=tk.W)
        self.progress_bar = ttk.Progressbar(
            status_frame,
            variable=self.progress_var,
            maximum=100,
            length=300
        )
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10))
        
        # ステータスラベル
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=2, sticky=tk.W)
        
        # 重みを設定
        status_frame.columnconfigure(1, weight=1)
        
    def setup_logger(self):
        """ログハンドラーのセットアップ"""
        self.log_handler = LogHandler(self.log_text)
        
    def update_log_display(self):
        """ログ表示の定期更新"""
        if self.log_handler:
            self.log_handler.update_display()
        self.root.after(100, self.update_log_display)
        
    def log_message(self, message: str, level: str = "INFO"):
        """ログメッセージを追加"""
        if self.log_handler:
            self.log_handler.write_log(message, level)
        
    def clear_log(self):
        """ログをクリア"""
        self.log_text.delete(1.0, tk.END)
        
    def update_test_result(self, test_name: str, status: str, message: str = "", details: Dict = None):
        """テスト結果を更新"""
        result = TestResult(test_name, status, message, details)
        self.test_results[test_name] = result
        
        # ツリービューを更新
        self.update_results_tree()
        
    def update_results_tree(self):
        """結果ツリービューを更新"""
        # 既存のアイテムをクリア
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # 結果を追加
        for test_name, result in self.test_results.items():
            status_text = {
                "pending": "待機中",
                "running": "実行中",
                "success": "成功",
                "failed": "失敗"
            }.get(result.status, result.status)
            
            time_text = result.timestamp.strftime("%H:%M:%S")
            
            self.results_tree.insert(
                "", tk.END,
                text=test_name,
                values=(status_text, result.message, time_text)
            )
        
    def update_progress(self, value: float, status: str = None):
        """プログレス更新"""
        self.progress_var.set(value)
        if status:
            self.status_var.set(status)
        
    def select_test_files(self):
        """テストファイル選択"""
        files = filedialog.askopenfilenames(
            title="DOCXファイルを選択",
            filetypes=[("Word文書", "*.docx"), ("すべて", "*.*")]
        )
        
        if files:
            self.selected_files = list(files)
            self.file_count_label.config(text=f"選択ファイル: {len(files)}個")
            self.log_message(f"テストファイル選択: {len(files)}個")
            
            for file in files:
                self.log_message(f"  - {Path(file).name}")
        
    def run_environment_check(self):
        """環境チェック実行"""
        def check_task():
            self.log_message("環境チェック開始", "INFO")
            self.update_test_result("環境チェック", "running", "実行中...")
            
            try:
                # Python環境確認
                python_version = sys.version
                self.log_message(f"Python: {python_version}")
                
                # パッケージ確認
                required_packages = [
                    ('requests', 'requests'),
                    ('psutil', 'psutil'),
                    ('python-dotenv', 'dotenv')
                ]
                
                missing_packages = []
                for package_name, import_name in required_packages:
                    try:
                        __import__(import_name)
                        self.log_message(f"✓ {package_name} 利用可能")
                    except ImportError:
                        missing_packages.append(package_name)
                        self.log_message(f"✗ {package_name} 不足", "ERROR")
                
                if missing_packages:
                    self.update_test_result(
                        "環境チェック", 
                        "failed", 
                        f"不足パッケージ: {', '.join(missing_packages)}"
                    )
                else:
                    self.update_test_result("環境チェック", "success", "すべての依存関係OK")
                    
            except Exception as e:
                self.log_message(f"環境チェックエラー: {e}", "ERROR")
                self.update_test_result("環境チェック", "failed", str(e))
        
        threading.Thread(target=check_task, daemon=True).start()
        
    def run_dependency_check(self):
        """依存関係チェック実行"""
        def dependency_task():
            self.log_message("依存関係チェック開始", "INFO")
            self.update_test_result("依存関係チェック", "running", "実行中...")
            
            try:
                # 環境変数チェック
                gmail_address = os.getenv('GMAIL_ADDRESS')
                gmail_password = os.getenv('GMAIL_APP_PASSWORD')
                
                if gmail_address and gmail_password:
                    self.log_message("✓ メール設定確認済み")
                    self.update_test_result("依存関係チェック", "success", "設定完了")
                else:
                    self.log_message("⚠️ メール設定未完了", "WARNING")
                    self.update_test_result("依存関係チェック", "failed", "メール設定が必要")
                    
            except Exception as e:
                self.log_message(f"依存関係チェックエラー: {e}", "ERROR")
                self.update_test_result("依存関係チェック", "failed", str(e))
        
        threading.Thread(target=dependency_task, daemon=True).start()
        
    def run_full_test(self):
        """完全テスト実行"""
        if self.is_testing:
            return
            
        self.is_testing = True
        self.run_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        def test_task():
            try:
                self.log_message("完全テスト開始", "INFO")
                self.update_progress(0, "テスト開始")
                
                # Windows PowerShellテストスイート実行
                test_suite = WindowsPowerShellTestSuite()
                
                # テスト項目の初期化
                test_items = [
                    "環境セットアップ",
                    "Pre-flightマネージャー初期化", 
                    "ファイル検証パイプライン",
                    "パフォーマンス監視",
                    "エラー回復"
                ]
                
                for item in test_items:
                    self.update_test_result(item, "pending", "待機中")
                
                # 各テストを実行
                progress_step = 100 / len(test_items)
                
                for i, (test_name, test_method) in enumerate([
                    ("環境セットアップ", test_suite.test_environment_setup),
                    ("Pre-flightマネージャー初期化", test_suite.test_preflight_manager_initialization),
                    ("ファイル検証パイプライン", test_suite.test_file_validation_pipeline),
                    ("パフォーマンス監視", test_suite.test_performance_monitoring),
                    ("エラー回復", test_suite.test_error_recovery)
                ]):
                    if not self.is_testing:  # 停止チェック
                        break
                        
                    self.update_test_result(test_name, "running", "実行中...")
                    self.update_progress(i * progress_step, f"実行中: {test_name}")
                    self.log_message(f"テスト実行: {test_name}")
                    
                    try:
                        result = test_method()
                        if result:
                            self.update_test_result(test_name, "success", "完了")
                            self.log_message(f"✅ {test_name} 成功")
                        else:
                            self.update_test_result(test_name, "failed", "失敗")
                            self.log_message(f"❌ {test_name} 失敗", "ERROR")
                    except Exception as e:
                        self.update_test_result(test_name, "failed", str(e))
                        self.log_message(f"❌ {test_name} 例外: {e}", "ERROR")
                
                if self.is_testing:
                    self.update_progress(100, "テスト完了")
                    self.log_message("完全テスト完了", "INFO")
                    
                    # 結果サマリー
                    success_count = sum(1 for r in self.test_results.values() if r.status == "success")
                    total_count = len([r for r in self.test_results.values() if r.status in ["success", "failed"]])
                    
                    if success_count == total_count:
                        messagebox.showinfo("テスト完了", "すべてのテストが成功しました！")
                    else:
                        messagebox.showwarning("テスト完了", f"一部のテストが失敗しました。\n成功: {success_count}/{total_count}")
                        
            except Exception as e:
                self.log_message(f"テスト実行エラー: {e}", "ERROR")
                messagebox.showerror("エラー", f"テスト実行中にエラーが発生しました:\n{e}")
            finally:
                self.is_testing = False
                self.run_button.config(state="normal")
                self.stop_button.config(state="disabled")
        
        threading.Thread(target=test_task, daemon=True).start()
        
    def stop_test(self):
        """テスト停止"""
        self.is_testing = False
        self.log_message("テスト停止要求", "WARNING")
        self.update_progress(0, "テスト停止")
        
    def on_closing(self):
        """アプリケーション終了時の処理"""
        if self.is_testing:
            if messagebox.askokcancel("終了確認", "テストが実行中です。終了しますか？"):
                self.is_testing = False
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    """メイン実行関数"""
    # tkinterの初期化
    root = tk.Tk()
    
    # スタイル設定
    style = ttk.Style()
    
    # 利用可能なテーマを確認
    available_themes = style.theme_names()
    if 'clam' in available_themes:
        style.theme_use('clam')
    elif 'alt' in available_themes:
        style.theme_use('alt')
    
    # アプリケーション作成
    app = IntegratedTestGUI(root)
    
    # 終了時の処理を設定
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # アプリケーション開始ログ
    app.log_message("TechZip Pre-flight Checker GUI 起動", "INFO")
    app.log_message("統合テストGUIへようこそ", "INFO")
    
    # GUIループ開始
    root.mainloop()


if __name__ == "__main__":
    main()