#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import debugging script - part 2
"""

import sys
import traceback
import os
from pathlib import Path

# パス設定
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent))

print(f"Current directory: {current_dir}")
print(f"Working directory: {os.getcwd()}")
print(f"GUI directory exists: {(current_dir / 'gui').exists()}")
print(f"result_dialog.py exists: {(current_dir / 'gui' / 'result_dialog.py').exists()}")

# ファイル直接実行テスト
gui_path = current_dir / 'gui'
result_dialog_path = gui_path / 'result_dialog.py'

print(f"\nTrying to execute result_dialog.py directly...")
try:
    # result_dialog.pyファイルを直接読み込み
    import importlib.util
    spec = importlib.util.spec_from_file_location("result_dialog", result_dialog_path)
    result_dialog = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result_dialog)
    print("✓ result_dialog.py executed successfully")
    
    # クラスの存在確認
    if hasattr(result_dialog, 'OverflowResultDialog'):
        print("✓ OverflowResultDialog class found")
    else:
        print("❌ OverflowResultDialog class not found")
        print(f"Available attributes: {dir(result_dialog)}")
        
except Exception as e:
    print(f"❌ Error executing result_dialog.py: {e}")
    traceback.print_exc()

print(f"\nTrying standard import with absolute path...")
try:
    # 絶対パス追加
    gui_path_str = str(gui_path)
    if gui_path_str not in sys.path:
        sys.path.insert(0, gui_path_str)
    
    print(f"Added to sys.path: {gui_path_str}")
    print("Updated sys.path:")
    for i, path in enumerate(sys.path[:10]):
        print(f"  {i}: {path}")
    
    # 直接インポート
    import result_dialog
    print("✓ result_dialog imported as module")
    
    # gui.result_dialog インポート
    from gui import result_dialog as gui_result_dialog
    print("✓ gui.result_dialog imported successfully")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    traceback.print_exc()