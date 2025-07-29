#!/usr/bin/env python3
"""
検出漏れページの詳細分析 v2
より広い範囲で文字を探索
"""

import pdfplumber
from pathlib import Path
from typing import List, Dict


class MissedPageAnalyzerV2:
    """検出漏れページの分析器 v2"""
    
    def __init__(self):
        self.mm_to_pt = 72 / 25.4
        # B5判の右マージン
        self.even_page_right_margin_mm = 15
        self.odd_page_right_margin_mm = 20
    
    def calculate_text_right_edge(self, page_width: float, page_number: int) -> float:
        """本文領域の右端座標を計算"""
        if page_number % 2 == 0:  # 偶数ページ
            right_margin_pt = self.even_page_right_margin_mm * self.mm_to_pt
        else:  # 奇数ページ
            right_margin_pt = self.odd_page_right_margin_mm * self.mm_to_pt
            
        return page_width - right_margin_pt
    
    def analyze_page(self, page, page_number: int):
        """ページの詳細分析"""
        print(f"\n{'='*60}")
        print(f"ページ {page_number} の詳細分析")
        print(f"{'='*60}")
        print(f"ページタイプ: {'偶数' if page_number % 2 == 0 else '奇数'}ページ")
        print(f"ページサイズ: {page.width:.1f} x {page.height:.1f} pt")
        
        text_right_edge = self.calculate_text_right_edge(page.width, page_number)
        print(f"本文領域右端: {text_right_edge:.1f} pt")
        
        # グレー背景矩形（コードブロック）を検出
        code_blocks = []
        all_rects = []
        for rect in page.rects:
            all_rects.append(rect)
            if rect.get('fill'):
                width = rect['x1'] - rect['x0']
                height = rect['y1'] - rect['y0']
                if width > 300 and height > 20:
                    code_blocks.append(rect)
                    print(f"\nコードブロック: x0={rect['x0']:.1f}, y0={rect['y0']:.1f}, "
                          f"x1={rect['x1']:.1f}, y1={rect['y1']:.1f} "
                          f"(幅={width:.1f}, 高さ={height:.1f})")
        
        print(f"\n総矩形数: {len(all_rects)}")
        print(f"コードブロック数: {len(code_blocks)}")
        
        # 文字の分布を分析
        print("\n--- 文字分布の分析 ---")
        chars_in_code = 0
        chars_outside_code = 0
        rightmost_chars = []
        
        for char in page.chars:
            # コードブロック内かチェック
            in_code_block = any(
                cb['x0'] <= char['x0'] <= cb['x1'] and
                cb['y0'] <= char['y0'] <= cb['y1']
                for cb in code_blocks
            )
            
            if in_code_block:
                chars_in_code += 1
                # コードブロック内で右端に近い文字を記録
                distance = char['x1'] - text_right_edge
                if distance > -50:  # 右端から50pt以内
                    rightmost_chars.append({
                        'char': char['text'],
                        'x0': char['x0'],
                        'x1': char['x1'],
                        'y0': char['y0'],
                        'distance': distance,
                        'char_type': self.classify_char(char['text'])
                    })
            else:
                chars_outside_code += 1
        
        print(f"コードブロック内の文字数: {chars_in_code}")
        print(f"コードブロック外の文字数: {chars_outside_code}")
        
        # 右端の文字を表示
        if rightmost_chars:
            rightmost_chars.sort(key=lambda x: x['distance'], reverse=True)
            print("\n--- コードブロック内の右端文字（上位20件） ---")
            print("No. | 文字 | 種別 | X座標 | 右端との距離 | 状態")
            print("-" * 70)
            
            for i, info in enumerate(rightmost_chars[:20]):
                status = "超過" if info['distance'] > 0 else "境界内"
                print(f"{i+1:2d} | '{info['char']}' | {info['char_type']:12s} | "
                      f"{info['x1']:6.1f} | {info['distance']:+8.2f}pt | {status}")
        
        # 閾値別の検出数を表示
        print("\n--- 英数字・ASCII記号の閾値別検出数 ---")
        ascii_chars = [c for c in rightmost_chars 
                      if c['char_type'] in ['digit', 'alphabet', 'ascii_symbol']]
        
        thresholds = [-0.5, -0.3, -0.1, 0, 0.1, 0.3, 0.5, 1.0]
        for threshold in thresholds:
            count = sum(1 for c in ascii_chars if c['distance'] > threshold)
            if count > 0 or threshold <= 0.5:
                print(f"閾値 {threshold:+.1f}pt: {count}文字")
        
        # 最も右にある英数字を詳細表示
        if ascii_chars:
            print("\n--- 最も右にある英数字（上位5件） ---")
            for i, char in enumerate(ascii_chars[:5]):
                print(f"{i+1}. '{char['char']}' at x1={char['x1']:.1f}, "
                      f"距離={char['distance']:.2f}pt")
    
    def classify_char(self, char: str) -> str:
        """文字を分類"""
        if not char:
            return 'empty'
        
        code = ord(char[0])
        
        if code < 128:
            if 48 <= code <= 57:
                return 'digit'
            elif 65 <= code <= 90 or 97 <= code <= 122:
                return 'alphabet'
            elif 32 <= code < 127:
                return 'ascii_symbol'
            else:
                return 'control'
        elif 0x3040 <= code <= 0x309F:
            return 'hiragana'
        elif 0x30A0 <= code <= 0x30FF:
            return 'katakana'
        elif 0x4E00 <= code <= 0x9FAF:
            return 'kanji'
        
        return 'other'
    
    def analyze_pdf(self, pdf_path: Path, target_pages: List[int]):
        """PDFの特定ページを分析"""
        print(f"分析対象: {pdf_path.name}")
        print(f"対象ページ: {target_pages}")
        
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page_num in target_pages:
                if 1 <= page_num <= len(pdf.pages):
                    page = pdf.pages[page_num - 1]
                    self.analyze_page(page, page_num)
                else:
                    print(f"\n警告: ページ {page_num} は存在しません")


def main():
    analyzer = MissedPageAnalyzerV2()
    
    # sample4.pdfの検出漏れページを分析
    pdf_path = Path("sample4.pdf")
    missed_pages = [30, 38, 76]
    
    analyzer.analyze_pdf(pdf_path, missed_pages)
    
    print("\n" + "="*60)
    print("分析結果のまとめ")
    print("="*60)
    print("検出漏れの原因を特定するため、閾値の調整が必要な可能性があります。")
    print("特に偶数ページでの検出感度を上げる必要があるかもしれません。")


if __name__ == "__main__":
    main()