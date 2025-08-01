"""
asyncqt修正版 - Qt6とasyncioの完全統合
"""
import asyncio
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

class AsyncioEventBridge(QObject):
    """asyncioとQt間のブリッジ"""
    
    def __init__(self, loop):
        super().__init__()
        self.loop = loop
        self.timer = QTimer()
        self.timer.timeout.connect(self._process_asyncio_events)
    
    def start(self, interval=10):
        """ブリッジを開始"""
        self.timer.start(interval)
    
    def stop(self):
        """ブリッジを停止"""
        self.timer.stop()
    
    def _process_asyncio_events(self):
        """asyncioイベントを処理"""
        if self.loop and not self.loop.is_closed():
            try:
                # 待機中のコールバックを実行
                self.loop._run_once_impl()
            except:
                pass

class QEventLoop:
    """Qt6対応のasyncioイベントループ"""
    
    def __init__(self, app=None):
        self.app = app if app else QApplication.instance()
        if not self.app:
            raise RuntimeError("QApplication instance required")
        
        # asyncioループを作成
        self.asyncio_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.asyncio_loop)
        
        # Qt-asyncio ブリッジを作成
        self.bridge = AsyncioEventBridge(self.asyncio_loop)
        self.bridge.start()
    
    def run_forever(self):
        """Qtアプリケーションを実行"""
        try:
            return self.app.exec()
        finally:
            self.bridge.stop()
            if not self.asyncio_loop.is_closed():
                self.asyncio_loop.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.bridge.stop()
        if not self.asyncio_loop.is_closed():
            self.asyncio_loop.close()