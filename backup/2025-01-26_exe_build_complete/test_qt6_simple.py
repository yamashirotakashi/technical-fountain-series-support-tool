#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""シンプルなQt6動作テスト"""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt

def main():
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("Qt6 Test")
    window.setGeometry(100, 100, 400, 200)
    
    label = QLabel("PyQt6 is working!", window)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    window.setCentralWidget(label)
    
    window.show()
    
    print("Qt6 テストウィンドウを表示しています...")
    print("ウィンドウを閉じてください")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()