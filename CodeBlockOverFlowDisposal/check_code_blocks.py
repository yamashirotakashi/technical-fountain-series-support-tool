#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check if PDFs have code blocks"""

import pdfplumber
from pathlib import Path

pdfs = ['sample.pdf', 'sample2.pdf', 'sample3.pdf', 'sample4.pdf', 'sample5.pdf']

for pdf_file in pdfs:
    if Path(pdf_file).exists():
        print(f"\n{pdf_file}:")
        with pdfplumber.open(pdf_file) as pdf:
            total_blocks = 0
            pages_with_blocks = []
            
            for i, page in enumerate(pdf.pages):
                page_num = i + 1
                blocks = []
                for rect in page.rects:
                    if rect.get('fill'):
                        width = rect['x1'] - rect['x0']
                        height = rect['y1'] - rect['y0']
                        if width > 100 and height > 10:
                            blocks.append(rect)
                
                if blocks:
                    total_blocks += len(blocks)
                    pages_with_blocks.append(page_num)
            
            print(f"  Total pages: {len(pdf.pages)}")
            print(f"  Pages with code blocks: {len(pages_with_blocks)}")
            print(f"  Total code blocks: {total_blocks}")
            if pages_with_blocks[:10]:
                print(f"  First 10 pages with blocks: {pages_with_blocks[:10]}")