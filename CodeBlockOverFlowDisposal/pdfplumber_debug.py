#!/usr/bin/env python3
"""
PDFPlumberデバッグ版 - グレー背景の矩形の色情報を調査
"""

import sys
from pathlib import Path
import pdfplumber


def analyze_page_rects(pdf_path: str, target_page: int = 48):
    """指定ページの矩形情報を分析"""
    
    with pdfplumber.open(pdf_path) as pdf:
        if target_page > len(pdf.pages):
            print(f"エラー: ページ{target_page}は存在しません（総ページ数: {len(pdf.pages)}）")
            return
            
        page = pdf.pages[target_page - 1]  # 0-indexed
        print(f"ページ {target_page} の分析")
        print(f"ページサイズ: {page.width} x {page.height} pt")
        print("=" * 60)
        
        # すべての矩形を取得
        rects = page.rects
        print(f"矩形の総数: {len(rects)}")
        
        # 塗りつぶしがある矩形をリストアップ
        filled_rects = []
        for i, rect in enumerate(rects):
            if rect.get('fill'):
                filled_rects.append((i, rect))
                
        print(f"塗りつぶしのある矩形: {len(filled_rects)}個")
        print("-" * 60)
        
        # 各塗りつぶし矩形の詳細を表示
        for idx, (i, rect) in enumerate(filled_rects):
            print(f"\n矩形 #{i}:")
            print(f"  位置: ({rect['x0']:.1f}, {rect['y0']:.1f}) - ({rect['x1']:.1f}, {rect['y1']:.1f})")
            print(f"  サイズ: {rect['x1'] - rect['x0']:.1f} x {rect['y1'] - rect['y0']:.1f} pt")
            
            fill = rect.get('fill')
            print(f"  塗りつぶし色の型: {type(fill)}")
            print(f"  塗りつぶし色の値: {fill}")
            
            # 色の解釈
            if isinstance(fill, tuple):
                if len(fill) >= 3:
                    r, g, b = fill[:3]
                    if isinstance(r, float):
                        r, g, b = int(r * 255), int(g * 255), int(b * 255)
                    print(f"  RGB値: ({r}, {g}, {b})")
                    
                    # グレースケール判定
                    if abs(r - g) < 10 and abs(g - b) < 10 and abs(r - b) < 10:
                        gray_value = (r + g + b) / 3
                        print(f"  グレースケール値: {gray_value:.1f}")
                        print(f"  グレー判定: {'YES' if 180 <= gray_value <= 250 else 'NO'}")
            
            # ストローク情報
            if rect.get('stroke'):
                print(f"  枠線あり: {rect.get('stroke')}")
                
            # 矩形内のテキストを取得（最初の数文字のみ）
            cropped = page.within_bbox((rect['x0'], rect['y0'], rect['x1'], rect['y1']))
            chars = cropped.chars
            if chars:
                sample_text = ''.join([c['text'] for c in chars[:20]])
                print(f"  内容サンプル: '{sample_text}...'")
                
        # テキスト情報も表示
        print("\n" + "=" * 60)
        print("ページ内のテキスト情報:")
        chars = page.chars
        print(f"文字総数: {len(chars)}")
        
        # 右端の文字を探す
        if chars:
            rightmost_chars = sorted(chars, key=lambda c: c['x1'], reverse=True)[:5]
            print("\n右端の文字TOP5:")
            for i, char in enumerate(rightmost_chars):
                print(f"  {i+1}. '{char['text']}' at x={char['x1']:.1f}")


def main():
    if len(sys.argv) < 2:
        print("使用法: python pdfplumber_debug.py PDFファイル [ページ番号]")
        sys.exit(1)
        
    pdf_path = sys.argv[1]
    page_num = int(sys.argv[2]) if len(sys.argv) > 2 else 48
    
    analyze_page_rects(pdf_path, page_num)


if __name__ == "__main__":
    main()