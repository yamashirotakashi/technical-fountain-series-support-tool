#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit Tests for MaximumOCRDetectorV3
重要関数の単体テスト - 品質チェックで特定された問題への対応
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# プロジェクトルートを追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from maximum_ocr_detector_v3 import MaximumOCRDetectorV3, FalsePositiveFilters

class TestFalsePositiveFilters(unittest.TestCase):
    """FalsePositiveFiltersクラスのテスト"""
    
    def setUp(self):
        self.filters = FalsePositiveFilters()
    
    def test_is_measurement_error(self):
        """測定誤差フィルタのテスト"""
        # 0.5pt以下は測定誤差として除外
        self.assertTrue(self.filters.is_measurement_error(0.3))
        self.assertTrue(self.filters.is_measurement_error(0.5))
        self.assertFalse(self.filters.is_measurement_error(0.6))
        self.assertFalse(self.filters.is_measurement_error(1.0))
    
    def test_is_pdf_internal_encoding(self):
        """PDF内部エンコーディングフィルタのテスト"""
        self.assertTrue(self.filters.is_pdf_internal_encoding("(cid:123)"))
        self.assertTrue(self.filters.is_pdf_internal_encoding("text(cid:456)more"))
        self.assertFalse(self.filters.is_pdf_internal_encoding("normal text"))
        self.assertFalse(self.filters.is_pdf_internal_encoding("()"))
    
    def test_is_page_number(self):
        """ページ番号フィルタのテスト"""
        self.assertTrue(self.filters.is_page_number("1"))
        self.assertTrue(self.filters.is_page_number("123"))
        self.assertFalse(self.filters.is_page_number("1234"))  # 4桁は除外しない
        self.assertFalse(self.filters.is_page_number("12a"))
        self.assertFalse(self.filters.is_page_number("abc"))
    
    def test_is_japanese_only(self):
        """日本語のみフィルタのテスト"""
        self.assertTrue(self.filters.is_japanese_only("こんにちは"))
        self.assertTrue(self.filters.is_japanese_only("テスト"))
        self.assertFalse(self.filters.is_japanese_only("hello"))
        self.assertFalse(self.filters.is_japanese_only("テストtest"))
        self.assertFalse(self.filters.is_japanese_only(""))
    
    def test_is_powershell_pattern(self):
        """PowerShellパターンフィルタのテスト"""
        self.assertTrue(self.filters.is_powershell_pattern("System::Console::WriteLine", 25))
        self.assertFalse(self.filters.is_powershell_pattern("System::", 8))  # 10文字以下
        self.assertFalse(self.filters.is_powershell_pattern("normal text without colon", 25))
    
    def test_is_file_extension(self):
        """ファイル拡張子フィルタのテスト"""
        self.assertTrue(self.filters.is_file_extension("script.ps1"))
        self.assertTrue(self.filters.is_file_extension("path/to/script.ps1"))
        self.assertFalse(self.filters.is_file_extension("script.py"))
        self.assertFalse(self.filters.is_file_extension("normal text"))
    
    def test_is_short_symbol_noise(self):
        """短い記号ノイズフィルタのテスト"""
        # 保護される記号（コードでよく使用される）
        self.assertFalse(self.filters.is_short_symbol_noise('"', 1))
        self.assertFalse(self.filters.is_short_symbol_noise("'", 1))
        self.assertFalse(self.filters.is_short_symbol_noise("(", 1))
        self.assertFalse(self.filters.is_short_symbol_noise("=", 1))
        self.assertFalse(self.filters.is_short_symbol_noise("+", 1))
        
        # 除外される記号（制御記号など）
        self.assertTrue(self.filters.is_short_symbol_noise("†", 1))
        self.assertTrue(self.filters.is_short_symbol_noise("§", 1))
        
        # アルファベット・数字は保護
        self.assertFalse(self.filters.is_short_symbol_noise("a", 1))
        self.assertFalse(self.filters.is_short_symbol_noise("1", 1))
        
        # 2文字の場合の処理
        self.assertTrue(self.filters.is_short_symbol_noise("†§", 2))
        self.assertFalse(self.filters.is_short_symbol_noise("()", 2))  # 保護される記号
        self.assertFalse(self.filters.is_short_symbol_noise("ab", 2))  # アルファベット
    
    def test_is_image_element_tag(self):
        """画像・線要素タグフィルタのテスト"""
        self.assertTrue(self.filters.is_image_element_tag("[IMAGE:test.png]"))
        self.assertTrue(self.filters.is_image_element_tag("[LINE]"))
        self.assertTrue(self.filters.is_image_element_tag("[RECT:x,y,w,h]"))
        self.assertFalse(self.filters.is_image_element_tag("[OTHER]"))
        self.assertFalse(self.filters.is_image_element_tag("normal text"))
    
    def test_is_index_pattern(self):
        """目次・索引パターンフィルタのテスト"""
        self.assertTrue(self.filters.is_index_pattern("第1章……10"))
        self.assertTrue(self.filters.is_index_pattern("項目・・・ページ"))
        self.assertFalse(self.filters.is_index_pattern("normal text"))
        self.assertFalse(self.filters.is_index_pattern("..."))

class TestMaximumOCRDetectorV3(unittest.TestCase):
    """MaximumOCRDetectorV3クラスのテスト"""
    
    def setUp(self):
        self.detector = MaximumOCRDetectorV3()
    
    def test_is_ascii_char(self):
        """ASCII文字判定のテスト"""
        self.assertTrue(self.detector.is_ascii_char("a"))
        self.assertTrue(self.detector.is_ascii_char("A"))
        self.assertTrue(self.detector.is_ascii_char("1"))
        self.assertTrue(self.detector.is_ascii_char("!"))
        self.assertFalse(self.detector.is_ascii_char("あ"))
        self.assertFalse(self.detector.is_ascii_char("テ"))
        self.assertFalse(self.detector.is_ascii_char(""))
        self.assertFalse(self.detector.is_ascii_char(None))
    
    def test_is_likely_false_positive_integration(self):
        """誤検知フィルタの統合テスト"""
        # 測定誤差
        self.assertTrue(self.detector.is_likely_false_positive("test", 0.3, 100))
        
        # PDF内部エンコーディング
        self.assertTrue(self.detector.is_likely_false_positive("(cid:123)", 1.0, 100))
        
        # ページ番号
        self.assertTrue(self.detector.is_likely_false_positive("42", 1.0, 100))
        
        # 有効なはみ出し（フィルタを通過すべき）
        self.assertFalse(self.detector.is_likely_false_positive("function()", 1.0, 100))
        self.assertFalse(self.detector.is_likely_false_positive('"', 1.16, 100))  # 重要なケース
    
    def test_margin_calculation(self):
        """マージン計算の正確性テスト"""
        mm_to_pt = self.detector.mm_to_pt
        
        # 奇数ページ: 右マージン10mm
        expected_odd = 10 * mm_to_pt
        self.assertAlmostEqual(expected_odd, 28.3465, places=3)
        
        # 偶数ページ: 右マージン18mm  
        expected_even = 18 * mm_to_pt
        self.assertAlmostEqual(expected_even, 51.0237, places=3)
    
    @patch('pdfplumber.open')
    def test_process_pdf_comprehensive_error_handling(self, mock_pdfplumber):
        """PDF処理のエラーハンドリングテスト"""
        # ファイルが存在しない場合
        non_existent_path = Path("non_existent.pdf")
        results = self.detector.process_pdf_comprehensive(non_existent_path)
        self.assertEqual(results, [])
        
        # pdfplumberでエラーが発生した場合
        mock_pdfplumber.side_effect = Exception("PDF読み込みエラー")
        test_path = Path("test.pdf")
        
        # ファイル存在をモック
        with patch.object(Path, 'exists', return_value=True):
            results = self.detector.process_pdf_comprehensive(test_path)
            self.assertEqual(results, [])
            self.assertIn("Processing error", str(self.detector.quality_metrics['quality_warnings']))
    
    def test_detect_overflows_mock_page(self):
        """detect_overflows関数のモックページテスト"""
        # モックページの作成
        mock_page = Mock()
        mock_page.width = 515.9  # B5幅
        
        # テスト用文字データ
        mock_chars = [
            # 正常な文字（はみ出しなし）
            {'text': 'a', 'x1': 400.0, 'y0': 100.0},
            # はみ出し文字（奇数ページ、右マージン28.3pt超過）
            {'text': 'b', 'x1': 500.0, 'y0': 200.0},  # 515.9 - 28.3 = 487.6 < 500.0
            # 日本語文字（除外されるべき）
            {'text': 'あ', 'x1': 500.0, 'y0': 300.0}
        ]
        mock_page.chars = mock_chars
        
        # 奇数ページでテスト
        results = self.detector.detect_overflows(mock_page, 1)
        
        # はみ出し検出結果の検証
        self.assertEqual(len(results), 1)  # 1つのはみ出しが検出されるはず
        self.assertEqual(results[0]['overflow_text'], 'b')
        self.assertAlmostEqual(results[0]['overflow_amount'], 12.4, places=1)  # 500.0 - 487.6

class TestCalculateMetrics(unittest.TestCase):
    """メトリクス計算のテスト"""
    
    def test_calculate_metrics_basic(self):
        """基本的なメトリクス計算のテスト"""
        # テスト用データ
        ground_truth = {
            'test1.pdf': [1, 2, 3],
            'test2.pdf': [4, 5]
        }
        
        results = {
            'test1.pdf': [1, 2, 6],  # 2正解、1誤検知
            'test2.pdf': [4]         # 1正解、1見逃し
        }
        
        # メトリクス計算（テスト関数として分離）
        def calculate_test_metrics(results_dict, ground_truth_dict):
            total_expected = sum(len(pages) for pages in ground_truth_dict.values())
            total_detected = sum(len(pages) for pages in results_dict.values())
            
            true_positives = 0
            false_positives = 0
            false_negatives = 0
            
            for pdf_file, expected in ground_truth_dict.items():
                detected = results_dict.get(pdf_file, [])
                
                tp = len([p for p in detected if p in expected])
                fp = len([p for p in detected if p not in expected])
                fn = len([p for p in expected if p not in detected])
                
                true_positives += tp
                false_positives += fp
                false_negatives += fn
            
            recall = true_positives / total_expected if total_expected > 0 else 0
            precision = true_positives / total_detected if total_detected > 0 else 1.0
            
            return {
                'recall': recall,
                'precision': precision,
                'true_positives': true_positives,
                'false_positives': false_positives,
                'false_negatives': false_negatives
            }
        
        metrics = calculate_test_metrics(results, ground_truth)
        
        # 検証
        self.assertEqual(metrics['true_positives'], 3)   # 1+2, 4 = 3正解
        self.assertEqual(metrics['false_positives'], 1)  # 6 = 1誤検知
        self.assertEqual(metrics['false_negatives'], 2)  # 3, 5 = 2見逃し
        self.assertEqual(metrics['recall'], 0.6)         # 3/5 = 0.6
        self.assertEqual(metrics['precision'], 0.75)     # 3/4 = 0.75

if __name__ == '__main__':
    # 詳細なテスト結果を表示
    unittest.main(verbosity=2)