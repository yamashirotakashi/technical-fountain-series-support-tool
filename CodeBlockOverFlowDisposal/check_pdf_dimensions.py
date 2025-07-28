#!/usr/bin/env python3
"""
PDFの実際のページサイズとマージンを確認
"""

import fitz
import sys
from pathlib import Path


def check_dimensions(pdf_path):
    """PDFの寸法を確認"""
    doc = fitz.open(str(pdf_path))
    
    print(f"=== {pdf_path.name} の寸法情報 ===")
    
    # 最初の数ページをチェック
    for i in range(min(5, len(doc))):
        page = doc[i]
        rect = page.rect
        
        print(f"\nページ {i+1}:")
        print(f"  幅: {rect.width:.2f}pt ({rect.width * 25.4 / 72:.1f}mm)")
        print(f"  高さ: {rect.height:.2f}pt ({rect.height * 25.4 / 72:.1f}mm)")
        
        # テキストブロックを取得して本文エリアを推定
        blocks = page.get_text("blocks")
        if blocks:
            x_coords = [b[0] for b in blocks if len(b[4].strip()) > 10]  # 本文らしいブロック
            if x_coords:
                left_margin = min(x_coords)
                right_margin = rect.width - max([b[2] for b in blocks if len(b[4].strip()) > 10])
                print(f"  推定左マージン: {left_margin:.1f}pt")
                print(f"  推定右マージン: {right_margin:.1f}pt")
                print(f"  推定本文幅: {rect.width - left_margin - right_margin:.1f}pt")
    
    # 48ページの詳細確認
    if len(doc) >= 48:
        print(f"\n=== ページ48の詳細 ===")
        page = doc[47]
        
        # 図形情報を取得
        drawings = page.get_drawings()
        gray_rects = []
        
        for item in drawings:
            if item['type'] == 'f':  # filled
                fill = item.get('fill')
                if fill and len(fill) >= 3:
                    r, g, b = fill[:3]
                    if r == g == b and 0.8 <= r <= 0.9:
                        rect = item['rect']
                        gray_rects.append(rect)
                        print(f"\n灰色矩形:")
                        print(f"  位置: ({rect[0]:.1f}, {rect[1]:.1f}) - ({rect[2]:.1f}, {rect[3]:.1f})")
                        print(f"  幅: {rect[2] - rect[0]:.1f}pt")
                        print(f"  右端: {rect[2]:.1f}pt")
                        print(f"  ページ右端からの距離: {page.rect.width - rect[2]:.1f}pt")
    
    doc.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_dimensions(Path(sys.argv[1]))
    else:
        print("使用方法: python check_pdf_dimensions.py <PDFファイル>")