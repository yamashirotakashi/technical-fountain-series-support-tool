# -*- coding: utf-8 -*-
"""
結果表示・学習データ収集ダイアログ

Phase 2C-1 実装
ユーザーフィードバック機能付きの結果表示
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QCheckBox, QGroupBox,
                             QScrollArea, QWidget, QGridLayout, QMessageBox,
                             QPlainTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from pathlib import Path
from typing import Dict, List

from ..core.learning_manager import WindowsLearningDataManager
from ..utils.windows_utils import is_windows

class OverflowResultDialog(QDialog):
    """溢れチェック結果表示・学習ダイアログ"""
    
    learning_data_saved = pyqtSignal(dict)
    
    def __init__(self, result, parent=None):
        super().__init__(parent)
        self.result = result
        self.page_checkboxes = {}
        self.learning_manager = WindowsLearningDataManager()
        
        self.setup_ui()
        self.populate_results()
        
    def setup_ui(self):
        """UI構築"""
        self.setWindowTitle(f"溢れチェック結果 - {self.result.pdf_name}")
        self.setMinimumSize(800, 700)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # ヘッダー情報
        header_group = self.create_header_group()
        layout.addWidget(header_group)
        
        # 検出結果リスト
        results_group = self.create_results_group()
        layout.addWidget(results_group)
        
        # 追加ページ入力
        additional_group = self.create_additional_pages_group()
        layout.addWidget(additional_group)
        
        # コメント入力
        comment_group = self.create_comment_group()
        layout.addWidget(comment_group)
        
        # ボタン部分
        button_layout = self.create_button_layout()
        layout.addLayout(button_layout)
        
    def create_header_group(self) -> QGroupBox:
        """ヘッダー情報グループ作成"""
        group_box = QGroupBox("処理結果サマリー")
        group_box.setStyleSheet(self.get_group_box_style())
        
        layout = QGridLayout(group_box)
        
        # PDFファイル名
        layout.addWidget(QLabel("ファイル名:"), 0, 0)
        layout.addWidget(QLabel(self.result.pdf_name), 0, 1)
        
        # 総ページ数
        layout.addWidget(QLabel("総ページ数:"), 1, 0)
        layout.addWidget(QLabel(f"{self.result.total_pages}ページ"), 1, 1)
        
        # 検出件数
        layout.addWidget(QLabel("検出件数:"), 2, 0)
        detection_label = QLabel(f"{self.result.detection_count}件")
        if self.result.detection_count > 0:
            detection_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        else:
            detection_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        layout.addWidget(detection_label, 2, 1)
        
        # 処理時間
        layout.addWidget(QLabel("処理時間:"), 3, 0)
        layout.addWidget(QLabel(f"{self.result.processing_time:.2f}秒"), 3, 1)
        
        return group_box
        
    def create_results_group(self) -> QGroupBox:
        """検出結果グループ作成"""
        group_box = QGroupBox("検出された溢れページ（チェックを外すと誤検出として学習されます）")
        group_box.setStyleSheet(self.get_group_box_style())
        
        layout = QVBoxLayout(group_box)
        
        if not self.result.overflow_pages:
            # 溢れが検出されなかった場合
            no_overflow_label = QLabel("✅ 溢れは検出されませんでした")
            no_overflow_label.setStyleSheet("""
                QLabel {
                    color: #27ae60;
                    font-size: 14pt;
                    font-weight: bold;
                    padding: 20px;
                    text-align: center;
                }
            """)
            layout.addWidget(no_overflow_label)
        else:
            # スクロール可能な結果リスト
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setMinimumHeight(200)
            
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)
            
            for page_data in self.result.overflow_pages:
                page_widget = self.create_page_result_widget(page_data)
                scroll_layout.addWidget(page_widget)
            
            scroll_area.setWidget(scroll_widget)
            layout.addWidget(scroll_area)
            
        return group_box
    
    def create_page_result_widget(self, page_data: Dict) -> QWidget:
        """個別ページ結果ウィジェット作成"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                margin: 2px;
                padding: 8px;
                background-color: #f8f9fa;
            }
        """)
        
        layout = QHBoxLayout(widget)
        
        # チェックボックス（デフォルトはチェック済み）
        page_number = page_data['page_number']
        checkbox = QCheckBox(f"ページ {page_number}")
        checkbox.setChecked(True)  # デフォルトで「実際に溢れがある」として設定
        checkbox.setStyleSheet("font-weight: bold; font-size: 11pt;")
        self.page_checkboxes[page_number] = checkbox
        
        # 溢れ内容
        overflow_text = page_data.get('overflow_text', '')[:50]  # 最初の50文字
        if len(page_data.get('overflow_text', '')) > 50:
            overflow_text += "..."
            
        content_label = QLabel(f"内容: {overflow_text}")
        content_label.setWordWrap(True)
        
        # 溢れ量
        overflow_amount = page_data.get('overflow_amount', 0.0)
        amount_label = QLabel(f"溢れ量: {overflow_amount:.1f}pt")
        amount_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        layout.addWidget(checkbox)
        layout.addWidget(content_label, 1)
        layout.addWidget(amount_label)
        
        return widget
    
    def create_additional_pages_group(self) -> QGroupBox:
        """追加ページ入力グループ作成"""
        group_box = QGroupBox("見落とされた溢れページ（カンマ、タブ、スペース、改行区切り）")
        group_box.setStyleSheet(self.get_group_box_style())
        
        layout = QVBoxLayout(group_box)
        
        # 説明
        description_label = QLabel(
            "検出されなかったが実際には溢れがあるページ番号を入力してください。\n"
            "例: 5, 12, 18 または 5 12 18 または各行に1つずつ"
        )
        description_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        
        # 入力エリア
        self.additional_pages_edit = QPlainTextEdit()
        self.additional_pages_edit.setMaximumHeight(80)
        self.additional_pages_edit.setPlaceholderText("追加のページ番号を入力...")
        self.additional_pages_edit.setStyleSheet("""
            QPlainTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11pt;
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
            }
            QPlainTextEdit:focus {
                border-color: #3498db;
            }
        """)
        
        layout.addWidget(description_label)
        layout.addWidget(self.additional_pages_edit)
        
        return group_box
    
    def create_comment_group(self) -> QGroupBox:
        """コメント入力グループ作成"""
        group_box = QGroupBox("備考・コメント（任意）")
        group_box.setStyleSheet(self.get_group_box_style())
        
        layout = QVBoxLayout(group_box)
        
        self.comment_edit = QPlainTextEdit()
        self.comment_edit.setMaximumHeight(80)
        self.comment_edit.setPlaceholderText("このPDFや検出結果についてコメントがあれば入力してください...")
        self.comment_edit.setStyleSheet("""
            QPlainTextEdit {
                font-size: 10pt;
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
            }
            QPlainTextEdit:focus {
                border-color: #3498db;
            }
        """)
        
        layout.addWidget(self.comment_edit)
        
        return group_box
    
    def create_button_layout(self) -> QHBoxLayout:
        """ボタンレイアウト作成"""
        layout = QHBoxLayout()
        
        # 学習データ保存ボタン
        save_learning_btn = QPushButton("学習データとして保存")
        save_learning_btn.clicked.connect(self.save_learning_data)
        save_learning_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        # キャンセルボタン
        cancel_btn = QPushButton("キャンセル")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-weight: bold;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        # 結果のみ確認ボタン
        ok_btn = QPushButton("結果確認のみ")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        layout.addWidget(save_learning_btn)
        layout.addStretch()
        layout.addWidget(ok_btn)
        layout.addWidget(cancel_btn)
        
        return layout
    
    def get_group_box_style(self) -> str:
        """グループボックス共通スタイル"""
        return """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
            }
        """
    
    def populate_results(self):
        """結果データを画面に反映"""
        # 結果が既に setup_ui で処理されているため、
        # 追加の処理が必要な場合はここに記述
        pass
    
    def parse_additional_pages(self) -> List[int]:
        """追加ページ番号を解析"""
        text = self.additional_pages_edit.toPlainText().strip()
        if not text:
            return []
        
        page_numbers = []
        
        # カンマ、タブ、スペース、改行で分割
        import re
        tokens = re.split(r'[,\t\s\n]+', text)
        
        for token in tokens:
            token = token.strip()
            if token.isdigit():
                page_num = int(token)
                if 1 <= page_num <= self.result.total_pages:
                    page_numbers.append(page_num)
        
        return sorted(list(set(page_numbers)))  # 重複除去・ソート
    
    def save_learning_data(self):
        """学習データを保存"""
        try:
            # 確認されたページ（チェックが入っているページ）
            confirmed_pages = []
            false_positives = []
            
            for page_number, checkbox in self.page_checkboxes.items():
                if checkbox.isChecked():
                    confirmed_pages.append(page_number)
                else:
                    false_positives.append(page_number)
            
            # 追加ページ
            additional_pages = self.parse_additional_pages()
            
            # 学習データの構築
            learning_data = {
                'pdf_path': str(self.result.pdf_path),
                'pdf_name': self.result.pdf_name,
                'detected_pages': [p['page_number'] for p in self.result.overflow_pages],
                'confirmed_pages': confirmed_pages,
                'additional_pages': additional_pages,
                'false_positives': false_positives,
                'user_notes': self.comment_edit.toPlainText().strip(),
                'app_version': '1.0.0',
                'processing_time': self.result.processing_time
            }
            
            # データベースに保存
            success = self.learning_manager.save_learning_data(learning_data)
            
            if success:
                QMessageBox.information(
                    self, 
                    "保存完了", 
                    f"学習データを保存しました。\n\n"
                    f"確認済み: {len(confirmed_pages)}件\n"
                    f"追加: {len(additional_pages)}件\n"
                    f"誤検出: {len(false_positives)}件"
                )
                
                # シグナル発出
                self.learning_data_saved.emit(learning_data)
                self.accept()
            else:
                QMessageBox.warning(self, "保存エラー", "学習データの保存に失敗しました。")
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "保存エラー", 
                f"学習データの保存中にエラーが発生しました:\n\n{str(e)}"
            )