#!/usr/bin/env python3
"""
全ページの塗りつぶし色をスキャン
"""

import fitz
from pathlib import Path
import sys


def scan_all_pages(pdf_path):
    """全ページの塗りつぶし色をスキャン"""
    doc = fitz.open(str(pdf_path))
    
    all_colors = {}
    gray_pages = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        drawings = page.get_drawings()
        
        for item in drawings:
            if item['type'] == 'f':  # filled
                fill = item.get('fill')
                if fill and len(fill) >= 3:
                    r, g, b = fill[:3]
                    
                    # 灰色系の色（R=G=B）のみ記録
                    if r == g == b:
                        color_key = f"{r:.3f}"
                        if color_key not in all_colors:
                            all_colors[color_key] = []
                        all_colors[color_key].append(page_num + 1)
                        
                        # 灰色っぽい色（0.7～0.95）のページを記録
                        if 0.7 <= r <= 0.95:
                            if page_num + 1 not in gray_pages:
                                gray_pages.append(page_num + 1)
    
    doc.close()
    
    print(f"=== {pdf_path.name} の灰色系色分析 ===")
    print(f"\n灰色系の色（RGB値が同じ）:")
    for color, pages in sorted(all_colors.items()):
        if len(pages) > 1:  # 複数ページで使用されている色
            print(f"  {color}: {len(pages)} ページで使用")
            if len(pages) <= 10:
                print(f"    ページ: {pages}")
    
    print(f"\n灰色っぽい塗りつぶしがあるページ（0.7～0.95）:")
    print(f"  {gray_pages[:20]}...")  # 最初の20ページ
    print(f"  合計: {len(gray_pages)} ページ")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        scan_all_pages(Path(sys.argv[1]))
    else:
        print("使用方法: python scan_all_colors.py <PDFファイル>")