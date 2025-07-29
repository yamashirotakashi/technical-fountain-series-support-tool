#!/usr/bin/env python3
"""
sample5.pdfの検出失敗原因を分析
"""

import pdfplumber
from pathlib import Path


def analyze_all_pages():
    """全ページの矩形配置を分析"""
    pdf_path = Path("sample5.pdf")
    
    odd_page_rect_positions = []
    even_page_rect_positions = []
    
    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages):
            page_num = i + 1
            
            # グレー背景矩形を検出
            for rect in page.rects:
                if rect.get('fill'):
                    width = rect['x1'] - rect['x0']
                    height = rect['y1'] - rect['y0']
                    if width > 300 and height > 20:
                        rect_info = {
                            'page': page_num,
                            'x0': rect['x0'],
                            'x1': rect['x1'],
                            'width': width
                        }
                        
                        if page_num % 2 == 1:  # 奇数ページ
                            odd_page_rect_positions.append(rect_info)
                        else:  # 偶数ページ
                            even_page_rect_positions.append(rect_info)
                        break  # 最初の矩形のみ記録
    
    # 統計を計算
    print("=== sample5.pdfの矩形配置分析 ===\n")
    
    if odd_page_rect_positions:
        x0_values = [r['x0'] for r in odd_page_rect_positions]
        x1_values = [r['x1'] for r in odd_page_rect_positions]
        
        print("【奇数ページの矩形】")
        print(f"サンプル数: {len(odd_page_rect_positions)}")
        print(f"X0範囲: {min(x0_values):.1f} - {max(x0_values):.1f}")
        print(f"X1範囲: {min(x1_values):.1f} - {max(x1_values):.1f}")
        print(f"代表的な矩形: ({x0_values[0]:.1f}, {x1_values[0]:.1f})")
    
    if even_page_rect_positions:
        x0_values = [r['x0'] for r in even_page_rect_positions]
        x1_values = [r['x1'] for r in even_page_rect_positions]
        
        print(f"\n【偶数ページの矩形】")
        print(f"サンプル数: {len(even_page_rect_positions)}")
        print(f"X0範囲: {min(x0_values):.1f} - {max(x0_values):.1f}")
        print(f"X1範囲: {min(x1_values):.1f} - {max(x1_values):.1f}")
        print(f"代表的な矩形: ({x0_values[0]:.1f}, {x1_values[0]:.1f})")
    
    # ページサイズとマージンを確認
    print("\n【ページレイアウト分析】")
    with pdfplumber.open(str(pdf_path)) as pdf:
        page = pdf.pages[0]
        page_width = page.width
        print(f"ページ幅: {page_width:.1f} pt")
        
        mm_to_pt = 72 / 25.4
        odd_right_edge = page_width - (20 * mm_to_pt)
        even_right_edge = page_width - (15 * mm_to_pt)
        
        print(f"奇数ページ本文右端: {odd_right_edge:.1f} pt")
        print(f"偶数ページ本文右端: {even_right_edge:.1f} pt")
        
        if odd_page_rect_positions:
            odd_rect_x1 = odd_page_rect_positions[0]['x1']
            print(f"\n奇数ページ矩形右端: {odd_rect_x1:.1f} pt")
            print(f"奇数ページ超過量: {odd_rect_x1 - odd_right_edge:.1f} pt")
        
        if even_page_rect_positions:
            even_rect_x1 = even_page_rect_positions[0]['x1']
            print(f"\n偶数ページ矩形右端: {even_rect_x1:.1f} pt")
            print(f"偶数ページ超過量: {even_rect_x1 - even_right_edge:.1f} pt")
    
    print("\n【検出失敗の原因】")
    print("1. 奇数ページと偶数ページで異なる矩形配置")
    print("   - 奇数ページ: 矩形が本文領域を11.3pt超過 → 検出される")
    print("   - 偶数ページ: 矩形が本文領域から38.3pt内側 → 検出されない")
    print("\n2. ページ128の実際のはみ出し")
    print("   - 矩形自体は本文領域内")
    print("   - 矩形内の文字がはみ出している可能性")
    print("   - 現在の検出ロジックでは文字レベルの検出が不十分")


def check_page_128_chars():
    """ページ128の文字を詳細チェック"""
    pdf_path = Path("sample5.pdf")
    
    print("\n\n=== ページ128の文字詳細分析 ===")
    
    with pdfplumber.open(str(pdf_path)) as pdf:
        page = pdf.pages[127]  # 0-indexed
        
        mm_to_pt = 72 / 25.4
        text_right_edge = page.width - (15 * mm_to_pt)  # 偶数ページ
        
        # すべての文字をチェック
        rightmost_chars = []
        for char in page.chars:
            if char['x1'] > text_right_edge - 50:  # 右端から50pt以内
                rightmost_chars.append({
                    'text': char['text'],
                    'x1': char['x1'],
                    'y0': char['y0'],
                    'distance': char['x1'] - text_right_edge
                })
        
        # 距離順にソート
        rightmost_chars.sort(key=lambda x: x['distance'], reverse=True)
        
        print(f"本文領域右端: {text_right_edge:.1f} pt")
        print(f"\n最も右にある文字（上位10件）:")
        for i, char in enumerate(rightmost_chars[:10]):
            status = "はみ出し" if char['distance'] > 0 else "領域内"
            print(f"{i+1}. '{char['text']}' at x={char['x1']:.1f}, "
                  f"距離={char['distance']:.2f}pt, Y={char['y0']:.1f} [{status}]")


if __name__ == "__main__":
    analyze_all_pages()
    check_page_128_chars()