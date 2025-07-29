#!/usr/bin/env python3
"""
精密なはみ出し検出 - 48ページの実測値を基準に本文領域を正確に設定
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import pdfplumber


class PreciseOverflowDetector:
    """48ページの実測値を基準とした精密なはみ出し検出"""
    
    def __init__(self):
        """初期化"""
        # 48ページの実測値
        self.page_48_width = 515.93  # ページ幅 (pt)
        self.reference_r_x1 = 438.0  # 'r'のx1座標（右端）
        
        # mm to pt変換
        self.mm_to_pt = 72 / 25.4
        
        # 本文領域の右端を計算
        # 48ページ（偶数ページ）での本文右端 = rの右端
        self.even_page_text_right = self.reference_r_x1
        
        # 奇数ページと偶数ページの本文幅は同じと仮定
        # 偶数ページ：左20mm、右15mm → 本文幅 = ページ幅 - 35mm
        # 奇数ページ：左15mm、右20mm → 本文幅 = ページ幅 - 35mm
        # ただし、実測値から逆算
        left_margin_even = 20 * self.mm_to_pt  # 偶数ページの左マージン
        self.text_width = self.even_page_text_right - left_margin_even
        
    def calculate_text_right_edge(self, page_width: float, page_number: int) -> float:
        """本文領域の右端座標を計算"""
        
        if page_number % 2 == 0:  # 偶数ページ
            # 48ページと同じ位置関係を保つ
            # ページ幅が異なる場合も、右マージンは一定と仮定
            right_margin = self.page_48_width - self.even_page_text_right
            return page_width - right_margin
        else:  # 奇数ページ
            # 奇数ページは左マージンが15mm、右マージンが20mm
            # 本文幅は同じなので、左マージン + 本文幅
            left_margin_odd = 15 * self.mm_to_pt
            return left_margin_odd + self.text_width
    
    def is_likely_overflow(self, char: Dict, text_right_edge: float, page_number: int) -> bool:
        """文字がはみ出しかどうかを判定"""
        # 文字の右端が本文右端を超えているか
        char_right = char['x1']
        
        # ページ番号などの特殊な位置にある文字は除外
        # Y座標が極端に上部（50pt以下）または下部（650pt以上）の文字は除外
        if char['y0'] < 50 or char['y0'] > 650:
            return False
        
        # 文字が本文右端を超えている場合
        if char_right > text_right_edge:
            # ただし、わずかな超過（1pt未満）は許容
            if char_right - text_right_edge < 1.0:
                return False
            return True
        
        return False
    
    def process_page(self, page, page_number: int) -> List[Dict]:
        """1ページを処理してはみ出しを検出"""
        overflows = []
        
        # 本文領域の右端を計算
        text_right_edge = self.calculate_text_right_edge(page.width, page_number)
        
        # すべての文字を取得
        chars = page.chars
        
        # 行ごとにグループ化
        lines = {}
        for char in chars:
            # Y座標を丸めて行を判定（2pt以内は同じ行）
            y_pos = round(char['y0'] / 2) * 2
            if y_pos not in lines:
                lines[y_pos] = []
            lines[y_pos].append(char)
        
        # 各行をチェック
        for y_pos, line_chars in lines.items():
            # 行の文字をX座標でソート
            line_chars.sort(key=lambda c: c['x0'])
            
            # 本文右端を超える文字を探す
            overflow_chars = []
            for char in line_chars:
                if self.is_likely_overflow(char, text_right_edge, page_number):
                    overflow_chars.append(char)
            
            if overflow_chars:
                # 連続する文字のみを対象とする（孤立した文字は除外）
                if len(overflow_chars) >= 2 or (len(overflow_chars) == 1 and len(line_chars) > 10):
                    # 行全体のテキストを取得
                    line_text = ''.join([c['text'] for c in line_chars])
                    
                    # はみ出し部分のテキスト
                    overflow_text = ''.join([c['text'] for c in overflow_chars])
                    
                    # 最も右の文字の位置
                    rightmost_char = max(overflow_chars, key=lambda c: c['x1'])
                    
                    overflows.append({
                        'page': page_number,
                        'y_position': y_pos,
                        'line_text': line_text,
                        'overflow_text': overflow_text,
                        'overflow_start': overflow_chars[0]['text'],
                        'overflow_start_pos': overflow_chars[0]['x0'],
                        'rightmost_pos': rightmost_char['x1'],
                        'overflow_amount': rightmost_char['x1'] - text_right_edge,
                        'text_right_edge': text_right_edge,
                        'char_count': len(overflow_chars)
                    })
        
        return overflows
    
    def process_pdf(self, pdf_path: Path) -> Dict[int, List[Dict]]:
        """PDFファイル全体を処理"""
        print(f"処理開始: {pdf_path}")
        print("48ページの実測値を基準とした精密な検出")
        
        overflow_pages = {}
        
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                total_pages = len(pdf.pages)
                
                for i, page in enumerate(pdf.pages):
                    page_number = i + 1
                    
                    if page_number % 10 == 0:
                        print(f"処理中: {page_number}/{total_pages} ページ...")
                    
                    # ページを処理
                    overflows = self.process_page(page, page_number)
                    
                    if overflows:
                        overflow_pages[page_number] = overflows
                        
        except Exception as e:
            print(f"エラー: {e}")
            raise
            
        return overflow_pages
    
    def save_results(self, pdf_path: Path, overflow_pages: Dict[int, List[Dict]], 
                    output_path: Path):
        """結果をtestresult.mdに保存"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 精密はみ出し検出結果\n\n")
            f.write(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## 検出パラメータ\n")
            f.write("- 検出方法: 48ページの実測値を基準とした精密検出\n")
            f.write("- 48ページ基準: 'r'の右端（x=438.0pt）を偶数ページの本文右端として使用\n")
            f.write("- 判定基準: 文字の右端が本文右端を1pt以上超える場合\n")
            f.write("- 除外条件: ページ番号領域、孤立した文字\n\n")
            
            f.write("## 検出結果\n\n")
            
            if overflow_pages:
                page_list = sorted(overflow_pages.keys())
                page_str = ", ".join(map(str, page_list))
                f.write(f"### {pdf_path.name}: ページ {page_str}\n\n")
                
                f.write("## 詳細情報\n\n")
                for page_num in page_list:
                    f.write(f"### ページ {page_num}\n")
                    overflows = overflow_pages[page_num]
                    f.write(f"検出数: {len(overflows)}件\n")
                    f.write(f"本文右端: {overflows[0]['text_right_edge']:.1f}pt\n\n")
                    
                    for i, overflow in enumerate(overflows[:5], 1):  # 最初の5件
                        f.write(f"{i}. はみ出し検出\n")
                        f.write(f"   行テキスト: `{overflow['line_text'][:60]}...`\n")
                        f.write(f"   はみ出し部分: `{overflow['overflow_text']}` ({overflow['char_count']}文字)\n")
                        f.write(f"   はみ出し開始: '{overflow['overflow_start']}' at {overflow['overflow_start_pos']:.1f}pt\n")
                        f.write(f"   はみ出し量: {overflow['overflow_amount']:.1f}pt\n\n")
                    
                    if len(overflows) > 5:
                        f.write(f"... 他 {len(overflows) - 5} 件\n\n")
            else:
                f.write(f"### {pdf_path.name}: はみ出しなし\n\n")
            
            f.write("\n## 注記\n")
            f.write("- 48ページの実測値から本文領域を精密に計算しています\n")
            f.write("- ページ番号などの特殊な位置の文字は除外しています\n")
            f.write("- 連続する複数文字のはみ出しのみを検出対象としています\n")


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='精密なはみ出し検出（48ページ基準）'
    )
    parser.add_argument('pdf_files', nargs='+', help='検査するPDFファイル')
    
    args = parser.parse_args()
    
    # 検出器を初期化
    detector = PreciseOverflowDetector()
    
    # 全結果を格納
    all_results = {}
    
    # 各PDFを処理
    for pdf_path_str in args.pdf_files:
        pdf_path = Path(pdf_path_str)
        if not pdf_path.exists():
            print(f"警告: ファイルが見つかりません: {pdf_path}")
            continue
        
        try:
            overflow_pages = detector.process_pdf(pdf_path)
            all_results[pdf_path.name] = overflow_pages
            
            # 結果サマリー
            if overflow_pages:
                page_list = sorted(overflow_pages.keys())
                total_overflows = sum(len(overflows) for overflows in overflow_pages.values())
                print(f"\n{pdf_path.name}: {len(page_list)}ページで計{total_overflows}件のはみ出しを検出")
                print(f"  検出ページ: {page_list}")
            else:
                print(f"\n{pdf_path.name}: はみ出しなし")
                
        except Exception as e:
            print(f"エラー: {pdf_path.name} の処理中にエラー: {e}")
            import traceback
            traceback.print_exc()
    
    # 結果を保存
    if all_results:
        output_path = Path("testresult.md")
        # 最初のPDFの結果を保存
        first_pdf = Path(args.pdf_files[0])
        first_results = all_results.get(first_pdf.name, {})
        detector.save_results(first_pdf, first_results, output_path)
        print(f"\n結果を {output_path} に保存しました。")
        print("PDFを目視確認して、実際のはみ出しと比較してください。")


if __name__ == "__main__":
    main()