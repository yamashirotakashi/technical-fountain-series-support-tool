"""
Git認証設定ダイアログ
Phase 0-3: Git認証UIの実装
"""
import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.common.auth.git_auth_manager import GitAuthManager, AuthConfig


class GitAuthDialog(ctk.CTkToplevel):
    """Git認証設定ダイアログ"""
    
    def __init__(self, parent):
        """
        Args:
            parent: 親ウィンドウ
        """
        super().__init__(parent)
        
        self.title("Git認証設定")
        self.geometry("600x400")
        self.resizable(False, False)
        
        # モーダルダイアログにする
        self.transient(parent)
        self.grab_set()
        
        # 認証マネージャー
        self.auth_manager = GitAuthManager()
        
        self.setup_ui()
        self.load_current_settings()
        
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
        # タイトル
        title_label = ctk.CTkLabel(
            self,
            text="Git認証設定",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # 説明
        desc_label = ctk.CTkLabel(
            self,
            text="GitHubへのアクセスに使用する認証情報を設定します",
            font=ctk.CTkFont(size=12)
        )
        desc_label.pack(pady=(0, 20))
        
        # 認証方式選択フレーム
        method_frame = ctk.CTkFrame(self)
        method_frame.pack(fill="x", padx=20, pady=10)
        
        method_label = ctk.CTkLabel(
            method_frame,
            text="認証方式:",
            font=ctk.CTkFont(size=14)
        )
        method_label.pack(anchor="w", padx=5, pady=5)
        
        self.method_var = ctk.StringVar(value="pat")
        
        pat_radio = ctk.CTkRadioButton(
            method_frame,
            text="Personal Access Token (推奨)",
            variable=self.method_var,
            value="pat",
            command=self.on_method_changed
        )
        pat_radio.pack(anchor="w", padx=20, pady=2)
        
        env_radio = ctk.CTkRadioButton(
            method_frame,
            text="環境変数",
            variable=self.method_var,
            value="env",
            command=self.on_method_changed
        )
        env_radio.pack(anchor="w", padx=20, pady=2)
        
        # 認証情報入力フレーム
        self.auth_frame = ctk.CTkFrame(self)
        self.auth_frame.pack(fill="x", padx=20, pady=10)
        
        # ユーザー名
        username_label = ctk.CTkLabel(self.auth_frame, text="ユーザー名:")
        username_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.username_entry = ctk.CTkEntry(self.auth_frame, width=300)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # トークン/パスワード
        token_label = ctk.CTkLabel(self.auth_frame, text="Personal Access Token:")
        token_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        self.token_entry = ctk.CTkEntry(self.auth_frame, width=300, show="*")
        self.token_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # テスト結果表示
        self.result_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.result_label.pack(pady=10)
        
        # ボタンフレーム
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        test_button = ctk.CTkButton(
            button_frame,
            text="接続テスト",
            command=self.test_connection,
            width=100
        )
        test_button.pack(side="left", padx=5)
        
        save_button = ctk.CTkButton(
            button_frame,
            text="保存",
            command=self.save_settings,
            width=100
        )
        save_button.pack(side="left", padx=5)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="キャンセル",
            command=self.destroy,
            width=100
        )
        cancel_button.pack(side="right", padx=5)
        
    def on_method_changed(self):
        """認証方式が変更されたときの処理"""
        method = self.method_var.get()
        if method == "env":
            # 環境変数モードでは入力を無効化
            self.username_entry.configure(state="disabled")
            self.token_entry.configure(state="disabled")
            self.result_label.configure(
                text="環境変数 GIT_USERNAME と GIT_TOKEN を使用します",
                text_color="gray"
            )
        else:
            # PAT モードでは入力を有効化
            self.username_entry.configure(state="normal")
            self.token_entry.configure(state="normal")
            self.result_label.configure(text="", text_color="white")
            
    def load_current_settings(self):
        """現在の設定を読み込む"""
        creds = self.auth_manager.get_credentials()
        if creds:
            auth_type = creds.get("auth_type", "")
            if auth_type == "env":
                self.method_var.set("env")
                self.on_method_changed()
            else:
                self.method_var.set("pat")
                self.username_entry.insert(0, creds.get("username", ""))
                # トークンは表示しない（セキュリティのため）
                if creds.get("password"):
                    self.token_entry.insert(0, "********")
                    
    def test_connection(self):
        """接続テストを実行"""
        self.result_label.configure(text="接続テスト中...", text_color="yellow")
        self.update()
        
        if self.auth_manager.test_connection("https://github.com"):
            self.result_label.configure(text="✓ 接続成功", text_color="green")
        else:
            self.result_label.configure(text="✗ 接続失敗", text_color="red")
            
    def save_settings(self):
        """設定を保存"""
        method = self.method_var.get()
        
        if method == "pat":
            username = self.username_entry.get().strip()
            token = self.token_entry.get().strip()
            
            if not username or not token:
                messagebox.showerror("エラー", "ユーザー名とトークンを入力してください")
                return
                
            # "********" の場合は保存をスキップ（既存の設定を維持）
            if token != "********":
                success = self.auth_manager.save_credentials(username, token)
                if success:
                    messagebox.showinfo("成功", "認証情報を保存しました")
                    self.destroy()
                else:
                    messagebox.showerror("エラー", "認証情報の保存に失敗しました")
            else:
                # トークンが変更されていない場合はそのまま閉じる
                self.destroy()
        else:
            # 環境変数モードの場合は特に保存する必要なし
            messagebox.showinfo("情報", "環境変数モードが選択されました")
            self.destroy()