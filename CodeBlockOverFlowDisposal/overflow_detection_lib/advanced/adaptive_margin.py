#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Adaptive margin calculation for Phase 2
動的マージン計算モジュール - ページレイアウトに応じた精密なマージン調整
"""

import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import statistics

logger = logging.getLogger(__name__)

class AdaptiveMarginCalculator:
    """
    動的マージン計算クラス
    ページレイアウトを解析し、最適なマージンを計算
    """
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.mm_to_pt = 2.83465
        
        # レイアウト検出の閾値
        self.header_detection_threshold = 50.0  # ヘッダー検出閾値 (pt)
        self.footer_detection_threshold = 50.0  # フッター検出閾値 (pt)
        self.column_detection_min_gap = 20.0    # 段組み検出の最小間隔 (pt)
        
        # キャッシュ
        self._layout_cache = {}
    
    def calculate_adaptive_margin(self, page, page_num: int) -> Dict[str, float]:
        """
        ページレイアウトに応じた動的マージン計算
        
        Args:
            page: pdfplumber page object
            page_num: ページ番号
            
        Returns:
            Dict: 計算されたマージン情報
                - right_margin_pt: 右マージン (pt)
                - confidence: 計算の信頼度 (0.0-1.0)
                - layout_type: 検出されたレイアウトタイプ
                - adjustments: 適用された調整項目
        """
        page_id = f"page_{page_num}"
        
        # キャッシュチェック
        if page_id in self._layout_cache:
            return self._layout_cache[page_id]
        
        # 基本マージン取得
        base_margin = self._get_base_margin(page_num)
        
        # レイアウト解析
        layout_info = self._analyze_page_layout(page)
        
        # マージン調整計算
        adjusted_margin = self._calculate_margin_adjustments(
            base_margin, layout_info, page
        )
        
        result = {
            'right_margin_pt': adjusted_margin,
            'confidence': layout_info['confidence'],
            'layout_type': layout_info['type'],
            'adjustments': layout_info['adjustments'],
            'base_margin_pt': base_margin
        }
        
        # キャッシュに保存
        self._layout_cache[page_id] = result
        
        return result
    
    def _get_base_margin(self, page_num: int) -> float:
        """基本マージンの取得"""
        if self.config_manager:
            return self.config_manager.get_margin_for_page(page_num)
        
        # デフォルト値
        if page_num % 2 == 1:  # 奇数ページ
            return 10 * self.mm_to_pt  # 28.3pt
        else:  # 偶数ページ
            return 18 * self.mm_to_pt  # 51.0pt
    
    def _analyze_page_layout(self, page) -> Dict:
        """
        ページレイアウトの詳細解析
        
        Returns:
            Dict: レイアウト情報
                - type: single_column, two_column, code_heavy, mixed
                - confidence: 解析の信頼度
                - adjustments: 推奨調整
                - details: 詳細情報
        """
        page_width = page.width
        page_height = page.height
        
        # 文字配置解析
        chars = page.chars
        text_positions = self._extract_text_positions(chars)
        
        # レイアウトパターン検出
        layout_patterns = {
            'single_column': self._detect_single_column(text_positions, page_width),
            'two_column': self._detect_two_column(text_positions, page_width),
            'code_heavy': self._detect_code_heavy_layout(chars),
            'header_footer': self._detect_header_footer(text_positions, page_height)
        }
        
        # 最も確からしいレイアウト選択
        primary_layout = max(layout_patterns.items(), key=lambda x: x[1]['confidence'])
        
        return {
            'type': primary_layout[0],
            'confidence': primary_layout[1]['confidence'],
            'adjustments': primary_layout[1]['adjustments'],
            'details': layout_patterns,
            'text_distribution': self._analyze_text_distribution(text_positions, page_width)
        }
    
    def _extract_text_positions(self, chars: List[Dict]) -> List[Dict]:
        """文字位置情報の抽出と整理"""
        positions = []
        for char in chars:
            if char.get('text', '').strip():
                positions.append({
                    'x': char.get('x0', 0),
                    'y': char.get('y0', 0),
                    'text': char.get('text', ''),
                    'width': char.get('x1', 0) - char.get('x0', 0),
                    'height': char.get('y1', 0) - char.get('y0', 0)
                })
        return positions
    
    def _detect_single_column(self, positions: List[Dict], page_width: float) -> Dict:
        """単一段組みレイアウトの検出"""
        if not positions:
            return {'confidence': 0.0, 'adjustments': []}
        
        # X座標の分布を解析
        x_coords = [pos['x'] for pos in positions]
        
        # 95%の文字が左寄せされている場合は単一段組み
        left_boundary = page_width * 0.1  # 10%位置
        right_boundary = page_width * 0.8  # 80%位置
        
        left_aligned_count = sum(1 for x in x_coords if x < left_boundary + 50)
        total_count = len(x_coords)
        
        if total_count == 0:
            return {'confidence': 0.0, 'adjustments': []}
        
        left_ratio = left_aligned_count / total_count
        
        confidence = min(left_ratio * 1.2, 1.0)  # 最大1.0
        
        adjustments = []
        if confidence > 0.8:
            adjustments.append('standard_margin')  # 標準マージン適用
        
        return {
            'confidence': confidence,
            'adjustments': adjustments,
            'left_ratio': left_ratio
        }
    
    def _detect_two_column(self, positions: List[Dict], page_width: float) -> Dict:
        """2段組みレイアウトの検出"""
        if not positions:
            return {'confidence': 0.0, 'adjustments': []}
        
        # X座標でクラスタリング
        x_coords = [pos['x'] for pos in positions]
        x_coords.sort()
        
        # 中央付近の大きな空白を検出
        center_region = (page_width * 0.3, page_width * 0.7)
        gaps = []
        
        for i in range(len(x_coords) - 1):
            gap_size = x_coords[i + 1] - x_coords[i]
            gap_center = (x_coords[i] + x_coords[i + 1]) / 2
            
            if (center_region[0] < gap_center < center_region[1] and 
                gap_size > self.column_detection_min_gap):
                gaps.append(gap_size)
        
        confidence = 0.0
        adjustments = []
        
        if gaps:
            max_gap = max(gaps)
            if max_gap > self.column_detection_min_gap * 2:
                confidence = min(max_gap / (page_width * 0.1), 1.0)
                adjustments.append('narrow_margin')  # 狭いマージン適用
        
        return {
            'confidence': confidence,
            'adjustments': adjustments,
            'max_gap': max(gaps) if gaps else 0
        }
    
    def _detect_code_heavy_layout(self, chars: List[Dict]) -> Dict:
        """コード中心レイアウトの検出"""
        if not chars:
            return {'confidence': 0.0, 'adjustments': []}
        
        code_indicators = {'{', '}', '(', ')', '[', ']', ';', ':', '=', '<', '>'}
        monospace_indicators = {'|', '_', '`', '#'}
        
        code_char_count = 0
        monospace_count = 0
        total_chars = 0
        
        for char in chars:
            text = char.get('text', '')
            if text.strip():
                total_chars += 1
                if text in code_indicators:
                    code_char_count += 1
                if text in monospace_indicators:
                    monospace_count += 1
        
        if total_chars == 0:
            return {'confidence': 0.0, 'adjustments': []}
        
        code_ratio = code_char_count / total_chars
        monospace_ratio = monospace_count / total_chars
        
        # コードが多い場合は特別なマージン調整
        confidence = min((code_ratio + monospace_ratio) * 2, 1.0)
        
        adjustments = []
        if confidence > 0.6:
            adjustments.append('code_margin')  # コード用マージン
        
        return {
            'confidence': confidence,
            'adjustments': adjustments,
            'code_ratio': code_ratio,
            'monospace_ratio': monospace_ratio
        }
    
    def _detect_header_footer(self, positions: List[Dict], page_height: float) -> Dict:
        """ヘッダー・フッター検出"""
        if not positions:
            return {'confidence': 0.0, 'adjustments': []}
        
        y_coords = [pos['y'] for pos in positions]
        
        # ページ上部・下部の文字数カウント
        header_count = sum(1 for y in y_coords if y > page_height - self.header_detection_threshold)
        footer_count = sum(1 for y in y_coords if y < self.footer_detection_threshold)
        total_count = len(y_coords)
        
        if total_count == 0:
            return {'confidence': 0.0, 'adjustments': []}
        
        header_ratio = header_count / total_count
        footer_ratio = footer_count / total_count
        
        confidence = min((header_ratio + footer_ratio) * 5, 1.0)
        
        adjustments = []
        if header_count > 0:
            adjustments.append('header_margin')
        if footer_count > 0:
            adjustments.append('footer_margin')
        
        return {
            'confidence': confidence,
            'adjustments': adjustments,
            'header_ratio': header_ratio,
            'footer_ratio': footer_ratio
        }
    
    def _analyze_text_distribution(self, positions: List[Dict], page_width: float) -> Dict:
        """テキスト分布の解析"""
        if not positions:
            return {'right_edge_density': 0.0, 'density_score': 0.0}
        
        # 右端近くのテキスト密度を計算
        right_region_start = page_width * 0.8
        right_edge_chars = [pos for pos in positions if pos['x'] > right_region_start]
        
        right_edge_density = len(right_edge_chars) / len(positions)
        
        # X座標の標準偏差（レイアウトの整然性指標）
        x_coords = [pos['x'] for pos in positions]
        density_score = 1.0 / (1.0 + statistics.stdev(x_coords) / page_width)
        
        return {
            'right_edge_density': right_edge_density,
            'density_score': density_score,
            'total_chars': len(positions)
        }
    
    def _calculate_margin_adjustments(self, base_margin: float, layout_info: Dict, page) -> float:
        """
        レイアウト情報に基づくマージン調整の計算
        
        Args:
            base_margin: 基本マージン
            layout_info: レイアウト解析結果
            page: ページオブジェクト
            
        Returns:
            float: 調整後マージン
        """
        adjusted_margin = base_margin
        adjustments = layout_info.get('adjustments', [])
        
        # 調整ファクター
        adjustment_factors = {
            'standard_margin': 1.0,      # 標準（変更なし）
            'narrow_margin': 0.8,        # 2段組み用：20%狭く
            'code_margin': 1.1,          # コード用：10%広く
            'header_margin': 0.95,       # ヘッダー考慮：5%狭く
            'footer_margin': 0.95,       # フッター考慮：5%狭く
        }
        
        # 複数調整の適用
        total_factor = 1.0
        for adjustment in adjustments:
            if adjustment in adjustment_factors:
                total_factor *= adjustment_factors[adjustment]
        
        adjusted_margin *= total_factor
        
        # レイアウトタイプ別の追加調整
        layout_type = layout_info.get('type', 'single_column')
        confidence = layout_info.get('confidence', 0.5)
        
        if layout_type == 'two_column' and confidence > 0.7:
            # 2段組みで高い信頼度の場合はさらに調整
            adjusted_margin *= 0.9
        elif layout_type == 'code_heavy' and confidence > 0.8:
            # コード中心で高い信頼度の場合は拡張
            adjusted_margin *= 1.15
        
        # 右端テキスト密度による微調整
        text_dist = layout_info.get('text_distribution', {})
        right_density = text_dist.get('right_edge_density', 0.0)
        
        if right_density > 0.1:  # 右端にテキストが多い場合
            adjusted_margin *= (1.0 + right_density * 0.2)
        
        # 安全範囲での制限
        min_margin = base_margin * 0.7  # 最小30%削減まで
        max_margin = base_margin * 1.3  # 最大30%拡張まで
        
        adjusted_margin = max(min_margin, min(adjusted_margin, max_margin))
        
        return adjusted_margin
    
    def get_margin_info(self, page, page_num: int) -> Dict:
        """マージン情報の詳細取得（デバッグ用）"""
        result = self.calculate_adaptive_margin(page, page_num)
        
        base_margin = result['base_margin_pt']
        adjusted_margin = result['right_margin_pt']
        adjustment_ratio = adjusted_margin / base_margin if base_margin > 0 else 1.0
        
        return {
            **result,
            'adjustment_ratio': adjustment_ratio,
            'adjustment_pt': adjusted_margin - base_margin,
            'margin_mm': adjusted_margin / self.mm_to_pt
        }
    
    def clear_cache(self):
        """キャッシュクリア"""
        self._layout_cache.clear()
        logger.info("Adaptive margin cache cleared")