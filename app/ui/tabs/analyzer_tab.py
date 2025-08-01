"""
Book Analyzerタブ
Phase 0-3: TechBook27 AnalyzerのUI統合
"""
import customtkinter as ctk
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# from app.modules.techbook27_analyzer.ui.analyzer_window import AnalyzerWindow
# Phase 0-3では直接実装するため、インポートを一時的にコメントアウト


class AnalyzerTab(ctk.CTkFrame):
    """Book Analyzerタブ"""
    
    def __init__(self, parent, **kwargs):
        """
        Args:
            parent: 親ウィジェット
        """
        super().__init__(parent, **kwargs)
        
        # Analyzerウィンドウの内容を埋め込む
        self.setup_ui()
        
    def setup_ui(self):
        """UIをセットアップ"""
        # タイトルラベル
        title_label = ctk.CTkLabel(
            self,
            text="TechBook27 Analyzer",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        # 説明ラベル
        desc_label = ctk.CTkLabel(
            self,
            text="技術書の画像処理とWord文書処理を行います",
            font=ctk.CTkFont(size=14)
        )
        desc_label.pack(pady=(0, 20))
        
        # Analyzerウィンドウの主要コンポーネントを作成
        # （AnalyzerWindowクラスから必要な部分を抽出）
        self.create_analyzer_components()
        
    def create_analyzer_components(self):
        """Analyzerのコンポーネントを作成"""
        # 入力フレーム
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=20, pady=10)
        
        # フォルダ選択
        folder_label = ctk.CTkLabel(input_frame, text="処理対象フォルダ:")
        folder_label.pack(side="left", padx=5)
        
        self.folder_var = ctk.StringVar()
        folder_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.folder_var,
            width=400
        )
        folder_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        browse_button = ctk.CTkButton(
            input_frame,
            text="参照",
            command=self.browse_folder,
            width=80
        )
        browse_button.pack(side="left", padx=5)
        
        # オプションフレーム
        options_frame = ctk.CTkFrame(self)
        options_frame.pack(fill="x", padx=20, pady=10)
        
        # オプションチェックボックス
        self.process_images_var = ctk.BooleanVar(value=True)
        images_check = ctk.CTkCheckBox(
            options_frame,
            text="画像処理を実行",
            variable=self.process_images_var
        )
        images_check.pack(side="left", padx=10)
        
        self.process_word_var = ctk.BooleanVar(value=True)
        word_check = ctk.CTkCheckBox(
            options_frame,
            text="Word文書処理を実行",
            variable=self.process_word_var
        )
        word_check.pack(side="left", padx=10)
        
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
        
    def browse_folder(self):
        """フォルダ選択ダイアログを表示"""
        from tkinter import filedialog
        folder = filedialog.askdirectory(title="処理対象フォルダを選択")
        if folder:
            self.folder_var.set(folder)
            self.log_message(f"フォルダを選択しました: {folder}")
            
    def start_processing(self):
        """処理を開始"""
        folder = self.folder_var.get()
        if not folder:
            self.log_message("エラー: フォルダが選択されていません", "ERROR")
            return
            
        self.log_message("処理を開始します...")
        
        # オプションを取得
        process_images = self.process_images_var.get()
        process_word = self.process_word_var.get()
        
        if not process_images and not process_word:
            self.log_message("エラー: 少なくとも1つの処理を選択してください", "ERROR")
            return
            
        # ここで実際の処理を実装
        # （Phase 1で実装予定）
        self.log_message(f"フォルダ: {folder}")
        self.log_message(f"画像処理: {'有効' if process_images else '無効'}")
        self.log_message(f"Word処理: {'有効' if process_word else '無効'}")
        self.log_message("（実際の処理はPhase 1で実装予定）")
        
    def log_message(self, message: str, level: str = "INFO"):
        """ログメッセージを表示"""
        self.log_text.insert("end", f"[{level}] {message}\n")
        self.log_text.see("end")  # 最新行にスクロール