"""進捗表示バーモジュール"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSlot


class ProgressPanel(QWidget):
    """進捗表示パネルウィジェット"""
    
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
        
        # 状態ラベル
        self.status_label = QLabel("待機中...")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #333;
                padding: 2px;
            }
        """)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        # 詳細ラベル
        detail_layout = QHBoxLayout()
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                color: #666;
            }
        """)
        self.time_label = QLabel("")
        self.time_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                color: #666;
            }
        """)
        
        detail_layout.addWidget(self.detail_label)
        detail_layout.addStretch()
        detail_layout.addWidget(self.time_label)
        
        # レイアウトに追加
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(detail_layout)
    
    @pyqtSlot(int, int)
    def set_total_items(self, total: int, current: int = 0):
        """
        処理する総アイテム数を設定
        
        Args:
            total: 総アイテム数
            current: 現在のアイテム番号
        """
        self.total_items = total
        self.current_item = current
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.update_detail_label()
    
    @pyqtSlot(int)
    def update_progress(self, value: int):
        """
        進捗を更新
        
        Args:
            value: 進捗値（0-100またはアイテム番号）
        """
        if self.total_items > 0:
            # アイテム番号として処理
            self.current_item = value
            self.progress_bar.setValue(value)
            percentage = int((value / self.total_items) * 100)
            self.progress_bar.setFormat(f"{percentage}%")
        else:
            # パーセンテージとして処理
            self.progress_bar.setValue(value)
            self.progress_bar.setFormat(f"{value}%")
        
        self.update_detail_label()
    
    @pyqtSlot(str)
    def update_status(self, message: str):
        """
        状態メッセージを更新
        
        Args:
            message: 状態メッセージ
        """
        self.status_label.setText(message)
    
    @pyqtSlot(str)
    def update_time(self, time_str: str):
        """
        経過時間を更新
        
        Args:
            time_str: 時間文字列
        """
        self.time_label.setText(time_str)
    
    def update_detail_label(self):
        """詳細ラベルを更新"""
        if self.total_items > 0:
            self.detail_label.setText(f"{self.current_item}/{self.total_items} 処理中")
        else:
            self.detail_label.setText("")
    
    def reset(self):
        """進捗をリセット"""
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        self.status_label.setText("待機中...")
        self.detail_label.setText("")
        self.time_label.setText("")
        self.total_items = 0
        self.current_item = 0
    
    def set_indeterminate(self, is_indeterminate: bool):
        """
        不確定進捗モードを設定
        
        Args:
            is_indeterminate: 不確定モードにする場合True
        """
        if is_indeterminate:
            self.progress_bar.setMaximum(0)
            self.progress_bar.setMinimum(0)
        else:
            self.progress_bar.setMaximum(100)
            self.progress_bar.setMinimum(0)