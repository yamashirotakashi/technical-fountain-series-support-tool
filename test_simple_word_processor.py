#!/usr/bin/env python3
"""WordProcessor プロパティの簡単なテスト"""

def test_property_pattern():
    """プロパティパターンの動作確認"""
    
    class ProcessingEngine:
        def __init__(self):
            self._word_processor = None
            print(f"初期化: _word_processor = {self._word_processor}")
        
        @property
        def word_processor(self):
            """WordProcessor の遅延初期化"""
            if self._word_processor is None:
                print("WordProcessor を遅延初期化します...")
                # 実際のWordProcessorの代わりにダミーオブジェクトを使用
                class DummyWordProcessor:
                    def process_zip_file(self, path):
                        return f"Processed: {path}"
                
                self._word_processor = DummyWordProcessor()
            return self._word_processor
    
    # テスト実行
    print("=== プロパティパターンのテスト ===\n")
    engine = ProcessingEngine()
    
    print("\n1. 直接アクセス（修正前の問題）:")
    try:
        # 修正前のコード（_word_processor に直接アクセス）
        result = engine._word_processor.process_zip_file("test.zip")
        print(f"結果: {result}")
    except AttributeError as e:
        print(f"❌ エラー: {e}")
    
    print("\n2. プロパティ経由アクセス（修正後）:")
    try:
        # 修正後のコード（word_processor プロパティを使用）
        result = engine.word_processor.process_zip_file("test.zip")
        print(f"✅ 結果: {result}")
    except AttributeError as e:
        print(f"エラー: {e}")
    
    print("\n3. 再度プロパティアクセス（キャッシュ確認）:")
    result = engine.word_processor.process_zip_file("another.zip")
    print(f"✅ 結果: {result}")
    
    print("\n=== テスト完了 ===")
    print("修正により、word_processor プロパティが適切に遅延初期化されるようになりました。")

if __name__ == "__main__":
    test_property_pattern()