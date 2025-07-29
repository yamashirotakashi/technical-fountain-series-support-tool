#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CodeBlock Overflow Checker - 独立版 最終実行ファイル
Windows PowerShell環境対応

Phase 2C-1 実装
依存関係解決済み実行ファイル
"""

import sys
import os
from pathlib import Path
import importlib.util

# 絶対パス設定
script_dir = Path(__file__).parent.absolute()
parent_dir = script_dir.parent

# 全ての必要なパスをsys.pathに追加
paths_to_add = [
    str(script_dir),
    str(parent_dir),
    str(script_dir / 'gui'),
    str(script_dir / 'core'), 
    str(script_dir / 'utils'),
]

for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

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

def load_module_with_dependencies(module_name, file_path, dependencies=None):
    """依存関係解決付きモジュール読み込み"""
    if dependencies:
        for dep_name, dep_path in dependencies.items():
            if dep_name not in sys.modules:
                print(f"  依存関係読み込み: {dep_name}")
                load_module_with_dependencies(dep_name, dep_path)
    
    if module_name not in sys.modules:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    else:
        return sys.modules[module_name]

def main():
    """アプリケーションメイン関数"""
    
    try:
        # PyQt6の確認
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        print("✓ PyQt6インポート成功")
        
        # 1. Windows utilsの読み込み（依存なし）
        utils_path = script_dir / 'utils' / 'windows_utils.py'
        windows_utils = load_module_with_dependencies('windows_utils', utils_path)
        setup_windows_environment = windows_utils.setup_windows_environment
        print("✓ Windows utilsロード成功")
        
        # 2. Learning managerの読み込み（windows_utilsに依存）
        learning_deps = {
            'windows_utils': utils_path
        }
        learning_path = script_dir / 'core' / 'learning_manager.py'
        learning_manager = load_module_with_dependencies('learning_manager', learning_path, learning_deps)
        WindowsLearningDataManager = learning_manager.WindowsLearningDataManager
        print("✓ Learning managerロード成功")
        
        # 3. PDF processorの読み込み（windows_utilsに依存）
        pdf_deps = {
            'windows_utils': utils_path
        }
        processor_path = script_dir / 'core' / 'pdf_processor.py'
        pdf_processor = load_module_with_dependencies('pdf_processor', processor_path, pdf_deps)
        PDFOverflowProcessor = pdf_processor.PDFOverflowProcessor
        print("✓ PDF processorロード成功")
        
        # 4. Result dialogの読み込み（learning_manager, windows_utilsに依存）
        result_deps = {
            'windows_utils': utils_path,
            'learning_manager': learning_path
        }
        result_dialog_path = script_dir / 'gui' / 'result_dialog.py'
        result_dialog = load_module_with_dependencies('result_dialog', result_dialog_path, result_deps)
        OverflowResultDialog = result_dialog.OverflowResultDialog
        print("✓ Result dialogロード成功")
        
        # 5. Main windowの読み込み（全ての依存関係）
        main_deps = {
            'windows_utils': utils_path,
            'pdf_processor': processor_path,
            'result_dialog': result_dialog_path
        }
        main_window_path = script_dir / 'gui' / 'main_window.py'
        main_window = load_module_with_dependencies('main_window', main_window_path, main_deps)
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
        
        print("✅ CodeBlock Overflow Checker 起動完了!")
        print("PDFファイルを選択して溢れチェック機能をお試しください。")
        
        return app.exec()
        
    except Exception as e:
        import traceback
        print(f"❌ アプリケーション起動エラー: {e}")
        print("詳細:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())