#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Overflow Detector Final - 最終版コードブロックはみ出し検出器
実際のはみ出しを検出する純粋なアルゴリズムベース実装
"""

import re
import json
import logging
import argparse
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path
import pdfplumber
from dataclasses import dataclass

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Config:
    """設定パラメータ"""
    # B5サイズ (mm)
    b5_width_mm: float = 182
    b5_height_mm: float = 257
    
    # mm to point conversion
    mm_to_pt: float = 2.83465
    
    # マージン設定 (mm) - 実際の分析結果に基づく
    odd_page_margins: Dict[str, float] = None
    even_page_margins: Dict[str, float] = None
    
    # 検出閾値
    overflow_threshold: float = 0.1  # 0.1pt以上のはみ出しを検出
    min_overflow_chars: int = 1  # 1文字から検出
    
    def __post_init__(self):
        if self.odd_page_margins is None:
            # 奇数ページ: 右マージン10mm
            self.odd_page_margins = {'top': 30, 'bottom': 20, 'left': 18, 'right': 10}
        if self.even_page_margins is None:
            # 偶数ページ: 右マージン18mm  
            self.even_page_margins = {'top': 30, 'bottom': 20, 'left': 10, 'right': 18}

class OverflowDetectorFinal:
    """最終版はみ出し検出器 - 純粋なアルゴリズムベース"""
    
    def __init__(self):
        self.config = Config()
        self.stats = {
            'total_pages': 0,
            'overflow_pages': 0,
            'total_overflows': 0,
            'filtered_overflows': 0
        }
    
    def is_ascii_char(self, char: str) -> bool:
        """ASCII文字（英数字・記号）かどうかの判定"""
        if not char or len(char) == 0:
            return False
        return ord(char[0]) < 128
    
    def is_likely_false_positive(self, overflow_text: str, overflow_amount: float) -> bool:
        """誤検知の可能性が高いパターンかどうかを判定"""
        # 非常に小さなはみ出し（1pt未満）
        if overflow_amount < 1.0:
            return True
        
        # 単一の句読点や記号
        if len(overflow_text) == 1 and overflow_text in '.,;:!?()[]{}"\'-':
            return overflow_amount < 5.0
        
        # その他はすべて有効な検出として扱う
        return False
    
    def detect_overflows(self, page, page_number: int) -> List[Dict]:
        """ページ内のすべてのはみ出しを検出"""
        overflows = []
        
        # 本文領域の右端を計算
        if page_number % 2 == 0:  # 偶数ページ
            right_margin_pt = self.config.even_page_margins['right'] * self.config.mm_to_pt
        else:  # 奇数ページ
            right_margin_pt = self.config.odd_page_margins['right'] * self.config.mm_to_pt
        
        text_right_edge = page.width - right_margin_pt
        
        # 行ごとのはみ出し文字を収集
        line_overflows = {}
        
        for char in page.chars:
            # ASCII文字のみを対象
            if self.is_ascii_char(char['text']):
                char_x1 = char['x1']
                overflow_amount = char_x1 - text_right_edge
                
                if overflow_amount > self.config.overflow_threshold:
                    y_pos = round(char['y0'])
                    
                    if y_pos not in line_overflows:
                        line_overflows[y_pos] = []
                    
                    line_overflows[y_pos].append({
                        'char': char['text'],
                        'x0': char['x0'],
                        'x1': char['x1'],
                        'y0': char['y0'],
                        'overflow': overflow_amount
                    })
        
        # 行ごとに集計
        for y_pos, chars_in_line in line_overflows.items():
            if len(chars_in_line) >= self.config.min_overflow_chars:
                # x座標順にソート
                chars_in_line.sort(key=lambda x: x['x0'])
                
                # 連続する文字をグループ化
                groups = []
                current_group = [chars_in_line[0]]
                
                for char in chars_in_line[1:]:
                    # 前の文字との距離が5pt以内なら同じグループ
                    if char['x0'] - current_group[-1]['x1'] < 5.0:
                        current_group.append(char)
                    else:
                        groups.append(current_group)
                        current_group = [char]
                
                groups.append(current_group)
                
                # 各グループを処理
                for group in groups:
                    overflow_text = ''.join([c['char'] for c in group])
                    max_overflow = max(c['overflow'] for c in group)
                    
                    # 誤検知フィルタリング
                    if not self.is_likely_false_positive(overflow_text, max_overflow):
                        overflows.append({
                            'y_position': y_pos,
                            'overflow_text': overflow_text,
                            'overflow_amount': max_overflow,
                            'char_count': len(group),
                            'first_char_x': group[0]['x0'],
                            'last_char_x': group[-1]['x1']
                        })
                    else:
                        self.stats['filtered_overflows'] += 1
        
        return overflows
    
    def detect_page(self, page, page_number: int, pdf_name: str) -> Dict:
        """1ページのはみ出し検出"""
        overflows = self.detect_overflows(page, page_number)
        has_overflow = len(overflows) > 0
        
        return {
            'page': page_number,
            'has_overflow': has_overflow,
            'overflows': overflows,
            'overflow_count': len(overflows)
        }
    
    def process_pdf(self, pdf_path: Path) -> List[Dict]:
        """PDFファイル全体を処理"""
        results = []
        pdf_name = pdf_path.name
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                self.stats['total_pages'] += total_pages
                
                logger.info(f"\n{'='*60}")
                logger.info(f"処理中: {pdf_name} ({total_pages}ページ)")
                logger.info(f"{'='*60}")
                
                for i, page in enumerate(pdf.pages):
                    page_number = i + 1
                    result = self.detect_page(page, page_number, pdf_name)
                    
                    if result['has_overflow']:
                        results.append(result)
                        self.stats['overflow_pages'] += 1
                        self.stats['total_overflows'] += result['overflow_count']
                        
                        # 検出情報を表示
                        logger.info(f"\nPage {page_number}: {result['overflow_count']}個のはみ出し検出")
                        for overflow in result['overflows']:
                            logger.info(f"  - '{overflow['overflow_text']}' ({overflow['overflow_amount']:.1f}pt)")
        
        except Exception as e:
            logger.error(f"エラー: {pdf_path} - {str(e)}")
        
        return results
    
    def print_summary(self, results: List[Dict], pdf_path: Path):
        """結果サマリーの表示"""
        logger.info(f"\n{'='*60}")
        logger.info(f"検出サマリー: {pdf_path.name}")
        logger.info(f"{'='*60}")
        logger.info(f"総ページ数: {self.stats['total_pages']}")
        logger.info(f"はみ出し検出ページ数: {self.stats['overflow_pages']}")
        logger.info(f"総はみ出し数: {self.stats['total_overflows']}")
        logger.info(f"フィルタリングされた検出: {self.stats['filtered_overflows']}")
        
        # ページ番号リスト
        if results:
            page_numbers = [r['page'] for r in results]
            logger.info(f"\nはみ出し検出ページ: {sorted(page_numbers)}")
            logger.info(f"検出ページ数: {len(page_numbers)}")

def main():
    parser = argparse.ArgumentParser(description='Overflow Detector Final - 最終版はみ出し検出器')
    parser.add_argument('pdf_file', help='処理するPDFファイル')
    parser.add_argument('-o', '--output', help='結果を保存するJSONファイル')
    args = parser.parse_args()
    
    pdf_path = Path(args.pdf_file)
    if not pdf_path.exists():
        logger.error(f"エラー: {pdf_path} が見つかりません")
        return
    
    detector = OverflowDetectorFinal()
    results = detector.process_pdf(pdf_path)
    
    detector.print_summary(results, pdf_path)
    
    if args.output:
        output_path = Path(args.output)
        output_data = {
            'pdf_file': str(pdf_path),
            'total_pages': detector.stats['total_pages'],
            'results': results,
            'stats': detector.stats
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        logger.info(f"\n結果を保存しました: {output_path}")

if __name__ == "__main__":
    main()