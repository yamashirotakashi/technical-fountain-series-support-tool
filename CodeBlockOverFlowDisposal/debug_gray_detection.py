#!/usr/bin/env python3
"""
灰色矩形検出のデバッグスクリプト
"""

import fitz
import sys
from pathlib import Path


def analyze_colors(pdf_path, target_page=48):
    """特定ページの塗りつぶし色を分析"""
    print(f"=== {pdf_path} のページ {target_page} を分析 ===")
    
    doc = fitz.open(str(pdf_path))
    
    if doc.page_count < target_page:
        print(f"エラー: PDFは {doc.page_count} ページしかありません")
        doc.close()
        return
    
    page = doc[target_page - 1]  # 0-indexed
    drawings = page.get_drawings()
    
    print(f"図形数: {len(drawings)}")
    
    # 塗りつぶし図形のみ
    filled = [d for d in drawings if d['type'] == 'f']
    print(f"塗りつぶし図形数: {len(filled)}")
    
    # 色の分布を確認
    colors = {}
    for i, item in enumerate(filled[:10]):  # 最初の10個
        fill = item.get('fill')
        if fill:
            color_key = f"RGB({fill[0]:.3f}, {fill[1]:.3f}, {fill[2]:.3f})"
            colors[color_key] = colors.get(color_key, 0) + 1
            
            rect = item['rect']
            print(f"\n図形 {i}:")
            print(f"  色: {color_key}")
            print(f"  位置: ({rect[0]:.1f}, {rect[1]:.1f}) - ({rect[2]:.1f}, {rect[3]:.1f})")
            print(f"  サイズ: {rect[2]-rect[0]:.1f} x {rect[3]-rect[1]:.1f}")
            
            # 灰色っぽい色を判定
            if len(fill) >= 3:
                r, g, b = fill[:3]
                if r == g == b and 0.8 <= r <= 1.0:
                    print(f"  → 灰色の候補！")
    
    print(f"\n色の分布:")
    for color, count in sorted(colors.items(), key=lambda x: x[1], reverse=True):
        print(f"  {color}: {count} 個")
    
    doc.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = Path(sys.argv[1])
        page = int(sys.argv[2]) if len(sys.argv) > 2 else 48
        analyze_colors(pdf_path, page)
    else:
        print("使用方法: python debug_gray_detection.py <PDFファイル> [ページ番号]")