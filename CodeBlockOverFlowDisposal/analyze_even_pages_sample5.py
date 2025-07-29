#!/usr/bin/env python3
"""
sample5.pdfの偶数ページを詳細分析
"""

import pdfplumber
from pathlib import Path
from typing import List, Dict


class EvenPageAnalyzer:
    """偶数ページの分析器"""
    
    def __init__(self):
        self.mm_to_pt = 72 / 25.4
        self.even_page_right_margin_mm = 15
        self.odd_page_right_margin_mm = 20
    
    def analyze_pdf(self, pdf_path: Path):
        """PDFの偶数ページを分析"""
        print(f"分析対象: {pdf_path.name}")
        print("=" * 60)
        
        even_pages_with_code = []
        even_pages_without_code = []
        
        with pdfplumber.open(str(pdf_path)) as pdf:
            total_pages = len(pdf.pages)
            
            # 偶数ページのみを分析
            for page_num in range(2, total_pages + 1, 2):  # 2, 4, 6, ...
                if page_num <= total_pages:
                    page = pdf.pages[page_num - 1]
                    
                    # コードブロック（グレー背景矩形）を検出
                    code_blocks = []
                    for rect in page.rects:
                        if rect.get('fill'):
                            width = rect['x1'] - rect['x0']
                            height = rect['y1'] - rect['y0']
                            if width > 300 and height > 20:
                                code_blocks.append(rect)
                    
                    if code_blocks:
                        even_pages_with_code.append({
                            'page': page_num,
                            'blocks': len(code_blocks),
                            'total_height': sum(b['y1'] - b['y0'] for b in code_blocks)
                        })
                    else:
                        even_pages_without_code.append(page_num)
        
        # 結果を表示
        print(f"\n総ページ数: {total_pages}")
        print(f"偶数ページ数: {total_pages // 2}")
        print(f"\nコードブロックがある偶数ページ: {len(even_pages_with_code)}ページ")
        print(f"コードブロックがない偶数ページ: {len(even_pages_without_code)}ページ")
        
        if even_pages_with_code:
            print("\n--- コードブロックがある偶数ページの詳細 ---")
            for info in even_pages_with_code[:10]:  # 最初の10ページ
                print(f"ページ {info['page']}: {info['blocks']}個のブロック, "
                      f"合計高さ {info['total_height']:.1f}pt")
            
            if len(even_pages_with_code) > 10:
                print(f"... 他 {len(even_pages_with_code) - 10} ページ")
        
        # サンプルページの詳細分析
        if even_pages_with_code:
            sample_page_num = even_pages_with_code[0]['page']
            print(f"\n--- サンプル: ページ {sample_page_num} の詳細分析 ---")
            self.analyze_sample_page(pdf_path, sample_page_num)
    
    def analyze_sample_page(self, pdf_path: Path, page_num: int):
        """特定ページの詳細分析"""
        with pdfplumber.open(str(pdf_path)) as pdf:
            page = pdf.pages[page_num - 1]
            
            print(f"ページサイズ: {page.width:.1f} x {page.height:.1f} pt")
            
            text_right_edge = page.width - (self.even_page_right_margin_mm * self.mm_to_pt)
            print(f"本文領域右端: {text_right_edge:.1f} pt")
            
            # コードブロックを分析
            for i, rect in enumerate(page.rects):
                if rect.get('fill'):
                    width = rect['x1'] - rect['x0']
                    height = rect['y1'] - rect['y0']
                    if width > 300 and height > 20:
                        overflow = rect['x1'] - text_right_edge
                        print(f"\nコードブロック {i+1}:")
                        print(f"  位置: ({rect['x0']:.1f}, {rect['y0']:.1f}) - "
                              f"({rect['x1']:.1f}, {rect['y1']:.1f})")
                        print(f"  サイズ: {width:.1f} x {height:.1f} pt")
                        print(f"  右端の超過: {overflow:.1f} pt")
                        
                        if overflow > -5.0:  # v5の偶数ページ閾値
                            print(f"  → 検出されるべき！")


def main():
    analyzer = EvenPageAnalyzer()
    pdf_path = Path("sample5.pdf")
    analyzer.analyze_pdf(pdf_path)


if __name__ == "__main__":
    main()