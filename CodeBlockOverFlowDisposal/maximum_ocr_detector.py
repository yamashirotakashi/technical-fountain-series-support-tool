#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Maximum OCR Detector - OCR手法の限界まで改良した検出器
85%達成に向けた包括的改善実装
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

try:
    import numpy as np
except ImportError:
    print("numpy not available. Using pure Python implementation.")
    np = None

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class MaximumOCRDetector:
    """OCR手法の限界まで改良した検出器"""
    
    def __init__(self):
        self.mm_to_pt = 2.83465
        self.quality_metrics = {
            'total_pages_processed': 0,
            'total_detections': 0,
            'quality_warnings': []
        }
    
    def is_any_visible_char(self, char: str) -> bool:
        """全ての視覚的文字を検出対象にする（ASCII + 日本語 + 記号）"""
        if not char or len(char) == 0:
            return False
        
        code = ord(char[0])
        
        # 制御文字を除外（TAB, LF, CR以外）
        if code < 32 and code not in [9, 10, 13]:
            return False
        
        # 全ての印刷可能文字を対象
        if code >= 32 and code <= 126:  # ASCII印刷可能文字
            return True
        
        # 日本語文字範囲
        if (0x3040 <= code <= 0x309F or  # ひらがな
            0x30A0 <= code <= 0x30FF or  # カタカナ  
            0x4E00 <= code <= 0x9FAF or  # 漢字
            0xFF00 <= code <= 0xFFEF):   # 全角記号・文字
            return True
        
        # その他のUnicode文字（記号等）
        return code > 127
    
    def calculate_adaptive_margin(self, page, page_number: int) -> float:
        """ページ内容に基づく適応的マージン計算"""
        
        # 全ての視覚的文字の位置を取得
        x_positions = []
        for char in page.chars:
            if self.is_any_visible_char(char['text']):
                x_positions.append(char['x1'])
        
        if len(x_positions) < 10:  # データ不足時はデフォルト
            return self.get_default_margin_boundary(page, page_number)
        
        # 統計的手法で境界を決定
        x_positions.sort()
        
        # 90パーセンタイルを通常の右端とする
        p90_index = int(len(x_positions) * 0.90)
        p95_index = int(len(x_positions) * 0.95)
        
        p90 = x_positions[p90_index]
        p95 = x_positions[p95_index]
        
        # 動的バッファ計算
        margin_buffer = max(p95 - p90, 5.0)  # 最小5pt保証
        
        # 適応的境界
        adaptive_boundary = p90 + margin_buffer * 0.6
        
        # 品質メトリクス記録
        self.quality_metrics['adaptive_margin_info'] = {
            'p90': p90,
            'p95': p95,
            'buffer': margin_buffer,
            'boundary': adaptive_boundary,
            'sample_size': len(x_positions)
        }
        
        return adaptive_boundary
    
    def get_default_margin_boundary(self, page, page_number: int) -> float:
        """デフォルトマージン境界（従来方式）"""
        if page_number % 2 == 1:  # 奇数ページ
            right_margin_pt = 10 * self.mm_to_pt  # 28.3pt
        else:  # 偶数ページ
            right_margin_pt = 18 * self.mm_to_pt  # 51.0pt
        
        return page.width - right_margin_pt
    
    def detect_with_multiple_thresholds(self, page, page_number: int, boundary: float) -> List[Dict]:
        """多段階閾値での検出"""
        thresholds = [0.1, 0.05, 0.02, 0.01]
        all_results = []
        detected_lines = set()  # 重複回避用
        
        for threshold in thresholds:
            threshold_results = self.detect_at_threshold(page, page_number, boundary, threshold)
            
            # 重複除去して追加
            for result in threshold_results:
                line_key = result['y_position']
                if line_key not in detected_lines:
                    detected_lines.add(line_key)
                    result['detection_threshold'] = threshold
                    all_results.append(result)
        
        return all_results
    
    def detect_at_threshold(self, page, page_number: int, boundary: float, threshold: float) -> List[Dict]:
        """指定閾値での検出"""
        overflows = []
        line_overflows = {}
        
        for char in page.chars:
            if self.is_any_visible_char(char['text']):
                char_x1 = char['x1']
                if char_x1 > boundary + threshold:
                    y_pos = round(char['y0'])
                    overflow_amount = char_x1 - boundary
                    
                    if y_pos not in line_overflows:
                        line_overflows[y_pos] = []
                    
                    line_overflows[y_pos].append({
                        'char': char['text'],
                        'x1': char['x1'],
                        'overflow': overflow_amount
                    })
        
        # 行ごとに集計
        for y_pos, chars_in_line in line_overflows.items():
            chars_in_line.sort(key=lambda x: x['x1'])
            overflow_text = ''.join([c['char'] for c in chars_in_line])
            max_overflow = max(c['overflow'] for c in chars_in_line)
            
            # 基本的な品質フィルタ
            if not self.is_likely_noise(overflow_text, max_overflow):
                overflows.append({
                    'y_position': y_pos,
                    'overflow_text': overflow_text,
                    'overflow_amount': max_overflow,
                    'char_count': len(chars_in_line)
                })
        
        return overflows
    
    def detect_image_elements(self, page, boundary: float) -> List[Dict]:
        """画像・図表要素のはみ出し検出"""
        image_overflows = []
        
        # 画像要素の検出
        for image in getattr(page, 'images', []):
            if image['x1'] > boundary:
                image_overflows.append({
                    'type': 'image',
                    'y_position': round(image['y0']),
                    'overflow_amount': image['x1'] - boundary,
                    'element_size': (image['width'], image['height']),
                    'overflow_text': f'[IMAGE:{image["width"]}x{image["height"]}]'
                })
        
        # 線・図表要素の検出
        for line in getattr(page, 'lines', []):
            if line['x1'] > boundary:
                image_overflows.append({
                    'type': 'line',
                    'y_position': round(line['y0']),
                    'overflow_amount': line['x1'] - boundary,
                    'element_size': (line.get('width', 0), line.get('height', 0)),
                    'overflow_text': f'[LINE]'
                })
        
        # 矩形要素の検出
        for rect in getattr(page, 'rects', []):
            if rect['x1'] > boundary:
                image_overflows.append({
                    'type': 'rect',
                    'y_position': round(rect['y0']),
                    'overflow_amount': rect['x1'] - boundary,
                    'element_size': (rect['width'], rect['height']),
                    'overflow_text': f'[RECT:{rect["width"]:.1f}x{rect["height"]:.1f}]'
                })
        
        return image_overflows
    
    def detect_statistical_outliers(self, page, boundary: float) -> List[Dict]:
        """統計的外れ値によるはみ出し検出"""
        
        # 全文字のX位置を収集
        x_positions = []
        char_data = []
        
        for char in page.chars:
            if self.is_any_visible_char(char['text']):
                x_positions.append(char['x1'])
                char_data.append({
                    'char': char['text'],
                    'x1': char['x1'],
                    'y0': char['y0']
                })
        
        if len(x_positions) < 20:  # データ不足
            return []
        
        # 統計的外れ値検出
        mean_x = statistics.mean(x_positions)
        std_x = statistics.stdev(x_positions)
        
        # 3σを超える外れ値かつboundary超過を検出
        outlier_threshold = mean_x + 2.5 * std_x
        boundary_threshold = max(boundary, outlier_threshold)
        
        outliers = []
        outlier_lines = {}
        
        for char_info in char_data:
            if char_info['x1'] > boundary_threshold:
                y_pos = round(char_info['y0'])
                if y_pos not in outlier_lines:
                    outlier_lines[y_pos] = []
                outlier_lines[y_pos].append(char_info)
        
        # 外れ値行を集計
        for y_pos, chars_in_line in outlier_lines.items():
            chars_in_line.sort(key=lambda x: x['x1'])
            overflow_text = ''.join([c['char'] for c in chars_in_line])
            max_overflow = max(c['x1'] for c in chars_in_line) - boundary
            
            if max_overflow > 0.02:  # 最小閾値
                outliers.append({
                    'y_position': y_pos,
                    'overflow_text': overflow_text,
                    'overflow_amount': max_overflow,
                    'char_count': len(chars_in_line),
                    'detection_method': 'statistical_outlier'
                })
        
        return outliers
    
    def is_likely_noise(self, text: str, overflow_amount: float) -> bool:
        """ノイズ・誤検知の判定"""
        text_stripped = text.strip()
        
        # 極小はみ出し（測定誤差レベル）
        if overflow_amount < 0.02:
            return True
        
        # 極短テキスト
        if len(text_stripped) <= 1:
            return True
        
        # PowerShell特有パターン（既存ロジック）
        if '::' in text_stripped and len(text_stripped) > 10:
            return True
        
        if '.ps1' in text_stripped:
            return True
        
        # 記号のみの短いテキスト
        if len(text_stripped) <= 2 and all(not c.isalnum() for c in text_stripped):
            return True
        
        return False
    
    def merge_and_deduplicate(self, *result_lists) -> List[Dict]:
        """複数の検出結果をマージ・重複除去"""
        all_results = []
        for result_list in result_lists:
            all_results.extend(result_list)
        
        # Y座標による重複除去
        unique_results = {}
        for result in all_results:
            y_key = result['y_position']
            if y_key not in unique_results:
                unique_results[y_key] = result
            else:
                # より多くの情報を持つ結果を保持
                if len(result.get('overflow_text', '')) > len(unique_results[y_key].get('overflow_text', '')):
                    unique_results[y_key] = result
        
        return list(unique_results.values())
    
    def detect_comprehensive(self, page, page_number: int) -> List[Dict]:
        """包括的検出の実行"""
        
        # 1. 適応的マージン計算
        adaptive_boundary = self.calculate_adaptive_margin(page, page_number)
        
        # 2. 多段階閾値検出
        threshold_results = self.detect_with_multiple_thresholds(page, page_number, adaptive_boundary)
        
        # 3. 画像要素検出
        image_results = self.detect_image_elements(page, adaptive_boundary)
        
        # 4. 統計的外れ値検出
        statistical_results = self.detect_statistical_outliers(page, adaptive_boundary)
        
        # 5. 結果統合・重複除去
        final_results = self.merge_and_deduplicate(threshold_results, image_results, statistical_results)
        
        # 6. 品質メトリクス更新
        self.quality_metrics['total_detections'] += len(final_results)
        
        return final_results
    
    def process_pdf_comprehensive(self, pdf_path: Path) -> List[Dict]:
        """PDF全体の包括的処理"""
        results = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                self.quality_metrics['total_pages_processed'] = total_pages
                
                logger.info(f"\n{'='*80}")
                logger.info(f"Maximum OCR Detection: {pdf_path.name} ({total_pages}ページ)")
                logger.info(f"{'='*80}")
                
                for i, page in enumerate(pdf.pages):
                    page_number = i + 1
                    page_results = self.detect_comprehensive(page, page_number)
                    
                    if page_results:
                        result = {
                            'page': page_number,
                            'overflows': page_results,
                            'overflow_count': len(page_results)
                        }
                        results.append(result)
                        
                        logger.info(f"\nPage {page_number}: {len(page_results)}個の改良検出")
                        for overflow in page_results:
                            method = overflow.get('detection_method', 'multi_threshold')
                            threshold = overflow.get('detection_threshold', 'N/A')
                            logger.info(f"  - '{overflow['overflow_text'][:50]}' "
                                      f"({overflow['overflow_amount']:.2f}pt, {method}, th:{threshold})")
        
        except Exception as e:
            logger.error(f"エラー: {pdf_path} - {str(e)}")
            self.quality_metrics['quality_warnings'].append(f"Processing error: {str(e)}")
        
        return results
    
    def print_quality_report(self, results: List[Dict], pdf_path: Path):
        """品質レポートの出力"""
        logger.info(f"\n{'='*80}")
        logger.info(f"Maximum OCR Quality Report: {pdf_path.name}")
        logger.info(f"{'='*80}")
        
        total_detections = sum(r['overflow_count'] for r in results)
        pages_with_detections = len(results)
        
        logger.info(f"処理ページ数: {self.quality_metrics['total_pages_processed']}")
        logger.info(f"検出ページ数: {pages_with_detections}")
        logger.info(f"総検出数: {total_detections}")
        
        if 'adaptive_margin_info' in self.quality_metrics:
            margin_info = self.quality_metrics['adaptive_margin_info']
            logger.info(f"\n適応的マージン情報:")
            logger.info(f"  - 90%ライン: {margin_info['p90']:.1f}pt")
            logger.info(f"  - 95%ライン: {margin_info['p95']:.1f}pt")
            logger.info(f"  - 動的境界: {margin_info['boundary']:.1f}pt")
            logger.info(f"  - サンプル数: {margin_info['sample_size']}")
        
        if self.quality_metrics['quality_warnings']:
            logger.info(f"\n品質警告:")
            for warning in self.quality_metrics['quality_warnings']:
                logger.info(f"  ⚠️ {warning}")
        
        # 検出詳細
        if results:
            detected_pages = [r['page'] for r in results]
            logger.info(f"\n検出ページリスト: {sorted(detected_pages)}")


def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Maximum OCR Detector')
    parser.add_argument('pdf_files', nargs='+', help='処理するPDFファイル')
    args = parser.parse_args()
    
    detector = MaximumOCRDetector()
    
    for pdf_file in args.pdf_files:
        pdf_path = Path(pdf_file)
        if not pdf_path.exists():
            logger.error(f"ファイルが見つかりません: {pdf_path}")
            continue
        
        results = detector.process_pdf_comprehensive(pdf_path)
        detector.print_quality_report(results, pdf_path)


if __name__ == "__main__":
    main()