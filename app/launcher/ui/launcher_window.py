"""
TECHGATEランチャーメインウィンドウ
Phase 1: ランチャーUI実装
"""
import customtkinter as ctk
from typing import Dict, Optional
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.launcher.ui.app_tile import AppTile
from app.launcher.plugin_loader import PluginLoader
from app.plugins.base_plugin import BasePlugin


class LauncherWindow(ctk.CTk):
    """TECHGATEランチャーのメインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        
        self.title("TECHGATE - 技術の泉シリーズ支援ツール ランチャー")
        self.geometry("800x600")
        
        # アプリケーションの設定
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # プラグインローダー
        self.plugin_loader = PluginLoader()
        self.app_tiles: Dict[str, AppTile] = {}
        
        self.setup_ui()
        self.load_plugins()
        
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
        # ヘッダー
        header_frame = ctk.CTkFrame(self, height=80)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        # タイトル
        title_label = ctk.CTkLabel(
            header_frame,
            text="TECHGATE",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=20)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="技術の泉シリーズ支援ツール ランチャー",
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.pack(side="left", padx=(0, 20), pady=25)
        
        # リフレッシュボタン
        refresh_button = ctk.CTkButton(
            header_frame,
            text="🔄 更新",
            command=self.refresh_plugins,
            width=80,
            height=32
        )
        refresh_button.pack(side="right", padx=20)
        
        # メインコンテンツエリア
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # スクロール可能なフレーム
        self.scroll_frame = ctk.CTkScrollableFrame(content_frame)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # グリッドレイアウトの設定
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_columnconfigure(1, weight=1)
        self.scroll_frame.grid_columnconfigure(2, weight=1)
        
        # ステータスバー
        status_frame = ctk.CTkFrame(self, height=30)
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="準備完了",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10)
        
    def load_plugins(self):
        """プラグインを読み込んで表示"""
        self.update_status("プラグインを読み込み中...")
        
        # プラグインを探索
        plugin_names = self.plugin_loader.discover_plugins()
        
        row = 0
        col = 0
        
        for plugin_name in plugin_names:
            # プラグインをロード
            plugin = self.plugin_loader.load_plugin(plugin_name)
            if plugin:
                # アプリタイルを作成
                tile = self.create_app_tile(plugin, row, col)
                self.app_tiles[plugin_name] = tile
                
                # 次の位置を計算
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
                    
        # 将来のアプリ用プレースホルダー
        self.add_placeholder_tile(row, col)
        
        self.update_status(f"{len(plugin_names)}個のアプリを読み込みました")
        
    def create_app_tile(self, plugin: BasePlugin, row: int, col: int) -> AppTile:
        """プラグインからアプリタイルを作成"""
        metadata = plugin.metadata
        
        def on_launch():
            self.launch_plugin(plugin)
            
        def on_settings():
            self.show_plugin_settings(plugin)
            
        tile = AppTile(
            self.scroll_frame,
            name=metadata.name,
            description=metadata.description,
            version=metadata.version,
            on_launch=on_launch,
            on_settings=on_settings if plugin.get_config_schema() else None,
            icon_path=metadata.icon_path
        )
        
        tile.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # プラグインの状態を反映
        if plugin.is_running:
            tile.set_running(True)
            
        return tile
        
    def add_placeholder_tile(self, row: int, col: int):
        """将来のアプリ用プレースホルダー"""
        placeholder = ctk.CTkFrame(
            self.scroll_frame,
            corner_radius=10,
            border_width=2,
            border_color=("gray50", "gray40"),
            fg_color=("gray90", "gray20")
        )
        placeholder.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # 最小サイズを設定
        placeholder.configure(width=250, height=280)
        
        label = ctk.CTkLabel(
            placeholder,
            text="+ 新しいアプリ\n\n今後追加予定",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray60")
        )
        label.pack(expand=True)
        
    def launch_plugin(self, plugin: BasePlugin):
        """プラグインを起動"""
        self.update_status(f"{plugin.metadata.name}を起動中...")
        
        # デフォルト設定で起動
        config = {"mode": "integrated"}
        success = plugin.launch(config)
        
        if success:
            self.update_status(f"{plugin.metadata.name}を起動しました")
            # タイルの状態を更新
            plugin_name = plugin.__class__.__name__
            if plugin_name in self.app_tiles:
                self.app_tiles[plugin_name].set_running(True)
        else:
            self.update_status(f"{plugin.metadata.name}の起動に失敗しました")
            
    def show_plugin_settings(self, plugin: BasePlugin):
        """プラグイン設定ダイアログを表示"""
        # TODO: 設定ダイアログの実装
        from tkinter import messagebox
        messagebox.showinfo(
            f"{plugin.metadata.name} 設定",
            "設定機能は Phase 2 で実装予定です"
        )
        
    def refresh_plugins(self):
        """プラグインを再読み込み"""
        # 既存のタイルをクリア
        for tile in self.app_tiles.values():
            tile.destroy()
        self.app_tiles.clear()
        
        # 再読み込み
        self.load_plugins()
        
    def update_status(self, message: str):
        """ステータスバーを更新"""
        self.status_label.configure(text=message)
        self.update()
        
    def on_closing(self):
        """ウィンドウクローズ時の処理"""
        # 実行中のプラグインを停止
        for plugin in self.plugin_loader.get_loaded_plugins():
            if plugin.is_running:
                plugin.stop()
                
        self.destroy()


def main():
    """エントリーポイント"""
    app = LauncherWindow()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()