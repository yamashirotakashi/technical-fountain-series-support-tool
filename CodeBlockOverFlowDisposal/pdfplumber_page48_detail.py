#!/usr/bin/env python3
"""
48ページの詳細分析 - 矩形とテキストの関係を詳しく調査
"""

import pdfplumber
from pathlib import Path


def analyze_page_48():
    """48ページの詳細分析"""
    
    with pdfplumber.open("sample.pdf") as pdf:
        page = pdf.pages[47]  # 48ページ（0-indexed）
        
        print("=== ページ48の詳細分析 ===")
        print(f"ページサイズ: {page.width} x {page.height} pt")
        
        # 矩形情報
        rects = page.rects
        print(f"\n矩形数: {len(rects)}")
        
        for i, rect in enumerate(rects):
            if rect.get('fill'):
                print(f"\n塗りつぶし矩形 #{i}:")
                print(f"  位置: ({rect['x0']:.1f}, {rect['y0']:.1f}) - ({rect['x1']:.1f}, {rect['y1']:.1f})")
                print(f"  幅×高さ: {rect['x1'] - rect['x0']:.1f} × {rect['y1'] - rect['y0']:.1f} pt")
                print(f"  fill値: {rect['fill']}")
                
                # この矩形内のテキストを取得
                cropped = page.within_bbox((rect['x0'], rect['y0'], rect['x1'], rect['y1']))
                chars = cropped.chars
                
                print(f"  矩形内の文字数: {len(chars)}")
                
                # 矩形の右端を超える文字を探す
                overflow_chars = []
                for char in chars:
                    if char['x1'] > rect['x1']:
                        overflow_chars.append(char)
                
                if overflow_chars:
                    print(f"  ★ 矩形を超える文字数: {len(overflow_chars)}")
                    # 最初の5文字を表示
                    for j, char in enumerate(overflow_chars[:5]):
                        print(f"    {j+1}. '{char['text']}' at x={char['x0']:.1f}-{char['x1']:.1f} (超過: {char['x1'] - rect['x1']:.1f}pt)")
                    
                    # 行ごとに分析
                    lines = {}
                    for char in chars:
                        y_pos = round(char['y0'])
                        if y_pos not in lines:
                            lines[y_pos] = []
                        lines[y_pos].append(char)
                    
                    print(f"\n  行数: {len(lines)}")
                    for y_pos, line_chars in sorted(lines.items()):
                        line_chars.sort(key=lambda c: c['x0'])
                        line_text = ''.join([c['text'] for c in line_chars])
                        rightmost = max(line_chars, key=lambda c: c['x1'])
                        
                        if rightmost['x1'] > rect['x1']:
                            print(f"    Y={y_pos}: '{line_text[:50]}...' (右端={rightmost['x1']:.1f}, 超過={rightmost['x1'] - rect['x1']:.1f}pt)")
                            # rから始まる部分を探す
                            r_index = -1
                            for idx, c in enumerate(line_chars):
                                if c['text'] == 'r' and c['x1'] > rect['x1']:
                                    r_index = idx
                                    break
                            if r_index >= 0:
                                overflow_text = ''.join([c['text'] for c in line_chars[r_index:]])
                                print(f"      → 'r'以降のはみ出し: '{overflow_text}'")
        
        # ページ全体のテキストで矩形外のものも確認
        print("\n=== ページ全体の右端文字 TOP10 ===")
        all_chars = page.chars
        rightmost_chars = sorted(all_chars, key=lambda c: c['x1'], reverse=True)[:10]
        for i, char in enumerate(rightmost_chars):
            print(f"{i+1}. '{char['text']}' at x={char['x1']:.1f} (y={char['y0']:.1f})")


if __name__ == "__main__":
    analyze_page_48()