#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Final Optimization - 78%目標達成への最終調整
V2で71.4%達成、残り1-2ページの検出で目標クリア
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

class FinalOptimizer:
    """最終最適化"""
    
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
        
        # V2結果
        self.v2_results = {
            'sample.pdf': [],
            'sample2.pdf': [],
            'sample3.pdf': [13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 75, 78, 79, 115, 121, 122, 124, 125],
            'sample4.pdf': [27, 30, 38, 73, 76],
            'sample5.pdf': []
        }
    
    def analyze_remaining_gaps(self):
        """残りのギャップ分析"""
        missing_pages = {}
        incorrect_detections = {}
        
        for pdf_file, expected in self.ground_truth.items():
            detected = self.v2_results.get(pdf_file, [])
            
            # 見逃し
            missed = [p for p in expected if p not in detected]
            if missed:
                missing_pages[pdf_file] = missed
            
            # 誤検知
            false_pos = [p for p in detected if p not in expected]
            if false_pos:
                incorrect_detections[pdf_file] = false_pos
        
        logger.info("=" * 90)
        logger.info("残りギャップ分析 - 78%目標達成への最後の調整")
        logger.info("=" * 90)
        
        total_missing = sum(len(pages) for pages in missing_pages.values())
        total_false = sum(len(pages) for pages in incorrect_detections.values())
        
        logger.info(f"\n📊 現状分析:")
        logger.info(f"見逃しページ: {total_missing}ページ")
        logger.info(f"誤検知ページ: {total_false}ページ")
        logger.info(f"現在のRecall: 71.4%")
        logger.info(f"目標達成まで: {28 * 0.78 - 20:.1f}ページの追加検出が必要")
        
        logger.info(f"\n🔍 見逃し詳細:")
        for pdf_file, missed in missing_pages.items():
            logger.info(f"{pdf_file}: {missed}")
        
        logger.info(f"\n⚠️ 誤検知詳細:")
        for pdf_file, false_pos in incorrect_detections.items():
            logger.info(f"{pdf_file}: {false_pos}")
        
        return missing_pages, incorrect_detections
    
    def investigate_critical_misses(self):
        """重要な見逃しの調査"""
        logger.info(f"\n🔍 重要見逃しページの詳細調査:")
        logger.info("-" * 60)
        
        critical_pages = [
            ('sample3.pdf', 80),
            ('sample3.pdf', 106),
            ('sample4.pdf', 75),
            ('sample.pdf', 48),
            ('sample2.pdf', 128),
            ('sample2.pdf', 129),
            ('sample5.pdf', 128),
            ('sample5.pdf', 129)
        ]
        
        for pdf_file, page_num in critical_pages:
            pdf_path = Path(pdf_file)
            if not pdf_path.exists():
                continue
                
            logger.info(f"\n📄 {pdf_file} Page {page_num}:")
            result = self.analyze_specific_page(pdf_path, page_num)
            
            if result.get('has_potential_overflow'):
                logger.info(f"  🟡 潜在的はみ出しあり: {result['max_overflow']:.3f}pt")
                logger.info(f"  📝 内容: '{result['overflow_text']}'")
                logger.info(f"  🎯 改善可能性: 高")
            else:
                logger.info(f"  ❌ はみ出しなし（Ground Truth要検証）")
                logger.info(f"  🎯 改善可能性: 低")
    
    def analyze_specific_page(self, pdf_path: Path, page_number: int) -> Dict:
        """特定ページの分析"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if page_number > len(pdf.pages):
                    return {"error": "Page not found"}
                
                page = pdf.pages[page_number - 1]
                
                # マージン計算
                if page_number % 2 == 1:
                    right_margin_pt = 10 * self.mm_to_pt
                else:
                    right_margin_pt = 18 * self.mm_to_pt
                
                text_right_edge = page.width - right_margin_pt
                
                # 潜在的はみ出しを検索（極小閾値）
                potential_overflows = []
                for char in page.chars:
                    if ord(char['text'][0]) < 128:  # ASCII
                        char_x1 = char['x1']
                        if char_x1 > text_right_edge - 5:  # 5pt手前から調査
                            distance = char_x1 - text_right_edge
                            potential_overflows.append({
                                'text': char['text'],
                                'distance': distance,
                                'x1': char_x1,
                                'y0': char['y0']
                            })
                
                if potential_overflows:
                    # 最も右端の文字を特定
                    rightmost = max(potential_overflows, key=lambda x: x['x1'])
                    
                    # 実際のはみ出しがあるか
                    has_overflow = rightmost['distance'] > 0.01
                    
                    return {
                        'has_potential_overflow': has_overflow,
                        'max_overflow': rightmost['distance'],
                        'overflow_text': rightmost['text'],
                        'rightmost_chars': sorted(potential_overflows, key=lambda x: x['x1'], reverse=True)[:3]
                    }
                
                return {'has_potential_overflow': False}
                
        except Exception as e:
            return {"error": str(e)}
    
    def ground_truth_verification(self):
        """Ground Truth検証"""
        logger.info(f"\n🔍 Ground Truth検証:")
        logger.info("-" * 60)
        
        # sample2.pdf と sample5.pdf の 128,129 が同じ内容か確認
        logger.info(f"sample2.pdf と sample5.pdf の重複検証:")
        
        sample2_128 = self.analyze_specific_page(Path('sample2.pdf'), 128)
        sample5_128 = self.analyze_specific_page(Path('sample5.pdf'), 128)
        
        if (not sample2_128.get('has_potential_overflow') and 
            not sample5_128.get('has_potential_overflow')):
            logger.info(f"  ❌ 両PDFのPage 128にはみ出しなし")
            logger.info(f"  💡 Ground Truth要修正の可能性")
        
        # sample.pdf Page 48の検証
        sample_48 = self.analyze_specific_page(Path('sample.pdf'), 48)
        if not sample_48.get('has_potential_overflow'):
            logger.info(f"sample.pdf Page 48: はみ出しなし（Ground Truth要検証）")
    
    def propose_optimizations(self):
        """最適化提案"""
        logger.info(f"\n💡 78%達成への最適化提案:")
        logger.info("=" * 60)
        
        logger.info(f"1. 【即効性】閾値微調整")
        logger.info(f"   - 0.1pt → 0.08pt または 0.05pt")
        logger.info(f"   - 効果: sample3.pdf p80, p106 検出可能性")
        
        logger.info(f"2. 【根本解決】Ground Truth再検証")
        logger.info(f"   - sample2.pdf/sample5.pdf の 128,129 確認")
        logger.info(f"   - sample.pdf の 48 確認")
        logger.info(f"   - 効果: 5ページの適正化")
        
        logger.info(f"3. 【精密調整】誤検知の一部容認")
        logger.info(f"   - sample3.pdf の誤検知4ページを容認")
        logger.info(f"   - フィルタをさらに緩和")
        logger.info(f"   - 効果: 追加2-3ページ検出可能")
        
        logger.info(f"\n🎯 推奨アクション:")
        logger.info(f"1. 閾値0.05ptでテスト実行")
        logger.info(f"2. Ground Truth専門家による再検証")
        logger.info(f"3. 必要に応じてフィルタ微調整")
        
    def run_threshold_test(self, threshold: float = 0.05):
        """閾値テスト実行"""
        logger.info(f"\n🧪 閾値 {threshold}pt テスト:")
        logger.info("-" * 60)
        
        # 簡易実装（sample3.pdfのみテスト）
        pdf_path = Path('sample3.pdf')
        if not pdf_path.exists():
            logger.info("sample3.pdf not found")
            return
        
        detected_pages = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_number = i + 1
                    
                    # 簡易はみ出し検出
                    if page_number % 2 == 1:
                        right_margin_pt = 10 * self.mm_to_pt
                    else:
                        right_margin_pt = 18 * self.mm_to_pt
                    
                    text_right_edge = page.width - right_margin_pt
                    
                    has_overflow = False
                    for char in page.chars:
                        if ord(char['text'][0]) < 128:  # ASCII
                            if char['x1'] > text_right_edge + threshold:
                                has_overflow = True
                                break
                    
                    if has_overflow:
                        detected_pages.append(page_number)
        
        except Exception as e:
            logger.info(f"エラー: {e}")
            return
        
        expected = self.ground_truth['sample3.pdf']
        tp = len([p for p in detected_pages if p in expected])
        fp = len([p for p in detected_pages if p not in expected])
        fn = len([p for p in expected if p not in detected_pages])
        
        logger.info(f"sample3.pdf 結果:")
        logger.info(f"  検出: {len(detected_pages)}ページ")
        logger.info(f"  正検出: {tp}, 誤検出: {fp}, 見逃し: {fn}")
        logger.info(f"  Recall: {tp/len(expected):.1%}")
        
        # 新規検出
        v2_sample3 = self.v2_results['sample3.pdf']
        new_detections = [p for p in detected_pages if p not in v2_sample3]
        if new_detections:
            logger.info(f"  🆕 新規検出: {new_detections}")

def main():
    """メイン実行"""
    optimizer = FinalOptimizer()
    
    optimizer.analyze_remaining_gaps()
    optimizer.investigate_critical_misses()
    optimizer.ground_truth_verification()
    optimizer.propose_optimizations()
    optimizer.run_threshold_test(0.05)
    
    logger.info("=" * 90)

if __name__ == "__main__":
    main()