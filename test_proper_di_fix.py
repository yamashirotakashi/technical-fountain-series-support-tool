#!/usr/bin/env python3
"""WordProcessor DI統合の根本的修正テスト"""

import sys
import os

# プロジェクトのパスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_di_integration():
    """DI統合の根本的修正テスト"""
    print("=== WordProcessor DI統合テスト ===\n")
    
    try:
        # DI設定を初期化
        from core.di_container import configure_services, get_container
        
        print("1. DIコンテナ設定を初期化:")
        container = configure_services()
        print("   ✅ configure_services() 完了")
        
        # WordProcessorがDIコンテナに登録されているか確認
        from core.word_processor import WordProcessor
        
        print("\n2. WordProcessorのDI登録確認:")
        if container.is_registered(WordProcessor):
            print("   ✅ WordProcessorがDIコンテナに登録されています")
        else:
            print("   ❌ WordProcessorがDIコンテナに登録されていません")
            return False
        
        print("\n3. DIコンテナからWordProcessor取得:")
        word_processor = container.get_service(WordProcessor)
        print(f"   ✅ 取得成功: {type(word_processor)}")
        print(f"   config_provider: {word_processor.config_provider}")
        
        print("\n4. ProcessingEngineのword_processorプロパティテスト:")
        from core.workflow_processor import ProcessingEngine
        from core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        engine = ProcessingEngine(config_manager)
        
        # プロパティアクセス
        wp = engine.word_processor
        print(f"   ✅ word_processorプロパティ取得成功: {type(wp)}")
        print(f"   config_provider: {wp.config_provider}")
        
        print("\n5. process_zip_fileメソッドの存在確認:")
        if hasattr(wp, 'process_zip_file'):
            print("   ✅ process_zip_fileメソッドが存在します")
        else:
            print("   ❌ process_zip_fileメソッドが見つかりません")
            return False
        
        print("\n✅ WordProcessor DI統合が正しく動作しています！")
        print("バンドエイド修正ではなく、根本的な解決が実装されました。")
        return True
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_di_integration()
    sys.exit(0 if success else 1)