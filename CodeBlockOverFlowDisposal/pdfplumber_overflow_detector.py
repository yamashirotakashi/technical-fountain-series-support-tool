#!/usr/bin/env python3
"""
PDFPlumberベースのコードブロックはみ出し検出
グレー背景の矩形（コードブロック）内のテキストのみを検出対象とする
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import pdfplumber
from pdfplumber.page import Page


class PDFPlumberOverflowDetector:
    """PDFPlumberを使用したコードブロックはみ出し検出"""
    
    # B5判のレイアウト（技術の泉シリーズ標準）
    PAGE_WIDTH_MM = 182
    PAGE_HEIGHT_MM = 257
    
    # 本文エリアのマージン（mm）
    # 偶数ページ（左ページ）
    EVEN_PAGE_LEFT_MARGIN_MM = 20    # 左マージン
    EVEN_PAGE_RIGHT_MARGIN_MM = 15   # 右マージン（はみ出し検出対象）
    
    # 奇数ページ（右ページ）
    ODD_PAGE_LEFT_MARGIN_MM = 15     # 左マージン
    ODD_PAGE_RIGHT_MARGIN_MM = 20    # 右マージン（はみ出し検出対象）
    
    # グレー背景の判定閾値（RGB値）
    GRAY_MIN = 200  # グレーと判定する最小値
    GRAY_MAX = 250  # グレーと判定する最大値
    
    # はみ出し判定の許容値（ポイント）
    OVERFLOW_TOLERANCE = 2  # 2pt以上のはみ出しを検出
    
    def __init__(self):
        """初期化"""
        self.results = {}
        self.mm_to_pt = 72 / 25.4  # mmからポイントへの変換係数
        
    def get_page_margins(self, page_number: int) -> Tuple[float, float]:
        """ページ番号に応じたマージンを取得（ポイント単位）"""
        if page_number % 2 == 0:  # 偶数ページ
            left_margin_pt = self.EVEN_PAGE_LEFT_MARGIN_MM * self.mm_to_pt
            right_margin_pt = self.EVEN_PAGE_RIGHT_MARGIN_MM * self.mm_to_pt
        else:  # 奇数ページ
            left_margin_pt = self.ODD_PAGE_LEFT_MARGIN_MM * self.mm_to_pt
            right_margin_pt = self.ODD_PAGE_RIGHT_MARGIN_MM * self.mm_to_pt
        
        return left_margin_pt, right_margin_pt
    
    def is_gray_rect(self, rect: Dict) -> bool:
        """矩形がグレー背景かどうかを判定"""
        # 塗りつぶし色を確認
        fill = rect.get('fill')
        if not fill:
            return False
            
        # fillがTrue（ブール値）の場合、塗りつぶしありと判定
        # この場合、コードブロックの可能性があるので、サイズで判定
        if fill is True:
            # 幅が300pt以上、高さが20pt以上なら、コードブロックの可能性
            width = rect['x1'] - rect['x0']
            height = rect['y1'] - rect['y0']
            return width > 300 and height > 20
            
        # 色が辞書形式の場合（RGB）
        if isinstance(fill, dict):
            # RGBが全て同じ値（グレースケール）で、指定範囲内
            r = fill.get('r', 0) * 255
            g = fill.get('g', 0) * 255
            b = fill.get('b', 0) * 255
            
            # グレースケールかチェック
            if abs(r - g) < 5 and abs(g - b) < 5 and abs(r - b) < 5:
                gray_value = (r + g + b) / 3
                return self.GRAY_MIN <= gray_value <= self.GRAY_MAX
                
        # 色がタプル形式の場合
        elif isinstance(fill, tuple) and len(fill) >= 3:
            r, g, b = fill[:3]
            if isinstance(r, float):
                r, g, b = r * 255, g * 255, b * 255
            
            # グレースケールかチェック
            if abs(r - g) < 5 and abs(g - b) < 5 and abs(r - b) < 5:
                gray_value = (r + g + b) / 3
                return self.GRAY_MIN <= gray_value <= self.GRAY_MAX
                
        return False
    
    def check_text_overflow_in_rect(self, page: Page, rect: Dict, 
                                   page_number: int) -> List[Dict]:
        """矩形内のテキストのはみ出しをチェック"""
        overflows = []
        
        # 矩形の座標
        rect_left = rect['x0']
        rect_right = rect['x1']
        rect_top = rect['y0']
        rect_bottom = rect['y1']
        
        # ページのマージンを取得
        _, right_margin_pt = self.get_page_margins(page_number)
        
        # 本文エリアの右端
        page_width = float(page.width)
        text_right_edge = page_width - right_margin_pt
        
        # 矩形内のテキストを取得
        # croppingで矩形内の領域を切り出し
        cropped = page.within_bbox((rect_left, rect_top, rect_right, rect_bottom))
        
        # テキストを文字単位で取得
        chars = cropped.chars
        
        # 行ごとにグループ化
        lines = {}
        for char in chars:
            y_pos = round(char['y0'])  # Y座標を丸めて行を判定
            if y_pos not in lines:
                lines[y_pos] = []
            lines[y_pos].append(char)
        
        # 各行をチェック
        for y_pos, line_chars in lines.items():
            # 行の文字をX座標でソート
            line_chars.sort(key=lambda c: c['x0'])
            
            # 行の最も右にある文字を確認
            if line_chars:
                rightmost_char = max(line_chars, key=lambda c: c['x1'])
                char_right = rightmost_char['x1']
                
                # 矩形の右端を超えているかチェック（特に「r」以降）
                # 48ページの場合、rから始まる部分がはみ出し
                if char_right > rect_right:
                    # 矩形を超えている文字を探す
                    overflow_chars = [c for c in line_chars if c['x1'] > rect_right]
                    if overflow_chars:
                        # 行全体のテキストを取得
                        line_text = ''.join([c['text'] for c in line_chars])
                        first_overflow = overflow_chars[0]
                        
                        overflows.append({
                            'text': line_text,
                            'char': first_overflow['text'],
                            'position': (first_overflow['x0'], first_overflow['y0']),
                            'overflow_amount': char_right - rect_right,
                            'rect_bounds': (rect_left, rect_top, rect_right, rect_bottom),
                            'rightmost_pos': char_right
                        })
        
        return overflows
    
    def process_page(self, page: Page, page_number: int) -> List[Dict]:
        """1ページを処理してはみ出しを検出"""
        page_overflows = []
        
        # ページ内の矩形を取得
        rects = page.rects
        
        # グレー背景の矩形を探す
        gray_rects = []
        for rect in rects:
            if self.is_gray_rect(rect):
                gray_rects.append(rect)
        
        # 各グレー矩形内のテキストをチェック
        for rect in gray_rects:
            overflows = self.check_text_overflow_in_rect(page, rect, page_number)
            page_overflows.extend(overflows)
        
        return page_overflows
    
    def process_pdf(self, pdf_path: Path) -> Dict[int, List[Dict]]:
        """PDFファイル全体を処理"""
        print(f"処理開始: {pdf_path}")
        print("グレー背景のコードブロック内のテキストのみを検出対象とします")
        
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
                        print(f"  ページ {page_number}: {len(overflows)} 件のはみ出しを検出")
                        
        except Exception as e:
            print(f"エラー: {e}")
            raise
            
        return overflow_pages
    
    def save_results(self, pdf_path: Path, overflow_pages: Dict[int, List[Dict]], 
                    output_path: Path):
        """結果をtestresult.mdに保存"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# PDFPlumberコードブロックはみ出し検出結果\n\n")
            f.write(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## 検出パラメータ\n")
            f.write("- 検出対象: グレー背景のコードブロック内のテキストのみ\n")
            f.write("- グレー判定閾値: RGB 200-250\n")
            f.write(f"- はみ出し許容値: {self.OVERFLOW_TOLERANCE}pt\n")
            f.write("- 検出対象: 右端のみ（左端は無視）\n")
            f.write("- 奇数ページ右マージン: 20mm\n")
            f.write("- 偶数ページ右マージン: 15mm\n\n")
            
            f.write("## 検出結果\n\n")
            
            if overflow_pages:
                page_list = sorted(overflow_pages.keys())
                page_str = ", ".join(map(str, page_list))
                f.write(f"### {pdf_path.name}: ページ {page_str}\n\n")
                
                f.write("## 詳細情報\n\n")
                for page_num in page_list:
                    f.write(f"### ページ {page_num}\n")
                    overflows = overflow_pages[page_num]
                    f.write(f"検出数: {len(overflows)}件\n\n")
                    
                    for i, overflow in enumerate(overflows, 1):
                        f.write(f"{i}. コードブロック内のはみ出し\n")
                        f.write(f"   テキスト: `{overflow['text'][:50]}...`\n")
                        f.write(f"   はみ出し文字: '{overflow['char']}'\n")
                        f.write(f"   はみ出し量: {overflow['overflow_amount']:.1f}pt\n")
                        f.write(f"   位置: ({overflow['position'][0]:.1f}, {overflow['position'][1]:.1f})\n")
                        f.write(f"   コードブロック範囲: {overflow['rect_bounds']}\n\n")
            else:
                f.write(f"### {pdf_path.name}: はみ出しなし\n\n")
            
            f.write("\n## 注記\n")
            f.write("- グレー背景のコードブロック内のテキストのみを検出対象としています\n")
            f.write("- 行番号や本文は検出対象外です\n")
            f.write("- 目視確認が必要です：PDFを開いて実際のはみ出しと比較してください\n")


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='PDFPlumberによるコードブロックはみ出し検出'
    )
    parser.add_argument('pdf_files', nargs='+', help='検査するPDFファイル')
    parser.add_argument('--tolerance', type=float, default=2.0,
                       help='はみ出し許容値（ポイント、デフォルト: 2.0）')
    
    args = parser.parse_args()
    
    # 検出器を初期化
    detector = PDFPlumberOverflowDetector()
    detector.OVERFLOW_TOLERANCE = args.tolerance
    
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
        # 最初のPDFの結果を保存（複数ファイル対応は要拡張）
        first_pdf = Path(args.pdf_files[0])
        first_results = all_results.get(first_pdf.name, {})
        detector.save_results(first_pdf, first_results, output_path)
        print(f"\n結果を {output_path} に保存しました。")
        print("PDFを目視確認して、実際のはみ出しと比較してください。")


if __name__ == "__main__":
    main()