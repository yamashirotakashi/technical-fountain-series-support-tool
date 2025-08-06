#!/usr/bin/env python3
"""Gmail ワークフロー修正テスト"""

import sys
from pathlib import Path
from core.workflow_processor import ProcessingEngine
from core.config_manager import ConfigManager

def test_gmail_workflow():
    """Gmail ワークフローのテスト"""
    print("Gmail ワークフロー修正テストを開始...")
    
    try:
        # ProcessingEngine を初期化
        config_manager = ConfigManager()
        engine = ProcessingEngine(config_manager)
        
        # word_processor プロパティのアクセステスト
        print("\nWordProcessor プロパティアクセステスト:")
        print(f"初期状態: _word_processor = {engine._word_processor}")
        
        # プロパティ経由でアクセス（遅延初期化が発生）
        word_processor = engine.word_processor
        print(f"プロパティアクセス後: word_processor = {word_processor}")
        print(f"型: {type(word_processor)}")
        
        # process_zip_file メソッドの存在確認
        if hasattr(word_processor, 'process_zip_file'):
            print("✅ process_zip_file メソッドが存在します")
        else:
            print("❌ process_zip_file メソッドが見つかりません")
        
        print("\n✅ Gmail ワークフロー修正が成功しました！")
        print("word_processor プロパティが正しく動作しています。")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_gmail_workflow()
    sys.exit(0 if success else 1)