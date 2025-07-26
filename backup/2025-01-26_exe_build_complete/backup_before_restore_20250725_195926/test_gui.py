#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GUIテストスクリプト"""
import sys
import os

# X11ディスプレイ設定
if 'DISPLAY' not in os.environ:
    os.environ['DISPLAY'] = ':0'

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
    from PyQt6.QtCore import Qt
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("テスト")
    window.setGeometry(100, 100, 400, 300)
    
    label = QLabel("PyQt5が正しく動作しています！", window)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    window.setCentralWidget(label)
    
    window.show()
    sys.exit(app.exec())
    
except Exception as e:
    print(f"エラー: {e}")
    print("\nWSL環境でGUIを実行するには以下が必要です:")
    print("1. Windows側でX11サーバー（VcXsrv、Xming等）を実行")
    print("2. または WSL2 + WSLg (Windows 11)")
    print("3. 環境変数 DISPLAY の設定")