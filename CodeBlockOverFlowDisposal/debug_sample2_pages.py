#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug sample2.pdf pages 128 and 129"""

import pdfplumber
from visual_hybrid_detector_v10 import VisualHybridDetectorV10

detector = VisualHybridDetectorV10()

with pdfplumber.open('sample2.pdf') as pdf:
    for page_num in [128, 129]:
        page = pdf.pages[page_num - 1]
        
        print(f"\n=== Page {page_num} ===")
        print(f"Page dimensions: {page.width:.1f} x {page.height:.1f}")
        
        # 本文領域の右端を計算
        if page_num % 2 == 0:  # 偶数ページ
            right_margin_pt = detector.config.even_page_margins['right'] * detector.config.mm_to_pt
        else:  # 奇数ページ
            right_margin_pt = detector.config.odd_page_margins['right'] * detector.config.mm_to_pt
        
        text_right_edge = page.width - right_margin_pt
        print(f"Text right edge: {text_right_edge:.1f}pt")
        
        # 右端に近い文字をチェック
        all_chars = [(char, char['x1']) for char in page.chars]
        all_chars.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\nRightmost 10 characters:")
        for char, x1 in all_chars[:10]:
            overflow = x1 - text_right_edge
            char_type = "ASCII" if detector.is_ascii_char(char['text']) else "non-ASCII"
            status = "OVERFLOW" if overflow > 0.1 else "within"
            print(f"  '{char['text']}' ({char_type}) at x1={x1:.1f} ({status}: {overflow:+.1f}pt)")
        
        # ASCII文字のみでオーバーフローをチェック
        ascii_overflow_chars = []
        for char in page.chars:
            if detector.is_ascii_char(char['text']):
                overflow = char['x1'] - text_right_edge
                if overflow > 0.1:
                    ascii_overflow_chars.append((char, overflow))
        
        if ascii_overflow_chars:
            print(f"\nASCII overflow characters found: {len(ascii_overflow_chars)}")
            ascii_overflow_chars.sort(key=lambda x: x[1], reverse=True)
            for char, overflow in ascii_overflow_chars[:5]:
                print(f"  '{char['text']}' at x1={char['x1']:.1f} (overflow: {overflow:.1f}pt)")
        else:
            print(f"\nNo ASCII overflow characters found")