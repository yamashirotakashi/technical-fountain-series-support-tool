"""
アプリケーションタイルウィジェット
Phase 1: ランチャーUIのアプリタイル表示
"""
import customtkinter as ctk
from typing import Callable, Optional
from pathlib import Path


class AppTile(ctk.CTkFrame):
    """アプリケーションタイル"""
    
    def __init__(self, 
                 parent,
                 name: str,
                 description: str,
                 version: str,
                 on_launch: Callable,
                 on_settings: Optional[Callable] = None,
                 icon_path: Optional[str] = None,
                 **kwargs):
        """
        Args:
            parent: 親ウィジェット
            name: アプリケーション名
            description: 説明
            version: バージョン
            on_launch: 起動時のコールバック
            on_settings: 設定時のコールバック（オプション）
            icon_path: アイコンパス（オプション）
        """
        super().__init__(parent, **kwargs)
        
        self.name = name
        self.on_launch = on_launch
        self.on_settings = on_settings
        self.is_running = False
        
        # タイルのスタイル設定
        self.configure(
            corner_radius=10,
            border_width=2,
            border_color=("gray70", "gray30")
        )
        
        self.setup_ui(name, description, version, icon_path)
        
    def setup_ui(self, name: str, description: str, version: str, icon_path: Optional[str]):
        """UIをセットアップ"""
        # パディング用のコンテナ
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # アイコン（将来実装）
        if icon_path and Path(icon_path).exists():
            # TODO: アイコン表示の実装
            pass
        else:
            # プレースホルダー
            icon_label = ctk.CTkLabel(
                container,
                text="📦",
                font=ctk.CTkFont(size=48)
            )
            icon_label.pack(pady=(0, 10))
        
        # アプリケーション名
        name_label = ctk.CTkLabel(
            container,
            text=name,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        name_label.pack()
        
        # バージョン
        version_label = ctk.CTkLabel(
            container,
            text=f"v{version}",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        version_label.pack()
        
        # 説明
        desc_label = ctk.CTkLabel(
            container,
            text=description,
            font=ctk.CTkFont(size=12),
            wraplength=200,
            justify="center"
        )
        desc_label.pack(pady=(10, 15))
        
        # ステータス表示
        self.status_label = ctk.CTkLabel(
            container,
            text="",
            font=ctk.CTkFont(size=11),
            height=20
        )
        self.status_label.pack()
        
        # ボタンフレーム
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(fill="x")
        
        # 起動ボタン
        self.launch_button = ctk.CTkButton(
            button_frame,
            text="起動",
            command=self._on_launch_clicked,
            width=80,
            height=32
        )
        self.launch_button.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        # 設定ボタン（オプション）
        if self.on_settings:
            settings_button = ctk.CTkButton(
                button_frame,
                text="⚙",
                command=self.on_settings,
                width=32,
                height=32,
                font=ctk.CTkFont(size=16)
            )
            settings_button.pack(side="right")
            
    def _on_launch_clicked(self):
        """起動ボタンクリック時の処理"""
        if not self.is_running:
            # 起動処理
            if self.on_launch:
                self.on_launch()
                self.set_running(True)
        else:
            # 停止処理（将来実装）
            pass
            
    def set_running(self, is_running: bool):
        """実行状態を設定"""
        self.is_running = is_running
        
        if is_running:
            self.launch_button.configure(text="実行中", state="disabled")
            self.status_label.configure(
                text="● 実行中",
                text_color="green"
            )
            # ボーダーの色を変更
            self.configure(border_color="green")
        else:
            self.launch_button.configure(text="起動", state="normal")
            self.status_label.configure(
                text="",
                text_color=("gray10", "gray90")
            )
            # ボーダーの色を戻す
            self.configure(border_color=("gray70", "gray30"))
            
    def set_status(self, status: str, color: str = None):
        """ステータステキストを設定"""
        self.status_label.configure(text=status)
        if color:
            self.status_label.configure(text_color=color)
            
    def update_info(self, name: str = None, description: str = None, version: str = None):
        """情報を更新"""
        # TODO: 動的な情報更新の実装
        pass