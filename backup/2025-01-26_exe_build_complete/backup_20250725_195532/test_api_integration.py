#!/usr/bin/env python3
"""
API統合テストスクリプト
"""
import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """必要なモジュールのインポートテスト"""
    print("Testing imports...")
    try:
        from core.api_processor import ApiProcessor
        print("✓ ApiProcessor imported successfully")
        
        from gui.dialogs.process_mode_dialog import ProcessModeDialog
        print("✓ ProcessModeDialog imported successfully")
        
        from gui.dialogs.warning_dialog import WarningDialog
        print("✓ WarningDialog imported successfully")
        
        from core.workflow_processor import WorkflowProcessor
        print("✓ WorkflowProcessor imported successfully")
        
        from gui.main_window import MainWindow, ProcessWorker
        print("✓ MainWindow and ProcessWorker imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_api_processor():
    """ApiProcessorの基本機能テスト"""
    print("\nTesting ApiProcessor...")
    try:
        from core.api_processor import ApiProcessor
        processor = ApiProcessor()
        
        # 基本的な属性の確認
        assert hasattr(processor, 'API_BASE_URL')
        assert hasattr(processor, 'API_USERNAME')
        assert hasattr(processor, 'API_PASSWORD')
        assert hasattr(processor, 'process_zip_file')
        
        print("✓ ApiProcessor attributes verified")
        print(f"  - API URL: {processor.API_BASE_URL}")
        print(f"  - Username: {processor.API_USERNAME}")
        
        return True
    except Exception as e:
        print(f"✗ ApiProcessor test failed: {e}")
        return False

def test_workflow_integration():
    """WorkflowProcessorのAPI統合テスト"""
    print("\nTesting WorkflowProcessor integration...")
    try:
        from core.workflow_processor import WorkflowProcessor
        
        # API方式でWorkflowProcessorを作成
        processor = WorkflowProcessor(process_mode="api")
        
        assert processor.process_mode == "api"
        assert hasattr(processor, 'api_processor')
        assert hasattr(processor, 'warning_dialog_needed')
        
        print("✓ WorkflowProcessor API mode verified")
        print(f"  - Process mode: {processor.process_mode}")
        
        return True
    except Exception as e:
        print(f"✗ WorkflowProcessor test failed: {e}")
        return False

def main():
    """メインテスト実行"""
    print("=== API Integration Test ===\n")
    
    all_tests_passed = True
    
    # インポートテスト
    if not test_imports():
        all_tests_passed = False
    
    # ApiProcessorテスト
    if not test_api_processor():
        all_tests_passed = False
    
    # WorkflowProcessor統合テスト
    if not test_workflow_integration():
        all_tests_passed = False
    
    print("\n=== Test Summary ===")
    if all_tests_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())