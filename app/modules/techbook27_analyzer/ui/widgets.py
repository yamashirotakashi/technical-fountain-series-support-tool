"""
Qt6カスタムウィジェット
単一責任: 再利用可能なUI部品の提供
"""
import queue
import time
from typing import Optional, List, Callable
from threading import Thread
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTextEdit, QLineEdit, QFileDialog, QProgressBar, QDialog,
    QCheckBox, QSpinBox, QComboBox, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QTextCursor


class ScrollableTextOutput(QTextEdit):
    """スクロール可能なテキスト出力ウィジェット"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        """初期化
        
        Args:
            parent: 親ウィジェット
        """
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 9))
        
        # メッセージキュー
        self.message_queue = queue.Queue()
        
        # タイマーでキューを処理
        self.timer = QTimer()
        self.timer.timeout.connect(self._process_queue)
        self.timer.start(100)  # 100ms間隔
    
    def add_message(self, message: str, auto_scroll: bool = True):
        """メッセージを追加
        
        Args:
            message: 追加するメッセージ
            auto_scroll: 自動スクロールするか
        """
        self.message_queue.put((message, auto_scroll))
    
    def _process_queue(self):
        """キューからメッセージを処理"""
        try:
            while not self.message_queue.empty():
                message, auto_scroll = self.message_queue.get_nowait()
                
                # カーソルを末尾に移動
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.setTextCursor(cursor)
                
                # メッセージを追加
                self.insertPlainText(f"{message}\n")
                
                if auto_scroll:
                    # 最後の行にスクロール
                    scrollbar = self.verticalScrollBar()
                    scrollbar.setValue(scrollbar.maximum())
                    
        except queue.Empty:
            pass
    
    def clear_output(self):
        """出力をクリア"""
        self.clear()


class FileSelector(QWidget):
    """ファイル選択ウィジェット"""
    
    file_selected = pyqtSignal(str)  # ファイルが選択された時のシグナル
    
    def __init__(self, label_text: str = "ファイル選択:", 
                 file_filter: str = "All Files (*)", parent: Optional[QWidget] = None):
        """初期化
        
        Args:
            label_text: ラベルテキスト
            file_filter: ファイルフィルタ
            parent: 親ウィジェット
        """
        super().__init__(parent)
        self.file_filter = file_filter
        
        # レイアウト作成
        layout = QHBoxLayout(self)
        
        # ラベル
        self.label = QLabel(label_text)
        layout.addWidget(self.label)
        
        # パス表示
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        layout.addWidget(self.path_edit)
        
        # 選択ボタン
        self.browse_btn = QPushButton("参照...")
        self.browse_btn.clicked.connect(self._select_file)
        layout.addWidget(self.browse_btn)
    
    def _select_file(self):
        """ファイル選択ダイアログを表示"""
        # デフォルトパスを設定
        default_path = r"G:\マイドライブ\[git]"
        if not Path(default_path).exists():
            default_path = ""
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, "ファイルを選択", default_path, self.file_filter
        )
        
        if file_path:
            self.path_edit.setText(file_path)
            self.file_selected.emit(file_path)
    
    def get_file_path(self) -> str:
        """選択されたファイルパスを取得"""
        return self.path_edit.text()
    
    def set_file_path(self, path: str):
        """ファイルパスを設定"""
        self.path_edit.setText(path)


class FolderSelector(QWidget):
    """フォルダ選択ウィジェット"""
    
    folder_selected = pyqtSignal(str)  # フォルダが選択された時のシグナル
    
    def __init__(self, label_text: str = "フォルダ選択:", parent: Optional[QWidget] = None):
        """初期化
        
        Args:
            label_text: ラベルテキスト
            parent: 親ウィジェット
        """
        super().__init__(parent)
        
        # レイアウト作成
        layout = QHBoxLayout(self)
        
        # ラベル
        self.label = QLabel(label_text)
        layout.addWidget(self.label)
        
        # パス表示
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        layout.addWidget(self.path_edit)
        
        # 選択ボタン
        self.browse_btn = QPushButton("参照...")
        self.browse_btn.clicked.connect(self._select_folder)
        layout.addWidget(self.browse_btn)
    
    def _select_folder(self):
        """フォルダ選択ダイアログを表示"""
        # デフォルトパスを設定
        default_path = r"G:\マイドライブ\[git]"
        if not Path(default_path).exists():
            default_path = ""
            
        folder_path = QFileDialog.getExistingDirectory(
            self, "フォルダを選択", default_path
        )
        
        if folder_path:
            self.path_edit.setText(folder_path)
            self.folder_selected.emit(folder_path)
    
    def get_folder_path(self) -> str:
        """選択されたフォルダパスを取得"""
        return self.path_edit.text()
    
    def set_folder_path(self, path: str):
        """フォルダパスを設定"""
        self.path_edit.setText(path)


class ProgressDialog(QDialog):
    """プログレスダイアログ"""
    
    cancel_requested = pyqtSignal()  # キャンセルが要求された時のシグナル
    
    def __init__(self, title: str = "処理中...", parent: Optional[QWidget] = None):
        """初期化
        
        Args:
            title: ダイアログタイトル
            parent: 親ウィジェット
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 120)
        
        # レイアウト作成
        layout = QVBoxLayout(self)
        
        # ステータスラベル
        self.status_label = QLabel("処理を開始しています...")
        layout.addWidget(self.status_label)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        # キャンセルボタン
        self.cancel_btn = QPushButton("キャンセル")
        self.cancel_btn.clicked.connect(self._on_cancel)
        layout.addWidget(self.cancel_btn)
        
        # フラグ
        self.is_cancelled = False
    
    def _on_cancel(self):
        """キャンセル処理"""
        self.is_cancelled = True
        self.cancel_requested.emit()
        self.status_label.setText("キャンセル中...")
        self.cancel_btn.setEnabled(False)
    
    def update_progress(self, value: int, status: str = ""):
        """プログレスを更新
        
        Args:
            value: 進捗値（0-100）
            status: ステータスメッセージ
        """
        self.progress_bar.setValue(value)
        if status:
            self.status_label.setText(status)
    
    def set_completed(self, message: str = "処理が完了しました"):
        """完了状態に設定"""
        self.progress_bar.setValue(100)
        self.status_label.setText(message)
        self.cancel_btn.setText("閉じる")
        self.cancel_btn.clicked.disconnect()
        self.cancel_btn.clicked.connect(self.accept)
        self.cancel_btn.setEnabled(True)


class OptionsPanel(QFrame):
    """オプションパネル"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        """初期化"""
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        
        # メインレイアウト
        self.layout = QVBoxLayout(self)
        
        # オプション辞書
        self.options = {}
    
    def add_checkbox(self, key: str, text: str, default: bool = False) -> QCheckBox:
        """チェックボックスを追加
        
        Args:
            key: オプションキー
            text: 表示テキスト
            default: デフォルト値
            
        Returns:
            作成されたQCheckBox
        """
        checkbox = QCheckBox(text)
        checkbox.setChecked(default)
        checkbox.stateChanged.connect(lambda state, k=key: self._update_option(k, state == Qt.CheckState.Checked))
        self.layout.addWidget(checkbox)
        self.options[key] = checkbox
        return checkbox
    
    def add_spinbox(self, key: str, label: str, default: int = 0, 
                   min_val: int = 0, max_val: int = 1000) -> QSpinBox:
        """スピンボックスを追加
        
        Args:
            key: オプションキー
            label: ラベルテキスト
            default: デフォルト値
            min_val: 最小値
            max_val: 最大値
            
        Returns:
            作成されたQSpinBox
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        
        layout.addWidget(QLabel(label))
        
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(default)
        spinbox.valueChanged.connect(lambda value, k=key: self._update_option(k, value))
        layout.addWidget(spinbox)
        
        self.layout.addWidget(container)
        self.options[key] = spinbox
        return spinbox
    
    def add_combobox(self, key: str, label: str, items: List[str], default: int = 0) -> QComboBox:
        """コンボボックスを追加
        
        Args:
            key: オプションキー
            label: ラベルテキスト
            items: アイテムリスト
            default: デフォルトインデックス
            
        Returns:
            作成されたQComboBox
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        
        layout.addWidget(QLabel(label))
        
        combobox = QComboBox()
        combobox.addItems(items)
        combobox.setCurrentIndex(default)
        combobox.currentTextChanged.connect(lambda text, k=key: self._update_option(k, text))
        layout.addWidget(combobox)
        
        self.layout.addWidget(container)
        self.options[key] = combobox
        return combobox
    
    def _update_option(self, key: str, value):
        """オプション値を更新"""
        # 実際の値の更新は親クラスで処理
        pass
    
    def get_values(self) -> dict:
        """現在の値を取得"""
        values = {}
        for key, widget in self.options.items():
            if isinstance(widget, QCheckBox):
                values[key] = widget.isChecked()
            elif isinstance(widget, QSpinBox):
                values[key] = widget.value()
            elif isinstance(widget, QComboBox):
                values[key] = widget.currentText()
        return values