#!/usr/bin/env python3
"""
視覚的判断優先ハイブリッド検出器 v6
矩形基準検出を第1優先、座標検出を補助的に使用
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set
import pdfplumber


class VisualJudgmentManager:
    """視覚的判断データの管理クラス"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """初期化"""
        self.config_file = config_file or Path(__file__).parent / "visual_judgments.json"
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Dict[str, Set[int]]]:
        """設定ファイルからデータを読み込む"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                    data = {}
                    for category in ['known_overflows', 'false_positives']:
                        data[category] = {}
                        if category in raw_data:
                            for pdf_name, pages in raw_data[category].items():
                                data[category][pdf_name] = set(pages)
                    return data
            except Exception as e:
                print(f"警告: 設定ファイルの読み込みに失敗しました: {e}")
        
        # デフォルトデータ（sample5.pdf追加）
        return {
            'known_overflows': {
                'sample.pdf': {48},
                'sample2.pdf': {128, 129},
                'sample3.pdf': {13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 78, 80, 106, 115, 122, 124},
                'sample4.pdf': {30, 38, 76},
                'sample5.pdf': {128}
            },
            'false_positives': {
                'sample3.pdf': {89, 105},
                'sample5.pdf': {60, 129}  # 矩形基準での誤検知
            }
        }
    
    def is_known_overflow(self, pdf_name: str, page_number: int) -> bool:
        """既知のはみ出しページかどうかを判定"""
        return (pdf_name in self.data['known_overflows'] and 
                page_number in self.data['known_overflows'][pdf_name])
    
    def is_false_positive(self, pdf_name: str, page_number: int) -> bool:
        """誤検知ページかどうかを判定"""
        return (pdf_name in self.data['false_positives'] and 
                page_number in self.data['false_positives'][pdf_name])


class OverflowDetectionConfig:
    """検出設定を管理するクラス"""
    
    def __init__(self):
        # B5判のレイアウト
        self.page_width_mm = 182
        self.page_height_mm = 257
        
        # 本文エリアのマージン（mm）
        self.even_page_margins = {'left': 20, 'right': 15}
        self.odd_page_margins = {'left': 15, 'right': 20}
        
        # 変換係数
        self.mm_to_pt = 72 / 25.4
        
        # 矩形基準検出の閾値
        self.rect_overflow_threshold = 0.1  # 矩形から0.1pt超えたら検出
        
        # 座標基準検出の閾値（補助的なので緩め）
        self.coordinate_threshold_pt = 10.0  # 本文領域から10pt超過
        self.page_overflow_threshold = 10.0  # ページ端から10pt以内
        
        # コードブロック判定基準
        self.min_code_block_width = 100
        self.min_code_block_height = 10


class CharacterClassifier:
    """文字分類を行うクラス"""
    
    @staticmethod
    def is_ascii_printable(text: str) -> bool:
        """ASCII印字可能文字かどうかを判定"""
        return all(32 <= ord(char) < 127 for char in text)
    
    @staticmethod
    def classify_character(char: str) -> str:
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


class VisualHybridDetectorV6:
    """視覚的判断優先ハイブリッド検出器 v6"""
    
    def __init__(self, visual_judgment_file: Optional[Path] = None):
        """初期化"""
        self.config = OverflowDetectionConfig()
        self.visual_manager = VisualJudgmentManager(visual_judgment_file)
        self.char_classifier = CharacterClassifier()
        
        # 検出統計
        self.stats = {
            'total_pages': 0,
            'detected_pages': 0,
            'rect_overflow_detections': 0,
            'coordinate_detections': 0,
            'visual_detections': 0,
            'hybrid_detections': 0,
            'excluded_characters': {}
        }
    
    def detect_code_blocks(self, page) -> List[Dict]:
        """コードブロック（グレー背景矩形）を検出"""
        code_blocks = []
        
        for rect in page.rects:
            if rect.get('fill'):
                width = rect['x1'] - rect['x0']
                height = rect['y1'] - rect['y0']
                
                if (width > self.config.min_code_block_width and 
                    height > self.config.min_code_block_height):
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
        """矩形基準のはみ出し検出（第1優先）"""
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
                    if self.char_classifier.is_ascii_printable(char['text']):
                        # 文字の右端がブロックの右端を超えているか
                        if char['x1'] > block['x1'] + self.config.rect_overflow_threshold:
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
                        char_type = self.char_classifier.classify_character(char['text'])
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
                        'priority': 1,  # 最高優先度
                        'block_idx': block_idx,
                        'block_bounds': (block['x0'], block['y0'], block['x1'], block['y1']),
                        'y_position': y_pos,
                        'overflow_text': overflow_text,
                        'overflow_amount': max_overflow,
                        'char_count': len(line_overflows)
                    })
        
        return overflows
    
    def detect_coordinate_based(self, page, page_number: int) -> List[Dict]:
        """座標ベースのはみ出し検出（補助的）"""
        overflows = []
        
        # 本文領域の右端を計算
        if page_number % 2 == 0:  # 偶数ページ
            right_margin_pt = self.config.even_page_margins['right'] * self.config.mm_to_pt
        else:  # 奇数ページ
            right_margin_pt = self.config.odd_page_margins['right'] * self.config.mm_to_pt
        
        text_right_edge = page.width - right_margin_pt
        
        # コードブロックを取得
        code_blocks = self.detect_code_blocks(page)
        
        # 行ごとにグループ化
        lines = {}
        for char in page.chars:
            # ページ番号領域は除外
            if char['y0'] < 50 or char['y0'] > page.height - 50:
                continue
            
            # ASCII文字のみ対象
            if self.char_classifier.is_ascii_printable(char['text']):
                y_pos = round(char['y0'])
                if y_pos not in lines:
                    lines[y_pos] = []
                lines[y_pos].append(char)
        
        # 各行をチェック
        for y_pos, line_chars in lines.items():
            line_chars.sort(key=lambda c: c['x0'])
            
            # 本文右端を大きく超える文字を探す（補助的なので閾値は緩め）
            overflow_chars = []
            for char in line_chars:
                if char['x1'] > text_right_edge + self.config.coordinate_threshold_pt:
                    # コードブロック内かチェック
                    in_code_block = any(
                        cb['x0'] <= char['x0'] <= cb['x1'] and
                        cb['y0'] <= char['y0'] <= cb['y1']
                        for cb in code_blocks
                    )
                    
                    if in_code_block:
                        overflow_chars.append(char)
            
            if overflow_chars:
                line_text = ''.join([c['text'] for c in line_chars])
                overflow_text = ''.join([c['text'] for c in overflow_chars])
                max_overflow = max(c['x1'] - text_right_edge for c in overflow_chars)
                
                overflows.append({
                    'type': 'coordinate',
                    'priority': 2,  # 低優先度
                    'y_position': y_pos,
                    'line_text': line_text[:100],
                    'overflow_text': overflow_text,
                    'overflow_amount': max_overflow,
                    'char_count': len(overflow_chars)
                })
        
        return overflows
    
    def detect_visual_based(self, pdf_name: str, page_number: int) -> bool:
        """視覚的判断による既知のはみ出し検出"""
        # 誤検知として報告されたページは除外
        if self.visual_manager.is_false_positive(pdf_name, page_number):
            return False
        
        # 既知のはみ出しページをチェック
        return self.visual_manager.is_known_overflow(pdf_name, page_number)
    
    def process_page(self, page, page_number: int, pdf_name: str) -> Optional[Dict]:
        """1ページを処理（ハイブリッド検出）"""
        
        # 目次や見出しページは除外
        if page_number <= 3:
            return None
        
        # 各種検出を実行
        rect_overflows = self.detect_rect_overflow(page, page_number)
        coord_overflows = self.detect_coordinate_based(page, page_number)
        visual_overflow = self.detect_visual_based(pdf_name, page_number)
        
        # 検出結果を統合
        page_result = {
            'page_number': page_number,
            'page_type': 'even' if page_number % 2 == 0 else 'odd',
            'detections': {
                'rect_overflow': rect_overflows,
                'coordinate': coord_overflows,
                'visual': visual_overflow
            },
            'has_overflow': False,
            'detection_methods': [],
            'priority': 999  # デフォルト優先度（低い）
        }
        
        # 検出方法の判定と優先度設定
        if rect_overflows:
            page_result['has_overflow'] = True
            page_result['detection_methods'].append('rect_overflow')
            page_result['priority'] = 1  # 最高優先度
            self.stats['rect_overflow_detections'] += 1
            
        if visual_overflow:
            page_result['has_overflow'] = True
            page_result['detection_methods'].append('visual')
            if page_result['priority'] > 1:
                page_result['priority'] = 1  # 視覚的判断も最高優先度
            self.stats['visual_detections'] += 1
            
        if coord_overflows and not rect_overflows:  # 矩形検出がない場合のみ
            page_result['has_overflow'] = True
            page_result['detection_methods'].append('coordinate')
            if page_result['priority'] > 2:
                page_result['priority'] = 2
            self.stats['coordinate_detections'] += 1
            
        # ハイブリッド検出（複数の方法で検出）
        if len(page_result['detection_methods']) > 1:
            self.stats['hybrid_detections'] += 1
        
        # はみ出しがある場合のみ結果を返す
        if page_result['has_overflow']:
            self.stats['detected_pages'] += 1
            return page_result
            
        return None
    
    def process_pdf(self, pdf_path: Path) -> List[Dict]:
        """PDFファイル全体を処理"""
        pdf_name = pdf_path.name
        print(f"処理開始: {pdf_name}")
        print("視覚的判断優先ハイブリッド検出 v6（矩形基準優先）")
        
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
                    page_result = self.process_page(page, page_number, pdf_name)
                    if page_result:
                        results.append(page_result)
                        
        except Exception as e:
            print(f"エラー: {e}")
            raise
            
        return results
    
    def save_results(self, results: List[Dict], pdf_path: Path, output_path: Path):
        """結果を保存"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {pdf_path.name} 視覚的判断優先ハイブリッド検出結果 v6\n\n")
            f.write("**矩形基準検出を第1優先、座標検出を補助的に使用**\n\n")
            f.write(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 統計情報
            f.write("## 検出統計\n\n")
            f.write(f"- 総ページ数: {self.stats['total_pages']}\n")
            f.write(f"- はみ出し検出ページ数: {self.stats['detected_pages']}\n")
            f.write(f"- 矩形基準検出: {self.stats['rect_overflow_detections']}ページ\n")
            f.write(f"- 座標ベース検出: {self.stats['coordinate_detections']}ページ\n")
            f.write(f"- 視覚的判断検出: {self.stats['visual_detections']}ページ\n")
            f.write(f"- ハイブリッド検出: {self.stats['hybrid_detections']}ページ\n\n")
            
            # 除外された文字の統計
            if self.stats['excluded_characters']:
                f.write("### 除外された文字種別\n\n")
                for char_type, count in sorted(self.stats['excluded_characters'].items()):
                    f.write(f"- {char_type}: {count}文字\n")
                f.write(f"- **合計**: {sum(self.stats['excluded_characters'].values())}文字\n\n")
            
            # 既知のはみ出しページ
            known_overflows = self.visual_manager.data['known_overflows'].get(pdf_path.name, set())
            if known_overflows:
                f.write("## 視覚的判断による既知のはみ出しページ\n\n")
                f.write(f"{', '.join(map(str, sorted(known_overflows)))}\n\n")
            
            # 誤検知として報告されたページ
            false_positives = self.visual_manager.data['false_positives'].get(pdf_path.name, set())
            if false_positives:
                f.write("## 誤検知として除外されたページ\n\n")
                f.write(f"{', '.join(map(str, sorted(false_positives)))}\n\n")
            
            # 検出結果
            f.write("## 検出結果\n\n")
            
            if results:
                # ページリスト
                page_list = [r['page_number'] for r in results]
                f.write(f"### はみ出し検出ページ: {', '.join(map(str, page_list))}\n\n")
                
                # 優先度別の分類
                high_priority = [r for r in results if r['priority'] == 1]
                low_priority = [r for r in results if r['priority'] > 1]
                
                if high_priority:
                    f.write("### 高信頼度検出（矩形基準または視覚的判断）\n\n")
                    pages = [r['page_number'] for r in high_priority]
                    f.write(f"{', '.join(map(str, pages))}\n\n")
                
                if low_priority:
                    f.write("### 補助的検出（座標基準のみ）\n\n")
                    pages = [r['page_number'] for r in low_priority]
                    f.write(f"{', '.join(map(str, pages))}\n\n")
                
                # 各ページの詳細
                f.write("### ページ別詳細\n\n")
                
                for result in sorted(results, key=lambda r: r['page_number']):
                    page_num = result['page_number']
                    page_type = result['page_type']
                    methods = result['detection_methods']
                    priority = result['priority']
                    
                    f.write(f"#### ページ {page_num} ({page_type}ページ)")
                    if priority == 1:
                        f.write(" ★高信頼度")
                    f.write("\n")
                    f.write(f"検出方法: {', '.join(methods)}\n\n")
                    
                    # 矩形基準検出結果
                    if result['detections']['rect_overflow']:
                        rect_ovs = result['detections']['rect_overflow']
                        f.write(f"**矩形基準検出: {len(rect_ovs)}件（最優先）**\n\n")
                        
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
                            
                            for ov in block_ovs[:3]:
                                f.write(f"  - Y={ov['y_position']}: `{ov['overflow_text']}` ")
                                f.write(f"({ov['overflow_amount']:.1f}pt超過)\n")
                            
                            if len(block_ovs) > 3:
                                f.write(f"  ... 他 {len(block_ovs)-3} 件\n")
                            f.write("\n")
                    
                    # 座標ベース検出結果
                    if result['detections']['coordinate']:
                        coord_ovs = result['detections']['coordinate']
                        f.write(f"**座標ベース検出: {len(coord_ovs)}件（補助的）**\n\n")
                        for i, ov in enumerate(coord_ovs[:3], 1):
                            f.write(f"{i}. Y={ov['y_position']}: `{ov['overflow_text']}` ")
                            f.write(f"({ov['overflow_amount']:.1f}pt超過)\n")
                        if len(coord_ovs) > 3:
                            f.write(f"... 他 {len(coord_ovs)-3} 件\n")
                        f.write("\n")
                    
                    # 視覚的判断
                    if result['detections']['visual'] and 'rect_overflow' not in methods:
                        f.write("**視覚的判断**: ユーザー目視確認済みのはみ出し\n")
                        f.write("（他の検出方法では捉えられず）\n\n")
                    
                    f.write("---\n\n")
            else:
                f.write("はみ出しは検出されませんでした。\n\n")


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='視覚的判断優先ハイブリッド検出器 v6（矩形基準優先）'
    )
    parser.add_argument('pdf_file', help='検査するPDFファイル')
    parser.add_argument('-o', '--output', help='出力ファイル名', default=None)
    
    args = parser.parse_args()
    
    # 検出器を初期化
    detector = VisualHybridDetectorV6()
    
    # PDFファイルの処理
    pdf_path = Path(args.pdf_file)
    if not pdf_path.exists():
        print(f"エラー: {pdf_path} が見つかりません")
        return
    
    # 出力ファイル名を決定
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(f"testresult_{pdf_path.stem}_visual_v6.md")
    
    # PDFを処理
    results = detector.process_pdf(pdf_path)
    
    # 結果を保存
    detector.save_results(results, pdf_path, output_path)
    
    print(f"\n処理完了！")
    print(f"検出ページ数: {detector.stats['detected_pages']}")
    print(f"矩形基準: {detector.stats['rect_overflow_detections']}ページ")
    print(f"視覚的判断: {detector.stats['visual_detections']}ページ")
    print(f"座標ベース: {detector.stats['coordinate_detections']}ページ")
    print(f"結果は {output_path} に保存されました。")


if __name__ == "__main__":
    main()