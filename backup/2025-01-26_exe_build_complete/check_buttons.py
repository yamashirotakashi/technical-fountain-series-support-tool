"""ボタンの表示状態を確認するスクリプト"""
import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def check_buttons():
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # InputPanelのボタンを確認
    input_panel = window.input_panel
    
    print("=== ボタンの状態確認 ===")
    print(f"処理ボタン: {hasattr(input_panel, 'process_button')} - 表示: {input_panel.process_button.isVisible() if hasattr(input_panel, 'process_button') else 'N/A'}")
    print(f"クリアボタン: {hasattr(input_panel, 'clear_button')} - 表示: {input_panel.clear_button.isVisible() if hasattr(input_panel, 'clear_button') else 'N/A'}")
    print(f"設定ボタン: {hasattr(input_panel, 'settings_button')} - 表示: {input_panel.settings_button.isVisible() if hasattr(input_panel, 'settings_button') else 'N/A'}")
    
    if hasattr(input_panel, 'settings_button'):
        print(f"設定ボタンのテキスト: {input_panel.settings_button.text()}")
        print(f"設定ボタンのサイズ: {input_panel.settings_button.size()}")
    
    print("\n=== 処理モード ===")
    print(f"現在の処理モード: {window.process_mode}")
    
    # 設定ボタンをクリックしてみる
    if hasattr(input_panel, 'settings_button'):
        print("\n設定ボタンをクリックします...")
        input_panel.settings_button.click()

if __name__ == "__main__":
    check_buttons()