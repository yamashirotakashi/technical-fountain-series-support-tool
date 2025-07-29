#!/usr/bin/env python3
"""
ページ128の実際のはみ出しを探す
"""

import pdfplumber
from pathlib import Path


def find_real_overflow():
    """ページ128で実際にはみ出している文字を探す"""
    pdf_path = Path("sample5.pdf")
    
    with pdfplumber.open(str(pdf_path)) as pdf:
        page = pdf.pages[127]  # 0-indexed
        
        mm_to_pt = 72 / 25.4
        text_right_edge = page.width - (15 * mm_to_pt)  # 偶数ページ
        
        print(f"=== ページ128の完全分析 ===")
        print(f"ページ幅: {page.width:.1f} pt")
        print(f"本文領域右端: {text_right_edge:.1f} pt")
        
        # コードブロック内の文字のみを分析
        code_blocks = []
        for rect in page.rects:
            if rect.get('fill'):
                width = rect['x1'] - rect['x0']
                height = rect['y1'] - rect['y0']
                if width > 300 and height > 20:
                    code_blocks.append(rect)
        
        print(f"\nコードブロック数: {len(code_blocks)}")
        
        # 各行を分析
        lines = {}
        for char in page.chars:
            # コードブロック内かチェック
            in_code_block = any(
                cb['x0'] <= char['x0'] <= cb['x1'] and
                cb['y0'] <= char['y0'] <= cb['y1']
                for cb in code_blocks
            )
            
            if in_code_block:
                y_pos = round(char['y0'])
                if y_pos not in lines:
                    lines[y_pos] = []
                lines[y_pos].append(char)
        
        # 各行の右端をチェック
        print("\n--- 各行の右端文字 ---")
        overflow_found = False
        
        for y_pos in sorted(lines.keys()):
            line_chars = sorted(lines[y_pos], key=lambda c: c['x0'])
            if line_chars:
                rightmost = max(line_chars, key=lambda c: c['x1'])
                distance = rightmost['x1'] - text_right_edge
                
                if distance > -10:  # 右端に近い行のみ表示
                    line_text = ''.join([c['text'] for c in line_chars])
                    print(f"\nY={y_pos}: {line_text[:80]}...")
                    print(f"  右端文字: '{rightmost['text']}' at x={rightmost['x1']:.1f}")
                    print(f"  距離: {distance:.2f}pt")
                    
                    if distance > 0:
                        print(f"  ★ はみ出し検出！")
                        overflow_found = True
                        
                        # ASCII文字かチェック
                        if ord(rightmost['text']) < 128:
                            print(f"  → ASCII文字のはみ出し")
                        else:
                            print(f"  → 非ASCII文字（日本語等）")
        
        if not overflow_found:
            print("\n※ コードブロック内にはみ出しは見つかりませんでした")
            
            # ページ全体で最も右にある文字を探す
            print("\n--- ページ全体の右端文字（上位5件） ---")
            all_chars = sorted(page.chars, key=lambda c: c['x1'], reverse=True)
            for i, char in enumerate(all_chars[:5]):
                distance = char['x1'] - text_right_edge
                print(f"{i+1}. '{char['text']}' at x={char['x1']:.1f}, "
                      f"Y={char['y0']:.1f}, 距離={distance:.2f}pt")
                
                if distance > 0:
                    print(f"   ★ ページ全体でのはみ出し検出！")
                    
                    # コードブロック内かチェック
                    in_code = any(
                        cb['x0'] <= char['x0'] <= cb['x1'] and
                        cb['y0'] <= char['y0'] <= cb['y1']
                        for cb in code_blocks
                    )
                    print(f"   コードブロック内: {'Yes' if in_code else 'No'}")


if __name__ == "__main__":
    find_real_overflow()