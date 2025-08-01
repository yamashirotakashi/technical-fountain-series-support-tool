"""
シンプルなテスト用EXE
PyInstallerの基本動作確認用
"""

import sys
import os

def main():
    print("=== PJinit Test EXE ===")
    print(f"Python Version: {sys.version}")
    print(f"Executable: {sys.executable}")
    print(f"Current Dir: {os.getcwd()}")
    
    # PyQt6のインポートテスト
    try:
        from PyQt6.QtCore import QT_VERSION_STR
        print(f"PyQt6 Version: {QT_VERSION_STR}")
    except Exception as e:
        print(f"PyQt6 Import Error: {e}")
    
    # 基本的なGUIテスト
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        app = QApplication(sys.argv)
        QMessageBox.information(None, "Test", "PJinit Test - PyQt6 is working!")
        print("GUI Test: OK")
    except Exception as e:
        print(f"GUI Error: {e}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()