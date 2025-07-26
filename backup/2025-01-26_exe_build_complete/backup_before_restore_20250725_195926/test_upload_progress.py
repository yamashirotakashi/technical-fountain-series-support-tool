#!/usr/bin/env python3
"""
アップロード進捗追跡のテスト
"""
import sys
import time
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QProgressBar, QLabel
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot

# プロジェクトのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from core.api_processor import ApiProcessor

class TestWorker(QThread):
    """テスト用ワーカースレッド"""
    log_message = pyqtSignal(str, str)
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, test_file_path):
        super().__init__()
        self.test_file_path = test_file_path
        
    def run(self):
        """テスト実行"""
        try:
            processor = ApiProcessor()
            
            # シグナル接続
            processor.log_message.connect(self.log_message.emit)
            processor.progress_updated.connect(self.progress_updated.emit)
            processor.status_updated.connect(self.status_updated.emit)
            
            # アップロードテスト
            self.log_message.emit("テストファイルのアップロードを開始します", "INFO")
            jobid = processor.upload_zip(Path(self.test_file_path))
            
            if jobid:
                self.log_message.emit(f"アップロード成功: Job ID = {jobid}", "INFO")
            else:
                self.log_message.emit("アップロード失敗", "ERROR")
                
        except Exception as e:
            self.log_message.emit(f"エラー: {str(e)}", "ERROR")
        finally:
            self.finished.emit()

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("アップロード進捗テスト")
        self.setGeometry(100, 100, 800, 600)
        
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # レイアウト
        layout = QVBoxLayout(central_widget)
        
        # ステータスラベル
        self.status_label = QLabel("準備完了")
        layout.addWidget(self.status_label)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        # ログ表示
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # テストボタン
        test_button = QPushButton("テスト用ZIPファイルをアップロード")
        test_button.clicked.connect(self.start_test)
        layout.addWidget(test_button)
        
        self.worker = None
        
    def start_test(self):
        """テスト開始"""
        # テスト用のZIPファイルを作成
        import tempfile
        import zipfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.zip', delete=False) as tmp:
            test_zip_path = tmp.name
            
        # 1MBのテストファイルを含むZIPを作成
        with zipfile.ZipFile(test_zip_path, 'w') as zf:
            # ダミーデータを作成
            dummy_data = b'A' * (1024 * 1024)  # 1MB
            zf.writestr('test_file.txt', dummy_data)
            
        self.log_text.append(f"テストファイル作成: {test_zip_path}")
        
        # ワーカースレッド開始
        self.worker = TestWorker(test_zip_path)
        self.worker.log_message.connect(self.append_log)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.status_updated.connect(self.update_status)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
        
    @pyqtSlot(str, str)
    def append_log(self, message, level):
        """ログ追加"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {level}: {message}")
        
    @pyqtSlot(int)
    def update_progress(self, value):
        """プログレスバー更新"""
        self.progress_bar.setValue(value)
        
    @pyqtSlot(str)
    def update_status(self, status):
        """ステータス更新"""
        self.status_label.setText(status)
        
    @pyqtSlot()
    def on_finished(self):
        """処理完了"""
        self.log_text.append("テスト完了")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())