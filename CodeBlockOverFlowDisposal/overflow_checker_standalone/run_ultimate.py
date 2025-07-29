#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CodeBlock Overflow Checker - 独立版 究極実行ファイル
Windows PowerShell環境対応

Phase 2C-1 実装
完全な名前空間解決済み実行ファイル
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

def load_module_with_namespace(module_name, file_path, namespace_aliases=None):
    """名前空間エイリアス付きモジュール読み込み"""
    if module_name not in sys.modules:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        
        # メインの名前で登録
        sys.modules[module_name] = module
        
        # 名前空間エイリアスも登録
        if namespace_aliases:
            for alias in namespace_aliases:
                sys.modules[alias] = module
        
        spec.loader.exec_module(module)
        return module
    else:
        return sys.modules[module_name]

def create_namespace_packages():
    """仮想名前空間パッケージを作成"""
    import types
    
    # coreパッケージを作成
    if 'core' not in sys.modules:
        core_module = types.ModuleType('core')
        core_module.__path__ = [str(script_dir / 'core')]
        sys.modules['core'] = core_module
    
    # guiパッケージを作成
    if 'gui' not in sys.modules:
        gui_module = types.ModuleType('gui')
        gui_module.__path__ = [str(script_dir / 'gui')]
        sys.modules['gui'] = gui_module
    
    # utilsパッケージを作成
    if 'utils' not in sys.modules:
        utils_module = types.ModuleType('utils')
        utils_module.__path__ = [str(script_dir / 'utils')]
        sys.modules['utils'] = utils_module

def main():
    """アプリケーションメイン関数"""
    
    # ログ設定をインポート
    sys.path.insert(0, str(script_dir / 'utils'))
    from logging_config import configure_logging
    configure_logging()
    
    try:
        # PyQt6の確認
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        print("✓ PyQt6インポート成功")
        
        # 名前空間パッケージを事前作成
        create_namespace_packages()
        print("✓ 名前空間パッケージ作成完了")
        
        # 1. Windows utilsの読み込み
        utils_path = script_dir / 'utils' / 'windows_utils.py'
        windows_utils = load_module_with_namespace(
            'windows_utils', 
            utils_path, 
            ['utils.windows_utils']
        )
        setup_windows_environment = windows_utils.setup_windows_environment
        print("✓ Windows utilsロード成功")
        
        # 2. Learning managerの読み込み
        learning_path = script_dir / 'core' / 'learning_manager.py'
        learning_manager = load_module_with_namespace(
            'learning_manager', 
            learning_path, 
            ['core.learning_manager']
        )
        WindowsLearningDataManager = learning_manager.WindowsLearningDataManager
        print("✓ Learning managerロード成功")
        
        # 3. PDF processorの読み込み
        processor_path = script_dir / 'core' / 'pdf_processor.py'
        pdf_processor = load_module_with_namespace(
            'pdf_processor', 
            processor_path, 
            ['core.pdf_processor']
        )
        PDFOverflowProcessor = pdf_processor.PDFOverflowProcessor
        print("✓ PDF processorロード成功")
        
        # 4. Result dialogの読み込み
        result_dialog_path = script_dir / 'gui' / 'result_dialog.py'
        result_dialog = load_module_with_namespace(
            'result_dialog', 
            result_dialog_path, 
            ['gui.result_dialog']
        )
        OverflowResultDialog = result_dialog.OverflowResultDialog
        print("✓ Result dialogロード成功")
        
        # 5. Main windowの読み込み
        main_window_path = script_dir / 'gui' / 'main_window.py'
        main_window = load_module_with_namespace(
            'main_window', 
            main_window_path, 
            ['gui.main_window']
        )
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
        
        print("🎉 CodeBlock Overflow Checker 起動完了!")
        print("📄 PDFファイルを選択して溢れチェック機能をお試しください。")
        print("🔍 技術書のB5判形式（515.9 x 728.5pt）に最適化されています。")
        
        return app.exec()
        
    except Exception as e:
        import traceback
        print(f"❌ アプリケーション起動エラー: {e}")
        print("詳細:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())