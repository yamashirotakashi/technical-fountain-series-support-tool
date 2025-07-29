#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CodeBlock Overflow Checker - 独立版
Windows PowerShell環境対応（パス修正版）

Phase 2C-1 実装
独立した溢れチェックアプリケーション
"""

import sys
import os
from pathlib import Path

# PowerShell環境での絶対パス設定
current_dir = Path(__file__).parent.absolute()
parent_dir = current_dir.parent

# 必要なパスを最優先で追加
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(parent_dir))

# Windows環境での文字コード対応
if sys.platform == 'win32':
    import locale
    import codecs
    # PowerShell環境でのUTF-8対応
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
    except:
        pass  # バッファーが存在しない場合はスキップ

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# モジュールインポート（例外処理付き）
try:
    from gui.main_window import OverflowCheckerMainWindow
    from utils.windows_utils import setup_windows_environment
except ImportError as e:
    print(f"モジュールインポートエラー: {e}")
    print(f"現在のディレクトリ: {current_dir}")
    print(f"Pythonパス: {sys.path[:3]}")
    sys.exit(1)

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