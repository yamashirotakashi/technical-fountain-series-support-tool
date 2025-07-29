#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Maximum OCR Detector V3 - 構造改善版
複雑度20の関数を分割し、保守性と拡張性を向上
Sequential Thinking批判的検証の結果を反映
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple
import statistics
import sys
import os

# プロジェクトルートを追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import pdfplumber
except ImportError:
    print("pdfplumber not available. Running in compatibility mode.")
    print("Install pdfplumber: pip install pdfplumber")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class FalsePositiveFilters:
    """誤検知フィルタ群（分割された実装）"""
    
    @staticmethod
    def is_measurement_error(overflow_amount: float) -> bool:
        """測定誤差の可能性があるはみ出し量かチェック"""
        return overflow_amount <= 0.5
    
    @staticmethod
    def is_pdf_internal_encoding(text_content: str) -> bool:
        """PDF内部エンコーディング文字かチェック"""
        return '(cid:' in text_content
    
    @staticmethod
    def is_page_number(text_content: str) -> bool:
        """ページ番号のみかチェック"""
        return text_content.isdigit() and len(text_content) <= 3
    
    @staticmethod
    def is_japanese_only(text_content: str) -> bool:
        """日本語文字のみかチェック（ASCII対象外）"""
        if not text_content:
            return False
        printable_chars = [c for c in text_content if c.isprintable()]
        if not printable_chars:
            return False
        return all(ord(c) > 127 for c in printable_chars)
    
    @staticmethod
    def is_powershell_pattern(text_content: str, text_length: int) -> bool:
        """PowerShell特有パターンかチェック"""
        return '::' in text_content and text_length > 10
    
    @staticmethod
    def is_file_extension(text_content: str) -> bool:
        """ファイル拡張子パターンかチェック"""
        return '.ps1' in text_content
    
    @staticmethod
    def is_short_symbol_noise(text_content: str, text_length: int) -> bool:
        """短い記号ノイズかチェック（改良版）"""
        if text_length == 1:
            char = text_content[0]
            # 重要な記号は保護（コードでよく使用される）
            protected_symbols = {
                '"', "'", '(', ')', '[', ']', '{', '}', '<', '>', 
                '=', '+', '-', '*', '/', '\\', '|', '&', '%', 
                '$', '#', '@', '!', '?', '.', ',', ';', ':'
            }
            return char not in protected_symbols and not char.isalnum()
        elif text_length == 2:
            # 2文字で両方とも制御記号の場合のみ除外
            excluded_symbols = {'"', "'", '(', ')', '[', ']', '{', '}', '<', '>', '=', '+', '-'}
            return all(not c.isalnum() and c not in excluded_symbols for c in text_content)
        return False
    
    @staticmethod
    def is_image_element_tag(text_content: str) -> bool:
        """画像・線要素タグかチェック"""
        return (text_content.startswith('[IMAGE:') or 
                text_content.startswith('[LINE]') or 
                text_content.startswith('[RECT:'))
    
    @staticmethod
    def is_index_pattern(text_content: str) -> bool:
        """目次・索引特有のパターンかチェック"""
        return '……' in text_content or '・・・' in text_content

class MaximumOCRDetectorV3:
    """構造改善版OCR検出器"""
    
    def __init__(self):
        self.mm_to_pt = 2.83465
        self.filters = FalsePositiveFilters()
        self.quality_metrics = {
            'total_pages_processed': 0,
            'total_detections': 0,
            'quality_warnings': []
        }
    
    def is_ascii_char(self, char: str) -> bool:
        """ASCII文字判定"""
        if not char or len(char) == 0:
            return False
        return ord(char[0]) < 128
    
    def is_likely_false_positive(self, overflow_text: str, overflow_amount: float, y_position: float) -> bool:
        """改良版誤検知フィルタリング（分割された実装）"""
        text_content = overflow_text.strip()
        text_length = len(overflow_text)
        
        # 各フィルタを順次適用（複雑度を分散）
        if self.filters.is_measurement_error(overflow_amount):
            return True
        
        if self.filters.is_pdf_internal_encoding(text_content):
            return True
        
        if self.filters.is_page_number(text_content):
            return True
        
        if self.filters.is_japanese_only(text_content):
            return True
        
        if self.filters.is_powershell_pattern(text_content, text_length):
            return True
        
        if self.filters.is_file_extension(text_content):
            return True
        
        if self.filters.is_short_symbol_noise(text_content, text_length):
            return True
        
        if self.filters.is_image_element_tag(text_content):
            return True
        
        if self.filters.is_index_pattern(text_content):
            return True
        
        return False
    
    def detect_overflows(self, page, page_number: int) -> List[Dict]:
        """確実なはみ出し検出"""
        overflows = []
        
        # マージン計算
        if page_number % 2 == 1:  # 奇数ページ
            right_margin_pt = 10 * self.mm_to_pt  # 28.3pt
        else:  # 偶数ページ
            right_margin_pt = 18 * self.mm_to_pt  # 51.0pt
        
        text_right_edge = page.width - right_margin_pt
        
        # 行ごとのはみ出し文字収集
        line_overflows = {}
        
        for char in page.chars:
            if self.is_ascii_char(char['text']):
                char_x1 = char['x1']
                if char_x1 > text_right_edge + 0.1:  # 0.1pt閾値
                    y_pos = round(char['y0'])
                    overflow_amount = char_x1 - text_right_edge
                    
                    if y_pos not in line_overflows:
                        line_overflows[y_pos] = []
                    
                    line_overflows[y_pos].append({
                        'char': char['text'],
                        'x1': char['x1'],
                        'overflow': overflow_amount
                    })
        
        # 行ごとに集計し、改良版誤検知フィルタリング適用
        for y_pos, chars_in_line in line_overflows.items():
            chars_in_line.sort(key=lambda x: x['x1'])
            overflow_text = ''.join([c['char'] for c in chars_in_line])
            max_overflow = max(c['overflow'] for c in chars_in_line)
            
            # 改良版誤検知フィルタリング適用
            if not self.is_likely_false_positive(overflow_text, max_overflow, y_pos):
                overflows.append({
                    'y_position': y_pos,
                    'overflow_text': overflow_text,
                    'overflow_amount': max_overflow,
                    'char_count': len(chars_in_line)
                })
        
        return overflows
    
    def process_pdf_comprehensive(self, pdf_path: Path) -> List[Dict]:
        """PDF全体の処理（V3版）"""
        results = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                self.quality_metrics['total_pages_processed'] = total_pages
                
                logger.info(f"\n{'='*80}")
                logger.info(f"Maximum OCR Detection V3: {pdf_path.name} ({total_pages}ページ)")
                logger.info(f"{'='*80}")
                
                for i, page in enumerate(pdf.pages):
                    page_number = i + 1
                    page_results = self.detect_overflows(page, page_number)
                    
                    if page_results:
                        result = {
                            'page': page_number,
                            'overflows': page_results,
                            'overflow_count': len(page_results)
                        }
                        results.append(result)
                        
                        logger.info(f"\nPage {page_number}: {len(page_results)}個の検出")
                        for overflow in page_results:
                            logger.info(f"  - '{overflow['overflow_text'][:50]}' ({overflow['overflow_amount']:.2f}pt)")
        
        except Exception as e:
            logger.error(f"エラー: {pdf_path} - {str(e)}")
            self.quality_metrics['quality_warnings'].append(f"Processing error: {str(e)}")
        
        return results
    
    def print_quality_report(self, results: List[Dict], pdf_path: Path):
        """品質レポートの出力"""
        logger.info(f"\n{'='*80}")
        logger.info(f"Maximum OCR V3 Quality Report: {pdf_path.name}")
        logger.info(f"{'='*80}")
        
        total_detections = sum(r['overflow_count'] for r in results)
        pages_with_detections = len(results)
        
        logger.info(f"処理ページ数: {self.quality_metrics['total_pages_processed']}")
        logger.info(f"検出ページ数: {pages_with_detections}")
        logger.info(f"総検出数: {total_detections}")
        
        if self.quality_metrics['quality_warnings']:
            logger.info(f"\n品質警告:")
            for warning in self.quality_metrics['quality_warnings']:
                logger.info(f"  ⚠️ {warning}")
        
        # 検出詳細
        if results:
            detected_pages = [r['page'] for r in results]
            logger.info(f"\n検出ページリスト: {sorted(detected_pages)}")
        
        logger.info("="*80)

def run_comprehensive_test():
    """全PDFでの包括的テスト（V3実装）"""
    detector = MaximumOCRDetectorV3()
    pdf_files = ['sample.pdf', 'sample2.pdf', 'sample3.pdf', 'sample4.pdf', 'sample5.pdf']
    
    all_results = {}
    
    logger.info("=" * 90)
    logger.info("Maximum OCR Detector V3 - 構造改善版性能テスト")
    logger.info("=" * 90)
    
    for pdf_file in pdf_files:
        pdf_path = Path(pdf_file)
        if not pdf_path.exists():
            logger.error(f"ファイルが見つかりません: {pdf_path}")
            continue
        
        results = detector.process_pdf_comprehensive(pdf_path)
        detector.print_quality_report(results, pdf_path)
        
        # 結果を保存
        detected_pages = [r['page'] for r in results]
        all_results[pdf_file] = detected_pages
    
    # 性能評価（現実的評価）
    ground_truth = {
        'sample.pdf': [48],
        'sample2.pdf': [128, 129],
        'sample3.pdf': [13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 78, 80, 106, 115, 122, 124],
        'sample4.pdf': [27, 30, 38, 73, 75, 76],
        'sample5.pdf': [128, 129]
    }
    
    # V2との比較
    v2_results = {
        'sample.pdf': [],
        'sample2.pdf': [],
        'sample3.pdf': [13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 75, 78, 79, 115, 121, 122, 124, 125],
        'sample4.pdf': [27, 30, 38, 73, 76],
        'sample5.pdf': []
    }
    
    def calculate_metrics(results_dict):
        total_expected = sum(len(pages) for pages in ground_truth.values())
        total_detected = sum(len(pages) for pages in results_dict.values())
        
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        for pdf_file, expected in ground_truth.items():
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
            'false_negatives': false_negatives,
            'total_detected': total_detected
        }
    
    v2_metrics = calculate_metrics(v2_results)
    v3_metrics = calculate_metrics(all_results)
    
    logger.info(f"\n📊 V2 vs V3 性能比較（現実的評価）:")
    logger.info("-" * 70)
    logger.info(f"{'指標':<15} {'V2':<15} {'V3':<15} {'改善':<15}")
    logger.info("-" * 70)
    logger.info(f"{'Recall':<15} {v2_metrics['recall']:<14.1%} {v3_metrics['recall']:<14.1%} {v3_metrics['recall']-v2_metrics['recall']:+.1%}")
    logger.info(f"{'Precision':<15} {v2_metrics['precision']:<14.1%} {v3_metrics['precision']:<14.1%} {v3_metrics['precision']-v2_metrics['precision']:+.1%}")
    logger.info(f"{'検出ページ数':<15} {v2_metrics['total_detected']:<14} {v3_metrics['total_detected']:<14} {v3_metrics['total_detected']-v2_metrics['total_detected']:+}")
    logger.info(f"{'正検出':<15} {v2_metrics['true_positives']:<14} {v3_metrics['true_positives']:<14} {v3_metrics['true_positives']-v2_metrics['true_positives']:+}")
    logger.info(f"{'誤検出':<15} {v2_metrics['false_positives']:<14} {v3_metrics['false_positives']:<14} {v3_metrics['false_positives']-v2_metrics['false_positives']:+}")
    logger.info(f"{'見逃し':<15} {v2_metrics['false_negatives']:<14} {v3_metrics['false_negatives']:<14} {v3_metrics['false_negatives']-v2_metrics['false_negatives']:+}")
    
    logger.info(f"\n🎯 目標達成状況（現実的評価）:")
    logger.info("-" * 50)
    logger.info(f"Phase 1目標（78%）: {'✅ 達成' if v3_metrics['recall'] >= 0.78 else '❌ 未達成'}")
    logger.info(f"最終目標（85%）  : {'✅ 達成' if v3_metrics['recall'] >= 0.85 else '❌ 未達成'}")
    logger.info(f"V3 Recall         : {v3_metrics['recall']:.1%}")
    
    if v3_metrics['recall'] < 0.78:
        needed_additional = int(28 * (0.78 - v3_metrics['recall']))
        logger.info(f"❌ Phase 1目標未達成、{needed_additional}ページの追加改善が必要")
    else:
        logger.info(f"✅ Phase 1目標達成済み")
    
    logger.info("\n🏗️ 構造改善成果:")
    logger.info("- 複雑度20関数を9つの単純関数に分割")
    logger.info("- FalsePositiveFiltersクラスによる責任分離")
    logger.info("- 各フィルタの独立テストが可能")
    logger.info("- 保守性とデバッグ容易性の大幅向上")
    
    logger.info("=" * 90)

def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Maximum OCR Detector V3')
    parser.add_argument('--test', action='store_true', help='包括的テストを実行')
    parser.add_argument('pdf_files', nargs='*', help='処理するPDFファイル')
    args = parser.parse_args()
    
    if args.test:
        run_comprehensive_test()
    else:
        detector = MaximumOCRDetectorV3()
        
        for pdf_file in args.pdf_files:
            pdf_path = Path(pdf_file)
            if not pdf_path.exists():
                logger.error(f"ファイルが見つかりません: {pdf_path}")
                continue
            
            results = detector.process_pdf_comprehensive(pdf_path)
            detector.print_quality_report(results, pdf_path)

if __name__ == "__main__":
    main()