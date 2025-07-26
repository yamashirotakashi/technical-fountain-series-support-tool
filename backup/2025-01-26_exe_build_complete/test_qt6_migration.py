#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Qt6バージョンテストスクリプト"""
import sys
try:
    from PyQt6.QtWidgets import QApplication
    from gui.main_window import MainWindow
    
    app = QApplication(sys.argv)
    print("✓ PyQt6のインポート成功")
    
    window = MainWindow()
    print("✓ MainWindowの作成成功")
    
    window.show()
    print("✓ ウィンドウ表示成功")
    print("\nQt6移行が正常に完了しました！")
    
except Exception as e:
    print(f"✗ エラー: {e}")
    import traceback
    traceback.print_exc()
