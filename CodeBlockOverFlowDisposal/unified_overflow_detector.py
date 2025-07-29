#!/usr/bin/env python3
"""
統合はみ出し検出器 - 複数のPDFタイプに対応
sample.pdf: 48ページのみ（偶数ページ）
sample2.pdf: 128ページ（偶数）と129ページ（奇数）
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import pdfplumber


class UnifiedOverflowDetector:
    """統合はみ出し検出器"""
    
    def __init__(self):
        """初期化"""
        self.mm_to_pt = 72 / 25.4
        
        # 既知のはみ出しページの実測値
        self.known_overflows = {
            'sample.pdf': {
                48: {  # 偶数ページ
                    'type': 'even',
                    'reference_char': 'r',
                    'reference_x1': 438.0,
                    'page_width': 515.93
                }
            },
            'sample2.pdf': {
                128: {  # 偶数ページ
                    'type': 'even',
                    'overflows': [
                        {'y': 137.6, 'char': ')', 'x1': 442.7},
                        {'y': 251.0, 'char': ')', 'x1': 442.7}
                    ],
                    'rect_right': 435.1,
                    'page_width': 515.93
                },
                129: {  # 奇数ページ
                    'type': 'odd',
                    'overflows': [
                        {'y': 520.3, 'text': 'Span)', 'x1': 482.8},
                        {'y': 619.5, 'text': 'pan)', 'x1': 478.1}
                    ],
                    'rect_right': 470.5,
                    'page_width': 515.93
                }
            }
        }
    
    def detect_code_blocks(self, page) -> List[Dict]:
        """コードブロック（グレー背景矩形）を検出"""
        code_blocks = []
        
        for rect in page.rects:
            if rect.get('fill'):
                # 塗りつぶしがある矩形
                width = rect['x1'] - rect['x0']
                height = rect['y1'] - rect['y0']
                
                # コードブロックサイズの判定（幅300pt以上、高さ20pt以上）
                if width > 300 and height > 20:
                    code_blocks.append(rect)
        
        return code_blocks
    
    def check_overflow_in_rect(self, page, rect: Dict, page_number: int, 
                              pdf_name: str) -> List[Dict]:
        """矩形内のはみ出しをチェック"""
        overflows = []
        
        # 矩形の右端
        rect_right = rect['x1']
        
        # 矩形内のテキストを取得
        cropped = page.within_bbox((rect['x0'], rect['y0'], rect['x1'], rect['y1']))
        chars = cropped.chars
        
        # 行ごとにグループ化
        lines = {}
        for char in chars:
            y_pos = round(char['y0'])
            if y_pos not in lines:
                lines[y_pos] = []
            lines[y_pos].append(char)
        
        # 各行をチェック
        for y_pos, line_chars in lines.items():
            line_chars.sort(key=lambda c: c['x0'])
            
            # 矩形の右端を超える文字を探す
            overflow_chars = []
            for char in line_chars:
                if char['x1'] > rect_right + 0.5:  # 0.5pt以上の超過
                    overflow_chars.append(char)
            
            if overflow_chars:
                # 行全体のテキストを取得
                line_text = ''.join([c['text'] for c in line_chars])
                
                # はみ出し部分のテキスト
                overflow_text = ''.join([c['text'] for c in overflow_chars])
                
                # 最も右の文字
                rightmost_char = max(overflow_chars, key=lambda c: c['x1'])
                
                overflows.append({
                    'page': page_number,
                    'y_position': y_pos,
                    'line_text': line_text,
                    'overflow_text': overflow_text,
                    'overflow_start': overflow_chars[0]['text'],
                    'overflow_start_pos': overflow_chars[0]['x0'],
                    'rightmost_pos': rightmost_char['x1'],
                    'overflow_amount': rightmost_char['x1'] - rect_right,
                    'rect_right': rect_right
                })
        
        return overflows
    
    def process_page(self, page, page_number: int, pdf_name: str) -> List[Dict]:
        """1ページを処理してはみ出しを検出"""
        all_overflows = []
        
        # コードブロックを検出
        code_blocks = self.detect_code_blocks(page)
        
        # 各コードブロック内のはみ出しをチェック
        for rect in code_blocks:
            overflows = self.check_overflow_in_rect(page, rect, page_number, pdf_name)
            all_overflows.extend(overflows)
        
        return all_overflows
    
    def process_pdf(self, pdf_path: Path) -> Dict[int, List[Dict]]:
        """PDFファイル全体を処理"""
        pdf_name = pdf_path.name
        print(f"処理開始: {pdf_name}")
        print("コードブロック（グレー背景矩形）内のはみ出しを検出")
        
        overflow_pages = {}
        
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                total_pages = len(pdf.pages)
                
                for i, page in enumerate(pdf.pages):
                    page_number = i + 1
                    
                    if page_number % 10 == 0:
                        print(f"処理中: {page_number}/{total_pages} ページ...")
                    
                    # ページを処理
                    overflows = self.process_page(page, page_number, pdf_name)
                    
                    if overflows:
                        overflow_pages[page_number] = overflows
                        
        except Exception as e:
            print(f"エラー: {e}")
            raise
            
        return overflow_pages
    
    def save_results(self, results: Dict[str, Dict], output_path: Path):
        """結果をtestresult.mdに保存"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 統合はみ出し検出結果\n\n")
            f.write(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## 検出パラメータ\n")
            f.write("- 検出方法: コードブロック（グレー背景矩形）の右端を基準\n")
            f.write("- 判定基準: 文字が矩形の右端を0.5pt以上超える場合\n")
            f.write("- 既知のはみ出し:\n")
            f.write("  - sample.pdf: 48ページ\n")
            f.write("  - sample2.pdf: 128ページ（2箇所）、129ページ（2箇所）\n\n")
            
            f.write("## 検出結果サマリー\n\n")
            
            for pdf_name, overflow_pages in results.items():
                if overflow_pages:
                    page_list = sorted(overflow_pages.keys())
                    total_overflows = sum(len(overflows) for overflows in overflow_pages.values())
                    f.write(f"### {pdf_name}\n")
                    f.write(f"- 検出ページ数: {len(page_list)}\n")
                    f.write(f"- 総はみ出し数: {total_overflows}\n")
                    f.write(f"- ページリスト: {', '.join(map(str, page_list[:20]))}")
                    if len(page_list) > 20:
                        f.write("...")
                    f.write("\n\n")
                else:
                    f.write(f"### {pdf_name}: はみ出しなし\n\n")
            
            f.write("## 詳細情報\n\n")
            
            # 既知のはみ出しページの詳細を優先表示
            for pdf_name in ['sample.pdf', 'sample2.pdf']:
                if pdf_name in results:
                    overflow_pages = results[pdf_name]
                    if pdf_name in self.known_overflows:
                        known_pages = self.known_overflows[pdf_name].keys()
                        
                        f.write(f"### {pdf_name} - 既知のはみ出しページ\n\n")
                        
                        for page_num in sorted(known_pages):
                            if page_num in overflow_pages:
                                f.write(f"#### ページ {page_num}\n")
                                overflows = overflow_pages[page_num]
                                f.write(f"検出数: {len(overflows)}件\n\n")
                                
                                for i, overflow in enumerate(overflows, 1):
                                    f.write(f"{i}. はみ出し検出\n")
                                    f.write(f"   Y座標: {overflow['y_position']}\n")
                                    f.write(f"   行テキスト: `{overflow['line_text'][:50]}...`\n")
                                    f.write(f"   はみ出し部分: `{overflow['overflow_text']}`\n")
                                    f.write(f"   矩形右端: {overflow['rect_right']:.1f}pt\n")
                                    f.write(f"   文字右端: {overflow['rightmost_pos']:.1f}pt\n")
                                    f.write(f"   はみ出し量: {overflow['overflow_amount']:.1f}pt\n\n")
            
            f.write("\n## 注記\n")
            f.write("- コードブロック（グレー背景矩形）内のテキストのみを検出対象としています\n")
            f.write("- 矩形の右端を基準として、それを超える文字をはみ出しと判定しています\n")
            f.write("- 目視確認が必要です：PDFを開いて実際のはみ出しと比較してください\n")


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='統合はみ出し検出器'
    )
    parser.add_argument('pdf_files', nargs='+', help='検査するPDFファイル')
    
    args = parser.parse_args()
    
    # 検出器を初期化
    detector = UnifiedOverflowDetector()
    
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
                
                # 既知のはみ出しページの確認
                if pdf_path.name in detector.known_overflows:
                    known_pages = set(detector.known_overflows[pdf_path.name].keys())
                    detected_pages = set(page_list)
                    
                    if known_pages.issubset(detected_pages):
                        print(f"  ✓ 既知のはみ出しページをすべて検出: {sorted(known_pages)}")
                    else:
                        missing = known_pages - detected_pages
                        print(f"  ✗ 未検出の既知ページ: {sorted(missing)}")
            else:
                print(f"\n{pdf_path.name}: はみ出しなし")
                
        except Exception as e:
            print(f"エラー: {pdf_path.name} の処理中にエラー: {e}")
            import traceback
            traceback.print_exc()
    
    # 結果を保存
    if all_results:
        output_path = Path("testresult.md")
        detector.save_results(all_results, output_path)
        print(f"\n結果を {output_path} に保存しました。")
        print("PDFを目視確認して、実際のはみ出しと比較してください。")


if __name__ == "__main__":
    main()