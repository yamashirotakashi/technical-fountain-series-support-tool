#!/usr/bin/env python3
"""
検出漏れページの詳細分析
"""

import pdfplumber
from pathlib import Path
from typing import List, Dict


class MissedPageAnalyzer:
    """検出漏れページの分析器"""
    
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
        print(f"\n=== ページ {page_number} の詳細分析 ===")
        print(f"ページタイプ: {'偶数' if page_number % 2 == 0 else '奇数'}ページ")
        print(f"ページサイズ: {page.width:.1f} x {page.height:.1f} pt")
        
        text_right_edge = self.calculate_text_right_edge(page.width, page_number)
        print(f"本文領域右端: {text_right_edge:.1f} pt")
        
        # グレー背景矩形（コードブロック）を検出
        code_blocks = []
        for rect in page.rects:
            if rect.get('fill'):
                width = rect['x1'] - rect['x0']
                height = rect['y1'] - rect['y0']
                if width > 300 and height > 20:
                    code_blocks.append(rect)
        
        print(f"コードブロック数: {len(code_blocks)}")
        
        # 右端に近い文字を分析
        print("\n--- 右端付近の文字分析 ---")
        
        # 行ごとにグループ化
        lines = {}
        for char in page.chars:
            if char['y0'] < 50 or char['y0'] > page.height - 50:
                continue
            y_pos = round(char['y0'])
            if y_pos not in lines:
                lines[y_pos] = []
            lines[y_pos].append(char)
        
        # 各行をチェック
        potential_overflows = []
        for y_pos, line_chars in lines.items():
            line_chars.sort(key=lambda c: c['x0'])
            
            # 右端に近い文字を探す
            for char in line_chars:
                distance_from_edge = char['x1'] - text_right_edge
                
                # 右端から前後5pt以内の文字を記録
                if abs(distance_from_edge) < 5:
                    # コードブロック内かチェック
                    in_code_block = any(
                        cb['x0'] <= char['x0'] <= cb['x1'] and
                        cb['y0'] <= char['y0'] <= cb['y1']
                        for cb in code_blocks
                    )
                    
                    if in_code_block:
                        char_info = {
                            'char': char['text'],
                            'x1': char['x1'],
                            'distance': distance_from_edge,
                            'y_pos': y_pos,
                            'char_type': self.classify_char(char['text'])
                        }
                        potential_overflows.append(char_info)
        
        # 最も右端に近い文字を表示
        if potential_overflows:
            potential_overflows.sort(key=lambda x: x['distance'], reverse=True)
            print("\n最も右端に近い文字（上位10件）:")
            for i, info in enumerate(potential_overflows[:10]):
                status = "超過" if info['distance'] > 0 else "境界内"
                print(f"{i+1}. Y={info['y_pos']}: '{info['char']}' "
                      f"({info['char_type']}) "
                      f"x1={info['x1']:.1f}, "
                      f"距離={info['distance']:.2f}pt [{status}]")
        
        # 閾値別の検出数を表示
        print("\n--- 閾値別の検出可能性 ---")
        thresholds = [0.1, 0.3, 0.5, 1.0, 2.0]
        for threshold in thresholds:
            count = sum(1 for info in potential_overflows 
                       if info['distance'] > threshold and 
                       info['char_type'] in ['digit', 'alphabet', 'ascii_symbol'])
            if count > 0:
                print(f"閾値 {threshold}pt: {count}文字が検出対象")
    
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
    analyzer = MissedPageAnalyzer()
    
    # sample4.pdfの検出漏れページを分析
    pdf_path = Path("sample4.pdf")
    missed_pages = [30, 38, 76]
    
    analyzer.analyze_pdf(pdf_path, missed_pages)


if __name__ == "__main__":
    main()