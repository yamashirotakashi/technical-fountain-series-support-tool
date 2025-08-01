"""
統合メインウィンドウ
Phase 0-3: CustomTkinterベースのタブ統合UI
"""
import customtkinter as ctk
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.ui.tabs.process_tab import ProcessTab
from app.ui.tabs.analyzer_tab import AnalyzerTab
from app.ui.dialogs.git_auth_dialog import GitAuthDialog


class IntegratedMainWindow(ctk.CTk):
    """統合メインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        
        self.title("TECHZIP - 技術の泉シリーズ制作支援ツール")
        self.geometry("1200x800")
        
        # アプリケーションの設定
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.setup_ui()
        self.setup_menu()
        
        # ウィンドウを中央に配置
        self.center_window()
        
    def center_window(self):
        """ウィンドウを画面中央に配置"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_ui(self):
        """UIをセットアップ"""
        # メインコンテナ
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # タイトルフレーム
        title_frame = ctk.CTkFrame(main_container)
        title_frame.pack(fill="x", pady=(0, 10))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="TECHZIP - 技術の泉シリーズ制作支援ツール",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=10)
        
        version_label = ctk.CTkLabel(
            title_frame,
            text="Phase 0-3: 最小UI統合テスト",
            font=ctk.CTkFont(size=12)
        )
        version_label.pack()
        
        # タブビュー
        self.tabview = ctk.CTkTabview(main_container)
        self.tabview.pack(fill="both", expand=True)
        
        # タブを追加
        self.process_tab = self.tabview.add("処理実行")
        self.analyzer_tab = self.tabview.add("Book Analyzer")
        
        # 各タブのコンテンツを設定
        self.setup_process_tab()
        self.setup_analyzer_tab()
        
        # デフォルトタブを設定
        self.tabview.set("処理実行")
        
        # ステータスバー
        status_frame = ctk.CTkFrame(self)
        status_frame.pack(fill="x", side="bottom")
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="準備完了",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
    def setup_process_tab(self):
        """処理実行タブをセットアップ"""
        # ProcessTabクラスを使用
        process_widget = ProcessTab(self.process_tab)
        process_widget.pack(fill="both", expand=True)
        
    def setup_analyzer_tab(self):
        """Book Analyzerタブをセットアップ"""
        # AnalyzerTabクラスを使用
        analyzer_widget = AnalyzerTab(self.analyzer_tab)
        analyzer_widget.pack(fill="both", expand=True)
        
    def setup_menu(self):
        """メニューバーをセットアップ"""
        # CustomTkinterではメニューバーがないため、ボタンで代用
        menu_frame = ctk.CTkFrame(self)
        menu_frame.pack(fill="x", side="top")
        
        # ファイルメニュー
        file_button = ctk.CTkButton(
            menu_frame,
            text="ファイル",
            width=80,
            command=self.show_file_menu
        )
        file_button.pack(side="left", padx=2)
        
        # ツールメニュー
        tools_button = ctk.CTkButton(
            menu_frame,
            text="ツール",
            width=80,
            command=self.show_tools_menu
        )
        tools_button.pack(side="left", padx=2)
        
        # ヘルプメニュー
        help_button = ctk.CTkButton(
            menu_frame,
            text="ヘルプ",
            width=80,
            command=self.show_help_menu
        )
        help_button.pack(side="left", padx=2)
        
    def show_file_menu(self):
        """ファイルメニューを表示"""
        # 簡易的にメッセージボックスで代用
        from tkinter import messagebox
        messagebox.showinfo("ファイル", "ファイルメニュー（Phase 1で実装予定）")
        
    def show_tools_menu(self):
        """ツールメニューを表示"""
        # Git認証設定ダイアログを表示
        dialog = GitAuthDialog(self)
        self.wait_window(dialog)
        
    def show_help_menu(self):
        """ヘルプメニューを表示"""
        from tkinter import messagebox
        messagebox.showinfo(
            "バージョン情報",
            "TECHZIP - 技術の泉シリーズ制作支援ツール\n"
            "Phase 0-3: 最小UI統合テスト\n\n"
            "TechBook27 Analyzer統合版"
        )
        
    def update_status(self, message: str):
        """ステータスバーを更新"""
        self.status_label.configure(text=message)


def main():
    """エントリーポイント"""
    app = IntegratedMainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()