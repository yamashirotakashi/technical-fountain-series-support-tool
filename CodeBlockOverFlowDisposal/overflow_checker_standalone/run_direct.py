#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CodeBlock Overflow Checker - 独立版 直接実行
Windows PowerShell環境対応

Phase 2C-1 実装
直接インポートによる問題回避
"""

import sys
import os
from pathlib import Path
import importlib.util

# 絶対パス設定
script_dir = Path(__file__).parent.absolute()
parent_dir = script_dir.parent

# Pythonパスを明示的に設定
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(script_dir / 'gui'))
sys.path.insert(0, str(script_dir / 'core'))
sys.path.insert(0, str(script_dir / 'utils'))

print(f"実行ディレクトリ: {script_dir}")

# Windows環境での文字コード対応
if sys.platform == 'win32':
    import locale
    import codecs
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
    except:
        pass

def load_module_from_file(module_name, file_path):
    """ファイルから直接モジュールを読み込み"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def main():
    """アプリケーションメイン関数"""
    
    try:
        # PyQt6の確認
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        print("✓ PyQt6インポート成功")
        
        # Windows utilsの直接読み込み
        utils_path = script_dir / 'utils' / 'windows_utils.py'
        windows_utils = load_module_from_file('windows_utils', utils_path)
        setup_windows_environment = windows_utils.setup_windows_environment
        print("✓ Windows utilsロード成功")
        
        # PDF processorの直接読み込み
        processor_path = script_dir / 'core' / 'pdf_processor.py'
        pdf_processor = load_module_from_file('pdf_processor', processor_path)
        PDFOverflowProcessor = pdf_processor.PDFOverflowProcessor
        print("✓ PDF processorロード成功")
        
        # Learning managerの直接読み込み
        learning_path = script_dir / 'core' / 'learning_manager.py'
        learning_manager = load_module_from_file('learning_manager', learning_path)
        WindowsLearningDataManager = learning_manager.WindowsLearningDataManager
        print("✓ Learning managerロード成功")
        
        # Result dialogの直接読み込み
        result_dialog_path = script_dir / 'gui' / 'result_dialog.py'
        result_dialog = load_module_from_file('result_dialog', result_dialog_path)
        OverflowResultDialog = result_dialog.OverflowResultDialog
        print("✓ Result dialogロード成功")
        
        # Main windowの直接読み込み
        main_window_path = script_dir / 'gui' / 'main_window.py'
        main_window = load_module_from_file('main_window', main_window_path)
        OverflowCheckerMainWindow = main_window.OverflowCheckerMainWindow
        print("✓ Main windowロード成功")
        
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