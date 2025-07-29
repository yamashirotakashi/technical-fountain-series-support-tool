# -*- coding: utf-8 -*-
"""
メインウィンドウ - 独立版溢れチェッカー

Phase 2C-1 実装
Windows PowerShell環境対応のメインGUI
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTextEdit, 
                             QProgressBar, QStatusBar, QFileDialog, QMessageBox,
                             QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont, QIcon
from pathlib import Path
import sys
import os

# 既存のOCR検出器をインポート（相対パス）
sys.path.append(str(Path(__file__).parent.parent.parent))
from overflow_detection_lib.core.detector import OCRBasedOverflowDetector

from ..core.pdf_processor import PDFOverflowProcessor
from .result_dialog import OverflowResultDialog
from ..utils.windows_utils import normalize_path, is_windows

class OverflowProcessorThread(QThread):
    """PDF処理用ワーカースレッド"""
    
    progress_updated = pyqtSignal(int, str)
    processing_completed = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, pdf_path, config):
        super().__init__()
        self.pdf_path = pdf_path
        self.config = config
        
    def run(self):
        try:
            processor = PDFOverflowProcessor(self.config)
            
            def progress_callback(page, total, detected):
                progress = int((page / total) * 100)
                self.progress_updated.emit(progress, f"ページ {page}/{total} - 検出: {detected}件")
            
            result = processor.process_pdf(self.pdf_path, progress_callback)
            self.processing_completed.emit(result)
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            self.error_occurred.emit(f"{str(e)}\n\n詳細:\n{error_detail}")

class OverflowCheckerMainWindow(QMainWindow):
    """メインウィンドウ - 独立版溢れチェッカー"""
    
    def __init__(self):
        super().__init__()
        self.processor_thread = None
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """UI構築"""
        self.setWindowTitle("CodeBlock Overflow Checker - 独立版")
        self.setMinimumSize(900, 700)
        
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # ヘッダー部分
        header_layout = self.create_header_section()
        layout.addLayout(header_layout)
        
        # ファイル選択部分
        file_group = self.create_file_selection_group()
        layout.addWidget(file_group)
        
        # 実行コントロール部分
        control_group = self.create_control_group()
        layout.addWidget(control_group)
        
        # 進捗表示部分
        progress_group = self.create_progress_group()
        layout.addWidget(progress_group)
        
        # ログ表示部分
        log_group = self.create_log_group()
        layout.addWidget(log_group)
        
        # ステータスバー
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("準備完了 - PDFファイルを選択してください")
        
    def create_header_section(self) -> QHBoxLayout:
        """ヘッダーセクション作成"""
        layout = QHBoxLayout()
        
        title_label = QLabel("CodeBlock Overflow Checker")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18pt;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
        """)
        
        version_label = QLabel("v1.0.0 - 独立版")
        version_label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #7f8c8d;
                padding: 10px;
            }
        """)
        
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(version_label)
        
        return layout
    
    def create_file_selection_group(self) -> QGroupBox:
        """ファイル選択グループ作成"""
        group_box = QGroupBox("PDFファイル選択")
        group_box.setStyleSheet(self.get_group_box_style())
        
        layout = QVBoxLayout(group_box)
        
        # 説明ラベル
        description_label = QLabel(
            "溢れチェックを実行するPDFファイルを選択してください。\n"
            "技術書のB5判形式（515.9 x 728.5pt）に対応しています。"
        )
        description_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        
        # ファイルパス部分
        file_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("PDFファイルパスを入力またはブラウズで選択...")
        self.file_path_edit.setStyleSheet(self.get_line_edit_style())
        
        file_browse_btn = QPushButton("ブラウズ")
        file_browse_btn.clicked.connect(self.browse_file)
        file_browse_btn.setStyleSheet(self.get_secondary_button_style())
        
        file_layout.addWidget(QLabel("ファイル:"))
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(file_browse_btn)
        
        layout.addWidget(description_label)
        layout.addLayout(file_layout)
        
        return group_box
    
    def create_control_group(self) -> QGroupBox:
        """実行コントロールグループ作成"""
        group_box = QGroupBox("実行制御")
        group_box.setStyleSheet(self.get_group_box_style())
        
        layout = QHBoxLayout(group_box)
        
        # 実行ボタン
        self.process_btn = QPushButton("溢れチェック実行")
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setStyleSheet(self.get_primary_button_style())
        
        # クリアボタン
        self.clear_btn = QPushButton("クリア")
        self.clear_btn.clicked.connect(self.clear_all)
        self.clear_btn.setStyleSheet(self.get_danger_button_style())
        
        # 設定ボタン
        self.settings_btn = QPushButton("設定")
        self.settings_btn.clicked.connect(self.open_settings)
        self.settings_btn.setStyleSheet(self.get_secondary_button_style())
        
        layout.addWidget(self.process_btn)
        layout.addWidget(self.clear_btn)
        layout.addWidget(self.settings_btn)
        layout.addStretch()
        
        return group_box
    
    def create_progress_group(self) -> QGroupBox:
        """進捗表示グループ作成"""
        group_box = QGroupBox("処理進捗")
        group_box.setStyleSheet(self.get_group_box_style())
        
        layout = QVBoxLayout(group_box)
        
        # 進捗バー
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        
        # 進捗ラベル
        self.progress_label = QLabel("準備完了")
        self.progress_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_label)
        
        return group_box
    
    def create_log_group(self) -> QGroupBox:
        """ログ表示グループ作成"""
        group_box = QGroupBox("実行ログ")
        group_box.setStyleSheet(self.get_group_box_style())
        
        layout = QVBoxLayout(group_box)
        
        # ログ表示
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
        """)
        
        layout.addWidget(self.log_text)
        
        return group_box
    
    def setup_styles(self):
        """メインウィンドウスタイル設定"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
        """)
    
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
    
    def get_primary_button_style(self) -> str:
        """プライマリボタンスタイル"""
        return """
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 11pt;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
    
    def get_secondary_button_style(self) -> str:
        """セカンダリボタンスタイル"""
        return """
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 11pt;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """
    
    def get_danger_button_style(self) -> str:
        """危険ボタンスタイル"""
        return """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 11pt;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """
    
    def get_line_edit_style(self) -> str:
        """ラインエディットスタイル"""
        return """
            QLineEdit {
                font-size: 10pt;
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """
    
    def browse_file(self):
        """ファイル参照ダイアログ"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "PDFファイルを選択",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
            self.add_log(f"ファイル選択: {Path(file_path).name}")
    
    def start_processing(self):
        """処理開始"""
        pdf_path = self.file_path_edit.text().strip()
        if not pdf_path:
            QMessageBox.warning(self, "エラー", "PDFファイルを選択してください。")
            return
        
        pdf_path = normalize_path(pdf_path)
        if not pdf_path.exists():
            QMessageBox.warning(self, "エラー", f"ファイルが存在しません:\n{pdf_path}")
            return
        
        self.add_log(f"処理開始: {pdf_path.name}")
        self.set_processing_state(True)
        
        # ワーカースレッドで処理実行
        self.processor_thread = OverflowProcessorThread(
            pdf_path, 
            self.get_processing_config()
        )
        self.processor_thread.progress_updated.connect(self.update_progress)
        self.processor_thread.processing_completed.connect(self.on_processing_completed)
        self.processor_thread.error_occurred.connect(self.on_processing_error)
        self.processor_thread.start()
    
    def get_processing_config(self):
        """処理設定取得"""
        return {
            'detection_sensitivity': 'medium',
            'enable_learning': True,
            'save_intermediate_results': True,
            'windows_environment': is_windows()
        }
    
    @pyqtSlot(int, str)
    def update_progress(self, progress, message):
        """進捗更新"""
        self.progress_bar.setValue(progress)
        self.progress_label.setText(message)
        self.add_log(message)
    
    @pyqtSlot(object)
    def on_processing_completed(self, result):
        """処理完了"""
        self.set_processing_state(False)
        self.add_log(f"処理完了: {len(result.overflow_pages) if hasattr(result, 'overflow_pages') else 0}件の溢れを検出")
        
        # 結果ダイアログ表示
        dialog = OverflowResultDialog(result, self)
        dialog.exec()
    
    @pyqtSlot(str)
    def on_processing_error(self, error_message):
        """処理エラー"""
        self.set_processing_state(False)
        self.add_log(f"エラー: {error_message}")
        QMessageBox.critical(self, "処理エラー", f"処理中にエラーが発生しました:\n\n{error_message}")
    
    def set_processing_state(self, processing):
        """処理状態設定"""
        self.process_btn.setEnabled(not processing)
        self.clear_btn.setEnabled(not processing)
        self.settings_btn.setEnabled(not processing)
        
        if processing:
            self.progress_bar.setValue(0)
            self.status_bar.showMessage("処理中...")
        else:
            self.progress_bar.setValue(100 if not processing else 0)
            self.status_bar.showMessage("準備完了")
    
    def clear_all(self):
        """全体クリア"""
        self.file_path_edit.clear()
        self.log_text.clear()
        self.progress_bar.setValue(0)
        self.progress_label.setText("準備完了")
        self.status_bar.showMessage("準備完了 - PDFファイルを選択してください")
        self.add_log("画面をクリアしました")
    
    def open_settings(self):
        """設定ダイアログを開く"""
        QMessageBox.information(self, "設定", "設定機能は今後実装予定です。")
    
    def add_log(self, message):
        """ログ追加"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_text.append(log_message)
        
        # スクロールを最下部に移動
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)