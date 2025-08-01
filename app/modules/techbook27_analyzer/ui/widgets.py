"""
カスタムウィジェット
単一責任: 再利用可能なUI部品の提供
"""
import customtkinter as ctk
import tkinter as tk
import queue
import time
from typing import Optional, List, Callable
from threading import Thread


class ScrollableTextOutput(ctk.CTkTextbox):
    """スクロール可能なテキスト出力ウィジェット"""
    
    def __init__(self, master, **kwargs):
        """
        Args:
            master: 親ウィジェット
            **kwargs: CTkTextboxの追加引数
        """
        super().__init__(master, **kwargs)
        self.configure(state="disabled")
        
        # メッセージキュー
        self.message_queue = queue.Queue()
        
        # キュー処理を開始
        self.after(100, self._process_queue)
        
    def append(self, text: str, timestamp: bool = True) -> None:
        """
        テキストを追加
        
        Args:
            text: 追加するテキスト
            timestamp: タイムスタンプを付けるか
        """
        if timestamp:
            formatted_text = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {text}"
        else:
            formatted_text = text
            
        self.message_queue.put(formatted_text)
        
    def clear(self) -> None:
        """テキストをクリア"""
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")
        
    def _process_queue(self) -> None:
        """キュー内のメッセージを処理"""
        try:
            while True:
                text = self.message_queue.get_nowait()
                self.configure(state="normal")
                self.insert("end", text + "\n")
                self.configure(state="disabled")
                self.see("end")
        except queue.Empty:
            pass
        finally:
            self.after(100, self._process_queue)


class FileSelector(ctk.CTkFrame):
    """ファイル選択ウィジェット"""
    
    def __init__(self, master, label: str = "ファイル:", 
                 file_types: Optional[List[tuple]] = None,
                 command: Optional[Callable] = None, **kwargs):
        """
        Args:
            master: 親ウィジェット
            label: ラベルテキスト
            file_types: ファイルタイプのリスト
            command: 選択時のコールバック
            **kwargs: CTkFrameの追加引数
        """
        super().__init__(master, **kwargs)
        
        self.file_types = file_types or [("All files", "*.*")]
        self.command = command
        
        # ラベル
        self.label = ctk.CTkLabel(self, text=label)
        self.label.pack(side=tk.LEFT, padx=5)
        
        # エントリー
        self.var = ctk.StringVar()
        self.entry = ctk.CTkEntry(self, textvariable=self.var, width=300)
        self.entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 参照ボタン
        self.browse_button = ctk.CTkButton(
            self, text="参照", command=self._browse, width=80
        )
        self.browse_button.pack(side=tk.LEFT, padx=5)
        
    def _browse(self) -> None:
        """ファイル選択ダイアログを表示"""
        file_path = ctk.filedialog.askopenfilename(filetypes=self.file_types)
        if file_path:
            self.var.set(file_path)
            if self.command:
                self.command(file_path)
                
    def get_path(self) -> str:
        """選択されたパスを取得"""
        return self.var.get()
        
    def set_path(self, path: str) -> None:
        """パスを設定"""
        self.var.set(path)


class FolderSelector(ctk.CTkFrame):
    """フォルダ選択ウィジェット"""
    
    def __init__(self, master, label: str = "フォルダ:", 
                 command: Optional[Callable] = None, **kwargs):
        """
        Args:
            master: 親ウィジェット
            label: ラベルテキスト
            command: 選択時のコールバック
            **kwargs: CTkFrameの追加引数
        """
        super().__init__(master, **kwargs)
        
        self.command = command
        
        # ラベル
        self.label = ctk.CTkLabel(self, text=label)
        self.label.pack(side=tk.LEFT, padx=5)
        
        # エントリー
        self.var = ctk.StringVar()
        self.entry = ctk.CTkEntry(self, textvariable=self.var, width=300)
        self.entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 参照ボタン
        self.browse_button = ctk.CTkButton(
            self, text="参照", command=self._browse, width=80
        )
        self.browse_button.pack(side=tk.LEFT, padx=5)
        
    def _browse(self) -> None:
        """フォルダ選択ダイアログを表示"""
        folder_path = ctk.filedialog.askdirectory()
        if folder_path:
            self.var.set(folder_path)
            if self.command:
                self.command(folder_path)
                
    def get_path(self) -> str:
        """選択されたパスを取得"""
        return self.var.get()
        
    def set_path(self, path: str) -> None:
        """パスを設定"""
        self.var.set(path)


class ProgressDialog(ctk.CTkToplevel):
    """進捗ダイアログ"""
    
    def __init__(self, parent, title: str = "処理中...", 
                 message: str = "処理を実行しています"):
        """
        Args:
            parent: 親ウィンドウ
            title: ダイアログタイトル
            message: メッセージ
        """
        super().__init__(parent)
        
        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)
        
        # モーダルにする
        self.transient(parent)
        self.grab_set()
        
        # メッセージラベル
        self.message_label = ctk.CTkLabel(
            self, text=message, 
            font=ctk.CTkFont(size=14)
        )
        self.message_label.pack(pady=20)
        
        # プログレスバー
        self.progress = ctk.CTkProgressBar(self, width=350)
        self.progress.pack(pady=10)
        self.progress.set(0)
        
        # キャンセルボタン
        self.cancel_button = ctk.CTkButton(
            self, text="キャンセル", command=self.cancel
        )
        self.cancel_button.pack(pady=10)
        
        self.cancelled = False
        
    def update_progress(self, value: float, message: Optional[str] = None) -> None:
        """
        進捗を更新
        
        Args:
            value: 進捗値（0.0〜1.0）
            message: メッセージ（オプション）
        """
        self.progress.set(value)
        if message:
            self.message_label.configure(text=message)
        self.update()
        
    def cancel(self) -> None:
        """キャンセル処理"""
        self.cancelled = True
        self.destroy()
        
    def is_cancelled(self) -> bool:
        """キャンセルされたか確認"""
        return self.cancelled