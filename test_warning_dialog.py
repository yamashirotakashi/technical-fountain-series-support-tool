#!/usr/bin/env python3
"""
警告ダイアログの単体テスト
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from gui.dialogs.warning_dialog import WarningDialog

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("警告ダイアログテスト")
        self.setGeometry(100, 100, 400, 300)
        
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # レイアウト
        layout = QVBoxLayout(central_widget)
        
        # テストボタン
        test_button = QPushButton("警告ダイアログを表示")
        test_button.clicked.connect(self.show_warning_dialog)
        layout.addWidget(test_button)
        
        # エラーダイアログテストボタン
        error_button = QPushButton("エラーダイアログを表示")
        error_button.clicked.connect(self.show_error_dialog)
        layout.addWidget(error_button)
    
    def show_warning_dialog(self):
        """警告ダイアログを表示"""
        messages = [
            "警告: ファイルが見つかりません",
            "警告: 設定が不完全です",
            "警告: バージョンが古い可能性があります"
        ]
        dialog = WarningDialog(messages, "partial_success", self)
        result = dialog.exec_()
        print(f"ダイアログ結果: {result}")
    
    def show_error_dialog(self):
        """エラーダイアログを表示"""
        messages = [
            "エラー: 変換に失敗しました",
            "エラー: ファイルが破損しています"
        ]
        dialog = WarningDialog(messages, "error", self)
        result = dialog.exec_()
        print(f"ダイアログ結果: {result}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())