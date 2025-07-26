#!/usr/bin/env python3
"""
最小限のAPIプロパティテスト
"""

class TestClass:
    def __init__(self):
        self._api_processor = None
    
    @property
    def api_processor(self):
        if self._api_processor is None:
            self._api_processor = "API Processor Instance"
        return self._api_processor

# テスト実行
obj = TestClass()
print(f"Has _api_processor: {hasattr(obj, '_api_processor')}")
print(f"Has api_processor: {hasattr(obj, 'api_processor')}")
print(f"_api_processor value: {obj._api_processor}")
print(f"api_processor value: {obj.api_processor}")
print(f"_api_processor after access: {obj._api_processor}")

# 属性エラーの再現テスト
try:
    # 直接アクセス
    result = obj.api_processor
    print(f"✓ Direct property access works: {result}")
except AttributeError as e:
    print(f"✗ AttributeError: {e}")