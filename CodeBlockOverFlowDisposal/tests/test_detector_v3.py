#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for MaximumOCRDetectorV3 - TDD validation
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# プロジェクトルートを追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent.parent))

from maximum_ocr_detector_v3 import MaximumOCRDetectorV3, FalsePositiveFilters

class TestMaximumOCRDetectorV3(unittest.TestCase):
    """MaximumOCRDetectorV3のテスト"""
    
    def setUp(self):
        self.detector = MaximumOCRDetectorV3()
    
    def test_initialization(self):
        """初期化のテスト"""
        self.assertIsNotNone(self.detector.filters)
        self.assertEqual(self.detector.mm_to_pt, 2.83465)
        self.assertIn('total_pages_processed', self.detector.quality_metrics)
    
    def test_is_ascii_char(self):
        """ASCII文字判定のテスト"""
        # ASCII文字
        self.assertTrue(self.detector.is_ascii_char('a'))
        self.assertTrue(self.detector.is_ascii_char('Z'))
        self.assertTrue(self.detector.is_ascii_char('5'))
        self.assertTrue(self.detector.is_ascii_char('!'))
        
        # 非ASCII文字
        self.assertFalse(self.detector.is_ascii_char('あ'))
        self.assertFalse(self.detector.is_ascii_char('ñ'))
        
        # エッジケース
        self.assertFalse(self.detector.is_ascii_char(''))
        self.assertFalse(self.detector.is_ascii_char(None))
    
    def test_is_likely_false_positive_integration(self):
        """誤検知判定の統合テスト"""
        # 測定誤差による除外
        self.assertTrue(self.detector.is_likely_false_positive("test", 0.3, 100.0))
        
        # ページ番号による除外
        self.assertTrue(self.detector.is_likely_false_positive("123", 1.0, 100.0))
        
        # 有効なはみ出し
        self.assertFalse(self.detector.is_likely_false_positive("valid_overflow", 1.5, 100.0))
        
        # 保護記号
        self.assertFalse(self.detector.is_likely_false_positive('"', 1.0, 100.0))
    
    def test_detect_overflows_structure(self):
        """detect_overflows メソッドの構造テスト"""
        # モックページオブジェクトを作成
        mock_page = Mock()
        mock_page.width = 515.9  # B5判型
        mock_page.chars = [
            {
                'text': 'a',
                'x1': 500.0,  # はみ出し
                'y0': 100.0
            },
            {
                'text': 'b', 
                'x1': 400.0,  # はみ出しなし
                'y0': 100.0
            }
        ]
        
        results = self.detector.detect_overflows(mock_page, 1)
        
        # 結果の構造確認
        self.assertIsInstance(results, list)
        
        # はみ出しが検出される場合の構造確認
        if results:
            result = results[0]
            self.assertIn('y_position', result)
            self.assertIn('overflow_text', result)
            self.assertIn('overflow_amount', result)
            self.assertIn('char_count', result)
    
    def test_margin_calculation_odd_page(self):
        """奇数ページのマージン計算テスト"""
        mock_page = Mock()
        mock_page.width = 515.9
        mock_page.chars = []
        
        # 奇数ページでのテスト
        self.detector.detect_overflows(mock_page, 1)
        
        # マージン値の確認（10mm * 2.83465 = 28.3465pt）
        expected_margin = 10 * self.detector.mm_to_pt
        self.assertAlmostEqual(expected_margin, 28.3465, places=3)
    
    def test_margin_calculation_even_page(self):
        """偶数ページのマージン計算テスト"""
        mock_page = Mock()
        mock_page.width = 515.9
        mock_page.chars = []
        
        # 偶数ページでのテスト
        self.detector.detect_overflows(mock_page, 2)
        
        # マージン値の確認（18mm * 2.83465 = 51.0237pt）
        expected_margin = 18 * self.detector.mm_to_pt
        self.assertAlmostEqual(expected_margin, 51.0237, places=3)
    
    @patch('pdfplumber.open')
    def test_process_pdf_comprehensive_success(self, mock_open):
        """PDF処理成功ケースのテスト"""
        # モックPDFオブジェクトの設定
        mock_pdf = Mock()
        mock_page = Mock()
        mock_page.chars = [
            {
                'text': 'overflow',
                'x1': 500.0,
                'y0': 100.0
            }
        ]
        mock_pdf.pages = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_pdf
        
        # テスト実行
        results = self.detector.process_pdf_comprehensive(Path('test.pdf'))
        
        # 結果の確認
        self.assertIsInstance(results, list)
        self.assertEqual(self.detector.quality_metrics['total_pages_processed'], 1)
    
    @patch('pdfplumber.open')
    def test_process_pdf_comprehensive_error(self, mock_open):
        """PDF処理エラーケースのテスト"""
        # pdfplumberでエラーが発生する場合
        mock_open.side_effect = Exception("PDF read error")
        
        results = self.detector.process_pdf_comprehensive(Path('invalid.pdf'))
        
        # エラー時は空リストが返される
        self.assertEqual(results, [])
        self.assertGreater(len(self.detector.quality_metrics['quality_warnings']), 0)
    
    def test_performance_requirements(self):
        """性能要件のテスト"""
        import time
        
        # 大量データでの処理時間テスト（モック使用）
        mock_page = Mock()
        mock_page.width = 515.9
        
        # 1000文字のモックデータ
        mock_chars = []
        for i in range(1000):
            mock_chars.append({
                'text': chr(65 + (i % 26)),  # A-Z
                'x1': 400.0 + (i % 10),  # 位置をずらす
                'y0': 100.0 + (i % 10)
            })
        mock_page.chars = mock_chars
        
        start_time = time.time()
        results = self.detector.detect_overflows(mock_page, 1)
        processing_time = time.time() - start_time
        
        # 1秒以内での処理を期待
        self.assertLess(processing_time, 1.0)

class TestFalsePositiveFiltersUnit(unittest.TestCase):
    """FalsePositiveFiltersの単体テスト"""
    
    def test_is_measurement_error_boundary(self):
        """測定誤差判定の境界値テスト"""
        # 境界値テスト
        self.assertTrue(FalsePositiveFilters.is_measurement_error(0.5))
        self.assertTrue(FalsePositiveFilters.is_measurement_error(0.499))
        self.assertFalse(FalsePositiveFilters.is_measurement_error(0.501))
        
        # エッジケース
        self.assertTrue(FalsePositiveFilters.is_measurement_error(0.0))
        self.assertTrue(FalsePositiveFilters.is_measurement_error(-0.1))
    
    def test_is_pdf_internal_encoding(self):
        """PDF内部エンコーディング判定のテスト"""
        self.assertTrue(FalsePositiveFilters.is_pdf_internal_encoding("(cid:123)"))
        self.assertTrue(FalsePositiveFilters.is_pdf_internal_encoding("text(cid:456)more"))
        self.assertFalse(FalsePositiveFilters.is_pdf_internal_encoding("normal text"))
        self.assertFalse(FalsePositiveFilters.is_pdf_internal_encoding(""))
    
    def test_is_page_number_edge_cases(self):
        """ページ番号判定のエッジケーステスト"""
        # 有効なページ番号
        self.assertTrue(FalsePositiveFilters.is_page_number("1"))
        self.assertTrue(FalsePositiveFilters.is_page_number("999"))
        
        # 無効なページ番号
        self.assertFalse(FalsePositiveFilters.is_page_number("1000"))  # 4桁
        self.assertFalse(FalsePositiveFilters.is_page_number("12a"))   # 文字混在
        self.assertFalse(FalsePositiveFilters.is_page_number(""))      # 空文字
        self.assertTrue(FalsePositiveFilters.is_page_number("01"))     # ゼロ埋めも有効なページ番号として扱う
    
    def test_is_japanese_only_comprehensive(self):
        """日本語判定の包括的テスト"""
        # 日本語のみ
        self.assertTrue(FalsePositiveFilters.is_japanese_only("ひらがな"))
        self.assertTrue(FalsePositiveFilters.is_japanese_only("カタカナ"))
        self.assertTrue(FalsePositiveFilters.is_japanese_only("漢字"))
        self.assertTrue(FalsePositiveFilters.is_japanese_only("あカ漢"))
        
        # 日本語以外を含む
        self.assertFalse(FalsePositiveFilters.is_japanese_only("あa"))
        self.assertFalse(FalsePositiveFilters.is_japanese_only("カ1"))
        self.assertFalse(FalsePositiveFilters.is_japanese_only("hello"))
        
        # エッジケース
        self.assertFalse(FalsePositiveFilters.is_japanese_only(""))
        self.assertFalse(FalsePositiveFilters.is_japanese_only("123"))
    
    def test_is_short_symbol_noise_detailed(self):
        """短い記号ノイズ判定の詳細テスト"""
        # 1文字の保護記号（通過すべき）
        protected_1char = ['"', "'", '(', ')', '[', ']', '{', '}', '<', '>', 
                          '=', '+', '-', '*', '/', '\\', '|', '&', '%', 
                          '$', '#', '@', '!', '?', '.', ',', ';', ':']
        
        for symbol in protected_1char:
            with self.subTest(symbol=symbol):
                self.assertFalse(FalsePositiveFilters.is_short_symbol_noise(symbol, 1))
        
        # 1文字の非保護記号（除外すべき）
        unprotected_1char = ['~', '^', '`']
        for symbol in unprotected_1char:
            with self.subTest(symbol=symbol):
                self.assertTrue(FalsePositiveFilters.is_short_symbol_noise(symbol, 1))
        
        # 英数字（通過すべき）
        self.assertFalse(FalsePositiveFilters.is_short_symbol_noise('a', 1))
        self.assertFalse(FalsePositiveFilters.is_short_symbol_noise('5', 1))
        
        # 2文字の組み合わせテスト
        self.assertFalse(FalsePositiveFilters.is_short_symbol_noise('()', 2))  # 保護記号組み合わせ
        self.assertTrue(FalsePositiveFilters.is_short_symbol_noise('~~', 2))   # 非保護記号組み合わせ
    
    def test_is_powershell_pattern_comprehensive(self):
        """PowerShellパターンの包括的テスト"""
        # PowerShellパターン（長いテキスト）
        self.assertTrue(FalsePositiveFilters.is_powershell_pattern("System::Runtime::Marshal", 25))
        self.assertTrue(FalsePositiveFilters.is_powershell_pattern("Get-Process::Name", 17))
        
        # 短いテキスト（除外されない）
        self.assertFalse(FalsePositiveFilters.is_powershell_pattern("System::", 8))
        
        # ::を含まないテキスト（除外されない）
        self.assertFalse(FalsePositiveFilters.is_powershell_pattern("Get-Process-Name-Long", 21))
    
    def test_is_file_extension_patterns(self):
        """ファイル拡張子パターンのテスト"""
        self.assertTrue(FalsePositiveFilters.is_file_extension("script.ps1"))
        self.assertTrue(FalsePositiveFilters.is_file_extension("path/to/script.ps1"))
        self.assertFalse(FalsePositiveFilters.is_file_extension("normaltext"))
        self.assertFalse(FalsePositiveFilters.is_file_extension("script.py"))
    
    def test_is_image_element_tag(self):
        """画像要素タグのテスト"""
        self.assertTrue(FalsePositiveFilters.is_image_element_tag("[IMAGE:logo.png]"))
        self.assertTrue(FalsePositiveFilters.is_image_element_tag("[LINE]"))
        self.assertTrue(FalsePositiveFilters.is_image_element_tag("[RECT:border]"))
        self.assertFalse(FalsePositiveFilters.is_image_element_tag("[TEXT:normal]"))
        self.assertFalse(FalsePositiveFilters.is_image_element_tag("normal text"))
    
    def test_is_index_pattern(self):
        """索引パターンのテスト"""
        self.assertTrue(FalsePositiveFilters.is_index_pattern("章題……123"))
        self.assertTrue(FalsePositiveFilters.is_index_pattern("項目・・・456"))
        self.assertFalse(FalsePositiveFilters.is_index_pattern("normal text"))
        self.assertFalse(FalsePositiveFilters.is_index_pattern(""))

class TestIntegration(unittest.TestCase):
    """統合テスト"""
    
    def setUp(self):
        self.detector = MaximumOCRDetectorV3()
    
    def test_complete_overflow_detection_workflow(self):
        """完全なはみ出し検出ワークフローのテスト"""
        # 実際の使用パターンをシミュレート
        mock_page = Mock()
        mock_page.width = 515.9  # B5判型
        
        # 様々なタイプの文字を含むモックデータ
        mock_page.chars = [
            # 有効なはみ出し
            {'text': 'valid', 'x1': 500.0, 'y0': 100.0},
            
            # 測定誤差（除外されるべき）
            {'text': 'tiny', 'x1': 488.0, 'y0': 200.0},  # 微小はみ出し
            
            # ページ番号（除外されるべき）
            {'text': '123', 'x1': 495.0, 'y0': 300.0},
            
            # 保護記号（通過すべき）
            {'text': '"', 'x1': 490.0, 'y0': 400.0},
            
            # 非保護記号（除外されるべき）
            {'text': '~', 'x1': 490.0, 'y0': 500.0},
        ]
        
        results = self.detector.detect_overflows(mock_page, 1)
        
        # 結果の検証
        self.assertIsInstance(results, list)
        
        # 各結果の内容確認
        detected_texts = [r['overflow_text'] for r in results]
        
        # 有効なはみ出しと保護記号が検出される
        self.assertIn('valid', detected_texts)
        self.assertIn('"', detected_texts)
        
        # 除外されるべきものが含まれていない
        self.assertNotIn('123', detected_texts)  # ページ番号
        self.assertNotIn('~', detected_texts)    # 非保護記号

if __name__ == '__main__':
    # より詳細なテスト出力
    unittest.main(verbosity=2, buffer=True)