#!/usr/bin/env python3
"""
sample2.pdf の129ページ（奇数ページ）の詳細分析
"""

import pdfplumber
from pathlib import Path


def analyze_page_129():
    """129ページの詳細分析"""
    
    pdf_path = "sample2.pdf"
    if not Path(pdf_path).exists():
        print(f"エラー: {pdf_path} が見つかりません")
        return
    
    with pdfplumber.open(pdf_path) as pdf:
        if len(pdf.pages) < 129:
            print(f"エラー: PDFは{len(pdf.pages)}ページしかありません")
            return
            
        page = pdf.pages[128]  # 129ページ（0-indexed）
        
        print("=== ページ129（奇数ページ）の詳細分析 ===")
        print(f"ページサイズ: {page.width} x {page.height} pt")
        
        # 矩形情報
        rects = page.rects
        print(f"\n矩形数: {len(rects)}")
        
        filled_rects = []
        for i, rect in enumerate(rects):
            if rect.get('fill'):
                filled_rects.append((i, rect))
                
        print(f"塗りつぶし矩形数: {len(filled_rects)}")
        
        for idx, (i, rect) in enumerate(filled_rects):
            print(f"\n塗りつぶし矩形 #{i}:")
            print(f"  位置: ({rect['x0']:.1f}, {rect['y0']:.1f}) - ({rect['x1']:.1f}, {rect['y1']:.1f})")
            print(f"  幅×高さ: {rect['x1'] - rect['x0']:.1f} × {rect['y1'] - rect['y0']:.1f} pt")
            print(f"  fill値: {rect['fill']}")
            
            # この矩形内のテキストを取得
            cropped = page.within_bbox((rect['x0'], rect['y0'], rect['x1'], rect['y1']))
            chars = cropped.chars
            
            print(f"  矩形内の文字数: {len(chars)}")
            
            if chars:
                # 最初の20文字を表示
                sample_text = ''.join([c['text'] for c in chars[:20]])
                print(f"  内容サンプル: '{sample_text}...'")
        
        # ページ全体のテキストで右端のものを確認
        print("\n=== ページ全体の右端文字 TOP20 ===")
        all_chars = page.chars
        rightmost_chars = sorted(all_chars, key=lambda c: c['x1'], reverse=True)[:20]
        
        print("右端からの文字:")
        for i, char in enumerate(rightmost_chars):
            print(f"{i+1}. '{char['text']}' at x={char['x0']:.1f}-{char['x1']:.1f} (y={char['y0']:.1f})")
        
        # 奇数ページの標準的な本文右端を計算
        # 奇数ページ：右マージン20mm
        mm_to_pt = 72 / 25.4
        right_margin_pt = 20 * mm_to_pt
        expected_text_right = page.width - right_margin_pt
        
        print(f"\n=== 奇数ページの本文右端（理論値） ===")
        print(f"ページ幅: {page.width:.1f}pt")
        print(f"右マージン: 20mm = {right_margin_pt:.1f}pt")
        print(f"本文右端（理論値）: {expected_text_right:.1f}pt")
        
        # はみ出している可能性のある文字を探す
        print(f"\n=== 本文右端（{expected_text_right:.1f}pt）を超える文字 ===")
        overflow_candidates = []
        for char in all_chars:
            if char['x1'] > expected_text_right + 1:  # 1pt以上超過
                overflow_candidates.append(char)
        
        # Y座標でグループ化して行ごとに表示
        lines = {}
        for char in overflow_candidates:
            y_pos = round(char['y0'])
            if y_pos not in lines:
                lines[y_pos] = []
            lines[y_pos].append(char)
        
        for y_pos in sorted(lines.keys())[:10]:  # 最初の10行
            line_chars = sorted(lines[y_pos], key=lambda c: c['x0'])
            line_text = ''.join([c['text'] for c in line_chars])
            rightmost = max(line_chars, key=lambda c: c['x1'])
            print(f"Y={y_pos}: '{line_text}' (右端={rightmost['x1']:.1f}, 超過={rightmost['x1'] - expected_text_right:.1f}pt)")


if __name__ == "__main__":
    analyze_page_129()