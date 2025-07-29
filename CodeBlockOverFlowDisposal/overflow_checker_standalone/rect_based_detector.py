#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
矩形基準視覚的検出器（スタンドアロン版）
コードブロック（グレー背景矩形）からのはみ出しを優先的に検出
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import pdfplumber
import logging
import os

# pdfplumberのデバッグログを抑制
logging.getLogger('pdfplumber').setLevel(logging.WARNING)
logging.getLogger('pdfminer').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class RectBasedOverflowDetector:
    """矩形基準の視覚的検出器"""
    
    def __init__(self):
        """初期化"""
        # 検出統計
        self.stats = {
            'total_pages': 0,
            'detected_pages': 0,
            'rect_overflow_detections': 0,  # 矩形からのはみ出し
            'page_overflow_detections': 0,   # ページからのはみ出し
            'excluded_characters': {}
        }
        
        # B5サイズ設定 (mm to points)
        self.b5_width_mm = 182
        self.b5_height_mm = 257
        self.mm_to_pt = 2.83465
        
        # マージン設定 (mm)
        self.odd_page_margins = {'top': 30, 'bottom': 20, 'left': 18, 'right': 10}
        self.even_page_margins = {'top': 30, 'bottom': 20, 'left': 10, 'right': 18}
    
    def is_ascii_printable(self, text: str) -> bool:
        """ASCII印字可能文字かどうかを判定"""
        return all(32 <= ord(char) < 127 for char in text)
    
    def detect_code_blocks(self, page) -> List[Dict]:
        """コードブロック（グレー背景矩形）を検出"""
        code_blocks = []
        
        for rect in page.rects:
            if rect.get('fill'):
                width = rect['x1'] - rect['x0']
                height = rect['y1'] - rect['y0']
                
                # コードブロックサイズの判定（小さすぎる矩形は除外）
                if width > 100 and height > 10:
                    code_blocks.append({
                        'x0': rect['x0'],
                        'y0': rect['y0'],
                        'x1': rect['x1'],
                        'y1': rect['y1'],
                        'width': width,
                        'height': height
                    })
        
        return code_blocks
    
    def detect_rect_overflow(self, page, page_number: int) -> List[Dict]:
        """矩形からのはみ出しを検出（最優先）"""
        overflows = []
        code_blocks = self.detect_code_blocks(page)
        
        if not code_blocks:
            return overflows
        
        # 各コードブロックに対してチェック
        for block_idx, block in enumerate(code_blocks):
            block_overflows = []
            
            # ブロック内の文字をチェック
            for char in page.chars:
                # 文字がブロック内に含まれるかチェック（Y座標）
                if block['y0'] <= char['y0'] <= block['y1']:
                    # ASCII文字のみ対象
                    if self.is_ascii_printable(char['text']):
                        # 文字の右端がブロックの右端を超えているか
                        if char['x1'] > block['x1']:
                            overflow_amount = char['x1'] - block['x1']
                            block_overflows.append({
                                'char': char['text'],
                                'x0': char['x0'],
                                'x1': char['x1'],
                                'y0': char['y0'],
                                'overflow_amount': overflow_amount
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
                    
                    overflows.append({
                        'type': 'rect_overflow',
                        'page': page_number,
                        'block_index': block_idx,
                        'y_position': y_pos,
                        'overflow_text': overflow_text,
                        'overflow_amount': max_overflow,
                        'block_bounds': {
                            'x0': block['x0'],
                            'x1': block['x1'],
                            'y0': block['y0'],
                            'y1': block['y1']
                        }
                    })
                    
                    self.stats['rect_overflow_detections'] += 1
        
        return overflows
    
    def detect_page_overflow(self, page, page_number: int) -> List[Dict]:
        """ページからのはみ出しを検出（英数字のみ）"""
        overflows = []
        
        # 本文領域の右端を計算
        if page_number % 2 == 0:  # 偶数ページ
            right_margin_pt = self.even_page_margins['right'] * self.mm_to_pt
        else:  # 奇数ページ
            right_margin_pt = self.odd_page_margins['right'] * self.mm_to_pt
        
        text_right_edge = page.width - right_margin_pt
        
        # 行ごとにテキストをグループ化
        lines = {}
        for char in page.chars:
            # ASCII文字のみ対象
            if self.is_ascii_printable(char['text']):
                # 文字の右端がページ本文領域を超えているか
                if char['x1'] > text_right_edge:
                    y_pos = round(char['y0'])
                    if y_pos not in lines:
                        lines[y_pos] = []
                    lines[y_pos].append({
                        'char': char['text'],
                        'x0': char['x0'],
                        'x1': char['x1'],
                        'overflow_amount': char['x1'] - text_right_edge
                    })
        
        # 各行の情報を収集
        for y_pos, line_chars in lines.items():
            line_chars.sort(key=lambda x: x['x0'])
            overflow_text = ''.join([c['char'] for c in line_chars])
            max_overflow = max(c['overflow_amount'] for c in line_chars)
            
            # 最小限のはみ出し量チェック（1pt以上）
            if max_overflow >= 1.0:
                overflows.append({
                    'type': 'page_overflow',
                    'page': page_number,
                    'y_position': y_pos,
                    'overflow_text': overflow_text,
                    'overflow_amount': max_overflow,
                    'text_right_edge': text_right_edge
                })
                
                self.stats['page_overflow_detections'] += 1
        
        return overflows
    
    def detect_file(self, pdf_path: Path) -> List[int]:
        """
        PDFファイルを解析して、溢れページを検出
        
        Args:
            pdf_path: 解析対象のPDFファイルパス
            
        Returns:
            溢れが検出されたページ番号のリスト（1-indexed）
        """
        overflow_pages = set()
        
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                self.stats['total_pages'] = len(pdf.pages)
                
                for page_idx, page in enumerate(pdf.pages):
                    page_number = page_idx + 1
                    
                    if page_idx % 10 == 0:
                        logger.info(f"処理中: {page_idx}/{len(pdf.pages)} ページ...")
                    
                    # 1. 矩形からのはみ出しを検出（優先）
                    rect_overflows = self.detect_rect_overflow(page, page_number)
                    
                    # 2. ページからのはみ出しを検出（英数字のみ）
                    page_overflows = self.detect_page_overflow(page, page_number)
                    
                    # いずれかのはみ出しがあればページを記録
                    if rect_overflows or page_overflows:
                        overflow_pages.add(page_number)
                        self.stats['detected_pages'] += 1
                        
                        # デバッグ情報
                        if rect_overflows:
                            logger.debug(f"ページ {page_number}: 矩形からのはみ出し {len(rect_overflows)}件")
                            for overflow in rect_overflows[:3]:  # 最初の3件を表示
                                logger.debug(f"  - {overflow['overflow_text'][:50]}... ({overflow['overflow_amount']:.1f}pt)")
                        
                        if page_overflows:
                            logger.debug(f"ページ {page_number}: ページからのはみ出し {len(page_overflows)}件")
                            for overflow in page_overflows[:3]:  # 最初の3件を表示
                                logger.debug(f"  - {overflow['overflow_text'][:50]}... ({overflow['overflow_amount']:.1f}pt)")
        
        except Exception as e:
            logger.error(f"PDF処理エラー: {e}")
            raise
        
        # 統計情報の出力
        logger.info(f"\n検出統計:")
        logger.info(f"  総ページ数: {self.stats['total_pages']}")
        logger.info(f"  検出ページ数: {self.stats['detected_pages']}")
        logger.info(f"  矩形からのはみ出し: {self.stats['rect_overflow_detections']}件")
        logger.info(f"  ページからのはみ出し: {self.stats['page_overflow_detections']}件")
        
        return sorted(list(overflow_pages))