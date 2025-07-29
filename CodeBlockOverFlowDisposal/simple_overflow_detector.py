#!/usr/bin/env python3
"""
シンプルなはみ出し検出 - 本文領域の右端基準
48ページの「r」の文字中心を基準として検出
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import pdfplumber


class SimpleOverflowDetector:
    """本文領域右端を基準としたシンプルなはみ出し検出"""
    
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
    
    def __init__(self):
        """初期化"""
        self.mm_to_pt = 72 / 25.4  # mmからポイントへの変換係数
        # 48ページのrの中心位置を基準値として設定（実測値）
        self.reference_r_center = 438.0  # デバッグ情報から取得したrのx座標
        # 48ページのページ幅（実測値）
        self.page_48_width = 515.93  # pt
        
    def get_page_margins(self, page_number: int) -> float:
        """ページ番号に応じた右マージンを取得（ポイント単位）"""
        if page_number % 2 == 0:  # 偶数ページ
            return self.EVEN_PAGE_RIGHT_MARGIN_MM * self.mm_to_pt
        else:  # 奇数ページ
            return self.ODD_PAGE_RIGHT_MARGIN_MM * self.mm_to_pt
    
    def calculate_text_right_edge(self, page_width: float, page_number: int) -> float:
        """本文領域の右端座標を計算"""
        right_margin_pt = self.get_page_margins(page_number)
        
        # 48ページの場合は実測値を使用
        if page_number == 48:
            return self.reference_r_center
        
        # その他のページは標準マージンから計算
        # ただし、48ページ（偶数ページ）の実測値を基準に調整
        base_right_edge = page_width - right_margin_pt
        
        # 48ページでの実測値と計算値の差分
        # 48ページは偶数ページなので、偶数ページの調整値を計算
        page_48_calculated = page_width - (self.EVEN_PAGE_RIGHT_MARGIN_MM * self.mm_to_pt)
        adjustment = self.reference_r_center - page_48_calculated
        
        if page_number % 2 == 0:  # 偶数ページ
            # 48ページと同じ調整を適用
            return base_right_edge + adjustment
        else:  # 奇数ページ
            # 奇数ページは左右が逆なので、調整も考慮
            return base_right_edge + adjustment
    
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
                # 文字の中心位置を計算
                char_center_x = (char['x0'] + char['x1']) / 2
                
                # 文字中心が本文右端を超えているかチェック
                if char_center_x > text_right_edge:
                    overflow_chars.append(char)
            
            if overflow_chars:
                # 行全体のテキストを取得
                line_text = ''.join([c['text'] for c in line_chars])
                
                # はみ出し部分のテキスト
                overflow_text = ''.join([c['text'] for c in overflow_chars])
                
                # 最も右の文字の位置
                rightmost_char = max(line_chars, key=lambda c: c['x1'])
                
                overflows.append({
                    'page': page_number,
                    'y_position': y_pos,
                    'line_text': line_text,
                    'overflow_text': overflow_text,
                    'overflow_start': overflow_chars[0]['text'],
                    'overflow_start_pos': overflow_chars[0]['x0'],
                    'rightmost_pos': rightmost_char['x1'],
                    'overflow_amount': rightmost_char['x1'] - text_right_edge,
                    'text_right_edge': text_right_edge
                })
        
        return overflows
    
    def process_pdf(self, pdf_path: Path) -> Dict[int, List[Dict]]:
        """PDFファイル全体を処理"""
        print(f"処理開始: {pdf_path}")
        print("本文領域右端を基準とした検出（48ページは'r'の中心位置を基準）")
        
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
            f.write("# シンプルはみ出し検出結果\n\n")
            f.write(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## 検出パラメータ\n")
            f.write("- 検出方法: 本文領域右端を基準（グレー背景に関係なく検出）\n")
            f.write("- 48ページ基準: 'r'の文字中心位置を本文右端として使用\n")
            f.write("- 判定基準: 文字の中心が本文右端を超える場合をはみ出しと判定\n")
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
                    f.write(f"検出数: {len(overflows)}件\n")
                    f.write(f"本文右端: {overflows[0]['text_right_edge']:.1f}pt\n\n")
                    
                    for i, overflow in enumerate(overflows[:10], 1):  # 最初の10件
                        f.write(f"{i}. はみ出し検出\n")
                        f.write(f"   行テキスト: `{overflow['line_text'][:60]}...`\n")
                        f.write(f"   はみ出し部分: `{overflow['overflow_text']}`\n")
                        f.write(f"   はみ出し開始: '{overflow['overflow_start']}' at {overflow['overflow_start_pos']:.1f}pt\n")
                        f.write(f"   はみ出し量: {overflow['overflow_amount']:.1f}pt\n\n")
                    
                    if len(overflows) > 10:
                        f.write(f"... 他 {len(overflows) - 10} 件\n\n")
            else:
                f.write(f"### {pdf_path.name}: はみ出しなし\n\n")
            
            f.write("\n## 注記\n")
            f.write("- 本文領域の右端を基準とし、グレー背景に関係なくすべての文字を検出対象としています\n")
            f.write("- 48ページでは実測値（'r'の文字中心）を基準としています\n")
            f.write("- 文字の中心位置で判定することで、境界付近の誤検出を減らしています\n")


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='シンプルなはみ出し検出（本文領域右端基準）'
    )
    parser.add_argument('pdf_files', nargs='+', help='検査するPDFファイル')
    
    args = parser.parse_args()
    
    # 検出器を初期化
    detector = SimpleOverflowDetector()
    
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
                print(f"  検出ページ: {page_list[:10]}{'...' if len(page_list) > 10 else ''}")
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