#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
詳細なはみ出し分析 - 実際のはみ出しを見つけるため
"""

import pdfplumber
from pathlib import Path

def analyze_pdf_detailed(pdf_path, target_pages):
    """PDFの詳細分析"""
    print(f"\n{'='*60}")
    print(f"詳細分析: {pdf_path}")
    print(f"対象ページ: {target_pages}")
    print(f"{'='*60}")
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num in target_pages:
            if page_num > len(pdf.pages):
                continue
                
            page = pdf.pages[page_num - 1]
            print(f"\n--- Page {page_num} ---")
            print(f"Page size: {page.width:.1f} x {page.height:.1f} pt")
            
            # 複数の右マージン基準で試してみる
            margin_tests = [
                ("10mm (奇数)", 10 * 2.83465),
                ("18mm (偶数)", 18 * 2.83465),
                ("15mm (中間)", 15 * 2.83465),
                ("20mm (広め)", 20 * 2.83465),
                ("5mm (狭め)", 5 * 2.83465)
            ]
            
            for margin_name, margin_pt in margin_tests:
                text_right_edge = page.width - margin_pt
                
                # はみ出し文字を探す
                overflow_chars = []
                for char in page.chars:
                    if char['x1'] > text_right_edge:
                        overflow_amount = char['x1'] - text_right_edge
                        overflow_chars.append((char, overflow_amount))
                
                if overflow_chars:
                    print(f"\n  {margin_name}マージン (右端: {text_right_edge:.1f}pt):")
                    print(f"    はみ出し文字数: {len(overflow_chars)}")
                    
                    # はみ出し量で並び替え
                    overflow_chars.sort(key=lambda x: x[1], reverse=True)
                    
                    # 上位5つを表示
                    for char, overflow in overflow_chars[:5]:
                        char_type = "ASCII" if ord(char['text'][0]) < 128 else "non-ASCII"
                        print(f"      '{char['text']}' ({char_type}) x1={char['x1']:.1f} "
                              f"y0={char['y0']:.1f} overflow={overflow:.1f}pt")
            
            # テキストブロック分析
            print(f"\n  テキストブロック分析:")
            try:
                # pdfplumberのextract_wordsを使用
                words = page.extract_words()
                rightmost_words = sorted(words, key=lambda w: w['x1'], reverse=True)[:10]
                
                for word in rightmost_words:
                    for margin_name, margin_pt in margin_tests[:2]:  # 最初の2つのマージンのみ
                        text_right_edge = page.width - margin_pt
                        if word['x1'] > text_right_edge:
                            overflow = word['x1'] - text_right_edge
                            print(f"    Word '{word['text']}' x1={word['x1']:.1f} "
                                  f"overflow={overflow:.1f}pt ({margin_name})")
                            break
                            
            except Exception as e:
                print(f"    テキストブロック分析エラー: {e}")

# 分析対象
targets = {
    'sample.pdf': [48],
    'sample2.pdf': [128, 129],
    'sample3.pdf': [13, 35, 36],  # 最初の3つだけ
    'sample4.pdf': [27, 30, 38],  # 最初の3つだけ
    'sample5.pdf': [128, 129]
}

for pdf_file, pages in targets.items():
    if Path(pdf_file).exists():
        analyze_pdf_detailed(pdf_file, pages)
    else:
        print(f"{pdf_file} not found")