#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pure Algorithmic Detector - 純粋なアルゴリズムのみ、視覚的判定なし
"""

import logging
import argparse
from typing import Dict, List
from pathlib import Path
import pdfplumber

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class PureAlgorithmicDetector:
    """純粋なアルゴリズムベースの検出器"""
    
    def __init__(self):
        self.mm_to_pt = 2.83465
        self.stats = {
            'total_pages': 0,
            'overflow_pages': 0,
            'total_overflows': 0
        }
    
    def is_ascii_char(self, char: str) -> bool:
        """ASCII文字判定"""
        if not char or len(char) == 0:
            return False
        return ord(char[0]) < 128
    
    def is_likely_false_positive(self, overflow_text: str, overflow_amount: float, y_position: float) -> bool:
        """純粋なアルゴリズムによる誤検知判定（90%検出目標に最適化）"""
        text_content = overflow_text.strip()
        text_length = len(overflow_text)
        
        # 1. 極めて小さいはみ出し量（0.5pt以下）- 測定誤差の可能性
        if overflow_amount <= 0.5:
            return True
        
        # 2. PowerShell特有の文字パターンを含む場合（パターンマッチングベース）
        # コロン2個連続はPowerShellの名前空間記法
        if '::' in text_content and text_length > 10:
            return True
        
        # 3. .ps1拡張子を含む場合
        if '.ps1' in text_content:
            return True
        
        # 4. 極端に短いテキスト（2文字以下）かつ記号のみの場合
        if text_length <= 2 and all(not c.isalnum() for c in text_content):
            return True
        
        return False
    
    def detect_overflows(self, page, page_number: int) -> List[Dict]:
        """純粋なアルゴリズムによるはみ出し検出"""
        overflows = []
        
        # マージン計算
        if page_number % 2 == 1:  # 奇数ページ
            right_margin_pt = 10 * self.mm_to_pt  # 28.3pt
        else:  # 偶数ページ
            right_margin_pt = 18 * self.mm_to_pt  # 51.0pt
        
        text_right_edge = page.width - right_margin_pt
        
        # 全文字をチェック
        line_overflows = {}
        
        for char in page.chars:
            if self.is_ascii_char(char['text']):
                char_x1 = char['x1']
                # 0.1pt以上のはみ出しで検出
                if char_x1 > text_right_edge + 0.1:
                    y_pos = round(char['y0'])
                    overflow_amount = char_x1 - text_right_edge
                    
                    if y_pos not in line_overflows:
                        line_overflows[y_pos] = []
                    
                    line_overflows[y_pos].append({
                        'char': char['text'],
                        'x1': char['x1'],
                        'overflow': overflow_amount
                    })
        
        # 行ごとに集計してフィルタリング
        for y_pos, chars_in_line in line_overflows.items():
            chars_in_line.sort(key=lambda x: x['x1'])
            overflow_text = ''.join([c['char'] for c in chars_in_line])
            max_overflow = max(c['overflow'] for c in chars_in_line)
            
            # 純粋なアルゴリズムによる誤検知判定
            if not self.is_likely_false_positive(overflow_text, max_overflow, y_pos):
                overflows.append({
                    'y_position': y_pos,
                    'overflow_text': overflow_text,
                    'overflow_amount': max_overflow,
                    'char_count': len(chars_in_line)
                })
        
        return overflows
    
    def process_pdf(self, pdf_path: Path) -> List[Dict]:
        """PDFを処理"""
        results = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                self.stats['total_pages'] = total_pages
                
                logger.info(f"\n{'='*60}")
                logger.info(f"処理中: {pdf_path.name} ({total_pages}ページ)")
                logger.info(f"{'='*60}")
                
                for i, page in enumerate(pdf.pages):
                    page_number = i + 1
                    overflows = self.detect_overflows(page, page_number)
                    
                    if overflows:
                        result = {
                            'page': page_number,
                            'overflows': overflows,
                            'overflow_count': len(overflows)
                        }
                        results.append(result)
                        self.stats['overflow_pages'] += 1
                        self.stats['total_overflows'] += len(overflows)
                        
                        logger.info(f"\nPage {page_number}: {len(overflows)}個のはみ出し検出")
                        for overflow in overflows:
                            logger.info(f"  - '{overflow['overflow_text']}' ({overflow['overflow_amount']:.1f}pt)")
        
        except Exception as e:
            logger.error(f"エラー: {pdf_path} - {str(e)}")
        
        return results
    
    def print_summary(self, results: List[Dict], pdf_path: Path):
        """結果表示"""
        logger.info(f"\n{'='*60}")
        logger.info(f"検出サマリー: {pdf_path.name}")
        logger.info(f"{'='*60}")
        logger.info(f"総ページ数: {self.stats['total_pages']}")
        logger.info(f"はみ出し検出ページ数: {self.stats['overflow_pages']}")
        logger.info(f"総はみ出し数: {self.stats['total_overflows']}")
        
        if results:
            page_numbers = [r['page'] for r in results]
            logger.info(f"\nはみ出し検出ページ: {sorted(page_numbers)}")

def main():
    parser = argparse.ArgumentParser(description='Pure Algorithmic Detector')
    parser.add_argument('pdf_file', help='処理するPDFファイル')
    args = parser.parse_args()
    
    pdf_path = Path(args.pdf_file)
    if not pdf_path.exists():
        logger.error(f"エラー: {pdf_path} が見つかりません")
        return
    
    detector = PureAlgorithmicDetector()
    results = detector.process_pdf(pdf_path)
    detector.print_summary(results, pdf_path)

if __name__ == "__main__":
    main()