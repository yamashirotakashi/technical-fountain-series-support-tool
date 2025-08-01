#!/usr/bin/env python3
"""
Qt6診断スクリプト - Windows環境でのQt6問題を診断・修復
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Python バージョン確認"""
    print("🐍 Python 環境確認")
    print("=" * 40)
    print(f"Python バージョン: {sys.version}")
    print(f"Python 実行ファイル: {sys.executable}")
    print(f"仮想環境: {'✅' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else '❌'}")
    
def check_qt_installation():
    """Qt関連パッケージの確認"""
    print("\n🔧 Qt関連パッケージ確認")
    print("=" * 40)
    
    packages_to_check = [
        'PyQt6',
        'PyQt6-Qt6', 
        'PyQt6-sip',
        'asyncqt'
    ]
    
    for package in packages_to_check:
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'show', package], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                version_line = next((line for line in lines if line.startswith('Version:')), None)
                version = version_line.split(': ')[1] if version_line else 'Unknown'
                print(f"✅ {package}: {version}")
            else:
                print(f"❌ {package}: 未インストール")
        except Exception as e:
            print(f"❌ {package}: 確認エラー ({e})")

def test_qt_imports():
    """Qt インポートテスト"""
    print("\n📦 Qt インポートテスト")
    print("=" * 40)
    
    # PyQt6 基本インポート
    try:
        import PyQt6
        print(f"✅ PyQt6: {PyQt6.__file__}")
    except ImportError as e:
        print(f"❌ PyQt6: {e}")
        return False
    
    # PyQt6.QtCore
    try:
        from PyQt6 import QtCore
        print(f"✅ PyQt6.QtCore: {QtCore.QT_VERSION_STR}")
    except ImportError as e:
        print(f"❌ PyQt6.QtCore: {e}")
        return False
    
    # PyQt6.QtWidgets
    try:
        from PyQt6 import QtWidgets
        print("✅ PyQt6.QtWidgets: OK")
    except ImportError as e:
        print(f"❌ PyQt6.QtWidgets: {e}")
        return False
    
    # QApplication 作成テスト
    try:
        app = QtWidgets.QApplication([])
        print("✅ QApplication 作成: OK")
        app.quit()
    except Exception as e:
        print(f"❌ QApplication 作成: {e}")
        return False
    
    # asyncqt インポート
    try:
        import asyncqt
        print("✅ asyncqt: OK")
    except ImportError as e:
        print(f"❌ asyncqt: {e}")
        return False
    
    return True

def suggest_fixes():
    """修復提案"""
    print("\n🔨 修復提案")
    print("=" * 40)
    print("以下のコマンドを順番に実行してください:\n")
    
    print("1. 現在のQt関連パッケージをアンインストール:")
    print("   pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip asyncqt -y\n")
    
    print("2. pipをアップグレード:")
    print("   python -m pip install --upgrade pip\n")
    
    print("3. Qt6パッケージを再インストール:")
    print("   pip install PyQt6>=6.5.0")
    print("   pip install PyQt6-Qt6>=6.5.0") 
    print("   pip install asyncqt>=0.8.0\n")
    
    print("4. 代替案 - PyQt5を使用:")
    print("   pip install PyQt5>=5.15.0")
    print("   pip install qasync>=0.10.0\n")
    
    print("5. システム環境変数の確認:")
    print("   QT_QPA_PLATFORM_PLUGIN_PATH が設定されている場合は削除")

def create_minimal_test():
    """最小限のQt6テストファイルを作成"""
    print("\n📝 最小限のテストファイル作成")
    print("=" * 40)
    
    test_content = '''#!/usr/bin/env python3
"""
最小限のQt6テスト
"""
import sys

def test_basic_qt():
    try:
        from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
        
        app = QApplication(sys.argv)
        
        window = QWidget()
        window.setWindowTitle("Qt6 テスト")
        window.setGeometry(100, 100, 300, 200)
        
        layout = QVBoxLayout()
        label = QLabel("Qt6 正常動作確認！")
        layout.addWidget(label)
        window.setLayout(layout)
        
        window.show()
        
        print("✅ Qt6 GUI正常表示")
        print("ウィンドウを閉じてください...")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Qt6 GUIエラー: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_basic_qt())
'''
    
    test_file = Path("test_qt_minimal.py")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"✅ テストファイル作成: {test_file}")
    print("実行方法: python test_qt_minimal.py")

def main():
    """メイン診断"""
    print("🔍 Qt6 診断ツール")
    print("=" * 50)
    
    check_python_version()
    check_qt_installation()
    
    if not test_qt_imports():
        suggest_fixes()
        create_minimal_test()
        return 1
    
    print("\n🎉 Qt6 正常に動作しています！")
    create_minimal_test()
    return 0

if __name__ == "__main__":
    sys.exit(main())