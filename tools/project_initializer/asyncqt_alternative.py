"""
asyncqt代替実装 - Qt6専用
"""
import asyncio
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

class QEventLoop:
    """asyncqt.QEventLoop の代替実装"""
    
    def __init__(self, app=None):
        self.app = app if app else QApplication.instance()
        if not self.app:
            raise RuntimeError("QApplication instance required")
        
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        # タイマーでasyncioイベントループを駆動
        self.timer = QTimer()
        self.timer.timeout.connect(self._process_events)
        self.timer.start(10)  # 10msごと
    
    def _process_events(self):
        """asyncioイベントを処理"""
        try:
            self._loop.stop()
            self._loop.run_until_complete(asyncio.sleep(0))
        except:
            pass
    
    def run_forever(self):
        """メインループ実行"""
        return self.app.exec()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.timer.stop()
        self._loop.close()
