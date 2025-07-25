#!/usr/bin/env python3
"""
API統合修正確認スクリプト
"""
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

def test_workflow_processor():
    """WorkflowProcessorのAPI処理テスト"""
    print("Testing WorkflowProcessor API mode...")
    
    # モックのQObjectを作成
    class MockQObject:
        def connect(self, func):
            pass
        def emit(self, *args):
            pass
    
    # PyQt5のモック
    sys.modules['PyQt5'] = type(sys)('PyQt5')
    sys.modules['PyQt5.QtCore'] = type(sys)('QtCore')
    sys.modules['PyQt5.QtCore'].QObject = object
    sys.modules['PyQt5.QtCore'].pyqtSignal = lambda *args: MockQObject()
    sys.modules['PyQt5.QtCore'].pyqtSlot = lambda *args: lambda f: f
    
    try:
        from core.workflow_processor import WorkflowProcessor
        
        # API方式でWorkflowProcessorを作成
        processor = WorkflowProcessor(process_mode="api")
        
        print(f"✓ Process mode: {processor.process_mode}")
        print(f"✓ Has _api_processor: {hasattr(processor, '_api_processor')}")
        print(f"✓ Has api_processor property: {hasattr(processor, 'api_processor')}")
        
        # api_processorプロパティにアクセス
        try:
            api_proc = processor.api_processor
            print("✓ api_processor property accessible")
        except Exception as e:
            print(f"✗ api_processor property error: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メインテスト実行"""
    print("=== API Fix Verification ===\n")
    
    if test_workflow_processor():
        print("\n✓ API processor fix verified!")
        return 0
    else:
        print("\n✗ API processor fix failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())