#!/usr/bin/env python3
"""
API Processor Property 修正検証スクリプト

AttributeError: 'ProcessingEngine' object has no attribute 'api_processor'
の修正を検証するためのテストスクリプト
"""
import sys
import logging
from pathlib import Path

# プロジェクトのルートをPATHに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """詳細ログ設定"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('api_processor_test.log', mode='w', encoding='utf-8')
        ]
    )

def test_api_processor_property():
    """api_processorプロパティの動作確認"""
    try:
        print("=" * 60)
        print("API Processor Property Test - 修正後検証")
        print("=" * 60)
        
        # Step 1: ConfigurationManagerの初期化
        print("\n1. ConfigurationManager初期化...")
        from core.workflow_processor import ConfigurationManager
        config_manager = ConfigurationManager()
        print("✓ ConfigurationManager初期化完了")
        
        # Step 2: ProcessingEngineの初期化
        print("\n2. ProcessingEngine初期化...")
        from core.workflow_processor import ProcessingEngine
        
        # Qt アプリケーション初期化（シグナル用）
        from PyQt6.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication([])
        
        processing_engine = ProcessingEngine(config_manager)
        print(f"✓ ProcessingEngine初期化完了: {type(processing_engine)}")
        
        # Step 3: 属性存在確認
        print("\n3. 属性存在確認...")
        print(f"  - hasattr(_api_processor): {hasattr(processing_engine, '_api_processor')}")
        print(f"  - hasattr(api_processor): {hasattr(processing_engine, 'api_processor')}")
        print(f"  - _api_processor初期値: {processing_engine._api_processor}")
        
        # Step 4: プロパティデスクリプタ確認
        print("\n4. プロパティデスクリプタ確認...")
        prop_descriptor = getattr(type(processing_engine), 'api_processor', None)
        print(f"  - api_processor descriptor: {prop_descriptor}")
        print(f"  - descriptor type: {type(prop_descriptor)}")
        print(f"  - is property: {isinstance(prop_descriptor, property)}")
        
        # Step 5: api_processorプロパティにアクセス
        print("\n5. api_processorプロパティアクセス...")
        try:
            api_proc = processing_engine.api_processor
            print("✓ api_processorプロパティアクセス成功")
            print(f"  - Type: {type(api_proc)}")
            print(f"  - Instance: {api_proc}")
            
            # Step 6: 2回目のアクセス（キャッシュ確認）
            print("\n6. api_processorプロパティ再アクセス（キャッシュ確認）...")
            api_proc2 = processing_engine.api_processor
            print("✓ 2回目のアクセス成功")
            print(f"  - Same instance: {api_proc is api_proc2}")
            
            return True
            
        except Exception as access_error:
            print(f"✗ api_processorアクセスエラー: {access_error}")
            print(f"  - Error type: {type(access_error)}")
            
            # 詳細デバッグ情報
            print(f"  - Available attributes: {[attr for attr in dir(processing_engine) if 'api' in attr.lower()]}")
            
            return False
    
    except Exception as e:
        print(f"✗ テスト実行中にエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_di_container_integration():
    """DI Container統合テスト"""
    try:
        print("\n" + "=" * 60)
        print("DI Container Integration Test")
        print("=" * 60)
        
        # DI Container接続テスト
        from core.di_container import get_container, configure_services
        # Configure services to register ApiProcessor
        container = configure_services()
        print(f"✓ DI Container設定完了: {type(container)}")
        
        from core.api_processor import ApiProcessor
        # Check if registered, if not register manually
        if not container.is_registered(ApiProcessor):
            print("⚠ ApiProcessor未登録 - 手動登録中...")
            container.register_transient(ApiProcessor, ApiProcessor)
        
        api_instance = container.get_service(ApiProcessor)
        print(f"✓ ApiProcessor DI取得成功: {type(api_instance)}")
        
        return True
        
    except Exception as e:
        print(f"✗ DI Container統合エラー: {e}")
        return False

def main():
    """メインテスト実行"""
    setup_logging()
    
    success_count = 0
    total_tests = 2
    
    # Test 1: API Processor Property
    if test_api_processor_property():
        success_count += 1
        print("\n✓ API Processor Property Test: PASSED")
    else:
        print("\n✗ API Processor Property Test: FAILED")
    
    # Test 2: DI Container Integration
    if test_di_container_integration():
        success_count += 1
        print("\n✓ DI Container Integration Test: PASSED")
    else:
        print("\n✗ DI Container Integration Test: FAILED")
    
    # 結果まとめ
    print("\n" + "=" * 60)
    print(f"テスト結果: {success_count}/{total_tests} 成功")
    print("=" * 60)
    
    if success_count == total_tests:
        print("🎉 すべてのテストが成功しました！")
        print("修正が正常に適用されています。")
        return 0
    else:
        print("⚠️  一部のテストが失敗しました。")
        print("追加の修正が必要な可能性があります。")
        return 1

if __name__ == "__main__":
    exit(main())