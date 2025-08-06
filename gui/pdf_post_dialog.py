from __future__ import annotations
#!/usr/bin/env python3
"""
PDF投稿確認ダイアログ
品質重視のUI実装
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from pathlib import Path
from typing import Optional, Tuple

from utils.logger import get_logger

logger = get_logger(__name__)


class PDFPostDialog(QDialog):
    """
    PDF投稿確認ダイアログ
    
    表示内容:
    - PDFファイル名（読み取り専用）
    - 投稿先チャネル名（読み取り専用）
    - 投稿メッセージ（編集可能）
    """
    
    # シグナル定義
    post_requested = pyqtSignal(str, str, str)  # pdf_path, channel, message
    
    def __init__(self, pdf_path: str, channel: str, default_message: str, author_slack_id: Optional[str] = None, parent=None):
        """
        初期化
        
        Args:
            pdf_path: PDFファイルのパス
            channel: 投稿先チャネル名
            default_message: デフォルトメッセージ
            author_slack_id: 著者のSlackID（オプション）
            parent: 親ウィジェット
        """
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.channel = channel
        self.default_message = default_message
        self.author_slack_id = author_slack_id
        
        self.setWindowTitle("Slack投稿確認")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self._init_ui()
        self._apply_styles()
        
        logger.debug(f"PDFPostDialog initialized - file: {pdf_path}, channel: {channel}")
    
    def _init_ui(self):
        """UIの初期化"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # タイトル
        title_label = QLabel("PDF投稿内容の確認")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # ファイル情報グループ
        file_group = QGroupBox("ファイル情報")
        file_layout = QVBoxLayout()
        
        # PDFファイル名
        pdf_name = Path(self.pdf_path).name
        file_label = QLabel(f"ファイル名: {pdf_name}")
        file_layout.addWidget(file_label)
        
        # ファイルパス（ツールチップとして表示）
        file_label.setToolTip(f"フルパス: {self.pdf_path}")
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 投稿先グループ
        channel_group = QGroupBox("投稿先")
        channel_layout = QVBoxLayout()
        
        channel_label = QLabel(f"チャネル: #{self.channel}")
        channel_label.setStyleSheet("QLabel { color: #1264a3; font-weight: bold; }")
        channel_layout.addWidget(channel_label)
        
        channel_group.setLayout(channel_layout)
        layout.addWidget(channel_group)
        
        # メッセージグループ
        message_group = QGroupBox("投稿メッセージ")
        message_layout = QVBoxLayout()
        
        self.message_edit = QTextEdit()
        
        # 著者メンションを含むメッセージの構築
        if self.author_slack_id:
            # Slackメンション形式に変換（<@UserID>形式）
            # 既に<@で始まっている場合はそのまま、そうでない場合は<@>で囲む
            if self.author_slack_id.startswith('<@') and self.author_slack_id.endswith('>'):
                slack_mention = self.author_slack_id
            elif self.author_slack_id.startswith('@'):
                # @だけの場合は@を除去して<@>で囲む
                slack_mention = f"<@{self.author_slack_id[1:]}>"
            else:
                # 何もついていない場合は<@>で囲む
                slack_mention = f"<@{self.author_slack_id}>"
            
            full_message = f"{slack_mention}\n\n{self.default_message}"
        else:
            full_message = self.default_message
            
        self.message_edit.setPlainText(full_message)
        self.message_edit.setMaximumHeight(100)
        self.message_edit.setPlaceholderText("メッセージを入力してください...")
        message_layout.addWidget(self.message_edit)
        
        # 文字数カウンター
        self.char_count_label = QLabel()
        self._update_char_count()
        message_layout.addWidget(self.char_count_label)
        
        # メッセージ変更時の処理
        self.message_edit.textChanged.connect(self._update_char_count)
        
        message_group.setLayout(message_layout)
        layout.addWidget(message_group)
        
        # 注意事項
        notice_label = QLabel(
            "※ 投稿後の取り消しはできません。内容をよく確認してください。"
        )
        notice_label.setStyleSheet("QLabel { color: #666; font-size: 11px; }")
        layout.addWidget(notice_label)
        
        # ボタン
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # キャンセルボタン
        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # 投稿ボタン
        self.post_button = QPushButton("投稿")
        self.post_button.clicked.connect(self._on_post_clicked)
        self.post_button.setDefault(True)
        button_layout.addWidget(self.post_button)
        
        layout.addLayout(button_layout)
    
    def _apply_styles(self):
        """スタイルの適用"""
        self.setStyleSheet("""
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
            QPushButton {
                min-width: 80px;
                padding: 5px 15px;
            }
            QPushButton:default {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:default:hover {
                background-color: #005a9e;
            }
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
            }
        """)
    
    def _update_char_count(self):
        """文字数カウンターの更新"""
        count = len(self.message_edit.toPlainText())
        self.char_count_label.setText(f"文字数: {count}")
        
        # 文字数が多すぎる場合の警告
        if count > 1000:
            self.char_count_label.setStyleSheet("QLabel { color: red; }")
        else:
            self.char_count_label.setStyleSheet("QLabel { color: #666; }")
    
    def _on_post_clicked(self):
        """投稿ボタンクリック時の処理"""
        message = self.message_edit.toPlainText().strip()
        
        if not message:
            QMessageBox.warning(
                self,
                "メッセージが空です",
                "投稿メッセージを入力してください。"
            )
            return
        
        # 最終確認
        reply = QMessageBox.question(
            self,
            "投稿確認",
            f"以下の内容で投稿しますか？\n\n"
            f"チャネル: #{self.channel}\n"
            f"ファイル: {Path(self.pdf_path).name}\n\n"
            f"この操作は取り消せません。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            logger.info(f"User confirmed posting to {self.channel}")
            self.accept()
    
    def get_message(self) -> str:
        """
        編集されたメッセージを取得
        
        Returns:
            メッセージテキスト
        """
        return self.message_edit.toPlainText().strip()
    
    def get_confirmation(self) -> Tuple[bool, str]:
        """
        ダイアログの結果を取得
        
        Returns:
            (投稿承認, メッセージ)
        """
        if self.exec() == QDialog.DialogCode.Accepted:
            return True, self.get_message()
        else:
            return False, ""