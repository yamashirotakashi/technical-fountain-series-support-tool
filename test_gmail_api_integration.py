#!/usr/bin/env python3
"""Gmail API方式の統合テスト"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_gmail_api_flow():
    """Gmail API方式の処理フロー全体をテスト"""
    print("=== Gmail API方式統合テスト ===\n")
    
    # Qtアプリケーション初期化
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # メインウィンドウを作成
    from gui.main_window import MainWindow
    window = MainWindow()
    
    # 処理方式をGmail API方式に設定
    print("1. 処理方式をGmail API方式に設定...")
    window.process_mode = "gmail_api"
    print(f"   設定完了: process_mode = {window.process_mode}")
    
    # テスト用Nコード
    test_n_codes = ["N00001"]
    
    # 処理開始をシミュレート
    print("\n2. 処理開始をシミュレート...")
    
    def simulate_processing():
        """処理開始を非同期でシミュレート"""
        # メールパスワードはGMAIL_APIを設定
        window.start_processing(test_n_codes)
        
        # 5秒後にアプリケーション終了
        QTimer.singleShot(5000, app.quit)
    
    # 100ms後に処理開始（GUIの初期化を待つ）
    QTimer.singleShot(100, simulate_processing)
    
    # GUIを表示
    window.show()
    
    # イベントループ実行
    app.exec()
    
    print("\n✓ Gmail API方式統合テスト完了")

if __name__ == "__main__":
    test_gmail_api_flow()