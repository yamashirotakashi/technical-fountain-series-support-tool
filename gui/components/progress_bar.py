"""プログレスバーパネルモジュール"""
from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSlot


class ProgressPanel(QWidget):
    """プログレスバーパネルウィジェット"""
    
    def __init__(self, parent=None):
        """
        ProgressPanelを初期化
        
        Args:
            parent: 親ウィジェット
        """
        super().__init__(parent)
        self.total_items = 0
        self.current_item = 0
        self.setup_ui()
    
    def setup_ui(self):
        """UIを構築"""
        layout = QVBoxLayout(self)
        
        # 状況ラベル
        self.status_label = QLabel("準備中...")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #333;
                margin-bottom: 5px;
                font-weight: bold;
            }
        """)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        # 詳細ラベル
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                color: #666;
                margin-top: 5px;
            }
        """)
        
        # レイアウトに追加
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.detail_label)
    
    @pyqtSlot(int)
    def update_progress(self, value: int):
        """
        プログレスを更新
        
        Args:
            value: 進捗値（0-100）
        """
        self.progress_bar.setValue(value)
    
    @pyqtSlot(str)
    def update_status(self, status: str):
        """
        ステータスを更新
        
        Args:
            status: ステータス文字列
        """
        self.status_label.setText(status)
    
    @pyqtSlot(str)
    def update_detail(self, detail: str):
        """
        詳細情報を更新
        
        Args:
            detail: 詳細文字列
        """
        self.detail_label.setText(detail)
    
    def set_total_items(self, total: int):
        """
        総アイテム数を設定
        
        Args:
            total: 総アイテム数
        """
        self.total_items = total
        self.current_item = 0
        self.progress_bar.setMaximum(total if total > 0 else 100)
        self.progress_bar.setValue(0)
    
    def increment_progress(self):
        """プログレスを1つ進める"""
        self.current_item += 1
        if self.total_items > 0:
            progress = int((self.current_item / self.total_items) * 100)
            self.progress_bar.setValue(progress)
    
    def reset(self):
        """プログレスをリセット"""
        self.progress_bar.setValue(0)
        self.current_item = 0
        self.update_status("準備完了")
        self.update_detail("")
    
    def set_range(self, minimum: int, maximum: int):
        """
        プログレスバーの範囲を設定
        
        Args:
            minimum: 最小値
            maximum: 最大値
        """
        self.progress_bar.setMinimum(minimum)
        self.progress_bar.setMaximum(maximum)