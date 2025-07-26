"""GUIのスクリーンショットを撮るテストスクリプト"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from gui.main_window import MainWindow

def take_screenshot():
    """ウィンドウのスクリーンショットを撮る"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"gui_screenshot_{timestamp}.png"
    
    # ウィンドウのスクリーンショットを撮る
    window.grab().save(filename)
    print(f"スクリーンショットを保存しました: {filename}")
    
    # アプリケーションを終了
    app.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # 1秒後にスクリーンショットを撮る
    QTimer.singleShot(1000, take_screenshot)
    
    sys.exit(app.exec())