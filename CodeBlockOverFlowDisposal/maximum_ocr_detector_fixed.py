#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Maximum OCR Detector Fixed - 誤検知540ページ問題の緊急修正版
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

class MaximumOCRDetectorFixed:
    """誤検知問題を修正したOCR検出器"""
    
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
    
    def is_likely_false_positive(self, overflow_text: str, overflow_amount: float, y_position: float) -> bool:
        """誤検知フィルタリング（大幅強化版）"""
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
        
        # 7. 極端に短いテキスト（2文字以下）かつ記号のみの場合
        if text_length <= 2 and all(not c.isalnum() for c in text_content):
            return True
        
        # 8. 画像・線要素タグ
        if text_content.startswith('[IMAGE:') or text_content.startswith('[LINE]') or text_content.startswith('[RECT:'):
            return True
        
        # 9. 目次・索引特有のパターン
        if '……' in text_content or '・・・' in text_content:
            return True
        
        return False
    
    def detect_overflows(self, page, page_number: int) -> List[Dict]:
        """確実なはみ出し検出（既存検証済みロジックベース）"""
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
        
        # 行ごとに集計し、誤検知フィルタリング適用
        for y_pos, chars_in_line in line_overflows.items():
            chars_in_line.sort(key=lambda x: x['x1'])
            overflow_text = ''.join([c['char'] for c in chars_in_line])
            max_overflow = max(c['overflow'] for c in chars_in_line)
            
            # 強化された誤検知フィルタリング適用
            if not self.is_likely_false_positive(overflow_text, max_overflow, y_pos):
                overflows.append({
                    'y_position': y_pos,
                    'overflow_text': overflow_text,
                    'overflow_amount': max_overflow,
                    'char_count': len(chars_in_line)
                })
        
        return overflows
    
    def process_pdf_comprehensive(self, pdf_path: Path) -> List[Dict]:
        """PDF全体の処理（誤検知修正版）"""
        results = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                self.quality_metrics['total_pages_processed'] = total_pages
                
                logger.info(f"\n{'='*80}")
                logger.info(f"Maximum OCR Detection Fixed: {pdf_path.name} ({total_pages}ページ)")
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
        logger.info(f"Fixed Maximum OCR Quality Report: {pdf_path.name}")
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


def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Maximum OCR Detector Fixed')
    parser.add_argument('pdf_files', nargs='+', help='処理するPDFファイル')
    args = parser.parse_args()
    
    detector = MaximumOCRDetectorFixed()
    
    for pdf_file in args.pdf_files:
        pdf_path = Path(pdf_file)
        if not pdf_path.exists():
            logger.error(f"ファイルが見つかりません: {pdf_path}")
            continue
        
        results = detector.process_pdf_comprehensive(pdf_path)
        detector.print_quality_report(results, pdf_path)


if __name__ == "__main__":
    main()