#!/usr/bin/env python3
"""
改良版はみ出し検出器
ユーザーフィードバックに基づいて精度を向上
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import pdfplumber


class ImprovedOverflowDetector:
    """改良版はみ出し検出器"""
    
    # B5判のレイアウト（技術の泉シリーズ標準）
    PAGE_WIDTH_MM = 182
    PAGE_HEIGHT_MM = 257
    
    # 本文エリアのマージン（mm）
    # 偶数ページ（左ページ）
    EVEN_PAGE_LEFT_MARGIN_MM = 20
    EVEN_PAGE_RIGHT_MARGIN_MM = 15
    
    # 奇数ページ（右ページ）
    ODD_PAGE_LEFT_MARGIN_MM = 15
    ODD_PAGE_RIGHT_MARGIN_MM = 20
    
    def __init__(self):
        """初期化"""
        self.mm_to_pt = 72 / 25.4
        
        # 除外ページリスト（目次、見出しなど）
        self.exclude_pages = set()
        
        # 検出統計
        self.stats = {
            'total_pages': 0,
            'code_block_pages': 0,
            'detected_pages': 0,
            'total_overflows': 0,
            'true_positives': 0  # 実際のはみ出し（コードブロック内）
        }
    
    def calculate_text_right_edge(self, page_width: float, page_number: int) -> float:
        """本文領域の右端座標を計算"""
        if page_number % 2 == 0:  # 偶数ページ
            right_margin_pt = self.EVEN_PAGE_RIGHT_MARGIN_MM * self.mm_to_pt
        else:  # 奇数ページ
            right_margin_pt = self.ODD_PAGE_RIGHT_MARGIN_MM * self.mm_to_pt
            
        return page_width - right_margin_pt
    
    def detect_code_blocks(self, page) -> List[Dict]:
        """コードブロック（グレー背景矩形）を検出"""
        code_blocks = []
        
        for rect in page.rects:
            if rect.get('fill'):
                width = rect['x1'] - rect['x0']
                height = rect['y1'] - rect['y0']
                
                # コードブロックサイズの判定（幅300pt以上、高さ20pt以上）
                if width > 300 and height > 20:
                    code_blocks.append(rect)
        
        return code_blocks
    
    def is_toc_or_heading_page(self, page, page_number: int) -> bool:
        """目次や見出しページかどうかを判定"""
        # ページ3以下は目次の可能性が高い
        if page_number <= 3:
            return True
        
        # テキストが少ないページは見出しページの可能性
        chars = page.chars
        if len(chars) < 100:  # 文字数が少ない
            return True
        
        # ページ上部に大きなフォントのテキストのみがある場合
        top_chars = [c for c in chars if c['y0'] < 200]
        if len(top_chars) > 0 and len(chars) < 200:
            # 見出しページの可能性
            return True
        
        return False
    
    def check_code_block_overflow(self, page, code_block: Dict, 
                                 page_number: int) -> List[Dict]:
        """コードブロック内のはみ出しをチェック（座標ベース）"""
        overflows = []
        
        # 本文領域の右端を計算（座標ベース）
        text_right_edge = self.calculate_text_right_edge(page.width, page_number)
        
        # 矩形の境界でクリップ（エラー回避）
        bbox = (
            max(0, code_block['x0']),
            max(0, code_block['y0']),
            min(page.width, code_block['x1']),
            min(page.height, code_block['y1'])
        )
        
        try:
            cropped = page.within_bbox(bbox)
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
                
                # 本文領域の右端を超える文字を探す（座標ベース）
                overflow_chars = []
                for char in line_chars:
                    # 座標ベースでの判定（本文領域基準）
                    if char['x1'] > text_right_edge + 1:  # 1pt以上の超過
                        overflow_chars.append(char)
                
                if overflow_chars:
                    line_text = ''.join([c['text'] for c in line_chars])
                    overflow_text = ''.join([c['text'] for c in overflow_chars])
                    rightmost_char = max(overflow_chars, key=lambda c: c['x1'])
                    
                    overflows.append({
                        'y_position': y_pos,
                        'line_text': line_text[:100],
                        'overflow_text': overflow_text,
                        'overflow_amount': rightmost_char['x1'] - text_right_edge,
                        'char_count': len(overflow_chars),
                        'rect_bounds': (code_block['x0'], code_block['y0'], 
                                      code_block['x1'], code_block['y1']),
                        'text_right_edge': text_right_edge
                    })
                    
        except ValueError as e:
            # 矩形がページ境界を超える場合はスキップ
            pass
        
        return overflows
    
    def process_page(self, page, page_number: int) -> Optional[Dict]:
        """1ページを処理（コードブロック内のはみ出しのみ）"""
        
        # 目次や見出しページは除外
        if self.is_toc_or_heading_page(page, page_number):
            self.exclude_pages.add(page_number)
            return None
        
        # コードブロックを検出
        code_blocks = self.detect_code_blocks(page)
        
        # コードブロックがないページは除外
        if not code_blocks:
            return None
        
        self.stats['code_block_pages'] += 1
        
        # 結果を格納
        page_results = {
            'page_number': page_number,
            'page_type': 'even' if page_number % 2 == 0 else 'odd',
            'code_block_count': len(code_blocks),
            'overflows': []
        }
        
        # 各コードブロックをチェック
        for code_block in code_blocks:
            overflows = self.check_code_block_overflow(page, code_block, page_number)
            page_results['overflows'].extend(overflows)
        
        # はみ出しがあるページのみ返す
        if page_results['overflows']:
            self.stats['detected_pages'] += 1
            self.stats['total_overflows'] += len(page_results['overflows'])
            return page_results
        
        return None
    
    def process_pdf(self, pdf_path: Path) -> List[Dict]:
        """PDFファイル全体を処理"""
        print(f"処理開始: {pdf_path.name}")
        print("改良版検出器 - コードブロック内のはみ出しのみを検出")
        
        results = []
        
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                total_pages = len(pdf.pages)
                self.stats['total_pages'] = total_pages
                
                for i, page in enumerate(pdf.pages):
                    page_number = i + 1
                    
                    if page_number % 10 == 0:
                        print(f"処理中: {page_number}/{total_pages} ページ...")
                    
                    # ページを処理
                    page_result = self.process_page(page, page_number)
                    if page_result:
                        results.append(page_result)
                        
        except Exception as e:
            print(f"エラー: {e}")
            raise
            
        return results
    
    def save_results(self, results: List[Dict], pdf_path: Path, output_path: Path):
        """結果を保存"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {pdf_path.name} 改良版はみ出し検出結果\n\n")
            f.write(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 統計情報
            f.write("## 検出統計\n\n")
            f.write(f"- 総ページ数: {self.stats['total_pages']}\n")
            f.write(f"- コードブロックを含むページ数: {self.stats['code_block_pages']}\n")
            f.write(f"- はみ出し検出ページ数: {self.stats['detected_pages']}\n")
            f.write(f"- 総はみ出し数: {self.stats['total_overflows']}\n")
            f.write(f"- 除外ページ数（目次・見出し）: {len(self.exclude_pages)}\n\n")
            
            # 検出パラメータ
            f.write("## 検出パラメータ\n\n")
            f.write("- 検出対象: コードブロック（グレー背景矩形）内のテキストのみ\n")
            f.write("- 判定基準: 本文領域の右端を1pt以上超える場合（座標ベース）\n")
            f.write("- 除外対象: 目次ページ、見出しページ、コードブロックがないページ\n\n")
            
            # 検出結果
            f.write("## 検出結果\n\n")
            
            if results:
                # ページリスト
                page_list = [r['page_number'] for r in results]
                f.write(f"### はみ出し検出ページ: {', '.join(map(str, page_list))}\n\n")
                
                # 各ページの詳細
                f.write("### ページ別詳細\n\n")
                
                for result in results:
                    page_num = result['page_number']
                    page_type = result['page_type']
                    overflows = result['overflows']
                    
                    f.write(f"#### ページ {page_num} ({page_type}ページ)\n")
                    f.write(f"- コードブロック数: {result['code_block_count']}\n")
                    f.write(f"- はみ出し検出数: {len(overflows)}\n\n")
                    
                    for i, ov in enumerate(overflows, 1):
                        f.write(f"{i}. **Y={ov['y_position']}**: `{ov['overflow_text']}` ")
                        f.write(f"({ov['overflow_amount']:.1f}pt超過, {ov['char_count']}文字)\n")
                        f.write(f"   - 行内容: `{ov['line_text'][:60]}...`\n")
                        if ov['overflow_amount'] > 100:
                            f.write(f"   - ⚠️ 大幅なはみ出し\n")
                        f.write("\n")
                    
                    f.write("---\n\n")
            else:
                f.write("はみ出しは検出されませんでした。\n\n")
            
            # 除外ページリスト
            if self.exclude_pages:
                f.write("## 除外ページ\n\n")
                f.write(f"目次・見出しページとして除外: {', '.join(map(str, sorted(self.exclude_pages)))}\n\n")
            
            # 注記
            f.write("## 注記\n\n")
            f.write("- コードブロック内のはみ出しのみを検出対象としています\n")
            f.write("- 目次ページや見出しページは自動的に除外されます\n")
            f.write("- コードブロックがないページは検出対象外です\n")
            f.write("- 実際のPDFと照合して最終確認をお願いします\n")


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='改良版はみ出し検出器'
    )
    parser.add_argument('pdf_file', help='検査するPDFファイル')
    parser.add_argument('-o', '--output', help='出力ファイル名', 
                       default=None)
    
    args = parser.parse_args()
    
    pdf_path = Path(args.pdf_file)
    if not pdf_path.exists():
        print(f"エラー: {pdf_path} が見つかりません")
        return
    
    # 出力ファイル名を決定
    if args.output:
        output_path = Path(args.output)
    else:
        # デフォルト: testresult_[ファイル名].md
        output_path = Path(f"testresult_{pdf_path.stem}.md")
    
    # 検出器を初期化
    detector = ImprovedOverflowDetector()
    
    # PDFを処理
    results = detector.process_pdf(pdf_path)
    
    # 結果を保存
    detector.save_results(results, pdf_path, output_path)
    
    print(f"\n処理完了！")
    print(f"検出ページ数: {detector.stats['detected_pages']}")
    print(f"総はみ出し数: {detector.stats['total_overflows']}")
    print(f"結果は {output_path} に保存されました。")


if __name__ == "__main__":
    main()