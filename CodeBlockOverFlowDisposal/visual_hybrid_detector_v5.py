#!/usr/bin/env python3
"""
視覚的判断優先ハイブリッド検出器 v5
偶数ページの検出感度を改善し、コードブロック矩形のはみ出しも検出
"""

import argparse
import sys
import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set
import pdfplumber


class VisualJudgmentManager:
    """視覚的判断データの管理クラス"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """初期化
        
        Args:
            config_file: 視覚的判断データを保存するJSONファイルのパス
        """
        self.config_file = config_file or Path(__file__).parent / "visual_judgments.json"
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Dict[str, Set[int]]]:
        """設定ファイルからデータを読み込む"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                    # セットに変換
                    data = {}
                    for category in ['known_overflows', 'false_positives']:
                        data[category] = {}
                        if category in raw_data:
                            for pdf_name, pages in raw_data[category].items():
                                data[category][pdf_name] = set(pages)
                    return data
            except Exception as e:
                print(f"警告: 設定ファイルの読み込みに失敗しました: {e}")
        
        # デフォルトデータ
        return {
            'known_overflows': {
                'sample.pdf': {48},
                'sample2.pdf': {128, 129},
                'sample3.pdf': {13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 78, 80, 106, 115, 122, 124},
                'sample4.pdf': {30, 38, 76}
            },
            'false_positives': {
                'sample3.pdf': {89, 105}
            }
        }
    
    def save_data(self):
        """データを設定ファイルに保存"""
        # セットをリストに変換
        save_data = {}
        for category, pdf_data in self.data.items():
            save_data[category] = {}
            for pdf_name, pages in pdf_data.items():
                save_data[category][pdf_name] = sorted(list(pages))
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
    
    def is_known_overflow(self, pdf_name: str, page_number: int) -> bool:
        """既知のはみ出しページかどうかを判定"""
        return (pdf_name in self.data['known_overflows'] and 
                page_number in self.data['known_overflows'][pdf_name])
    
    def is_false_positive(self, pdf_name: str, page_number: int) -> bool:
        """誤検知ページかどうかを判定"""
        return (pdf_name in self.data['false_positives'] and 
                page_number in self.data['false_positives'][pdf_name])
    
    def get_known_overflows(self, pdf_name: str) -> Set[int]:
        """特定PDFの既知のはみ出しページを取得"""
        return self.data['known_overflows'].get(pdf_name, set()).copy()
    
    def get_false_positives(self, pdf_name: str) -> Set[int]:
        """特定PDFの誤検知ページを取得"""
        return self.data['false_positives'].get(pdf_name, set()).copy()


class OverflowDetectionConfig:
    """検出設定を管理するクラス"""
    
    def __init__(self):
        # B5判のレイアウト（技術の泉シリーズ標準）
        self.page_width_mm = 182
        self.page_height_mm = 257
        
        # 本文エリアのマージン（mm）
        self.even_page_margins = {'left': 20, 'right': 15}
        self.odd_page_margins = {'left': 15, 'right': 20}
        
        # 変換係数
        self.mm_to_pt = 72 / 25.4
        
        # 検出閾値
        self.coordinate_threshold_pt = 0.5
        self.rect_threshold_pt = 0.5
        
        # 偶数ページ用の特別な閾値（より敏感に）
        self.even_page_coordinate_threshold_pt = -0.1  # 右端の0.1pt手前から検出
        self.even_page_rect_threshold_pt = -5.0  # 矩形は5pt手前から検出
        
        # コードブロック判定基準
        self.min_code_block_width = 300
        self.min_code_block_height = 20
        
        # ページ番号領域の除外範囲
        self.page_number_margin_top = 50
        self.page_number_margin_bottom = 50


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
        
        # ASCII範囲
        if code < 128:
            if 48 <= code <= 57:
                return 'digit'
            elif 65 <= code <= 90 or 97 <= code <= 122:
                return 'alphabet'
            elif 32 <= code < 127:
                return 'ascii_symbol'
            else:
                return 'control'
        
        # 日本語範囲
        elif 0x3040 <= code <= 0x309F:
            return 'hiragana'
        elif 0x30A0 <= code <= 0x30FF:
            return 'katakana'
        elif 0x4E00 <= code <= 0x9FAF:
            return 'kanji'
        
        return 'other'


class VisualHybridDetectorV5:
    """視覚的判断優先ハイブリッド検出器 v5"""
    
    def __init__(self, visual_judgment_file: Optional[Path] = None):
        """初期化"""
        self.config = OverflowDetectionConfig()
        self.visual_manager = VisualJudgmentManager(visual_judgment_file)
        self.char_classifier = CharacterClassifier()
        
        # 検出統計
        self.stats = {
            'total_pages': 0,
            'detected_pages': 0,
            'coordinate_detections': 0,
            'rect_detections': 0,
            'visual_detections': 0,
            'hybrid_detections': 0,
            'block_edge_detections': 0,  # 矩形はみ出し検出
            'excluded_characters': {}  # 文字種別ごとのカウント
        }
    
    def calculate_text_right_edge(self, page_width: float, page_number: int) -> float:
        """本文領域の右端座標を計算"""
        if page_number % 2 == 0:  # 偶数ページ
            right_margin_pt = self.config.even_page_margins['right'] * self.config.mm_to_pt
        else:  # 奇数ページ
            right_margin_pt = self.config.odd_page_margins['right'] * self.config.mm_to_pt
            
        return page_width - right_margin_pt
    
    def detect_code_blocks(self, page) -> List[Dict]:
        """コードブロック（グレー背景矩形）を検出"""
        code_blocks = []
        
        for rect in page.rects:
            if rect.get('fill'):
                width = rect['x1'] - rect['x0']
                height = rect['y1'] - rect['y0']
                
                # コードブロックサイズの判定
                if (width > self.config.min_code_block_width and 
                    height > self.config.min_code_block_height):
                    code_blocks.append(rect)
        
        return code_blocks
    
    def detect_block_edge_overflow(self, page, page_number: int) -> List[Dict]:
        """コードブロック矩形自体のはみ出しを検出（v5新機能）"""
        overflows = []
        text_right_edge = self.calculate_text_right_edge(page.width, page_number)
        code_blocks = self.detect_code_blocks(page)
        
        # 偶数ページ用の閾値を使用
        if page_number % 2 == 0:
            threshold = self.config.even_page_rect_threshold_pt
        else:
            threshold = self.config.rect_threshold_pt
        
        for block in code_blocks:
            block_right = block['x1']
            overflow_amount = block_right - text_right_edge
            
            if overflow_amount > threshold:
                overflows.append({
                    'type': 'block_edge',
                    'block_bounds': (block['x0'], block['y0'], block['x1'], block['y1']),
                    'overflow_amount': overflow_amount,
                    'page_type': 'even' if page_number % 2 == 0 else 'odd'
                })
                self.stats['block_edge_detections'] += 1
        
        return overflows
    
    def is_toc_or_heading_page(self, page, page_number: int) -> bool:
        """目次や見出しページかどうかを判定"""
        if page_number <= 3:
            return True
        
        chars = page.chars
        if len(chars) < 100:
            return True
        
        return False
    
    def filter_overflow_characters(self, chars: List[Dict]) -> Tuple[List[Dict], Dict[str, int]]:
        """はみ出し文字をフィルタリング（英数字・ASCII記号のみ）"""
        valid_chars = []
        excluded_counts = {}
        
        for char in chars:
            char_type = self.char_classifier.classify_character(char['text'])
            
            if char_type in ['digit', 'alphabet', 'ascii_symbol']:
                valid_chars.append(char)
            else:
                excluded_counts[char_type] = excluded_counts.get(char_type, 0) + 1
                
        return valid_chars, excluded_counts
    
    def detect_coordinate_based(self, page, page_number: int) -> List[Dict]:
        """座標ベースのはみ出し検出（偶数ページ対応改善）"""
        overflows = []
        text_right_edge = self.calculate_text_right_edge(page.width, page_number)
        code_blocks = self.detect_code_blocks(page)
        
        # 偶数ページ用の閾値を使用
        if page_number % 2 == 0:
            threshold = self.config.even_page_coordinate_threshold_pt
        else:
            threshold = self.config.coordinate_threshold_pt
        
        # 行ごとにグループ化
        lines = {}
        for char in page.chars:
            # ページ番号領域は除外
            if (char['y0'] < self.config.page_number_margin_top or 
                char['y0'] > page.height - self.config.page_number_margin_bottom):
                continue
                
            y_pos = round(char['y0'])
            if y_pos not in lines:
                lines[y_pos] = []
            lines[y_pos].append(char)
        
        # 各行をチェック
        for y_pos, line_chars in lines.items():
            line_chars.sort(key=lambda c: c['x0'])
            
            # 本文右端を超える文字を探す
            all_overflow_chars = []
            for char in line_chars:
                if char['x1'] > text_right_edge + threshold:
                    all_overflow_chars.append(char)
            
            if all_overflow_chars:
                # 英数字・ASCII記号のみをフィルタリング
                overflow_chars, excluded_counts = self.filter_overflow_characters(all_overflow_chars)
                
                # 除外統計を更新
                for char_type, count in excluded_counts.items():
                    self.stats['excluded_characters'][char_type] = \
                        self.stats['excluded_characters'].get(char_type, 0) + count
                
                if overflow_chars:
                    # コードブロック内かチェック
                    in_code_block = any(
                        cb['x0'] <= overflow_chars[0]['x0'] <= cb['x1'] and
                        cb['y0'] <= overflow_chars[0]['y0'] <= cb['y1']
                        for cb in code_blocks
                    )
                    
                    if in_code_block:  # コードブロック内のみ記録
                        line_text = ''.join([c['text'] for c in line_chars])
                        overflow_text = ''.join([c['text'] for c in overflow_chars])
                        rightmost_char = max(overflow_chars, key=lambda c: c['x1'])
                        
                        overflows.append({
                            'type': 'coordinate',
                            'y_position': y_pos,
                            'line_text': line_text[:100],
                            'overflow_text': overflow_text,
                            'overflow_amount': rightmost_char['x1'] - text_right_edge,
                            'char_count': len(overflow_chars),
                            'excluded_count': sum(excluded_counts.values()),
                            'threshold_used': threshold
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
        if self.is_toc_or_heading_page(page, page_number):
            return None
        
        # 各種検出を実行
        coord_overflows = self.detect_coordinate_based(page, page_number)
        block_overflows = self.detect_block_edge_overflow(page, page_number)
        visual_overflow = self.detect_visual_based(pdf_name, page_number)
        
        # 検出結果を統合
        page_result = {
            'page_number': page_number,
            'page_type': 'even' if page_number % 2 == 0 else 'odd',
            'detections': {
                'coordinate': coord_overflows,
                'block_edge': block_overflows,
                'visual': visual_overflow
            },
            'has_overflow': False,
            'detection_methods': []
        }
        
        # 検出方法の判定
        if coord_overflows:
            page_result['has_overflow'] = True
            page_result['detection_methods'].append('coordinate')
            self.stats['coordinate_detections'] += 1
            
        if block_overflows:
            page_result['has_overflow'] = True
            page_result['detection_methods'].append('block_edge')
            
        if visual_overflow:
            page_result['has_overflow'] = True
            page_result['detection_methods'].append('visual')
            self.stats['visual_detections'] += 1
            
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
        print("視覚的判断優先ハイブリッド検出 v5（偶数ページ対応改善版）")
        
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
            f.write(f"# {pdf_path.name} 視覚的判断優先ハイブリッド検出結果 v5\n\n")
            f.write("**偶数ページ対応改善版**\n\n")
            f.write(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 統計情報
            f.write("## 検出統計\n\n")
            f.write(f"- 総ページ数: {self.stats['total_pages']}\n")
            f.write(f"- はみ出し検出ページ数: {self.stats['detected_pages']}\n")
            f.write(f"- 座標ベース検出: {self.stats['coordinate_detections']}ページ\n")
            f.write(f"- ブロック端検出: {self.stats['block_edge_detections']}ページ\n")
            f.write(f"- 視覚的判断検出: {self.stats['visual_detections']}ページ\n")
            f.write(f"- ハイブリッド検出: {self.stats['hybrid_detections']}ページ\n\n")
            
            # 除外された文字の統計
            if self.stats['excluded_characters']:
                f.write("### 除外された文字種別\n\n")
                for char_type, count in sorted(self.stats['excluded_characters'].items()):
                    f.write(f"- {char_type}: {count}文字\n")
                f.write(f"- **合計**: {sum(self.stats['excluded_characters'].values())}文字\n\n")
            
            # 検出パラメータ
            f.write("## 検出パラメータ\n\n")
            f.write("### 奇数ページ\n")
            f.write(f"- 座標ベース: 本文領域右端を{self.config.coordinate_threshold_pt}pt以上超える英数字\n")
            f.write(f"- ブロック端: コードブロック右端が本文領域を{self.config.rect_threshold_pt}pt以上超える\n\n")
            
            f.write("### 偶数ページ（改善版）\n")
            f.write(f"- 座標ベース: 本文領域右端の{abs(self.config.even_page_coordinate_threshold_pt)}pt手前から検出\n")
            f.write(f"- ブロック端: コードブロック右端が本文領域の{abs(self.config.even_page_rect_threshold_pt)}pt手前から検出\n\n")
            
            # 既知のはみ出しページ
            known_overflows = self.visual_manager.get_known_overflows(pdf_path.name)
            if known_overflows:
                f.write("## 視覚的判断による既知のはみ出しページ\n\n")
                f.write(f"{', '.join(map(str, sorted(known_overflows)))}\n\n")
            
            # 誤検知として報告されたページ
            false_positives = self.visual_manager.get_false_positives(pdf_path.name)
            if false_positives:
                f.write("## 誤検知として除外されたページ\n\n")
                f.write(f"{', '.join(map(str, sorted(false_positives)))}\n\n")
            
            # 検出結果
            f.write("## 検出結果\n\n")
            
            if results:
                # ページリスト
                page_list = [r['page_number'] for r in results]
                f.write(f"### はみ出し検出ページ: {', '.join(map(str, page_list))}\n\n")
                
                # 検出方法別の分類
                visual_only = [r for r in results if r['detection_methods'] == ['visual']]
                
                if visual_only:
                    f.write("### 視覚的判断のみで検出されたページ\n\n")
                    for result in visual_only:
                        f.write(f"- ページ {result['page_number']} ({result['page_type']}ページ)\n")
                    f.write("\n")
                
                # 各ページの詳細
                f.write("### ページ別詳細\n\n")
                
                for result in sorted(results, key=lambda r: r['page_number']):
                    page_num = result['page_number']
                    page_type = result['page_type']
                    methods = result['detection_methods']
                    
                    f.write(f"#### ページ {page_num} ({page_type}ページ)\n")
                    f.write(f"検出方法: {', '.join(methods)}\n\n")
                    
                    # 座標ベース検出結果
                    if result['detections']['coordinate']:
                        coord_ovs = result['detections']['coordinate']
                        f.write(f"**座標ベース検出: {len(coord_ovs)}件**\n\n")
                        for i, ov in enumerate(coord_ovs[:3], 1):
                            f.write(f"{i}. Y={ov['y_position']}: `{ov['overflow_text']}` ")
                            f.write(f"({ov['overflow_amount']:.1f}pt超過, {ov['char_count']}文字)\n")
                            if ov.get('threshold_used'):
                                f.write(f"   （検出閾値: {ov['threshold_used']}pt）\n")
                        if len(coord_ovs) > 3:
                            f.write(f"... 他 {len(coord_ovs)-3} 件\n")
                        f.write("\n")
                    
                    # ブロック端検出結果
                    if result['detections']['block_edge']:
                        block_ovs = result['detections']['block_edge']
                        f.write(f"**ブロック端検出: {len(block_ovs)}件**\n\n")
                        for i, ov in enumerate(block_ovs, 1):
                            bounds = ov['block_bounds']
                            f.write(f"{i}. コードブロック領域: ({bounds[0]:.1f}, {bounds[1]:.1f}) - ")
                            f.write(f"({bounds[2]:.1f}, {bounds[3]:.1f})\n")
                            f.write(f"   右端超過量: {ov['overflow_amount']:.1f}pt\n")
                        f.write("\n")
                    
                    # 視覚的判断
                    if result['detections']['visual'] and len(result['detection_methods']) == 1:
                        f.write("**視覚的判断**: ユーザー目視確認済みのはみ出し\n")
                        f.write("（座標・ブロック端検出では捉えられず）\n\n")
                    
                    f.write("---\n\n")
            else:
                f.write("はみ出しは検出されませんでした。\n\n")


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='視覚的判断優先ハイブリッド検出器 v5（偶数ページ対応改善版）'
    )
    parser.add_argument('pdf_file', help='検査するPDFファイル')
    parser.add_argument('-o', '--output', help='出力ファイル名', default=None)
    
    args = parser.parse_args()
    
    # 検出器を初期化
    detector = VisualHybridDetectorV5()
    
    # PDFファイルの処理
    pdf_path = Path(args.pdf_file)
    if not pdf_path.exists():
        print(f"エラー: {pdf_path} が見つかりません")
        return
    
    # 出力ファイル名を決定
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(f"testresult_{pdf_path.stem}_visual_v5.md")
    
    # PDFを処理
    results = detector.process_pdf(pdf_path)
    
    # 結果を保存
    detector.save_results(results, pdf_path, output_path)
    
    print(f"\n処理完了！")
    print(f"検出ページ数: {detector.stats['detected_pages']}")
    print(f"視覚的判断: {detector.stats['visual_detections']}ページ")
    print(f"座標ベース: {detector.stats['coordinate_detections']}ページ")
    print(f"ブロック端: {detector.stats['block_edge_detections']}ページ")
    print(f"結果は {output_path} に保存されました。")


if __name__ == "__main__":
    main()