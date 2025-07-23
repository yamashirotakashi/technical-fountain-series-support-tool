"""処理方式選択ダイアログ"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QRadioButton,
                             QButtonGroup, QLabel, QPushButton, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal


class ProcessModeDialog(QDialog):
    """処理方式（従来方式/API方式）を選択するダイアログ"""
    
    # 処理方式の定義
    MODE_TRADITIONAL = "traditional"
    MODE_API = "api"
    
    # シグナル
    mode_selected = pyqtSignal(str)  # 選択された処理方式
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_mode = self.MODE_TRADITIONAL  # デフォルトは従来方式
        self.setup_ui()
    
    def setup_ui(self):
        """UIを構築"""
        self.setWindowTitle("処理方式の選択")
        self.setModal(True)
        self.setFixedSize(400, 250)
        
        # メインレイアウト
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 説明ラベル
        description = QLabel(
            "変換処理の方式を選択してください。\n"
            "従来方式: メール経由でファイルを送信\n"
            "API方式: 直接APIを使用して高速変換"
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # ラジオボタングループ
        group_box = QGroupBox("処理方式")
        group_layout = QVBoxLayout()
        group_box.setLayout(group_layout)
        
        # ボタングループ
        self.button_group = QButtonGroup()
        
        # 従来方式ラジオボタン
        self.traditional_radio = QRadioButton("従来方式（メール経由）")
        self.traditional_radio.setChecked(True)  # デフォルトで選択
        self.button_group.addButton(self.traditional_radio)
        group_layout.addWidget(self.traditional_radio)
        
        # 従来方式の説明
        traditional_desc = QLabel(
            "  • メールでファイルを送信\n"
            "  • 返信を待って結果を取得\n"
            "  • 安定性が高い"
        )
        traditional_desc.setStyleSheet("QLabel { margin-left: 20px; color: #666; }")
        group_layout.addWidget(traditional_desc)
        
        # スペース
        group_layout.addSpacing(10)
        
        # API方式ラジオボタン
        self.api_radio = QRadioButton("API方式（直接変換）")
        self.button_group.addButton(self.api_radio)
        group_layout.addWidget(self.api_radio)
        
        # API方式の説明
        api_desc = QLabel(
            "  • APIを直接使用\n"
            "  • 高速処理が可能\n"
            "  • 詳細な警告メッセージを取得"
        )
        api_desc.setStyleSheet("QLabel { margin-left: 20px; color: #666; }")
        group_layout.addWidget(api_desc)
        
        layout.addWidget(group_box)
        
        # スペース
        layout.addStretch()
        
        # ボタン
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # OKボタン
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        button_layout.addWidget(ok_button)
        
        # キャンセルボタン
        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # スタイルを設定
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QRadioButton {
                font-size: 10pt;
                padding: 5px;
            }
            QPushButton {
                min-width: 80px;
                padding: 5px 15px;
            }
        """)
    
    def get_selected_mode(self) -> str:
        """選択された処理方式を取得"""
        if self.traditional_radio.isChecked():
            return self.MODE_TRADITIONAL
        else:
            return self.MODE_API
    
    def accept(self):
        """OKボタンが押された時の処理"""
        self.selected_mode = self.get_selected_mode()
        self.mode_selected.emit(self.selected_mode)
        super().accept()