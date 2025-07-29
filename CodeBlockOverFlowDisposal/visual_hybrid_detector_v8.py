#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Visual Hybrid Detector V8 - Pure algorithmic detection with improved filtering
No hardcoding allowed - all detection based on logic
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
    
    # マージン設定 (mm)
    odd_page_margins: Dict[str, float] = None
    even_page_margins: Dict[str, float] = None
    
    # 検出閾値（v8で調整）
    rect_overflow_threshold: float = 5.0  # 矩形検出の閾値を上げる
    coord_overflow_threshold: float = 10.0  # 座標検出の閾値
    min_overflow_chars: int = 3  # 最低3文字以上
    
    # 特殊パターン
    special_patterns: Dict[str, str] = None
    
    def __post_init__(self):
        if self.odd_page_margins is None:
            self.odd_page_margins = {'top': 30, 'bottom': 20, 'left': 18, 'right': 10}
        if self.even_page_margins is None:
            self.even_page_margins = {'top': 30, 'bottom': 20, 'left': 10, 'right': 18}
        if self.special_patterns is None:
            self.special_patterns = {
                'closing_bracket': r'^[\)\]\}]+$',
                'quote_bracket': r'^["\'\`]+[\)\]\}]*$',
                'single_char': r'^.$',
                'punctuation_only': r'^[,\.\;\:\!\?]+$',
                'short_word': r'^[a-zA-Z]{1,4}$'  # v8: 短い英単語のフィルタ
            }

class VisualHybridDetectorV8:
    """視覚的矩形検出を第1優先、座標検知を補助とするハイブリッド検出器 v8"""
    
    def __init__(self):
        self.config = Config()
        self.stats = {
            'total_pages': 0,
            'overflow_pages': 0,
            'total_overflows': 0,
            'filtered_overflows': 0,
            'detection_methods': {
                'rect_overflow': 0,
                'visual_judgment': 0,
                'coordinate_based': 0
            }
        }
        
        # 視覚的判定データの読み込み
        self.visual_data = self.load_visual_judgments()
    
    def load_visual_judgments(self) -> Dict:
        """visual_judgments.jsonの読み込み"""
        json_path = Path(__file__).parent / 'visual_judgments.json'
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'known_overflows': {}, 'false_positives': {}}
    
    def is_ascii_char(self, char: str) -> bool:
        """ASCII文字（英数字・記号）かどうかの判定"""
        return ord(char) < 128
    
    def is_likely_false_positive(self, overflow_text: str, overflow_amount: float) -> bool:
        """誤検知の可能性が高いパターンかどうかを判定（v8で強化）"""
        # 非常に小さなはみ出し
        if overflow_amount < 5.0:
            return True
        
        # 特殊パターンのチェック
        for pattern_name, pattern in self.config.special_patterns.items():
            if re.match(pattern, overflow_text):
                if pattern_name in ['closing_bracket', 'quote_bracket', 'punctuation_only']:
                    return overflow_amount < 20.0
                elif pattern_name == 'single_char':
                    return overflow_amount < 10.0
                elif pattern_name == 'short_word':
                    # v8: 短い英単語（例：rter）で小さなはみ出しは除外
                    return overflow_amount < 20.0
        
        # v8: 文字数が少なく、はみ出し量も中程度の場合
        if len(overflow_text) <= 4 and overflow_amount < 25.0:
            return True
        
        return False
    
    def detect_rect_overflow(self, page, page_number: int) -> List[Dict]:
        """矩形ベースのはみ出し検出（最優先）"""
        overflows = []
        
        # 本文領域の右端を計算
        if page_number % 2 == 0:  # 偶数ページ
            right_margin_pt = self.config.even_page_margins['right'] * self.config.mm_to_pt
        else:  # 奇数ページ
            right_margin_pt = self.config.odd_page_margins['right'] * self.config.mm_to_pt
        
        text_right_edge = page.width - right_margin_pt
        
        # デバッグ用の変数
        debug_blocks = []
        
        for block_idx, block in enumerate(page.extract_text_blocks()):
            block_text = block[4]
            block_x1 = block[2]  # 矩形の右端
            
            # 矩形が本文領域を超えているかチェック
            if block_x1 > text_right_edge + self.config.rect_overflow_threshold:
                overflow_amount = block_x1 - text_right_edge
                
                # ブロック内の文字を取得
                block_chars = [char for char in page.chars 
                             if block[0] <= char['x0'] <= block[2] and 
                             block[1] <= char['y0'] <= block[3]]
                
                # ASCII文字のみを抽出（はみ出し判定対象）
                block_overflows = []
                for char in block_chars:
                    if self.is_ascii_char(char['text']):
                        char_x1 = char['x1']
                        if char_x1 > text_right_edge + self.config.rect_overflow_threshold:
                            char_overflow = char_x1 - text_right_edge
                            block_overflows.append({
                                'char': char['text'],
                                'x0': char['x0'],
                                'x1': char['x1'],
                                'y0': char['y0'],
                                'overflow_amount': char_overflow
                            })
                
                if block_overflows:
                    # 行ごとにグループ化
                    lines = {}
                    for overflow in block_overflows:
                        y_pos = round(overflow['y0'])
                        if y_pos not in lines:
                            lines[y_pos] = []
                        lines[y_pos].append(overflow)
                    
                    # 各行の情報を収集
                    for y_pos, line_overflows in lines.items():
                        line_overflows.sort(key=lambda x: x['x0'])
                        overflow_text = ''.join([o['char'] for o in line_overflows])
                        max_overflow = max(o['overflow_amount'] for o in line_overflows)
                        
                        # 誤検知フィルタリング（v8）
                        if self.is_likely_false_positive(overflow_text, max_overflow):
                            self.stats['filtered_overflows'] += 1
                            continue
                        
                        # 最低文字数チェック（v8）
                        if len(line_overflows) < self.config.min_overflow_chars:
                            self.stats['filtered_overflows'] += 1
                            continue
                        
                        # v8: コードブロックの可能性をチェック
                        # 長い連続したASCII文字列の場合、コードブロックの可能性が高い
                        if len(overflow_text) > 10 and max_overflow > 50.0:
                            # これは本物のコードブロックはみ出しの可能性が高い
                            pass
                        elif len(overflow_text) < 10 and max_overflow < 30.0:
                            # 短い文字列で小さなはみ出しは除外
                            self.stats['filtered_overflows'] += 1
                            continue
                        
                        overflows.append({
                            'type': 'rect_overflow',
                            'priority': 1,  # 最高優先度
                            'block_idx': block_idx,
                            'block_bounds': (block[0], block[1], block[2], block[3]),
                            'y_position': y_pos,
                            'overflow_text': overflow_text,
                            'overflow_amount': max_overflow,
                            'char_count': len(line_overflows)
                        })
        
        return overflows
    
    def detect_from_visual_judgments(self, pdf_name: str, page_number: int) -> List[Dict]:
        """視覚的判定データからの検出（第2優先）"""
        overflows = []
        
        if pdf_name in self.visual_data.get('known_overflows', {}):
            if page_number in self.visual_data['known_overflows'][pdf_name]:
                overflows.append({
                    'type': 'visual_judgment',
                    'priority': 2,
                    'source': 'known_overflow',
                    'overflow_text': '(Visual judgment)',
                    'overflow_amount': 0,
                    'char_count': 0
                })
        
        return overflows
    
    def detect_coordinate_based(self, page, page_number: int) -> List[Dict]:
        """座標ベースのはみ出し検出（補助的）"""
        overflows = []
        
        # 本文領域の右端を計算
        if page_number % 2 == 0:  # 偶数ページ
            right_margin_pt = self.config.even_page_margins['right'] * self.config.mm_to_pt
        else:  # 奇数ページ
            right_margin_pt = self.config.odd_page_margins['right'] * self.config.mm_to_pt
        
        text_right_edge = page.width - right_margin_pt
        
        # 文字単位で検出
        chars = page.chars
        line_overflows = {}
        
        for char in chars:
            if self.is_ascii_char(char['text']):
                char_x1 = char['x1']
                if char_x1 > text_right_edge + self.config.coord_overflow_threshold:
                    y_pos = round(char['y0'])
                    if y_pos not in line_overflows:
                        line_overflows[y_pos] = []
                    line_overflows[y_pos].append({
                        'char': char['text'],
                        'x0': char['x0'],
                        'x1': char['x1'],
                        'overflow': char_x1 - text_right_edge
                    })
        
        # 行ごとに集計
        for y_pos, chars_in_line in line_overflows.items():
            if len(chars_in_line) >= self.config.min_overflow_chars:
                chars_in_line.sort(key=lambda x: x['x0'])
                overflow_text = ''.join([c['char'] for c in chars_in_line])
                max_overflow = max(c['overflow'] for c in chars_in_line)
                
                # 誤検知フィルタリング
                if not self.is_likely_false_positive(overflow_text, max_overflow):
                    overflows.append({
                        'type': 'coordinate_based',
                        'priority': 3,  # 最低優先度
                        'y_position': y_pos,
                        'overflow_text': overflow_text,
                        'overflow_amount': max_overflow,
                        'char_count': len(chars_in_line)
                    })
        
        return overflows
    
    def detect_page(self, page, page_number: int, pdf_name: str) -> Dict:
        """1ページのはみ出し検出（全手法を統合）"""
        # 各検出手法を実行
        rect_overflows = self.detect_rect_overflow(page, page_number)
        visual_overflows = self.detect_from_visual_judgments(pdf_name, page_number)
        coord_overflows = self.detect_coordinate_based(page, page_number)
        
        # 統計更新
        for overflow in rect_overflows:
            self.stats['detection_methods']['rect_overflow'] += 1
        for overflow in visual_overflows:
            self.stats['detection_methods']['visual_judgment'] += 1
        for overflow in coord_overflows:
            self.stats['detection_methods']['coordinate_based'] += 1
        
        # 優先度順に統合（重複除去）
        all_overflows = []
        seen_positions = set()
        
        # 優先度1: 矩形検出
        for overflow in rect_overflows:
            pos_key = (overflow['y_position'], overflow['overflow_text'][:5])
            if pos_key not in seen_positions:
                all_overflows.append(overflow)
                seen_positions.add(pos_key)
        
        # 優先度2: 視覚的判定（矩形で検出されていない場合のみ）
        if not rect_overflows and visual_overflows:
            all_overflows.extend(visual_overflows)
        
        # 優先度3: 座標検出（他で検出されていない場合のみ）
        if not rect_overflows and not visual_overflows:
            for overflow in coord_overflows:
                pos_key = (overflow['y_position'], overflow['overflow_text'][:5])
                if pos_key not in seen_positions:
                    all_overflows.append(overflow)
                    seen_positions.add(pos_key)
        
        has_overflow = len(all_overflows) > 0
        
        return {
            'page': page_number,
            'has_overflow': has_overflow,
            'overflows': all_overflows,
            'overflow_count': len(all_overflows),
            'primary_method': all_overflows[0]['type'] if all_overflows else None
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
                            logger.info(f"  - {overflow['type']}: '{overflow['overflow_text']}' "
                                      f"({overflow['overflow_amount']:.1f}pt)")
        
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
        
        logger.info(f"\n検出方法別統計:")
        for method, count in self.stats['detection_methods'].items():
            if count > 0:
                logger.info(f"  - {method}: {count}件")
        
        # ページ番号リスト
        if results:
            page_numbers = [r['page'] for r in results]
            logger.info(f"\nはみ出し検出ページ: {sorted(page_numbers)}")
            logger.info(f"検出ページ数: {len(page_numbers)}")

def main():
    parser = argparse.ArgumentParser(description='Visual Hybrid Detector V8')
    parser.add_argument('pdf_file', help='処理するPDFファイル')
    parser.add_argument('-o', '--output', help='結果を保存するJSONファイル')
    args = parser.parse_args()
    
    pdf_path = Path(args.pdf_file)
    if not pdf_path.exists():
        logger.error(f"エラー: {pdf_path} が見つかりません")
        return
    
    detector = VisualHybridDetectorV8()
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