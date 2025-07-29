#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug page 129 with final detector"""

import pdfplumber
from overflow_detector_final import OverflowDetectorFinal

detector = OverflowDetectorFinal()

with pdfplumber.open('sample5.pdf') as pdf:
    page = pdf.pages[128]  # Page 129 (0-indexed)
    page_num = 129
    
    print(f"=== Page {page_num} Debug ===")
    print(f"Page dimensions: {page.width:.1f} x {page.height:.1f}")
    
    # Calculate text edge
    if page_num % 2 == 0:  # 偶数ページ
        right_margin_pt = detector.config.even_page_margins['right'] * detector.config.mm_to_pt
        margin_type = "偶数ページ (18mm)"
    else:  # 奇数ページ
        right_margin_pt = detector.config.odd_page_margins['right'] * detector.config.mm_to_pt
        margin_type = "奇数ページ (10mm)"
    
    text_right_edge = page.width - right_margin_pt
    print(f"Margin type: {margin_type}")
    print(f"Text right edge: {text_right_edge:.1f}pt")
    
    # Check for overflow characters
    overflow_chars = []
    for char in page.chars:
        if detector.is_ascii_char(char['text']):
            overflow_amount = char['x1'] - text_right_edge
            if overflow_amount > detector.config.overflow_threshold:
                overflow_chars.append((char, overflow_amount))
    
    print(f"\nOverflow characters found: {len(overflow_chars)}")
    
    if overflow_chars:
        overflow_chars.sort(key=lambda x: x[1], reverse=True)
        print("Top 10 overflow characters:")
        for char, overflow in overflow_chars[:10]:
            print(f"  '{char['text']}' at x1={char['x1']:.1f}, y0={char['y0']:.1f} (overflow: {overflow:.1f}pt)")
    
    # Test the detector
    result = detector.detect_page(page, page_num, 'sample5.pdf')
    print(f"\nDetector result:")
    print(f"  Has overflow: {result['has_overflow']}")
    print(f"  Overflow count: {result['overflow_count']}")
    
    if result['overflows']:
        print("  Detected overflows:")
        for overflow in result['overflows']:
            print(f"    '{overflow['overflow_text']}' ({overflow['overflow_amount']:.1f}pt)")