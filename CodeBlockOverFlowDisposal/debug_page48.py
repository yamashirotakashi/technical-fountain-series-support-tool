#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug page 48 of sample.pdf"""

import pdfplumber
from visual_hybrid_detector_v9 import VisualHybridDetectorV9

detector = VisualHybridDetectorV9()

with pdfplumber.open('sample.pdf') as pdf:
    page = pdf.pages[47]  # Page 48 (0-indexed)
    page_num = 48
    
    print(f"Page dimensions: {page.width} x {page.height}")
    
    # Check for code blocks
    code_blocks = detector.detect_code_blocks(page)
    print(f"\nCode blocks found: {len(code_blocks)}")
    for i, block in enumerate(code_blocks):
        print(f"  Block {i}: x0={block['x0']:.1f}, y0={block['y0']:.1f}, x1={block['x1']:.1f}, y1={block['y1']:.1f}")
    
    # Check rect overflow detection
    rect_overflows = detector.detect_rect_overflow(page, page_num)
    print(f"\nRect overflows detected: {len(rect_overflows)}")
    for overflow in rect_overflows:
        print(f"  {overflow['overflow_text']} ({overflow['overflow_amount']:.1f}pt)")
    
    # Check all characters in code blocks
    if code_blocks:
        print(f"\nChecking characters in first code block:")
        block = code_blocks[0]
        
        # Get text area boundary
        right_margin_pt = detector.config.odd_page_margins['right'] * detector.config.mm_to_pt
        text_right_edge = page.width - right_margin_pt
        print(f"Text right edge: {text_right_edge:.1f}pt")
        
        # Check characters
        chars_in_block = [char for char in page.chars 
                         if block['x0'] <= char['x0'] <= block['x1'] and 
                         block['y0'] <= char['y0'] <= block['y1']]
        
        print(f"Total chars in block: {len(chars_in_block)}")
        
        # Find rightmost ASCII characters
        ascii_chars = [(char, char['x1']) for char in chars_in_block 
                      if detector.is_ascii_char(char['text'])]
        ascii_chars.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\nRightmost ASCII characters:")
        for char, x1 in ascii_chars[:10]:
            overflow = x1 - text_right_edge
            print(f"  '{char['text']}' at x1={x1:.1f} (overflow: {overflow:.1f}pt)")
        
        # Check ALL characters (including non-ASCII)
        all_chars = [(char, char['x1']) for char in chars_in_block]
        all_chars.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\nRightmost ALL characters:")
        for char, x1 in all_chars[:10]:
            overflow = x1 - text_right_edge
            char_type = "ASCII" if detector.is_ascii_char(char['text']) else "non-ASCII"
            print(f"  '{char['text']}' ({char_type}) at x1={x1:.1f} (overflow: {overflow:.1f}pt)")
        
    # Check ALL characters on the page
    print(f"\n\nChecking ALL characters on page {page_num}:")
    all_page_chars = [(char, char['x1']) for char in page.chars]
    all_page_chars.sort(key=lambda x: x[1], reverse=True)
    
    print(f"Total chars on page: {len(all_page_chars)}")
    print(f"\nRightmost characters on entire page:")
    for char, x1 in all_page_chars[:20]:
        overflow = x1 - text_right_edge
        char_type = "ASCII" if detector.is_ascii_char(char['text']) else "non-ASCII"
        print(f"  '{char['text']}' ({char_type}) at x1={x1:.1f}, y0={char['y0']:.1f} (overflow: {overflow:.1f}pt)")