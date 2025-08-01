#!/usr/bin/env python3
"""
最小限のQt6テスト
"""
import sys

def test_basic_qt():
    try:
        from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
        
        app = QApplication(sys.argv)
        
        window = QWidget()
        window.setWindowTitle("Qt6 テスト")
        window.setGeometry(100, 100, 300, 200)
        
        layout = QVBoxLayout()
        label = QLabel("Qt6 正常動作確認！")
        layout.addWidget(label)
        window.setLayout(layout)
        
        window.show()
        
        print("✅ Qt6 GUI正常表示")
        print("ウィンドウを閉じてください...")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Qt6 GUIエラー: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_basic_qt())
