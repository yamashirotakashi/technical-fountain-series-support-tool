"""警告メッセージダイアログ"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QLabel, QPushButton, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap, QFont


class WarningDialog(QDialog):
    """API処理の警告メッセージを表示するダイアログ"""
    
    def __init__(self, messages: list, result_type: str = "warning", parent=None):
        """
        Args:
            messages: 表示する警告メッセージのリスト
            result_type: "warning" (一部成功) または "error" (失敗)
            parent: 親ウィジェット
        """
        super().__init__(parent)
        self.messages = messages
        self.result_type = result_type
        self.setup_ui()
    
    def setup_ui(self):
        """UIを構築"""
        # タイトル設定
        if self.result_type == "error":
            self.setWindowTitle("変換エラー")
            icon_type = "error"
            title_text = "変換処理が失敗しました"
            description = "以下のエラーが発生しました："
        else:
            self.setWindowTitle("変換警告")
            icon_type = "warning"
            title_text = "変換処理は成功しましたが、警告があります"
            description = "以下の警告メッセージを確認してください："
        
        self.setModal(True)
        self.setMinimumSize(700, 500)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # システムサウンドを再生（エラーまたは警告音）
        from PyQt5.QtWidgets import QApplication
        if self.result_type == "error":
            QApplication.beep()  # エラー音
        
        # ダイアログを中央に表示
        if self.parent():
            self.move(
                self.parent().x() + (self.parent().width() - 700) // 2,
                self.parent().y() + (self.parent().height() - 500) // 2
            )
        
        # メインレイアウト
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # ヘッダー部分
        header_layout = QHBoxLayout()
        
        # アイコン
        icon_label = QLabel()
        if icon_type == "error":
            icon_label.setPixmap(self.style().standardPixmap(
                self.style().SP_MessageBoxCritical
            ).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon_label.setPixmap(self.style().standardPixmap(
                self.style().SP_MessageBoxWarning
            ).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(icon_label)
        
        # タイトルと説明
        text_layout = QVBoxLayout()
        
        title_label = QLabel(title_text)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        text_layout.addWidget(desc_label)
        
        header_layout.addLayout(text_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # メッセージ表示エリア
        group_box = QGroupBox("メッセージ詳細")
        group_layout = QVBoxLayout()
        group_box.setLayout(group_layout)
        
        # テキストエディット（読み取り専用）
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        
        # メッセージを整形して表示
        formatted_messages = []
        for i, msg in enumerate(self.messages, 1):
            # ReVIEWの警告メッセージの形式を見やすく整形
            if "WARN" in msg:
                # 警告レベルとメッセージを分離
                formatted_msg = msg.replace("⚠", "").strip()
                formatted_messages.append(f"[{i:3d}] {formatted_msg}")
            else:
                formatted_messages.append(f"[{i:3d}] {msg}")
        
        self.text_edit.setPlainText("\n".join(formatted_messages))
        
        # フォント設定（等幅フォント）
        font = QFont("Consolas, Monaco, 'Courier New', monospace")
        font.setPointSize(9)
        self.text_edit.setFont(font)
        
        group_layout.addWidget(self.text_edit)
        layout.addWidget(group_box)
        
        # 統計情報
        if len(self.messages) > 1:
            stats_label = QLabel(f"合計: {len(self.messages)} 件のメッセージ")
            stats_label.setStyleSheet("QLabel { color: #666; }")
            layout.addWidget(stats_label)
        
        # ボタン
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # クリップボードにコピーボタン
        self.copy_button = QPushButton("クリップボードにコピー")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(self.copy_button)
        
        # 閉じるボタン
        self.close_button = QPushButton("閉じる")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setDefault(True)
        button_layout.addWidget(self.close_button)
        
        # デバッグ：ボタンの状態を確認
        print(f"[DEBUG] コピーボタン有効: {self.copy_button.isEnabled()}")
        print(f"[DEBUG] 閉じるボタン有効: {self.close_button.isEnabled()}")
        
        layout.addLayout(button_layout)
        
        # 閉じるボタンにフォーカスを設定
        self.close_button.setFocus()
        
        # スタイル設定
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
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
            }
            QPushButton {
                min-width: 100px;
                padding: 5px 15px;
            }
        """)
    
    @pyqtSlot()
    def copy_to_clipboard(self):
        """メッセージをクリップボードにコピー"""
        try:
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(self.text_edit.toPlainText())
            
            # ボタンのテキストを一時的に変更
            sender = self.sender()
            if sender:
                original_text = sender.text()
                sender.setText("コピーしました！")
                sender.setEnabled(False)
                
                # 2秒後に元に戻す
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(2000, lambda: (
                    sender.setText(original_text),
                    sender.setEnabled(True)
                ))
        except Exception as e:
            print(f"クリップボードコピーエラー: {e}")