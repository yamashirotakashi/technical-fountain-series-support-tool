#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CodeBlock Overflow Checker - 独立版
Windows PowerShell環境対応

Phase 2C-1 実装
独立した溢れチェックアプリケーション
"""

import sys
import os
from pathlib import Path

# Windows環境での文字コード対応
if sys.platform == 'win32':
    import locale
    import codecs
    # PowerShell環境でのUTF-8対応
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from .gui.main_window import OverflowCheckerMainWindow
from .utils.windows_utils import setup_windows_environment

def main():
    """アプリケーションメイン関数"""
    
    # Windows環境セットアップ
    setup_windows_environment()
    
    # High DPI対応（Windows）
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("CodeBlock Overflow Checker")
    app.setOrganizationName("Technical Fountain")
    
    # Windowsスタイル適用
    app.setStyle("Fusion")
    
    try:
        # メインウィンドウ作成
        window = OverflowCheckerMainWindow()
        window.show()
        
        return app.exec()
        
    except Exception as e:
        import traceback
        print(f"アプリケーション起動エラー: {e}")
        print("詳細:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())