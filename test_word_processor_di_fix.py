#!/usr/bin/env python3
"""WordProcessor DI問題修正テスト"""

import sys
import os
import tempfile
from pathlib import Path

# プロジェクトのパスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_word_processor_initialization():
    """WordProcessor の初期化テスト（DI回避）"""
    print("=== WordProcessor DI問題修正テスト ===\n")
    
    try:
        # WordProcessorを直接インポート
        from core.word_processor import WordProcessor
        
        print("1. 引数なしで初期化:")
        processor1 = WordProcessor()
        print(f"   ✅ 成功: {type(processor1)}")
        print(f"   config_provider: {processor1.config_provider}")
        
        print("\n2. Noneを渡して初期化:")
        processor2 = WordProcessor(None)
        print(f"   ✅ 成功: {type(processor2)}")
        print(f"   config_provider: {processor2.config_provider}")
        
        print("\n3. process_zip_fileメソッドの存在確認:")
        if hasattr(processor1, 'process_zip_file'):
            print("   ✅ process_zip_fileメソッドが存在します")
            
            # ダミーZIPファイルでテスト
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
                tmp_path = Path(tmp.name)
                tmp.write(b"dummy zip content")
            
            try:
                # 実際のメソッド呼び出し（エラーが出ても構わない）
                result = processor1.process_zip_file(tmp_path)
                print(f"   ✅ メソッド呼び出し成功: {result}")
            except Exception as e:
                print(f"   ⚠️ メソッド呼び出しエラー（想定内）: {type(e).__name__}")
            finally:
                tmp_path.unlink()
        else:
            print("   ❌ process_zip_fileメソッドが見つかりません")
        
        print("\n✅ WordProcessor DI問題が解決されました！")
        print("DIコンテナを使わずに正常に初期化できます。")
        return True
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_word_processor_initialization()
    sys.exit(0 if success else 1)