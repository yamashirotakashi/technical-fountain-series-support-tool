"""シンプルなファイル選択ダイアログ"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QCheckBox, QPushButton, QLabel, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt


class SimpleFileSelectorDialog(QDialog):
    """ファイル選択用のシンプルなダイアログ"""
    
    def __init__(self, file_list, parent=None):
        super().__init__(parent)
        self.file_list = file_list
        self.checkboxes = []
        self.selected_files = []
        self._init_ui()
        
    def _init_ui(self):
        """UI初期化"""
        self.setWindowTitle("ファイル選択")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        layout = QVBoxLayout()
        
        # タイトル
        title = QLabel("ペーストするファイルを選択してください:")
        layout.addWidget(title)
        
        # スクロールエリア
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # チェックボックス作成
        for file_path in self.file_list:
            checkbox = QCheckBox(file_path.name)
            checkbox.setChecked(True)  # デフォルトで全選択
            checkbox.file_path = file_path  # ファイルパスを保持
            self.checkboxes.append(checkbox)
            scroll_layout.addWidget(checkbox)
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("全て選択")
        select_all_btn.clicked.connect(self._select_all)
        button_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton("全て解除")
        deselect_all_btn.clicked.connect(self._deselect_all)
        button_layout.addWidget(deselect_all_btn)
        
        button_layout.addStretch()
        
        paste_btn = QPushButton("ファイルをペースト")
        paste_btn.clicked.connect(self._on_paste)
        button_layout.addWidget(paste_btn)
        
        cancel_btn = QPushButton("キャンセル")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def _select_all(self):
        """全て選択"""
        for checkbox in self.checkboxes:
            checkbox.setChecked(True)
            
    def _deselect_all(self):
        """全て解除"""
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)
            
    def _on_paste(self):
        """ペーストボタン押下"""
        self.selected_files = [
            cb.file_path for cb in self.checkboxes if cb.isChecked()
        ]
        if not self.selected_files:
            # 何も選択されていない場合は何もしない
            return
        self.accept()
        
    def get_selected_files(self):
        """選択されたファイルを取得"""
        return self.selected_files