"""
Qt6ベース基底ウィンドウクラス
単一責任: 共通UIコンポーネントとレイアウトの提供
"""
import sys
from typing import Optional, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGroupBox, QLabel, QFrame, QApplication, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor


class BaseWindow(QMainWindow):
    """基底ウィンドウクラス - Qt6ベース"""
    
    # シグナル定義
    window_closed = pyqtSignal()
    
    def __init__(self, title: str = "TechImgFile", width: int = 800, height: int = 600):
        """初期化
        
        Args:
            title: ウィンドウタイトル
            width: ウィンドウ幅
            height: ウィンドウ高さ
        """
        super().__init__()
        self.setWindowTitle(title)
        self.setMinimumSize(width, height)
        self.resize(width, height)
        
        # メインウィジェットとレイアウト
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self._setup_styles()
        self._setup_ui()
    
    def _setup_styles(self):
        """スタイルシートの設定"""
        style = """
        QMainWindow {
            background-color: #f0f0f0;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 5px;
            margin-top: 1em;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QPushButton {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 8px 16px;
            text-align: center;
            font-size: 14px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
        """
        self.setStyleSheet(style)
    
    def _setup_ui(self):
        """UI初期設定 - サブクラスでオーバーライド"""
        pass
    
    def add_section(self, title: str, widget: QWidget) -> QGroupBox:
        """セクションを追加
        
        Args:
            title: セクションタイトル
            widget: 追加するウィジェット
            
        Returns:
            作成されたQGroupBox
        """
        group_box = QGroupBox(title)
        layout = QVBoxLayout()
        layout.addWidget(widget)
        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)
        return group_box
    
    def show_error(self, title: str, message: str):
        """エラーダイアログを表示"""
        QMessageBox.critical(self, title, message)
    
    def show_info(self, title: str, message: str):
        """情報ダイアログを表示"""
        QMessageBox.information(self, title, message)
    
    def show_warning(self, title: str, message: str):
        """警告ダイアログを表示"""
        QMessageBox.warning(self, title, message)
    
    def ask_yes_no(self, title: str, message: str) -> bool:
        """Yes/Noダイアログを表示"""
        reply = QMessageBox.question(self, title, message, 
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        return reply == QMessageBox.StandardButton.Yes
    
    def closeEvent(self, event):
        """ウィンドウクローズイベント"""
        if self.confirm_close():
            self.window_closed.emit()
            event.accept()
        else:
            event.ignore()
    
    def confirm_close(self) -> bool:
        """終了確認 - サブクラスでオーバーライド可能"""
        return True
    
    def show_window(self):
        """ウィンドウを表示"""
        self.show()
        self.raise_()
        self.activateWindow()


class FramedSection(QGroupBox):
    """フレーム付きセクションウィジェット"""
    
    def __init__(self, title: str, parent: Optional[QWidget] = None):
        """初期化
        
        Args:
            title: セクションタイトル
            parent: 親ウィジェット
        """
        super().__init__(title, parent)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
    
    def add_widget(self, widget: QWidget):
        """ウィジェットを追加"""
        self.layout.addWidget(widget)
    
    def add_layout(self, layout):
        """レイアウトを追加"""
        self.layout.addLayout(layout)


def create_app() -> QApplication:
    """QApplicationインスタンスを作成"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app