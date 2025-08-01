"""
基底ウィンドウクラス
単一責任: 共通UI機能の提供
"""
import customtkinter as ctk
from typing import Optional, Callable
import tkinter as tk
from abc import ABC, abstractmethod


class BaseWindow(ctk.CTk, ABC):
    """基底ウィンドウクラス"""
    
    def __init__(self, title: str = "Application", 
                 width: int = 1000, height: int = 800):
        """
        Args:
            title: ウィンドウタイトル
            width: ウィンドウ幅
            height: ウィンドウ高さ
        """
        super().__init__()
        
        # ウィンドウ設定
        self.title(title)
        self.geometry(f"{width}x{height}")
        
        # テーマ設定
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # 閉じるボタンのハンドラー
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # UIを構築
        self.setup_ui()
        
    @abstractmethod
    def setup_ui(self) -> None:
        """UIをセットアップ（サブクラスで実装）"""
        pass
        
    def on_closing(self) -> None:
        """ウィンドウを閉じる時の処理"""
        if self.confirm_close():
            self.destroy()
            
    def confirm_close(self) -> bool:
        """
        終了確認
        
        Returns:
            bool: 終了してよいか
        """
        return True
        
    def show_error(self, title: str, message: str) -> None:
        """エラーダイアログを表示"""
        ctk.messagebox.showerror(title, message)
        
    def show_info(self, title: str, message: str) -> None:
        """情報ダイアログを表示"""
        ctk.messagebox.showinfo(title, message)
        
    def show_warning(self, title: str, message: str) -> None:
        """警告ダイアログを表示"""
        ctk.messagebox.showwarning(title, message)
        
    def ask_yes_no(self, title: str, message: str) -> bool:
        """Yes/Noダイアログを表示"""
        return ctk.messagebox.askyesno(title, message)


class FramedSection(ctk.CTkFrame):
    """セクション用フレーム"""
    
    def __init__(self, parent, title: Optional[str] = None, **kwargs):
        """
        Args:
            parent: 親ウィジェット
            title: セクションタイトル
            **kwargs: CTkFrameの追加引数
        """
        super().__init__(parent, **kwargs)
        
        if title:
            self.title_label = ctk.CTkLabel(
                self, 
                text=title,
                font=ctk.CTkFont(size=14, weight="bold")
            )
            self.title_label.pack(pady=(5, 10), padx=10, anchor="w")
            
        # コンテンツ用フレーム
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    def get_content_frame(self) -> ctk.CTkFrame:
        """コンテンツフレームを取得"""
        return self.content_frame