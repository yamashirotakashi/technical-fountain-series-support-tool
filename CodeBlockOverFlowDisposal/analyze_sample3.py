#!/usr/bin/env python3
"""
sample3.pdf専用のはみ出し検出と分析
ハイブリッド検出器を使用してtestresult3.mdに結果を保存
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import pdfplumber


class Sample3Analyzer:
    """sample3.pdf専用分析器"""
    
    # B5判のレイアウト（技術の泉シリーズ標準）
    PAGE_WIDTH_MM = 182
    PAGE_HEIGHT_MM = 257
    
    # 本文エリアのマージン（mm）
    # 偶数ページ（左ページ）
    EVEN_PAGE_LEFT_MARGIN_MM = 20    # 左マージン
    EVEN_PAGE_RIGHT_MARGIN_MM = 15   # 右マージン
    
    # 奇数ページ（右ページ）
    ODD_PAGE_LEFT_MARGIN_MM = 15     # 左マージン  
    ODD_PAGE_RIGHT_MARGIN_MM = 20    # 右マージン
    
    def __init__(self):
        """初期化"""
        self.mm_to_pt = 72 / 25.4
        self.detection_stats = {
            'total_pages': 0,
            'pages_with_overflow': 0,
            'total_overflows': 0,
            'code_block_overflows': 0,
            'text_overflows': 0
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
                
                # コードブロックサイズの判定
                if width > 300 and height > 20:
                    code_blocks.append(rect)
        
        return code_blocks
    
    def analyze_page(self, page, page_number: int) -> Dict:
        """1ページを詳細分析"""
        results = {
            'page_number': page_number,
            'page_type': 'even' if page_number % 2 == 0 else 'odd',
            'page_width': page.width,
            'page_height': page.height,
            'code_blocks': [],
            'overflows': {
                'coordinate_based': [],
                'rect_based': [],
                'high_confidence': []  # 両方で検出
            }
        }
        
        # 本文領域の右端
        text_right_edge = self.calculate_text_right_edge(page.width, page_number)
        results['text_right_edge'] = text_right_edge
        
        # コードブロックを検出
        code_blocks = self.detect_code_blocks(page)
        results['code_blocks'] = code_blocks
        
        # 1. 座標ベースの検出（本文領域基準）
        all_chars = page.chars
        
        # 行ごとにグループ化
        lines = {}
        for char in all_chars:
            # ページ番号領域は除外
            if char['y0'] < 50 or char['y0'] > page.height - 50:
                continue
                
            y_pos = round(char['y0'])
            if y_pos not in lines:
                lines[y_pos] = []
            lines[y_pos].append(char)
        
        # 各行をチェック
        for y_pos, line_chars in lines.items():
            line_chars.sort(key=lambda c: c['x0'])
            
            # 本文右端を超える文字を探す
            overflow_chars = []
            for char in line_chars:
                if char['x1'] > text_right_edge + 1:  # 1pt以上の超過
                    overflow_chars.append(char)
            
            if overflow_chars:
                line_text = ''.join([c['text'] for c in line_chars])
                overflow_text = ''.join([c['text'] for c in overflow_chars])
                
                # コードブロック内かチェック
                in_code_block = False
                containing_rect = None
                for rect in code_blocks:
                    if (rect['x0'] <= overflow_chars[0]['x0'] <= rect['x1'] and
                        rect['y0'] <= overflow_chars[0]['y0'] <= rect['y1']):
                        in_code_block = True
                        containing_rect = rect
                        break
                
                results['overflows']['coordinate_based'].append({
                    'y_position': y_pos,
                    'line_text': line_text[:100],  # 最初の100文字
                    'overflow_text': overflow_text,
                    'overflow_amount': max(c['x1'] for c in overflow_chars) - text_right_edge,
                    'in_code_block': in_code_block,
                    'char_count': len(overflow_chars)
                })
        
        # 2. 矩形ベースの検出（コードブロック基準）
        for rect in code_blocks:
            rect_right = rect['x1']
            
            # 矩形の境界でクリップ
            bbox = (
                max(0, rect['x0']),
                max(0, rect['y0']),
                min(page.width, rect['x1']),
                min(page.height, rect['y1'])
            )
            
            try:
                cropped = page.within_bbox(bbox)
                chars = cropped.chars
                
                # 行ごとにグループ化
                rect_lines = {}
                for char in chars:
                    y_pos = round(char['y0'])
                    if y_pos not in rect_lines:
                        rect_lines[y_pos] = []
                    rect_lines[y_pos].append(char)
                
                # 各行をチェック
                for y_pos, line_chars in rect_lines.items():
                    line_chars.sort(key=lambda c: c['x0'])
                    
                    # 矩形の右端を超える文字を探す
                    overflow_chars = []
                    for char in line_chars:
                        if char['x1'] > rect_right + 0.5:
                            overflow_chars.append(char)
                    
                    if overflow_chars:
                        line_text = ''.join([c['text'] for c in line_chars])
                        overflow_text = ''.join([c['text'] for c in overflow_chars])
                        
                        results['overflows']['rect_based'].append({
                            'y_position': y_pos,
                            'line_text': line_text[:100],
                            'overflow_text': overflow_text,
                            'overflow_amount': max(c['x1'] for c in overflow_chars) - rect_right,
                            'rect_bounds': (rect['x0'], rect['y0'], rect['x1'], rect['y1']),
                            'char_count': len(overflow_chars)
                        })
                        
            except ValueError:
                # 矩形がページ境界を超える場合はスキップ
                pass
        
        # 3. 高信頼度（両方で検出）を特定
        for co in results['overflows']['coordinate_based']:
            if co['in_code_block']:
                for ro in results['overflows']['rect_based']:
                    if abs(co['y_position'] - ro['y_position']) < 2:
                        results['overflows']['high_confidence'].append({
                            **co,
                            'detection_method': 'both',
                            'rect_overflow': ro['overflow_amount']
                        })
                        break
        
        return results
    
    def process_pdf(self, pdf_path: Path) -> List[Dict]:
        """PDFファイル全体を処理"""
        print(f"処理開始: {pdf_path.name}")
        print("ハイブリッド検出（座標＋矩形ベース）による分析")
        
        all_results = []
        
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                total_pages = len(pdf.pages)
                self.detection_stats['total_pages'] = total_pages
                
                for i, page in enumerate(pdf.pages):
                    page_number = i + 1
                    
                    if page_number % 10 == 0:
                        print(f"処理中: {page_number}/{total_pages} ページ...")
                    
                    # ページを分析
                    page_results = self.analyze_page(page, page_number)
                    
                    # はみ出しがあるページのみ記録
                    if (page_results['overflows']['coordinate_based'] or 
                        page_results['overflows']['rect_based']):
                        all_results.append(page_results)
                        self.detection_stats['pages_with_overflow'] += 1
                        
                        # 統計更新
                        coord_count = len(page_results['overflows']['coordinate_based'])
                        rect_count = len(page_results['overflows']['rect_based'])
                        self.detection_stats['total_overflows'] += max(coord_count, rect_count)
                        
                        # コードブロック内のはみ出し数
                        cb_overflows = sum(1 for ov in page_results['overflows']['coordinate_based'] 
                                         if ov['in_code_block'])
                        self.detection_stats['code_block_overflows'] += cb_overflows
                        self.detection_stats['text_overflows'] += coord_count - cb_overflows
                        
        except Exception as e:
            print(f"エラー: {e}")
            raise
            
        return all_results
    
    def save_results(self, results: List[Dict], output_path: Path):
        """結果をtestresult3.mdに保存"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# sample3.pdf はみ出し検出結果\n\n")
            f.write(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 統計情報
            f.write("## 検出統計\n\n")
            f.write(f"- 総ページ数: {self.detection_stats['total_pages']}\n")
            f.write(f"- はみ出し検出ページ数: {self.detection_stats['pages_with_overflow']}\n")
            f.write(f"- 総はみ出し数: {self.detection_stats['total_overflows']}\n")
            f.write(f"- コードブロック内: {self.detection_stats['code_block_overflows']}\n")
            f.write(f"- 本文: {self.detection_stats['text_overflows']}\n\n")
            
            # 検出パラメータ
            f.write("## 検出パラメータ\n\n")
            f.write("- 座標判定: 本文領域の右端を基準（ページ番号領域は除外）\n")
            f.write("- 矩形判定: コードブロック（グレー背景）の右端を基準\n")
            f.write("- 偶数ページ右マージン: 15mm\n")
            f.write("- 奇数ページ右マージン: 20mm\n\n")
            
            # ページごとの詳細
            f.write("## ページごとの検出結果\n\n")
            
            # 高信頼度（両方で検出）のものを先に表示
            high_confidence_pages = [r for r in results 
                                    if r['overflows']['high_confidence']]
            
            if high_confidence_pages:
                f.write("### 高信頼度検出（座標・矩形両方で検出）\n\n")
                for result in high_confidence_pages:
                    page_num = result['page_number']
                    page_type = result['page_type']
                    high_conf = result['overflows']['high_confidence']
                    
                    f.write(f"#### ページ {page_num} ({page_type}ページ)\n\n")
                    for i, ov in enumerate(high_conf, 1):
                        f.write(f"{i}. Y={ov['y_position']}: `{ov['overflow_text']}` ")
                        f.write(f"({ov['overflow_amount']:.1f}pt超過)\n")
                        f.write(f"   行内容: {ov['line_text'][:50]}...\n\n")
                f.write("\n")
            
            # その他の検出結果
            f.write("### その他の検出結果\n\n")
            
            for result in results[:30]:  # 最初の30ページ
                page_num = result['page_number']
                page_type = result['page_type']
                
                f.write(f"#### ページ {page_num} ({page_type}ページ)\n")
                f.write(f"本文右端: {result['text_right_edge']:.1f}pt\n\n")
                
                # 座標ベース
                coord_ovs = result['overflows']['coordinate_based']
                if coord_ovs:
                    f.write(f"**座標ベース検出: {len(coord_ovs)}件**\n")
                    in_cb = sum(1 for ov in coord_ovs if ov['in_code_block'])
                    f.write(f"（コードブロック内: {in_cb}件）\n\n")
                    
                    # コードブロック内のものを優先表示
                    cb_ovs = [ov for ov in coord_ovs if ov['in_code_block']]
                    for i, ov in enumerate(cb_ovs[:3], 1):
                        f.write(f"{i}. Y={ov['y_position']}: `{ov['overflow_text']}` ")
                        f.write(f"({ov['overflow_amount']:.1f}pt, {ov['char_count']}文字)\n")
                    
                    if len(cb_ovs) > 3:
                        f.write(f"... 他 {len(cb_ovs)-3} 件\n")
                    f.write("\n")
                
                # 矩形ベース
                rect_ovs = result['overflows']['rect_based']
                if rect_ovs:
                    f.write(f"**矩形ベース検出: {len(rect_ovs)}件**\n\n")
                    for i, ov in enumerate(rect_ovs[:3], 1):
                        f.write(f"{i}. Y={ov['y_position']}: `{ov['overflow_text']}` ")
                        f.write(f"({ov['overflow_amount']:.1f}pt)\n")
                    
                    if len(rect_ovs) > 3:
                        f.write(f"... 他 {len(rect_ovs)-3} 件\n")
                    f.write("\n")
                
                f.write("---\n\n")
            
            if len(results) > 30:
                f.write(f"\n... 他 {len(results)-30} ページ省略\n\n")
            
            # 注記
            f.write("## 注記\n\n")
            f.write("- 高信頼度検出: 座標ベースと矩形ベースの両方で検出されたもの\n")
            f.write("- コードブロック内の検出を優先的に表示しています\n")
            f.write("- 目視確認時は、特に高信頼度検出に注目してください\n")
            f.write("- 各ページの実際のPDFと照合して、はみ出しの妥当性を確認してください\n")


def main():
    """メイン処理"""
    pdf_path = Path("sample3.pdf")
    if not pdf_path.exists():
        print(f"エラー: {pdf_path} が見つかりません")
        return
    
    # 分析器を初期化
    analyzer = Sample3Analyzer()
    
    # PDFを処理
    results = analyzer.process_pdf(pdf_path)
    
    # 結果を保存
    output_path = Path("testresult3.md")
    analyzer.save_results(results, output_path)
    
    print(f"\n分析完了！")
    print(f"検出ページ数: {analyzer.detection_stats['pages_with_overflow']}")
    print(f"総はみ出し数: {analyzer.detection_stats['total_overflows']}")
    print(f"結果は {output_path} に保存されました。")
    print("\nPDFを開いて目視確認し、実際のはみ出しと比較してください。")


if __name__ == "__main__":
    main()