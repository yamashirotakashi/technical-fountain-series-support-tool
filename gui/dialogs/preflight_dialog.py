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
            
            # 結果をチェック（すでにリアルタイムで表示済み）
            if not self._cancelled:
                self.status_updated.emit("検証処理が完了しました")
                # 完了時は状態をクリア
                self.batch_processor.state_manager.clear_state()
                
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
        elif job.status == "checking":
            self.status_updated.emit(f"結果待機中: {filename}")
        elif job.status == "error":
            self.file_checked.emit(filename, True, job.error_message or "エラー")
            self.status_updated.emit(f"エラー: {filename} - {job.error_message}")
        elif job.status == "success":
            self.file_checked.emit(filename, False, "成功")
            self.status_updated.emit(f"✓ 検証成功: {filename}")
            
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
        self.check_saved_state()
        
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
        
        # 追加説明
        info_label = QLabel("エラーが発見されたファイルはリアルタイムで表示されます")
        info_label.setFont(QFont("メイリオ", 8))
        info_label.setStyleSheet("color: gray;")
        header_layout.addWidget(info_label)
        
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 検証結果リスト
        list_label = QLabel("検証結果: (✅ 成功 / ❌ エラー)")
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
        
        # 中断ボタン
        self.pause_button = QPushButton("中断")
        self.pause_button.clicked.connect(self.pause_check)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)
        
        # 再開ボタン
        self.resume_button = QPushButton("再開")
        self.resume_button.clicked.connect(self.resume_check)
        self.resume_button.setEnabled(False)
        button_layout.addWidget(self.resume_button)
        
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
        
    def check_saved_state(self):
        """保存された状態をチェック"""
        from core.preflight.state_manager import PreflightStateManager
        state_manager = PreflightStateManager()
        state = state_manager.load_state()
        
        if state and state.get('jobs'):
            # 未完了のジョブがある場合
            incomplete_jobs = [job for job in state['jobs'].values() 
                             if job.get('status') not in ['success', 'error']]
            
            if incomplete_jobs:
                reply = QMessageBox.question(
                    self,
                    "前回の処理を再開",
                    f"前回中断された処理が見つかりました。\n"
                    f"未完了のファイル: {len(incomplete_jobs)}件\n\n"
                    f"再開しますか？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.resume_button.setEnabled(True)
                    self.status_label.setText("前回の処理を再開できます")
                    self.status_label.setStyleSheet("color: blue;")
        
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
        self.pause_button.setEnabled(True)
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
        else:
            # 成功したファイルも表示（緑色）
            item = QListWidgetItem(f"✅ {filename}")
            item.setForeground(Qt.GlobalColor.darkGreen)
            self.error_list.addItem(item)
            
    @pyqtSlot(str)
    def add_error_file(self, filename):
        """エラーファイルを追加"""
        item = QListWidgetItem(f"❌ {filename}")
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
    def pause_check(self):
        """検証を中断"""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.pause_button.setEnabled(False)
            self.resume_button.setEnabled(True)
            self.status_label.setText("検証を中断しました")
            self.status_label.setStyleSheet("color: orange;")
            
    @pyqtSlot()
    def resume_check(self):
        """検証を再開"""
        # メールアドレスを取得
        import os
        email = os.getenv("GMAIL_ADDRESS")
        if not email:
            QMessageBox.critical(
                self,
                "設定エラー",
                "環境変数GMAIL_ADDRESSが設定されていません。"
            )
            return
            
        # 状態を復元して処理を再開
        from core.preflight.batch_processor import BatchProcessor
        batch_processor = BatchProcessor()
        
        if batch_processor.resume_from_state():
            self.status_label.setText("保存された状態から再開中...")
            self.resume_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.progress_bar.setVisible(True)
            
            # 復元されたファイルリストを作成
            self.word_files = [Path(job.file_path) for job in batch_processor.jobs.values()]
            
            # ワーカースレッドを開始（復元されたバッチプロセッサーを使用）
            self.worker = PreflightWorker(self.word_files, email)
            self.worker.batch_processor = batch_processor
            self.worker.file_checked.connect(self.on_file_checked)
            self.worker.progress_updated.connect(self.progress_bar.setValue)
            self.worker.status_updated.connect(self.update_status)
            self.worker.finished.connect(self.on_check_finished)
            self.worker.start()
        else:
            QMessageBox.warning(
                self,
                "再開失敗",
                "保存された状態が見つかりません。"
            )
            
    @pyqtSlot()
    def on_check_finished(self):
        """チェック完了時の処理"""
        self.select_folder_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.set_check_complete()
        
    @pyqtSlot()
    def set_check_complete(self):
        """チェック完了を設定"""
        total_files = self.error_list.count()
        error_count = 0
        success_count = 0
        
        # エラーと成功をカウント
        for i in range(total_files):
            item_text = self.error_list.item(i).text()
            if item_text.startswith("❌"):
                error_count += 1
            elif item_text.startswith("✅"):
                success_count += 1
        
        if error_count == 0 and success_count > 0:
            self.status_label.setText(f"✓ すべてのファイルがPDF変換可能です ({success_count}件)")
            self.status_label.setStyleSheet("color: green;")
        elif error_count > 0:
            self.status_label.setText(f"✗ チェック完了 - 成功: {success_count}件 / エラー: {error_count}件")
            self.status_label.setStyleSheet("color: red;")
        else:
            self.status_label.setText("チェック完了")
            self.status_label.setStyleSheet("")
            
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