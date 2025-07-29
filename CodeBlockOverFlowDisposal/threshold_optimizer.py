#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Threshold Optimizer - 閾値最適化実験ツール
sample4.pdf Page 38の見逃し問題を解決し、78%目標達成を目指す
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple
import sys

try:
    import pdfplumber
except ImportError:
    print("pdfplumber not available.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class ThresholdOptimizer:
    """閾値最適化実験"""
    
    def __init__(self):
        self.mm_to_pt = 2.83465
        
        # Ground Truth
        self.ground_truth = {
            'sample.pdf': [48],
            'sample2.pdf': [128, 129],
            'sample3.pdf': [13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 78, 80, 106, 115, 122, 124],
            'sample4.pdf': [27, 30, 38, 73, 75, 76],
            'sample5.pdf': [128, 129]
        }
        
        # テスト閾値
        self.test_thresholds = [0.1, 0.05, 0.02, 0.01]
    
    def is_ascii_char(self, char: str) -> bool:
        """ASCII文字判定"""
        if not char or len(char) == 0:
            return False
        return ord(char[0]) < 128
    
    def is_likely_false_positive_relaxed(self, overflow_text: str, overflow_amount: float, y_position: float, threshold: float) -> bool:
        """緩和された誤検知フィルタリング"""
        text_content = overflow_text.strip()
        text_length = len(overflow_text)
        
        # 1. 極めて小さいはみ出し量（閾値に応じて調整）
        min_threshold = max(0.2, threshold * 2)  # 閾値の2倍または0.2ptの大きい方
        if overflow_amount <= min_threshold:
            return True
        
        # 2. (cid:X)文字を含む場合
        if '(cid:' in text_content:
            return True
        
        # 3. ページ番号のみの場合
        if text_content.isdigit() and len(text_content) <= 3:
            return True
        
        # 4. 日本語文字のみの場合
        if all(ord(c) > 127 for c in text_content if c.isprintable()):
            return True
        
        # 5. PowerShell特有の文字パターン
        if '::' in text_content and text_length > 10:
            return True
        
        # 6. .ps1拡張子
        if '.ps1' in text_content:
            return True
        
        # 7. 極端に短いテキストかつ記号のみ
        if text_length <= 2 and all(not c.isalnum() for c in text_content):
            return True
        
        # 8. 画像・線要素タグ
        if text_content.startswith('[IMAGE:') or text_content.startswith('[LINE]') or text_content.startswith('[RECT:'):
            return True
        
        # 9. 目次・索引特有のパターン
        if '……' in text_content or '・・・' in text_content:
            return True
        
        return False
    
    def detect_overflows_with_threshold(self, page, page_number: int, threshold: float) -> List[Dict]:
        """指定閾値でのはみ出し検出"""
        overflows = []
        
        # マージン計算
        if page_number % 2 == 1:  # 奇数ページ
            right_margin_pt = 10 * self.mm_to_pt
        else:  # 偶数ページ
            right_margin_pt = 18 * self.mm_to_pt
        
        text_right_edge = page.width - right_margin_pt
        
        # 行ごとのはみ出し文字収集
        line_overflows = {}
        
        for char in page.chars:
            if self.is_ascii_char(char['text']):
                char_x1 = char['x1']
                if char_x1 > text_right_edge + threshold:
                    y_pos = round(char['y0'])
                    overflow_amount = char_x1 - text_right_edge
                    
                    if y_pos not in line_overflows:
                        line_overflows[y_pos] = []
                    
                    line_overflows[y_pos].append({
                        'char': char['text'],
                        'x1': char['x1'],
                        'overflow': overflow_amount
                    })
        
        # 行ごとに集計し、緩和されたフィルタリング適用
        for y_pos, chars_in_line in line_overflows.items():
            chars_in_line.sort(key=lambda x: x['x1'])
            overflow_text = ''.join([c['char'] for c in chars_in_line])
            max_overflow = max(c['overflow'] for c in chars_in_line)
            
            # 緩和されたフィルタリング適用
            if not self.is_likely_false_positive_relaxed(overflow_text, max_overflow, y_pos, threshold):
                overflows.append({
                    'y_position': y_pos,
                    'overflow_text': overflow_text,
                    'overflow_amount': max_overflow,
                    'char_count': len(chars_in_line)
                })
        
        return overflows
    
    def test_threshold_on_pdf(self, pdf_path: Path, threshold: float) -> List[int]:
        """指定閾値でPDF全体をテスト"""
        detected_pages = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_number = i + 1
                    overflows = self.detect_overflows_with_threshold(page, page_number, threshold)
                    
                    if overflows:
                        detected_pages.append(page_number)
        
        except Exception as e:
            logger.error(f"エラー: {pdf_path} - {str(e)}")
        
        return detected_pages
    
    def calculate_metrics(self, detected_results: Dict[str, List[int]]) -> Dict:
        """性能メトリクス計算"""
        total_expected = sum(len(pages) for pages in self.ground_truth.values())
        total_detected = sum(len(pages) for pages in detected_results.values())
        
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        for pdf_file, expected in self.ground_truth.items():
            detected = detected_results.get(pdf_file, [])
            
            tp = len([p for p in detected if p in expected])
            fp = len([p for p in detected if p not in expected])
            fn = len([p for p in expected if p not in detected])
            
            true_positives += tp
            false_positives += fp
            false_negatives += fn
        
        recall = true_positives / total_expected if total_expected > 0 else 0
        precision = true_positives / total_detected if total_detected > 0 else 1.0
        
        return {
            'total_expected': total_expected,
            'total_detected': total_detected,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'recall': recall,
            'precision': precision
        }
    
    def run_threshold_optimization(self):
        """閾値最適化実験の実行"""
        logger.info("=" * 90)
        logger.info("閾値最適化実験 - 78%目標達成への道筋")
        logger.info("=" * 90)
        
        pdf_files = ['sample.pdf', 'sample2.pdf', 'sample3.pdf', 'sample4.pdf', 'sample5.pdf']
        results_by_threshold = {}
        
        for threshold in self.test_thresholds:
            logger.info(f"\n📊 閾値 {threshold}pt での実験:")
            logger.info("-" * 60)
            
            threshold_results = {}
            
            for pdf_file in pdf_files:
                pdf_path = Path(pdf_file)
                if not pdf_path.exists():
                    logger.info(f"❌ {pdf_file}: ファイルが見つかりません")
                    continue
                
                detected_pages = self.test_threshold_on_pdf(pdf_path, threshold)
                threshold_results[pdf_file] = detected_pages
                
                expected = self.ground_truth[pdf_file]
                tp = len([p for p in detected_pages if p in expected])
                fp = len([p for p in detected_pages if p not in expected])
                fn = len([p for p in expected if p not in detected_pages])
                
                logger.info(f"{pdf_file}: {len(detected_pages)}検出 (TP:{tp}, FP:{fp}, FN:{fn})")
                
                # 新規検出の表示
                if threshold == 0.1:  # ベースライン比較
                    baseline_results = {
                        'sample.pdf': [],
                        'sample2.pdf': [],
                        'sample3.pdf': [13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 75, 78, 79, 115, 121, 122, 124, 125],
                        'sample4.pdf': [27, 30, 73, 76],
                        'sample5.pdf': []
                    }
                    baseline = baseline_results.get(pdf_file, [])
                else:
                    baseline = results_by_threshold[0.1].get(pdf_file, [])
                
                new_detections = [p for p in detected_pages if p not in baseline]
                if new_detections:
                    logger.info(f"  🆕 新規検出: {new_detections}")
            
            # 全体性能計算
            metrics = self.calculate_metrics(threshold_results)
            results_by_threshold[threshold] = threshold_results
            
            logger.info(f"\n全体性能:")
            logger.info(f"  Recall: {metrics['recall']:.1%} ({metrics['true_positives']}/{metrics['total_expected']})")
            logger.info(f"  Precision: {metrics['precision']:.1%} ({metrics['true_positives']}/{metrics['total_detected']})")
            logger.info(f"  誤検知: {metrics['false_positives']}ページ")
            
            # 目標達成判定
            if metrics['recall'] >= 0.78:
                logger.info(f"  🎯 Phase 1目標達成！")
            else:
                needed = int(28 * (0.78 - metrics['recall']))
                logger.info(f"  ⚠️  目標まで残り{needed}ページ")
        
        # 推奨閾値の決定
        self._recommend_optimal_threshold(results_by_threshold)
    
    def _recommend_optimal_threshold(self, results_by_threshold: Dict):
        """最適閾値の推奨"""
        logger.info(f"\n💡 最適閾値の推奨:")
        logger.info("=" * 60)
        
        best_threshold = None
        best_score = 0
        
        for threshold, threshold_results in results_by_threshold.items():
            metrics = self.calculate_metrics(threshold_results)
            
            # スコア計算（Recall重視、Precision考慮）
            if metrics['precision'] >= 0.75:  # 最低75%の精度を要求
                score = metrics['recall'] * 100 + metrics['precision'] * 20
                
                if score > best_score:
                    best_score = score
                    best_threshold = threshold
        
        if best_threshold:
            best_metrics = self.calculate_metrics(results_by_threshold[best_threshold])
            logger.info(f"🏆 推奨閾値: {best_threshold}pt")
            logger.info(f"   Recall: {best_metrics['recall']:.1%}")
            logger.info(f"   Precision: {best_metrics['precision']:.1%}")
            logger.info(f"   誤検知: {best_metrics['false_positives']}ページ")
            
            if best_metrics['recall'] >= 0.78:
                logger.info(f"   ✅ Phase 1目標達成！")
            else:
                logger.info(f"   ⚠️  追加改善が必要")
        else:
            logger.info("❌ 適切な閾値が見つかりませんでした")
        
        logger.info("=" * 90)

def main():
    """メイン実行関数"""
    optimizer = ThresholdOptimizer()
    optimizer.run_threshold_optimization()

if __name__ == "__main__":
    main()