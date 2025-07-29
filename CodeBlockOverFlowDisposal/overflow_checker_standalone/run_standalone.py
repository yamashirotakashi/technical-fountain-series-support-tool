#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CodeBlock Overflow Checker - 独立版 実行ファイル
Windows PowerShell環境対応

Phase 2C-1 実装
独立した溢れチェックアプリケーション
"""

import sys
import os
from pathlib import Path

# 絶対パス設定（PowerShell環境対応）
script_dir = Path(__file__).parent.absolute()
parent_dir = script_dir.parent

# Pythonパスを明示的に設定
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

print(f"実行ディレクトリ: {script_dir}")
print(f"Pythonパス追加: {script_dir}")

# Windows環境での文字コード対応
if sys.platform == 'win32':
    import locale
    import codecs
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
    except:
        pass

# 必要なライブラリの動的インポート
def import_with_error_handling():
    """エラー処理付きモジュールインポート"""
    try:
        # PyQt6の確認
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        print("✓ PyQt6インポート成功")
        
        # utilsモジュールの確認
        from utils.windows_utils import setup_windows_environment
        print("✓ Windows utilsインポート成功")
        
        # coreモジュールの確認
        from core.pdf_processor import PDFOverflowProcessor
        print("✓ PDF processorインポート成功")
        
        # guiモジュールの確認
        from gui.main_window import OverflowCheckerMainWindow
        print("✓ Main windowインポート成功")
        
        return QApplication, Qt, setup_windows_environment, OverflowCheckerMainWindow
        
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        print(f"現在のディレクトリ構造:")
        for item in script_dir.iterdir():
            print(f"  {item.name}")
        sys.exit(1)

def main():
    """アプリケーションメイン関数"""
    
    # モジュールインポート
    QApplication, Qt, setup_windows_environment, OverflowCheckerMainWindow = import_with_error_handling()
    
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
        print("🚀 アプリケーション起動中...")
        
        # メインウィンドウ作成
        window = OverflowCheckerMainWindow()
        window.show()
        
        print("✓ アプリケーション起動完了")
        return app.exec()
        
    except Exception as e:
        import traceback
        print(f"❌ アプリケーション起動エラー: {e}")
        print("詳細:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())