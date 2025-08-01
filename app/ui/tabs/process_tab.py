"""
処理実行タブ（既存機能のラッパー）
Phase 0-3: 既存のMainWindowの機能をタブとして分離
"""
import customtkinter as ctk
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal
from pathlib import Path
import sys


class ProcessTab(ctk.CTkFrame):
    """処理実行タブ（既存機能）"""
    
    # シグナル定義（PyQt6のMainWindowとの連携用）
    start_processing_requested = pyqtSignal(list, str)  # n_codes, process_mode
    
    def __init__(self, parent, main_window=None, **kwargs):
        """
        Args:
            parent: 親ウィジェット
            main_window: 既存のMainWindowインスタンス（PyQt6）
        """
        super().__init__(parent, **kwargs)
        self.main_window = main_window
        self.setup_ui()
        
    def setup_ui(self):
        """UIをセットアップ"""
        # タイトルラベル
        title_label = ctk.CTkLabel(
            self,
            text="技術の泉シリーズ 変換処理",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        # 説明ラベル
        desc_label = ctk.CTkLabel(
            self,
            text="Re:VIEWから超原稿用紙（Word）形式への自動変換",
            font=ctk.CTkFont(size=14)
        )
        desc_label.pack(pady=(0, 20))
        
        # 入力フレーム
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=20, pady=10)
        
        # Nコード入力
        ncode_label = ctk.CTkLabel(input_frame, text="Nコード:")
        ncode_label.pack(anchor="w", padx=5, pady=5)
        
        self.ncode_text = ctk.CTkTextbox(input_frame, height=100)
        self.ncode_text.pack(fill="x", padx=5, pady=5)
        self.ncode_text.insert("1.0", "# Nコードを入力（カンマ、タブ、スペース、改行区切り）\n# 例: N02279, N02280")
        
        # 処理モード選択
        mode_frame = ctk.CTkFrame(self)
        mode_frame.pack(fill="x", padx=20, pady=10)
        
        mode_label = ctk.CTkLabel(mode_frame, text="処理モード:")
        mode_label.pack(side="left", padx=5)
        
        self.mode_var = ctk.StringVar(value="api")
        api_radio = ctk.CTkRadioButton(
            mode_frame,
            text="API方式（推奨）",
            variable=self.mode_var,
            value="api"
        )
        api_radio.pack(side="left", padx=10)
        
        traditional_radio = ctk.CTkRadioButton(
            mode_frame,
            text="従来方式（メール監視）",
            variable=self.mode_var,
            value="traditional"
        )
        traditional_radio.pack(side="left", padx=10)
        
        # 処理ボタン
        process_button = ctk.CTkButton(
            self,
            text="処理開始",
            command=self.start_processing,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        process_button.pack(pady=20)
        
        # ログ表示エリア
        log_frame = ctk.CTkFrame(self)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        log_label = ctk.CTkLabel(log_frame, text="処理ログ:")
        log_label.pack(anchor="w", padx=5, pady=5)
        
        self.log_text = ctk.CTkTextbox(log_frame, height=200)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
    def start_processing(self):
        """処理を開始"""
        # Nコードを取得
        ncode_text = self.ncode_text.get("1.0", "end-1c")
        n_codes = []
        
        for line in ncode_text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # カンマ、タブ、スペースで分割
                codes = line.replace(',', ' ').replace('\t', ' ').split()
                n_codes.extend(codes)
        
        if not n_codes:
            self.log_message("エラー: Nコードが入力されていません", "ERROR")
            return
            
        # 処理モードを取得
        process_mode = self.mode_var.get()
        
        self.log_message(f"処理を開始します: {', '.join(n_codes)}")
        self.log_message(f"処理モード: {process_mode}")
        
        # 既存のMainWindowの処理を呼び出す（Phase 1で実装）
        if self.main_window:
            # PyQt6のMainWindowとの連携
            self.start_processing_requested.emit(n_codes, process_mode)
        else:
            # スタンドアロンモード（テスト用）
            self.log_message("（実際の処理はPhase 1で実装予定）")
            
    def log_message(self, message: str, level: str = "INFO"):
        """ログメッセージを表示"""
        self.log_text.insert("end", f"[{level}] {message}\n")
        self.log_text.see("end")  # 最新行にスクロール
        
    def append_log_from_main(self, message: str, level: str = "INFO"):
        """MainWindowからのログを受け取る"""
        self.log_message(message, level)