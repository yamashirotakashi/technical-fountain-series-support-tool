#!/usr/bin/env python3
"""
APIプロパティの動作確認スクリプト
"""
import sys
import logging
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# ログ設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_workflow_processor():
    """WorkflowProcessorのapi_processorプロパティをテスト"""
    print("=== WorkflowProcessor API Property Test ===\n")
    
    # PyQt5のモックを設定
    class MockSignal:
        def connect(self, func):
            print(f"  - Signal connected to {func}")
        def emit(self, *args):
            pass
    
    class MockQObject:
        def __init__(self):
            pass
    
    # モジュールのモック
    sys.modules['PyQt5'] = type(sys)('PyQt5')
    sys.modules['PyQt5.QtCore'] = type(sys)('QtCore')
    sys.modules['PyQt5.QtCore'].QObject = MockQObject
    sys.modules['PyQt5.QtCore'].pyqtSignal = lambda *args: MockSignal()
    sys.modules['PyQt5.QtCore'].pyqtSlot = lambda *args: lambda f: f
    sys.modules['PyQt5.QtCore'].QCoreApplication = type('QCoreApplication', (), {'processEvents': lambda: None})
    
    # その他の依存関係をモック
    sys.modules['google'] = type(sys)('google')
    sys.modules['google.oauth2'] = type(sys)('oauth2')
    sys.modules['google.oauth2.service_account'] = type(sys)('service_account')
    sys.modules['googleapiclient'] = type(sys)('googleapiclient')
    sys.modules['googleapiclient.discovery'] = type(sys)('discovery')
    
    try:
        print("1. WorkflowProcessorをインポート...")
        from core.workflow_processor import WorkflowProcessor
        print("✓ インポート成功\n")
        
        print("2. API方式でインスタンス作成...")
        processor = WorkflowProcessor(process_mode="api")
        print("✓ インスタンス作成成功\n")
        
        print("3. 属性の確認...")
        print(f"  - process_mode: {processor.process_mode}")
        print(f"  - hasattr(_api_processor): {hasattr(processor, '_api_processor')}")
        print(f"  - hasattr(api_processor): {hasattr(processor, 'api_processor')}")
        print(f"  - _api_processor値: {processor._api_processor}\n")
        
        print("4. api_processorプロパティにアクセス...")
        try:
            api_proc = processor.api_processor
            print(f"✓ api_processor取得成功: {api_proc}\n")
        except AttributeError as e:
            print(f"✗ AttributeError: {e}")
            print(f"  利用可能な属性: {[attr for attr in dir(processor) if not attr.startswith('__')]}")
            return False
        
        print("5. 再度アクセス（キャッシュ確認）...")
        api_proc2 = processor.api_processor
        print(f"✓ 2回目のアクセス成功")
        print(f"  同じインスタンス: {api_proc is api_proc2}\n")
        
        return True
        
    except Exception as e:
        print(f"✗ エラー: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_workflow_processor()
    
    print("\n=== テスト結果 ===")
    if success:
        print("✓ すべてのテストが成功しました")
        print("\nアプリケーションを再起動して、詳細ログを確認してください:")
        print("1. python set_debug_log.py")
        print("2. python main.py")
    else:
        print("✗ テストが失敗しました")
        print("\nコードに問題がある可能性があります")