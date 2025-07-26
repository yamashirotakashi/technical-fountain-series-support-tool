"""Pre-flight Check結果表示ダイアログ"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QPushButton, QLabel, QListWidgetItem, QProgressBar,
                             QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal, QThread
from PyQt6.QtGui import QFont
from pathlib import Path
from typing import List, Optional

from core.preflight.batch_processor import BatchProcessor, BatchJob
from utils.logger import get_logger


class PreflightWorker(QThread):
    """Pre-flight Check処理用ワーカースレッド"""
    
    # シグナル
    file_checked = pyqtSignal(str, bool, str)  # filename, is_error, message
    progress_updated = pyqtSignal(int)  # progress percentage
    status_updated = pyqtSignal(str)  # status message
    finished = pyqtSignal()
    
    def __init__(self, files: List[Path], email: str):
        super().__init__()
        self.files = files
        self.email = email
        self.batch_processor = BatchProcessor()
        self.logger = get_logger(__name__)
        self._cancelled = False
        
        # コールバックを設定
        self.batch_processor.on_job_updated = self._on_job_updated
        self.batch_processor.on_progress_updated = self._on_progress_updated
        
    def run(self):
        """Pre-flight Checkを実行"""
        try:
            total_files = len(self.files)
            self.status_updated.emit(f"検証開始: {total_files}ファイル")
            
            # ファイルを追加
            file_paths = [str(f) for f in self.files]
            self.batch_processor.add_files(file_paths)
            
            # バッチ処理を実行
            results = self.batch_processor.process_batch(self.email)
            
            # 結果をチェック
            error_count = 0
            for file_path, job in results.items():
                if job.status == "error":
                    error_count += 1
                    filename = Path(file_path).name
                    self.file_checked.emit(filename, True, job.error_message or "エラー")
                    
            if not self._cancelled:
                if error_count == 0:
                    self.status_updated.emit("✓ すべてのファイルがPDF変換可能です")
                else:
                    self.status_updated.emit(f"✗ チェック完了 - エラーファイル: {error_count}件")
                
        except Exception as e:
            self.logger.error(f"Pre-flight Checkエラー: {e}", exc_info=True)
            self.status_updated.emit(f"エラー: {str(e)}")
            
        finally:
            self.finished.emit()
            
    def cancel(self):
        """処理をキャンセル"""
        self._cancelled = True
        self.batch_processor.cancel()
        
    def _on_job_updated(self, job: BatchJob):
        """ジョブ更新時のコールバック"""
        filename = Path(job.file_path).name
        
        if job.status == "uploading":
            self.status_updated.emit(f"アップロード中: {filename}")
        elif job.status == "uploaded":
            self.status_updated.emit(f"アップロード完了: {filename}")
        elif job.status == "error":
            self.file_checked.emit(filename, True, job.error_message or "エラー")
        elif job.status == "success":
            self.status_updated.emit(f"検証成功: {filename}")
            
    def _on_progress_updated(self, completed: int, total: int):
        """進捗更新時のコールバック"""
        if total > 0:
            progress = int(completed / total * 100)
            self.progress_updated.emit(progress)


class PreflightDialog(QDialog):
    """リアルタイムエラー表示ダイアログ"""
    
    closed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pre-flight Check")
        self.setMinimumSize(700, 500)
        self.worker: Optional[PreflightWorker] = None
        self.setup_ui()
        
    def setup_ui(self):
        """UIを設定"""
        layout = QVBoxLayout(self)
        
        # ヘッダーセクション
        header_layout = QVBoxLayout()
        
        # タイトル
        title_label = QLabel("Pre-flight Quality Check")
        title_label.setFont(QFont("メイリオ", 12, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        # 説明
        desc_label = QLabel("WordファイルのPDF変換可能性を事前に検証します")
        desc_label.setFont(QFont("メイリオ", 9))
        header_layout.addWidget(desc_label)
        
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # エラーファイルリスト
        list_label = QLabel("検証結果:")
        list_label.setFont(QFont("メイリオ", 10, QFont.Weight.Bold))
        layout.addWidget(list_label)
        
        self.error_list = QListWidget()
        self.error_list.setFont(QFont("メイリオ", 9))
        layout.addWidget(self.error_list)
        
        # ステータスラベル
        self.status_label = QLabel("待機中...")
        self.status_label.setFont(QFont("メイリオ", 9))
        layout.addWidget(self.status_label)
        
        # ボタンレイアウト
        button_layout = QHBoxLayout()
        
        # フォルダ選択ボタン
        self.select_folder_button = QPushButton("フォルダ選択")
        self.select_folder_button.clicked.connect(self.select_folder)
        button_layout.addWidget(self.select_folder_button)
        
        # 開始ボタン
        self.start_button = QPushButton("検証開始")
        self.start_button.clicked.connect(self.start_check)
        self.start_button.setEnabled(False)
        button_layout.addWidget(self.start_button)
        
        # リストクリアボタン
        self.clear_button = QPushButton("リストクリア")
        self.clear_button.clicked.connect(self.clear_list)
        button_layout.addWidget(self.clear_button)
        
        button_layout.addStretch()
        
        # 閉じるボタン
        self.close_button = QPushButton("閉じる")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # 選択されたフォルダ
        self.selected_folder: Optional[Path] = None
        self.word_files: List[Path] = []
        
    @pyqtSlot()
    def select_folder(self):
        """フォルダを選択"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "検証するWordファイルが含まれるフォルダを選択",
            str(Path.home())
        )
        
        if folder:
            self.selected_folder = Path(folder)
            # Wordファイルを検索
            self.word_files = list(self.selected_folder.glob("*.docx"))
            
            if self.word_files:
                self.status_label.setText(
                    f"選択: {self.selected_folder.name} ({len(self.word_files)}個のWordファイル)"
                )
                self.start_button.setEnabled(True)
            else:
                QMessageBox.warning(
                    self,
                    "ファイルが見つかりません",
                    "選択したフォルダにWordファイル(.docx)が見つかりませんでした。"
                )
                self.start_button.setEnabled(False)
                
    @pyqtSlot()
    def start_check(self):
        """Pre-flight Checkを開始"""
        if not self.word_files:
            return
            
        # メールアドレスを取得（環境変数から）
        import os
        email = os.getenv("GMAIL_ADDRESS")
        if not email:
            QMessageBox.critical(
                self,
                "設定エラー",
                "環境変数GMAIL_ADDRESSが設定されていません。"
            )
            return
            
        # UIを更新
        self.select_folder_button.setEnabled(False)
        self.start_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # ワーカースレッドを開始
        self.worker = PreflightWorker(self.word_files, email)
        self.worker.file_checked.connect(self.on_file_checked)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.status_updated.connect(self.update_status)
        self.worker.finished.connect(self.on_check_finished)
        self.worker.start()
        
    @pyqtSlot(str, bool, str)
    def on_file_checked(self, filename: str, is_error: bool, message: str):
        """ファイルチェック結果を受信"""
        if is_error:
            self.add_error_file(filename)
            
    @pyqtSlot(str)
    def add_error_file(self, filename):
        """エラーファイルを追加"""
        item = QListWidgetItem(filename)
        item.setForeground(Qt.GlobalColor.red)
        self.error_list.addItem(item)
        
        # エラー数を更新
        error_count = self.error_list.count()
        self.update_status(f"エラーファイル: {error_count}件")
        
    @pyqtSlot(str)
    def update_status(self, status):
        """ステータスを更新"""
        self.status_label.setText(status)
        
    @pyqtSlot()
    def on_check_finished(self):
        """チェック完了時の処理"""
        self.select_folder_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.set_check_complete()
        
    @pyqtSlot()
    def set_check_complete(self):
        """チェック完了を設定"""
        error_count = self.error_list.count()
        if error_count == 0:
            self.status_label.setText("✓ すべてのファイルがPDF変換可能です")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText(f"✗ チェック完了 - エラーファイル: {error_count}件")
            self.status_label.setStyleSheet("color: red;")
            
    @pyqtSlot()
    def clear_list(self):
        """リストをクリア"""
        self.error_list.clear()
        self.status_label.setText("リストがクリアされました")
        self.status_label.setStyleSheet("")
        self.selected_folder = None
        self.word_files = []
        self.start_button.setEnabled(False)
        
    def closeEvent(self, event):
        """閉じるイベント"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "確認",
                "検証が実行中です。中止して閉じますか？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
                
            self.worker.cancel()
            self.worker.wait()
            
        self.closed.emit()
        super().closeEvent(event)