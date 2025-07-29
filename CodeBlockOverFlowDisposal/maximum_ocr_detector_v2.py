#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Maximum OCR Detector V2 - フィルタ修正版
「短いテキスト+記号のみ」フィルタを改良し、78%目標達成を目指す
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

class MaximumOCRDetectorV2:
    """フィルタ修正版OCR検出器"""
    
    def __init__(self):
        self.mm_to_pt = 2.83465
        self.quality_metrics = {
            'total_pages_processed': 0,
            'total_detections': 0,
            'quality_warnings': []
        }
    
    def is_ascii_char(self, char: str) -> bool:
        """ASCII文字判定（既存の検証済みロジック）"""
        if not char or len(char) == 0:
            return False
        return ord(char[0]) < 128
    
    def is_likely_false_positive_v2(self, overflow_text: str, overflow_amount: float, y_position: float) -> bool:
        """改良版誤検知フィルタリング - 有効なはみ出しを保護"""
        text_content = overflow_text.strip()
        text_length = len(overflow_text)
        
        # 1. 極めて小さいはみ出し量（0.5pt以下）- 測定誤差の可能性
        if overflow_amount <= 0.5:
            return True
        
        # 2. (cid:X)文字を含む場合（最も多い誤検知原因）
        if '(cid:' in text_content:
            return True
        
        # 3. ページ番号のみの場合
        if text_content.isdigit() and len(text_content) <= 3:
            return True
        
        # 4. 日本語文字のみの場合（はみ出し対象はASCII文字）
        if all(ord(c) > 127 for c in text_content if c.isprintable()):
            return True
        
        # 5. PowerShell特有の文字パターンを含む場合
        if '::' in text_content and text_length > 10:
            return True
        
        # 6. .ps1拡張子を含む場合
        if '.ps1' in text_content:
            return True
        
        # 7. 【修正】極端に短いテキスト + 記号のみフィルタ
        # 以前: 2文字以下かつ記号のみを除外 → 有効な引用符等も除外
        # 改良: 1文字かつ制御記号・特殊記号のみを除外、通常の引用符等は保護
        if text_length == 1:
            char = text_content[0]
            # 通常の引用符、括弧等は保護（コードでよく使用される）
            protected_symbols = {'"', "'", '(', ')', '[', ']', '{', '}', '<', '>', '=', '+', '-', '*', '/', '\\', '|', '&', '%', '$', '#', '@', '!', '?', '.', ',', ';', ':'}
            if char not in protected_symbols and not char.isalnum():
                return True
        elif text_length == 2 and all(not c.isalnum() and c not in {'"', "'", '(', ')', '[', ']', '{', '}', '<', '>', '=', '+', '-'} for c in text_content):
            # 2文字で両方とも特殊記号の場合のみ除外
            return True
        
        # 8. 画像・線要素タグ
        if text_content.startswith('[IMAGE:') or text_content.startswith('[LINE]') or text_content.startswith('[RECT:'):
            return True
        
        # 9. 目次・索引特有のパターン
        if '……' in text_content or '・・・' in text_content:
            return True
        
        return False
    
    def detect_overflows(self, page, page_number: int) -> List[Dict]:
        """確実なはみ出し検出（改良版フィルタリング）"""
        overflows = []
        
        # マージン計算（既存の検証済みロジック）
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
            if not self.is_likely_false_positive_v2(overflow_text, max_overflow, y_pos):
                overflows.append({
                    'y_position': y_pos,
                    'overflow_text': overflow_text,
                    'overflow_amount': max_overflow,
                    'char_count': len(chars_in_line)
                })
        
        return overflows
    
    def process_pdf_comprehensive(self, pdf_path: Path) -> List[Dict]:
        """PDF全体の処理（V2版）"""
        results = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                self.quality_metrics['total_pages_processed'] = total_pages
                
                logger.info(f"\n{'='*80}")
                logger.info(f"Maximum OCR Detection V2: {pdf_path.name} ({total_pages}ページ)")
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
        logger.info(f"Maximum OCR V2 Quality Report: {pdf_path.name}")
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
    """全PDFでの包括的テスト"""
    detector = MaximumOCRDetectorV2()
    pdf_files = ['sample.pdf', 'sample2.pdf', 'sample3.pdf', 'sample4.pdf', 'sample5.pdf']
    
    all_results = {}
    
    logger.info("=" * 90)
    logger.info("Maximum OCR Detector V2 - 包括的性能テスト")
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
    
    # 性能評価
    ground_truth = {
        'sample.pdf': [48],
        'sample2.pdf': [128, 129],
        'sample3.pdf': [13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 78, 80, 106, 115, 122, 124],
        'sample4.pdf': [27, 30, 38, 73, 75, 76],
        'sample5.pdf': [128, 129]
    }
    
    # V1との比較
    v1_results = {
        'sample.pdf': [],
        'sample2.pdf': [],
        'sample3.pdf': [13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 75, 78, 79, 115, 121, 122, 124, 125],
        'sample4.pdf': [27, 30, 73, 76],
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
    
    v1_metrics = calculate_metrics(v1_results)
    v2_metrics = calculate_metrics(all_results)
    
    logger.info(f"\n📊 V1 vs V2 性能比較:")
    logger.info("-" * 70)
    logger.info(f"{'指標':<15} {'V1':<15} {'V2':<15} {'改善':<15}")
    logger.info("-" * 70)
    logger.info(f"{'Recall':<15} {v1_metrics['recall']:<14.1%} {v2_metrics['recall']:<14.1%} {v2_metrics['recall']-v1_metrics['recall']:+.1%}")
    logger.info(f"{'Precision':<15} {v1_metrics['precision']:<14.1%} {v2_metrics['precision']:<14.1%} {v2_metrics['precision']-v1_metrics['precision']:+.1%}")
    logger.info(f"{'検出ページ数':<15} {v1_metrics['total_detected']:<14} {v2_metrics['total_detected']:<14} {v2_metrics['total_detected']-v1_metrics['total_detected']:+}")
    logger.info(f"{'正検出':<15} {v1_metrics['true_positives']:<14} {v2_metrics['true_positives']:<14} {v2_metrics['true_positives']-v1_metrics['true_positives']:+}")
    logger.info(f"{'誤検出':<15} {v1_metrics['false_positives']:<14} {v2_metrics['false_positives']:<14} {v2_metrics['false_positives']-v1_metrics['false_positives']:+}")
    logger.info(f"{'見逃し':<15} {v1_metrics['false_negatives']:<14} {v2_metrics['false_negatives']:<14} {v2_metrics['false_negatives']-v1_metrics['false_negatives']:+}")
    
    logger.info(f"\n🎯 目標達成状況:")
    logger.info("-" * 50)
    logger.info(f"Phase 1目標（78%）: {'✅ 達成' if v2_metrics['recall'] >= 0.78 else '❌ 未達成'}")
    logger.info(f"最終目標（85%）  : {'✅ 達成' if v2_metrics['recall'] >= 0.85 else '❌ 未達成'}")
    logger.info(f"V2 Recall         : {v2_metrics['recall']:.1%}")
    
    if v2_metrics['recall'] >= 0.85:
        logger.info(f"🎉 最終目標達成！Phase 2は不要です。")
    elif v2_metrics['recall'] >= 0.78:
        needed_additional = int(28 * (0.85 - v2_metrics['recall']))
        logger.info(f"⚠️  Phase 1目標達成、残り{needed_additional}ページでPhase 2不要")
    else:
        needed_additional = int(28 * (0.78 - v2_metrics['recall']))
        logger.info(f"❌ Phase 1目標未達成、{needed_additional}ページの追加改善が必要")
    
    logger.info("=" * 90)

def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Maximum OCR Detector V2')
    parser.add_argument('--test', action='store_true', help='包括的テストを実行')
    parser.add_argument('pdf_files', nargs='*', help='処理するPDFファイル')
    args = parser.parse_args()
    
    if args.test:
        run_comprehensive_test()
    else:
        detector = MaximumOCRDetectorV2()
        
        for pdf_file in args.pdf_files:
            pdf_path = Path(pdf_file)
            if not pdf_path.exists():
                logger.error(f"ファイルが見つかりません: {pdf_path}")
                continue
            
            results = detector.process_pdf_comprehensive(pdf_path)
            detector.print_quality_report(results, pdf_path)

if __name__ == "__main__":
    main()