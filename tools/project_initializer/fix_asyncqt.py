#!/usr/bin/env python3
"""
asyncqt専用修復スクリプト
PyQt6は動作するが、asyncqtが認識しない問題を解決
"""

import sys
import subprocess
import os

def fix_asyncqt_qt6():
    """asyncqtのQt6認識問題を修復"""
    print("🔧 asyncqt Qt6認識問題の修復")
    print("=" * 40)
    
    # 1. asyncqtのアンインストール
    print("1. asyncqtをアンインストール中...")
    subprocess.run([sys.executable, '-m', 'pip', 'uninstall', 'asyncqt', '-y'])
    
    # 2. キャッシュクリア
    print("2. pipキャッシュをクリア中...")
    subprocess.run([sys.executable, '-m', 'pip', 'cache', 'purge'])
    
    # 3. 特定バージョンのasyncqtをインストール
    print("3. 互換性の高いasyncqtバージョンをインストール中...")
    
    # Qt6対応バージョンを明示的にインストール
    versions_to_try = [
        "asyncqt==0.8.0",  # 現在のバージョン
        "asyncqt==0.7.2",  # 安定版
        "asyncqt==0.6.3",  # 古い安定版
    ]
    
    for version in versions_to_try:
        print(f"   {version} を試行中...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            '--no-cache-dir',  # キャッシュを使わない
            '--force-reinstall',  # 強制再インストール
            version
        ])
        
        if result.returncode == 0:
            # インストール成功、テスト実行
            if test_asyncqt_import():
                print(f"✅ {version} インストール・テスト成功")
                return True
            else:
                print(f"❌ {version} インストール成功だがテスト失敗")
                continue
        else:
            print(f"❌ {version} インストール失敗")
            continue
    
    return False

def test_asyncqt_import():
    """asyncqtインポートテスト"""
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        from asyncqt import QEventLoop
        print("   ✓ asyncqt インポート成功")
        
        # QEventLoop作成テスト
        loop = QEventLoop(app)
        print("   ✓ QEventLoop 作成成功")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"   ❌ asyncqt テストエラー: {e}")
        return False

def create_alternative_eventloop():
    """asyncqtの代替実装を作成"""
    print("\n🔄 asyncqt代替実装を作成中...")
    
    alternative_code = '''"""
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
'''
    
    with open('asyncqt_alternative.py', 'w', encoding='utf-8') as f:
        f.write(alternative_code)
    
    print("✅ asyncqt代替実装作成完了: asyncqt_alternative.py")
    return True

def update_main_window():
    """main_window.pyを代替実装対応に更新"""
    print("\n📝 main_window.py を代替実装対応に更新中...")
    
    try:
        with open('main_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # asyncqtインポートを条件分岐に変更
        new_import = '''# asyncqt インポート（代替実装対応）
try:
    from asyncqt import QEventLoop
    print("✅ 標準asyncqt使用")
except ImportError:
    from asyncqt_alternative import QEventLoop
    print("⚠️ asyncqt代替実装使用")
'''
        
        # 既存のasyncqtインポート行を置換
        content = content.replace(
            'from asyncqt import QEventLoop',
            new_import
        )
        
        with open('main_window.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ main_window.py 更新完了")
        return True
        
    except Exception as e:
        print(f"❌ main_window.py 更新エラー: {e}")
        return False

def main():
    """メイン修復処理"""
    print("🚀 asyncqt Qt6専用修復スクリプト")
    print("=" * 50)
    
    # 1. asyncqt修復を試行
    if fix_asyncqt_qt6():
        print("\n🎉 asyncqt修復成功！")
        print("アプリケーションを実行してください: python run.py")
        return 0
    
    # 2. 修復失敗時は代替実装を作成
    print("\n⚠️ asyncqt修復失敗、代替実装を作成します...")
    
    if create_alternative_eventloop() and update_main_window():
        print("\n🎉 代替実装作成成功！")
        print("アプリケーションを実行してください: python run.py")
        
        # テスト実行
        print("\n🧪 代替実装テスト実行中...")
        test_result = subprocess.run([sys.executable, 'run.py'])
        return test_result.returncode
    
    print("\n❌ すべての修復方法が失敗しました")
    return 1

if __name__ == "__main__":
    sys.exit(main())