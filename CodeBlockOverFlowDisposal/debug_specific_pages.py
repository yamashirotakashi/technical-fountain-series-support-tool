#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pdfplumber
from pathlib import Path
from visual_hybrid_detector_v7 import VisualHybridDetectorV7

detector = VisualHybridDetectorV7()

debug_cases = [
    ('sample3.pdf', 81),
    ('sample3.pdf', 117),
]

for pdf_path, page_num in debug_cases:
    print(f"\n=== {pdf_path} Page {page_num} ===")
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num - 1]
        results = detector.detect_rect_overflow(page, page_num)
        if results:
            for result in results:
                print(f"Rectangle: {result['overflow_amount']:.1f}pt - '{result['overflow_text']}'")
        
        if page_num in detector.visual_judgments.get('known_overflows', {}).get(pdf_path, []):
            print("In known_overflows")
