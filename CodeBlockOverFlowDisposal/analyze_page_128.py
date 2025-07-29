#!/usr/bin/env python3
"""
sample5.pdf ページ128の詳細分析
"""

import pdfplumber
from pathlib import Path


def analyze_page_128():
    """ページ128を詳細分析"""
    pdf_path = Path("sample5.pdf")
    
    with pdfplumber.open(str(pdf_path)) as pdf:
        if len(pdf.pages) >= 128:
            page = pdf.pages[127]  # 0-indexed
            
            print(f"=== ページ128の詳細分析 ===")
            print(f"ページサイズ: {page.width:.1f} x {page.height:.1f} pt")
            
            # B5判の偶数ページマージン
            mm_to_pt = 72 / 25.4
            right_margin_pt = 15 * mm_to_pt  # 偶数ページは15mm
            text_right_edge = page.width - right_margin_pt
            
            print(f"本文領域右端: {text_right_edge:.1f} pt")
            
            # コードブロック（グレー背景矩形）を検出
            print("\n--- グレー背景矩形 ---")
            code_blocks = []
            for i, rect in enumerate(page.rects):
                if rect.get('fill'):
                    width = rect['x1'] - rect['x0']
                    height = rect['y1'] - rect['y0']
                    print(f"矩形{i+1}: ({rect['x0']:.1f}, {rect['y0']:.1f}) - "
                          f"({rect['x1']:.1f}, {rect['y1']:.1f}) "
                          f"幅={width:.1f}, 高さ={height:.1f}")
                    
                    if width > 300 and height > 20:
                        code_blocks.append(rect)
                        overflow = rect['x1'] - text_right_edge
                        print(f"  → コードブロック認定, 右端超過: {overflow:.1f} pt")
            
            # 右端付近の文字を分析
            print("\n--- 右端付近の文字（本文領域±20pt） ---")
            right_chars = []
            for char in page.chars:
                distance = char['x1'] - text_right_edge
                if abs(distance) < 20:
                    right_chars.append({
                        'text': char['text'],
                        'x0': char['x0'],
                        'x1': char['x1'],
                        'y0': char['y0'],
                        'distance': distance,
                        'type': classify_char(char['text'])
                    })
            
            # 距離順にソート
            right_chars.sort(key=lambda x: x['distance'], reverse=True)
            
            print("No. | 文字 | 種別 | X座標 | 右端との距離")
            print("-" * 50)
            for i, char in enumerate(right_chars[:20]):
                status = "超過" if char['distance'] > 0 else "境界内"
                print(f"{i+1:2d} | '{char['text']}' | {char['type']:10s} | "
                      f"{char['x1']:6.1f} | {char['distance']:+8.2f}pt [{status}]")
            
            # ASCII文字のみを抽出
            print("\n--- ASCII文字で右端を超えているもの ---")
            ascii_overflow = [c for c in right_chars 
                            if c['type'] in ['digit', 'alphabet', 'ascii_symbol'] 
                            and c['distance'] > 0]
            
            if ascii_overflow:
                for char in ascii_overflow:
                    print(f"'{char['text']}' at x={char['x1']:.1f}, "
                          f"超過量={char['distance']:.2f}pt, Y={char['y0']:.1f}")
            else:
                print("ASCII文字のはみ出しは検出されませんでした")
            
            # v5の検出閾値でチェック
            print(f"\n--- v5検出器の閾値でのチェック ---")
            print(f"偶数ページ座標閾値: -0.1pt（右端の0.1pt手前から検出）")
            print(f"偶数ページ矩形閾値: -5.0pt（右端の5pt手前から検出）")
            
            # 座標ベース検出
            coord_detect = [c for c in right_chars 
                          if c['type'] in ['digit', 'alphabet', 'ascii_symbol'] 
                          and c['distance'] > -0.1]
            
            print(f"\n座標ベースで検出される文字: {len(coord_detect)}個")
            if coord_detect:
                for c in coord_detect[:5]:
                    print(f"  '{c['text']}' (距離={c['distance']:.2f}pt)")
            
            # 矩形ベース検出
            rect_detect = [cb for cb in code_blocks 
                         if cb['x1'] - text_right_edge > -5.0]
            
            print(f"\n矩形ベースで検出されるブロック: {len(rect_detect)}個")
            for cb in rect_detect:
                print(f"  右端超過: {cb['x1'] - text_right_edge:.1f}pt")


def classify_char(char: str) -> str:
    """文字を分類"""
    if not char:
        return 'empty'
    
    code = ord(char[0])
    
    if code < 128:
        if 48 <= code <= 57:
            return 'digit'
        elif 65 <= code <= 90 or 97 <= code <= 122:
            return 'alphabet'
        elif 32 <= code < 127:
            return 'ascii_symbol'
        else:
            return 'control'
    elif 0x3040 <= code <= 0x309F:
        return 'hiragana'
    elif 0x30A0 <= code <= 0x30FF:
        return 'katakana'
    elif 0x4E00 <= code <= 0x9FAF:
        return 'kanji'
    
    return 'other'


if __name__ == "__main__":
    analyze_page_128()