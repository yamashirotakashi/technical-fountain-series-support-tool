#!/usr/bin/env python3
"""
矩形基準視覚的検出器
コードブロック（グレー背景矩形）からのはみ出しを優先的に検出
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set
import pdfplumber


class RectBasedVisualDetector:
    """矩形基準の視覚的検出器"""
    
    def __init__(self):
        """初期化"""
        # 検出統計
        self.stats = {
            'total_pages': 0,
            'detected_pages': 0,
            'rect_overflow_detections': 0,  # 矩形からのはみ出し
            'page_overflow_detections': 0,   # ページからのはみ出し
            'excluded_characters': {}
        }
    
    def is_ascii_printable(self, text: str) -> bool:
        """ASCII印字可能文字かどうかを判定"""
        return all(32 <= ord(char) < 127 for char in text)
    
    def detect_code_blocks(self, page) -> List[Dict]:
        """コードブロック（グレー背景矩形）を検出"""
        code_blocks = []
        
        for rect in page.rects:
            if rect.get('fill'):
                width = rect['x1'] - rect['x0']
                height = rect['y1'] - rect['y0']
                
                # コードブロックサイズの判定（小さすぎる矩形は除外）
                if width > 100 and height > 10:
                    code_blocks.append({
                        'x0': rect['x0'],
                        'y0': rect['y0'],
                        'x1': rect['x1'],
                        'y1': rect['y1'],
                        'width': width,
                        'height': height
                    })
        
        return code_blocks
    
    def detect_rect_overflow(self, page, page_number: int) -> List[Dict]:
        """矩形からのはみ出しを検出（最優先）"""
        overflows = []
        code_blocks = self.detect_code_blocks(page)
        
        if not code_blocks:
            return overflows
        
        # 各コードブロックに対してチェック
        for block_idx, block in enumerate(code_blocks):
            block_overflows = []
            
            # ブロック内の文字をチェック
            for char in page.chars:
                # 文字がブロック内に含まれるかチェック（Y座標）
                if block['y0'] <= char['y0'] <= block['y1']:
                    # ASCII文字のみ対象
                    if self.is_ascii_printable(char['text']):
                        # 文字の右端がブロックの右端を超えているか
                        if char['x1'] > block['x1']:
                            overflow_amount = char['x1'] - block['x1']
                            block_overflows.append({
                                'char': char['text'],
                                'x0': char['x0'],
                                'x1': char['x1'],
                                'y0': char['y0'],
                                'overflow_amount': overflow_amount
                            })
                    else:
                        # 統計を更新
                        char_type = self.classify_character(char['text'])
                        self.stats['excluded_characters'][char_type] = \
                            self.stats['excluded_characters'].get(char_type, 0) + 1
            
            if block_overflows:
                # 行ごとにグループ化
                lines = {}
                for overflow in block_overflows:
                    y_pos = round(overflow['y0'])
                    if y_pos not in lines:
                        lines[y_pos] = []
                    lines[y_pos].append(overflow)
                
                # 各行の情報を収集
                for y_pos, line_overflows in lines.items():
                    line_overflows.sort(key=lambda x: x['x0'])
                    overflow_text = ''.join([o['char'] for o in line_overflows])
                    max_overflow = max(o['overflow_amount'] for o in line_overflows)
                    
                    overflows.append({
                        'type': 'rect_overflow',
                        'block_idx': block_idx,
                        'block_bounds': (block['x0'], block['y0'], block['x1'], block['y1']),
                        'y_position': y_pos,
                        'overflow_text': overflow_text,
                        'overflow_amount': max_overflow,
                        'char_count': len(line_overflows)
                    })
        
        return overflows
    
    def detect_page_overflow(self, page, page_number: int) -> List[Dict]:
        """ページからのはみ出しを検出（副次的）"""
        overflows = []
        page_width = page.width
        
        # ページ右端を基準
        page_right_edge = page_width - 10  # 最小マージン10pt
        
        # 行ごとにグループ化
        lines = {}
        for char in page.chars:
            # ページ番号領域は除外
            if char['y0'] < 50 or char['y0'] > page.height - 50:
                continue
            
            # ASCII文字のみ対象
            if self.is_ascii_printable(char['text']):
                y_pos = round(char['y0'])
                if y_pos not in lines:
                    lines[y_pos] = []
                lines[y_pos].append(char)
        
        # 各行をチェック
        for y_pos, line_chars in lines.items():
            line_chars.sort(key=lambda c: c['x0'])
            
            # ページ右端を超える文字を探す
            overflow_chars = []
            for char in line_chars:
                if char['x1'] > page_right_edge:
                    overflow_chars.append(char)
            
            if overflow_chars:
                line_text = ''.join([c['text'] for c in line_chars])
                overflow_text = ''.join([c['text'] for c in overflow_chars])
                max_overflow = max(c['x1'] - page_right_edge for c in overflow_chars)
                
                overflows.append({
                    'type': 'page_overflow',
                    'y_position': y_pos,
                    'line_text': line_text[:100],
                    'overflow_text': overflow_text,
                    'overflow_amount': max_overflow,
                    'char_count': len(overflow_chars)
                })
        
        return overflows
    
    def classify_character(self, char: str) -> str:
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
    
    def process_page(self, page, page_number: int) -> Optional[Dict]:
        """1ページを処理"""
        
        # 目次や見出しページは除外
        if page_number <= 3:
            return None
        
        # 矩形からのはみ出しを検出（優先）
        rect_overflows = self.detect_rect_overflow(page, page_number)
        
        # ページからのはみ出しを検出（副次的）
        page_overflows = self.detect_page_overflow(page, page_number)
        
        # 検出結果を統合
        if rect_overflows or page_overflows:
            page_result = {
                'page_number': page_number,
                'page_type': 'even' if page_number % 2 == 0 else 'odd',
                'detections': {
                    'rect_overflow': rect_overflows,
                    'page_overflow': page_overflows
                }
            }
            
            # 統計を更新
            if rect_overflows:
                self.stats['rect_overflow_detections'] += 1
            if page_overflows:
                self.stats['page_overflow_detections'] += 1
            
            self.stats['detected_pages'] += 1
            return page_result
        
        return None
    
    def process_pdf(self, pdf_path: Path) -> List[Dict]:
        """PDFファイル全体を処理"""
        pdf_name = pdf_path.name
        print(f"処理開始: {pdf_name}")
        print("矩形基準視覚的検出（コードブロックからのはみ出し優先）")
        
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
            f.write(f"# {pdf_path.name} 矩形基準視覚的検出結果\n\n")
            f.write("**コードブロックからのはみ出しを優先検出**\n\n")
            f.write(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 統計情報
            f.write("## 検出統計\n\n")
            f.write(f"- 総ページ数: {self.stats['total_pages']}\n")
            f.write(f"- はみ出し検出ページ数: {self.stats['detected_pages']}\n")
            f.write(f"- 矩形からのはみ出し: {self.stats['rect_overflow_detections']}ページ\n")
            f.write(f"- ページからのはみ出し: {self.stats['page_overflow_detections']}ページ\n\n")
            
            # 除外された文字の統計
            if self.stats['excluded_characters']:
                f.write("### 除外された文字種別\n\n")
                for char_type, count in sorted(self.stats['excluded_characters'].items()):
                    f.write(f"- {char_type}: {count}文字\n")
                f.write(f"- **合計**: {sum(self.stats['excluded_characters'].values())}文字\n\n")
            
            # 検出結果
            f.write("## 検出結果\n\n")
            
            if results:
                # ページリスト
                page_list = [r['page_number'] for r in results]
                f.write(f"### はみ出し検出ページ: {', '.join(map(str, page_list))}\n\n")
                
                # 矩形からのはみ出しのみのページ
                rect_only = [r for r in results if r['detections']['rect_overflow'] and not r['detections']['page_overflow']]
                if rect_only:
                    f.write("### 矩形からのはみ出しのみ検出されたページ\n\n")
                    pages = [r['page_number'] for r in rect_only]
                    f.write(f"{', '.join(map(str, pages))}\n\n")
                
                # 各ページの詳細
                f.write("### ページ別詳細\n\n")
                
                for result in sorted(results, key=lambda r: r['page_number']):
                    page_num = result['page_number']
                    page_type = result['page_type']
                    
                    f.write(f"#### ページ {page_num} ({page_type}ページ)\n\n")
                    
                    # 矩形からのはみ出し
                    if result['detections']['rect_overflow']:
                        rect_ovs = result['detections']['rect_overflow']
                        f.write(f"**矩形からのはみ出し: {len(rect_ovs)}件**\n\n")
                        
                        # ブロックごとにグループ化
                        blocks = {}
                        for ov in rect_ovs:
                            block_idx = ov['block_idx']
                            if block_idx not in blocks:
                                blocks[block_idx] = []
                            blocks[block_idx].append(ov)
                        
                        for block_idx, block_ovs in blocks.items():
                            bounds = block_ovs[0]['block_bounds']
                            f.write(f"コードブロック{block_idx + 1} ")
                            f.write(f"({bounds[0]:.1f}, {bounds[1]:.1f}) - ({bounds[2]:.1f}, {bounds[3]:.1f})\n")
                            
                            for ov in block_ovs[:3]:  # 最初の3件
                                f.write(f"  - Y={ov['y_position']}: `{ov['overflow_text']}` ")
                                f.write(f"({ov['overflow_amount']:.1f}pt超過)\n")
                            
                            if len(block_ovs) > 3:
                                f.write(f"  ... 他 {len(block_ovs)-3} 件\n")
                            f.write("\n")
                    
                    # ページからのはみ出し
                    if result['detections']['page_overflow']:
                        page_ovs = result['detections']['page_overflow']
                        f.write(f"**ページからのはみ出し: {len(page_ovs)}件**\n\n")
                        for i, ov in enumerate(page_ovs[:3], 1):
                            f.write(f"{i}. Y={ov['y_position']}: `{ov['overflow_text']}` ")
                            f.write(f"({ov['overflow_amount']:.1f}pt超過)\n")
                        if len(page_ovs) > 3:
                            f.write(f"... 他 {len(page_ovs)-3} 件\n")
                        f.write("\n")
                    
                    f.write("---\n\n")
            else:
                f.write("はみ出しは検出されませんでした。\n\n")


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='矩形基準視覚的検出器（コードブロックからのはみ出し優先）'
    )
    parser.add_argument('pdf_file', help='検査するPDFファイル')
    parser.add_argument('-o', '--output', help='出力ファイル名', default=None)
    
    args = parser.parse_args()
    
    # 検出器を初期化
    detector = RectBasedVisualDetector()
    
    # PDFファイルの処理
    pdf_path = Path(args.pdf_file)
    if not pdf_path.exists():
        print(f"エラー: {pdf_path} が見つかりません")
        return
    
    # 出力ファイル名を決定
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(f"testresult_{pdf_path.stem}_rect_based.md")
    
    # PDFを処理
    results = detector.process_pdf(pdf_path)
    
    # 結果を保存
    detector.save_results(results, pdf_path, output_path)
    
    print(f"\n処理完了！")
    print(f"検出ページ数: {detector.stats['detected_pages']}")
    print(f"矩形からのはみ出し: {detector.stats['rect_overflow_detections']}ページ")
    print(f"ページからのはみ出し: {detector.stats['page_overflow_detections']}ページ")
    print(f"結果は {output_path} に保存されました。")


if __name__ == "__main__":
    main()