#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for filter modules - TDD validation
"""

import unittest
import sys
from pathlib import Path

# プロジェクトルートを追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from CodeBlockOverFlowDisposal.overflow_detection_lib.filters import (
        MeasurementErrorFilter,
        PageNumberFilter,
        JapaneseTextFilter,
        SymbolOnlyFilter,
        PowerShellFilter,
        FilterChain
    )
except ImportError:
    # フォールバック：V3実装から直接インポート
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from maximum_ocr_detector_v3 import FalsePositiveFilters

class TestMeasurementErrorFilter(unittest.TestCase):
    """測定誤差フィルタのテスト"""
    
    def setUp(self):
        self.filter = MeasurementErrorFilter(threshold_pt=0.5)
    
    def test_small_overflow_filtered(self):
        """微小はみ出しが誤検知として判定されること"""
        result = self.filter.apply("a", 0.3, 100.0)
        self.assertTrue(result.is_false_positive)
        self.assertGreater(result.confidence, 0.9)
    
    def test_large_overflow_passes(self):
        """大きなはみ出しが有効と判定されること"""
        result = self.filter.apply("hello", 1.5, 100.0)
        self.assertFalse(result.is_false_positive)
        self.assertGreater(result.confidence, 0.7)
    
    def test_threshold_boundary(self):
        """閾値境界での動作確認"""
        # 閾値以下
        result_below = self.filter.apply("test", 0.5, 100.0)
        self.assertTrue(result_below.is_false_positive)
        
        # 閾値より大きい
        result_above = self.filter.apply("test", 0.6, 100.0)
        self.assertFalse(result_above.is_false_positive)

class TestPageNumberFilter(unittest.TestCase):
    """ページ番号フィルタのテスト"""
    
    def setUp(self):
        self.filter = PageNumberFilter(max_digits=3)
    
    def test_single_digit_page_number(self):
        """1桁ページ番号の検出"""
        result = self.filter.apply("5", 1.0, 100.0)
        self.assertTrue(result.is_false_positive)
        self.assertIn("ページ番号", result.reason)
    
    def test_multi_digit_page_number(self):
        """複数桁ページ番号の検出"""
        result = self.filter.apply("123", 1.0, 100.0)
        self.assertTrue(result.is_false_positive)
    
    def test_non_page_number_passes(self):
        """非ページ番号が通過すること"""
        result = self.filter.apply("abc", 1.0, 100.0)
        self.assertFalse(result.is_false_positive)
    
    def test_too_long_number(self):
        """桁数上限を超える数字が通過すること"""
        result = self.filter.apply("1234", 1.0, 100.0)
        self.assertFalse(result.is_false_positive)

class TestSymbolOnlyFilter(unittest.TestCase):
    """記号のみフィルタのテスト"""
    
    def setUp(self):
        self.filter = SymbolOnlyFilter()
    
    def test_protected_single_symbol(self):
        """保護対象の単一記号が通過すること"""
        protected_symbols = ['"', "'", '(', ')', '[', ']', '{', '}']
        for symbol in protected_symbols:
            with self.subTest(symbol=symbol):
                result = self.filter.apply(symbol, 1.0, 100.0)
                self.assertFalse(result.is_false_positive)
    
    def test_unprotected_single_symbol(self):
        """非保護記号が除外されること"""
        result = self.filter.apply("~", 1.0, 100.0)
        self.assertTrue(result.is_false_positive)
    
    def test_alphanumeric_passes(self):
        """英数字が通過すること"""
        result = self.filter.apply("a", 1.0, 100.0)
        self.assertFalse(result.is_false_positive)
    
    def test_protected_combination(self):
        """保護対象記号の組み合わせが通過すること"""
        result = self.filter.apply("()", 1.0, 100.0)
        self.assertFalse(result.is_false_positive)

class TestJapaneseTextFilter(unittest.TestCase):
    """日本語テキストフィルタのテスト"""
    
    def setUp(self):
        self.filter = JapaneseTextFilter()
    
    def test_short_japanese_filtered(self):
        """短い日本語テキストが除外されること"""
        result = self.filter.apply("あ", 1.0, 100.0)
        self.assertTrue(result.is_false_positive)
    
    def test_longer_japanese_passes(self):
        """長い日本語テキストが通過すること"""
        result = self.filter.apply("あいうえお", 1.0, 100.0)
        self.assertFalse(result.is_false_positive)
    
    def test_english_passes(self):
        """英語テキストが通過すること"""
        result = self.filter.apply("hello", 1.0, 100.0)
        self.assertFalse(result.is_false_positive)

class TestPowerShellFilter(unittest.TestCase):
    """PowerShellフィルタのテスト"""
    
    def setUp(self):
        self.filter = PowerShellFilter(min_length=10)
    
    def test_powershell_pattern_filtered(self):
        """PowerShellパターンが除外されること"""
        result = self.filter.apply("Get-Process -Name explorer", 1.0, 100.0)
        self.assertTrue(result.is_false_positive)
    
    def test_ps1_extension_filtered(self):
        """PS1拡張子が除外されること"""
        result = self.filter.apply("script.ps1 execution", 1.0, 100.0)
        self.assertTrue(result.is_false_positive)
    
    def test_short_powershell_passes(self):
        """短いPowerShell風テキストが通過すること"""
        result = self.filter.apply("Get-", 1.0, 100.0)
        self.assertFalse(result.is_false_positive)
    
    def test_normal_text_passes(self):
        """通常テキストが通過すること"""
        result = self.filter.apply("normal text content", 1.0, 100.0)
        self.assertFalse(result.is_false_positive)

class TestFilterChain(unittest.TestCase):
    """フィルタチェーンのテスト"""
    
    def setUp(self):
        self.chain = FilterChain()
        self.chain.add_filter(MeasurementErrorFilter(0.5))
        self.chain.add_filter(PageNumberFilter(3))
        self.chain.add_filter(SymbolOnlyFilter())
    
    def test_first_filter_catches(self):
        """最初のフィルタで誤検知が検出されること"""
        result = self.chain.apply("test", 0.3, 100.0)  # 測定誤差で除外
        self.assertTrue(result.is_false_positive)
        self.assertEqual(result.filter_name, "MeasurementError")
    
    def test_second_filter_catches(self):
        """2番目のフィルタで誤検知が検出されること"""
        result = self.chain.apply("123", 1.0, 100.0)  # ページ番号で除外
        self.assertTrue(result.is_false_positive)
        self.assertEqual(result.filter_name, "PageNumber")
    
    def test_all_filters_pass(self):
        """全フィルタ通過時の動作確認"""
        result = self.chain.apply("valid_overflow", 1.5, 100.0)
        self.assertFalse(result.is_false_positive)
        self.assertEqual(result.filter_name, "FilterChain")
    
    def test_empty_chain(self):
        """空のフィルタチェーンの動作確認"""
        empty_chain = FilterChain()
        result = empty_chain.apply("test", 1.0, 100.0)
        self.assertFalse(result.is_false_positive)
        self.assertEqual(result.filter_name, "NoFilter")

class TestFalsePositiveFiltersV3(unittest.TestCase):
    """V3実装のフィルタテスト（フォールバック）"""
    
    def setUp(self):
        # V3のFalsePositiveFiltersクラスをインポート
        from maximum_ocr_detector_v3 import FalsePositiveFilters
        self.FalsePositiveFilters = FalsePositiveFilters
    
    def test_measurement_error(self):
        """測定誤差判定のテスト"""
        self.assertTrue(self.FalsePositiveFilters.is_measurement_error(0.3))
        self.assertTrue(self.FalsePositiveFilters.is_measurement_error(0.5))
        self.assertFalse(self.FalsePositiveFilters.is_measurement_error(0.6))
    
    def test_page_number_detection(self):
        """ページ番号検出のテスト"""
        self.assertTrue(self.FalsePositiveFilters.is_page_number("1"))
        self.assertTrue(self.FalsePositiveFilters.is_page_number("123"))
        self.assertFalse(self.FalsePositiveFilters.is_page_number("1234"))
        self.assertFalse(self.FalsePositiveFilters.is_page_number("12a"))
    
    def test_protected_symbols(self):
        """保護記号の判定テスト"""
        # 保護対象は除外されない
        self.assertFalse(self.FalsePositiveFilters.is_short_symbol_noise('"', 1))
        self.assertFalse(self.FalsePositiveFilters.is_short_symbol_noise("'", 1))
        self.assertFalse(self.FalsePositiveFilters.is_short_symbol_noise("(", 1))
        
        # 非保護記号は除外される
        self.assertTrue(self.FalsePositiveFilters.is_short_symbol_noise("~", 1))
        self.assertTrue(self.FalsePositiveFilters.is_short_symbol_noise("^", 1))
    
    def test_japanese_detection(self):
        """日本語検出のテスト"""
        self.assertTrue(self.FalsePositiveFilters.is_japanese_only("あ"))
        self.assertTrue(self.FalsePositiveFilters.is_japanese_only("カタカナ"))
        self.assertTrue(self.FalsePositiveFilters.is_japanese_only("漢字"))
        self.assertFalse(self.FalsePositiveFilters.is_japanese_only("hello"))
        self.assertFalse(self.FalsePositiveFilters.is_japanese_only("123"))
    
    def test_powershell_patterns(self):
        """PowerShellパターンのテスト"""
        self.assertTrue(self.FalsePositiveFilters.is_powershell_pattern("System::Runtime", 15))
        self.assertFalse(self.FalsePositiveFilters.is_powershell_pattern("System::Runtime", 5))
        self.assertFalse(self.FalsePositiveFilters.is_powershell_pattern("normal text", 15))

if __name__ == '__main__':
    unittest.main(verbosity=2)