#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Missed Page Analyzer - 見逃しページの詳細診断ツール
67.9% → 78%への改善のため、見逃し9ページの原因を分析
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys

try:
    import pdfplumber
except ImportError:
    print("pdfplumber not available. Running in compatibility mode.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class MissedPageAnalyzer:
    """見逃しページの詳細分析"""
    
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
        
        # 現在の検出結果
        self.current_results = {
            'sample.pdf': [],
            'sample2.pdf': [],
            'sample3.pdf': [13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 75, 78, 79, 115, 121, 122, 124, 125],
            'sample4.pdf': [27, 30, 73, 76],
            'sample5.pdf': []
        }
    
    def get_missed_pages(self) -> Dict[str, List[int]]:
        """見逃しページのリストを取得"""
        missed = {}
        for pdf_file, expected in self.ground_truth.items():
            detected = self.current_results.get(pdf_file, [])
            missed_pages = [p for p in expected if p not in detected]
            if missed_pages:
                missed[pdf_file] = missed_pages
        return missed
    
    def analyze_page_details(self, pdf_path: Path, page_number: int) -> Dict:
        """特定ページの詳細分析"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if page_number > len(pdf.pages):
                    return {"error": f"Page {page_number} not found"}
                
                page = pdf.pages[page_number - 1]  # 0-indexed
                
                # マージン計算
                if page_number % 2 == 1:  # 奇数ページ
                    right_margin_pt = 10 * self.mm_to_pt  # 28.3pt
                else:  # 偶数ページ
                    right_margin_pt = 18 * self.mm_to_pt  # 51.0pt
                
                text_right_edge = page.width - right_margin_pt
                
                # ASCII文字の分析
                ascii_chars = []
                potential_overflows = []
                
                for char in page.chars:
                    if ord(char['text'][0]) < 128:  # ASCII文字
                        char_x1 = char['x1']
                        distance_from_edge = char_x1 - text_right_edge
                        
                        ascii_chars.append({
                            'text': char['text'],
                            'x1': char_x1,
                            'y0': char['y0'],
                            'distance_from_edge': distance_from_edge
                        })
                        
                        # 閾値チェック（複数レベル）
                        if distance_from_edge > 0.01:  # 非常に緩い閾値
                            potential_overflows.append({
                                'text': char['text'],
                                'x1': char_x1,
                                'y0': char['y0'],
                                'overflow_amount': distance_from_edge,
                                'threshold_0_1': distance_from_edge > 0.1,
                                'threshold_0_05': distance_from_edge > 0.05,
                                'threshold_0_02': distance_from_edge > 0.02,
                                'threshold_0_01': distance_from_edge > 0.01
                            })
                
                return {
                    'page_number': page_number,
                    'page_width': page.width,
                    'page_height': page.height,
                    'right_margin_pt': right_margin_pt,
                    'text_right_edge': text_right_edge,
                    'total_chars': len(page.chars),
                    'ascii_chars_count': len(ascii_chars),
                    'potential_overflows_count': len(potential_overflows),
                    'potential_overflows': potential_overflows[:10],  # 最初の10個
                    'rightmost_ascii_chars': sorted(ascii_chars, key=lambda x: x['x1'], reverse=True)[:5]
                }
                
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_missed_patterns(self) -> Dict:
        """見逃しパターンの分析"""
        missed_pages = self.get_missed_pages()
        analysis = {
            'total_missed': sum(len(pages) for pages in missed_pages.values()),
            'by_pdf': {},
            'common_patterns': []
        }
        
        for pdf_file, pages in missed_pages.items():
            pdf_path = Path(pdf_file)
            if not pdf_path.exists():
                analysis['by_pdf'][pdf_file] = {"error": "File not found"}
                continue
                
            page_analyses = []
            for page_num in pages:
                page_analysis = self.analyze_page_details(pdf_path, page_num)
                page_analyses.append(page_analysis)
            
            analysis['by_pdf'][pdf_file] = {
                'missed_pages': pages,
                'analyses': page_analyses
            }
        
        # 共通パターンの分析
        self._find_common_patterns(analysis)
        
        return analysis
    
    def _find_common_patterns(self, analysis: Dict):
        """共通パターンの検出"""
        patterns = []
        
        # sample2.pdf と sample5.pdf の 128, 129 ページ
        if ('sample2.pdf' in analysis['by_pdf'] and 
            'sample5.pdf' in analysis['by_pdf']):
            sample2_pages = analysis['by_pdf']['sample2.pdf'].get('missed_pages', [])
            sample5_pages = analysis['by_pdf']['sample5.pdf'].get('missed_pages', [])
            
            common_pages = set(sample2_pages) & set(sample5_pages)
            if common_pages:
                patterns.append({
                    'type': 'common_pages_across_pdfs',
                    'pages': list(common_pages),
                    'pdfs': ['sample2.pdf', 'sample5.pdf'],
                    'description': '複数PDFで同じページ番号が見逃されている'
                })
        
        # 高ページ番号の傾向
        all_missed = []
        for pdf_data in analysis['by_pdf'].values():
            if 'missed_pages' in pdf_data:
                all_missed.extend(pdf_data['missed_pages'])
        
        if all_missed:
            avg_page = sum(all_missed) / len(all_missed)
            high_page_count = sum(1 for p in all_missed if p > 100)
            
            if high_page_count > len(all_missed) * 0.5:
                patterns.append({
                    'type': 'high_page_numbers',
                    'average_page': avg_page,
                    'high_page_ratio': high_page_count / len(all_missed),
                    'description': '高いページ番号に見逃しが集中'
                })
        
        analysis['common_patterns'] = patterns
    
    def print_detailed_report(self):
        """詳細レポートの出力"""
        logger.info("=" * 90)
        logger.info("見逃しページ詳細診断レポート")
        logger.info("=" * 90)
        
        analysis = self.analyze_missed_patterns()
        
        logger.info(f"\n📊 見逃し概要:")
        logger.info(f"総見逃しページ数: {analysis['total_missed']}")
        logger.info(f"目標まで必要な改善: {28 * 0.78 - (28 - analysis['total_missed']):.1f}ページの追加検出")
        
        # PDF別詳細
        for pdf_file, data in analysis['by_pdf'].items():
            if 'error' in data:
                logger.info(f"\n❌ {pdf_file}: {data['error']}")
                continue
                
            logger.info(f"\n📄 {pdf_file}:")
            logger.info(f"見逃しページ: {data['missed_pages']}")
            
            for page_analysis in data['analyses']:
                if 'error' in page_analysis:
                    logger.info(f"  Page {page_analysis.get('page_number', '?')}: エラー - {page_analysis['error']}")
                    continue
                
                p = page_analysis
                logger.info(f"  Page {p['page_number']}:")
                logger.info(f"    サイズ: {p['page_width']:.1f} x {p['page_height']:.1f}pt")
                logger.info(f"    右マージン: {p['right_margin_pt']:.1f}pt")
                logger.info(f"    ASCII文字数: {p['ascii_chars_count']}/{p['total_chars']}")
                logger.info(f"    潜在はみ出し: {p['potential_overflows_count']}個")
                
                if p['potential_overflows']:
                    logger.info(f"    潜在はみ出し詳細:")
                    for overflow in p['potential_overflows']:
                        thresholds = []
                        if overflow['threshold_0_1']: thresholds.append("0.1pt")
                        if overflow['threshold_0_05']: thresholds.append("0.05pt") 
                        if overflow['threshold_0_02']: thresholds.append("0.02pt")
                        threshold_str = f"({', '.join(thresholds)})" if thresholds else "(none)"
                        
                        logger.info(f"      '{overflow['text']}' +{overflow['overflow_amount']:.3f}pt {threshold_str}")
                
                if p['rightmost_ascii_chars']:
                    logger.info(f"    右端ASCII文字:")
                    for char in p['rightmost_ascii_chars']:
                        logger.info(f"      '{char['text']}' x1={char['x1']:.1f}pt (edge{char['distance_from_edge']:+.3f}pt)")
        
        # 共通パターン
        if analysis['common_patterns']:
            logger.info(f"\n🔍 共通パターン:")
            for i, pattern in enumerate(analysis['common_patterns'], 1):
                logger.info(f"{i}. {pattern['description']}")
                if pattern['type'] == 'common_pages_across_pdfs':
                    logger.info(f"   ページ: {pattern['pages']}, PDF: {pattern['pdfs']}")
                elif pattern['type'] == 'high_page_numbers':
                    logger.info(f"   平均ページ番号: {pattern['average_page']:.1f}")
                    logger.info(f"   高ページ番号率: {pattern['high_page_ratio']:.1%}")
        
        logger.info("=" * 90)

def main():
    """メイン実行関数"""
    analyzer = MissedPageAnalyzer()
    analyzer.print_detailed_report()

if __name__ == "__main__":
    main()