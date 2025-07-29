#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Visual Hybrid Detector V9 - Balanced detection without hardcoding
Pure algorithmic approach with appropriate filtering
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
    
    # 検出閾値（v9: バランスのとれた値）
    rect_overflow_threshold: float = 1.0  # 矩形検出の閾値
    coord_overflow_threshold: float = 2.0  # 座標検出の閾値
    min_overflow_chars: int = 2  # 最低2文字以上
    
    # コードブロック検出パラメータ
    min_code_block_width: float = 100
    min_code_block_height: float = 10
    
    def __post_init__(self):
        if self.odd_page_margins is None:
            self.odd_page_margins = {'top': 30, 'bottom': 20, 'left': 18, 'right': 10}
        if self.even_page_margins is None:
            self.even_page_margins = {'top': 30, 'bottom': 20, 'left': 10, 'right': 18}

class VisualHybridDetectorV9:
    """視覚的矩形検出を第1優先、座標検知を補助とするハイブリッド検出器 v9"""
    
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
        if not char or len(char) == 0:
            return False
        return ord(char[0]) < 128
    
    def detect_code_blocks(self, page) -> List[Dict]:
        """コードブロック（グレー背景矩形）を検出"""
        code_blocks = []
        
        for rect in page.rects:
            if rect.get('fill'):
                width = rect['x1'] - rect['x0']
                height = rect['y1'] - rect['y0']
                
                if (width > self.config.min_code_block_width and 
                    height > self.config.min_code_block_height):
                    code_blocks.append({
                        'x0': rect['x0'],
                        'y0': rect['y0'],
                        'x1': rect['x1'],
                        'y1': rect['y1'],
                        'width': width,
                        'height': height
                    })
        
        return code_blocks
    
    def is_likely_false_positive(self, overflow_text: str, overflow_amount: float) -> bool:
        """誤検知の可能性が高いパターンかどうかを判定（v9: 適度なフィルタリング）"""
        # 非常に小さなはみ出し（2pt未満）
        if overflow_amount < 2.0:
            return True
        
        # 特殊パターンのチェック
        # 閉じ括弧のみ
        if re.match(r'^[\)\]\}]+$', overflow_text):
            return overflow_amount < 10.0
        
        # 引用符と閉じ括弧
        if re.match(r'^["\)]+$', overflow_text):
            return overflow_amount < 10.0
        
        # 単一文字
        if len(overflow_text) == 1:
            return overflow_amount < 5.0
        
        # 句読点のみ
        if re.match(r'^[,\.\;\:\!\?]+$', overflow_text):
            return overflow_amount < 5.0
        
        # v9: 短い断片的な文字列（例: "rter", "l.ps1"など）
        # ただし、はみ出し量が大きい場合は検出する
        if len(overflow_text) <= 4 and overflow_amount < 20.0:
            # プログラミング関連の拡張子やパターンは除外しない
            if re.search(r'\.(ps1|py|js|cpp|hpp|txt|md|sh|bat)$', overflow_text, re.IGNORECASE):
                return False
            if re.search(r'Protocol|ecurityProtocol|StorageClass', overflow_text, re.IGNORECASE):
                return False
            return True
        
        return False
    
    def detect_rect_overflow(self, page, page_number: int) -> List[Dict]:
        """矩形ベースのはみ出し検出（最優先）"""
        overflows = []
        code_blocks = self.detect_code_blocks(page)
        
        if not code_blocks:
            return overflows
        
        # 各コードブロックに対してチェック
        for block_idx, block in enumerate(code_blocks):
            block_overflows = self.check_block_overflow(page, block, page_number)
            
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
                    
                    # 誤検知フィルタリング（v9）
                    if self.is_likely_false_positive(overflow_text, max_overflow):
                        self.stats['filtered_overflows'] += 1
                        continue
                    
                    # 最低文字数チェック（v9）
                    if len(line_overflows) < self.config.min_overflow_chars:
                        self.stats['filtered_overflows'] += 1
                        continue
                    
                    overflows.append({
                        'type': 'rect_overflow',
                        'priority': 1,  # 最高優先度
                        'block_idx': block_idx,
                        'block_bounds': (block['x0'], block['y0'], block['x1'], block['y1']),
                        'y_position': y_pos,
                        'overflow_text': overflow_text,
                        'overflow_amount': max_overflow,
                        'char_count': len(line_overflows)
                    })
        
        return overflows
    
    def check_block_overflow(self, page, block: Dict, page_number: int) -> List[Dict]:
        """特定のブロック内のはみ出しをチェック"""
        # 本文領域の右端を計算
        if page_number % 2 == 0:  # 偶数ページ
            right_margin_pt = self.config.even_page_margins['right'] * self.config.mm_to_pt
        else:  # 奇数ページ
            right_margin_pt = self.config.odd_page_margins['right'] * self.config.mm_to_pt
        
        text_right_edge = page.width - right_margin_pt
        
        # ブロック内の文字を取得
        block_chars = [char for char in page.chars 
                      if block['x0'] <= char['x0'] <= block['x1'] and 
                      block['y0'] <= char['y0'] <= block['y1']]
        
        # ASCII文字のみを抽出（はみ出し判定対象）
        overflows = []
        for char in block_chars:
            if self.is_ascii_char(char['text']):
                char_x1 = char['x1']
                if char_x1 > text_right_edge + self.config.rect_overflow_threshold:
                    char_overflow = char_x1 - text_right_edge
                    overflows.append({
                        'char': char['text'],
                        'x0': char['x0'],
                        'x1': char['x1'],
                        'y0': char['y0'],
                        'overflow_amount': char_overflow
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
    parser = argparse.ArgumentParser(description='Visual Hybrid Detector V9')
    parser.add_argument('pdf_file', help='処理するPDFファイル')
    parser.add_argument('-o', '--output', help='結果を保存するJSONファイル')
    args = parser.parse_args()
    
    pdf_path = Path(args.pdf_file)
    if not pdf_path.exists():
        logger.error(f"エラー: {pdf_path} が見つかりません")
        return
    
    detector = VisualHybridDetectorV9()
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