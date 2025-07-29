#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
マージン設定とはみ出し検出の詳細デバッグ
"""

import pdfplumber
from pathlib import Path

def analyze_page_margins(pdf_path, page_num):
    """ページのマージンと文字配置を詳細分析"""
    print(f"\n=== {pdf_path} - Page {page_num} ===")
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num - 1]
        
        # ページ情報
        print(f"Page dimensions: {page.width:.1f} x {page.height:.1f}pt")
        
        # 現在の設定値
        mm_to_pt = 2.83465
        if page_num % 2 == 1:  # 奇数ページ
            left_margin = 18 * mm_to_pt  # 50.9pt
            right_margin = 10 * mm_to_pt  # 28.3pt
        else:  # 偶数ページ  
            left_margin = 10 * mm_to_pt  # 28.3pt
            right_margin = 18 * mm_to_pt  # 50.9pt
        
        text_left = left_margin
        text_right = page.width - right_margin
        
        print(f"Current margins: left={left_margin:.1f}pt, right={right_margin:.1f}pt")
        print(f"Text area: {text_left:.1f} to {text_right:.1f}pt")
        
        # 実際の文字の分布を調査
        chars = page.chars
        if not chars:
            print("No characters found")
            return
        
        # X座標の分布
        x_positions = [char['x0'] for char in chars]
        x_positions.extend([char['x1'] for char in chars])
        
        min_x = min(x_positions)
        max_x = max(x_positions)
        
        print(f"Actual text range: {min_x:.1f} to {max_x:.1f}pt")
        print(f"Left overflow: {text_left - min_x:.1f}pt")
        print(f"Right overflow: {max_x - text_right:.1f}pt")
        
        # ASCII文字のみの分布
        ascii_chars = [char for char in chars if ord(char['text'][0]) < 128]
        if ascii_chars:
            ascii_x = [char['x1'] for char in ascii_chars]
            max_ascii_x = max(ascii_x)
            print(f"Max ASCII char position: {max_ascii_x:.1f}pt")
            print(f"ASCII overflow: {max_ascii_x - text_right:.1f}pt")
            
            # 最も右のASCII文字を表示
            rightmost_ascii = max(ascii_chars, key=lambda c: c['x1'])
            print(f"Rightmost ASCII: '{rightmost_ascii['text']}' at {rightmost_ascii['x1']:.1f}pt")

def main():
    # 各PDFから1つのknown overflowページを調査
    test_cases = [
        ('sample2.pdf', 128),
        ('sample3.pdf', 13),
        ('sample4.pdf', 27),
        ('sample5.pdf', 128)
    ]
    
    for pdf_file, page_num in test_cases:
        if Path(pdf_file).exists():
            analyze_page_margins(pdf_file, page_num)

if __name__ == "__main__":
    main()