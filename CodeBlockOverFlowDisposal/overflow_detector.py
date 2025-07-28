#!/usr/bin/env python3
"""
コードブロックはみ出し検出システム
技術の泉シリーズのPDFからコードブロックのテキストはみ出しを検出

Stage 1: 灰色背景コードブロックの検出（1日実装）
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Tuple
import pdfplumber
import fitz  # PyMuPDF


class CodeBlockOverflowDetector:
    """コードブロックのはみ出し検出クラス"""
    
    # 定数定義
    GRAY_COLOR = 0.85         # NextPublishingの標準グレー（実測値）
    COLOR_TOLERANCE = 0.05    # 色の許容誤差（0.8～0.9をカバー）
    MIN_OVERFLOW = 0.1        # 最小はみ出し幅（pt）
    
    def __init__(self):
        """初期化"""
        self.results = []     # 検出結果の保存
        self.errors = []      # エラー情報の保存
        self.start_time = None
        self.end_time = None
    
    def detect_file(self, pdf_path: Path) -> List[int]:
        """
        PDFファイルを解析してはみ出しページを検出
        
        Args:
            pdf_path: 解析対象のPDFファイルパス
            
        Returns:
            はみ出しが検出されたページ番号のリスト（1-indexed）
        """
        self.start_time = datetime.now()
        overflow_pages = []
        doc_fitz = None
        
        try:
            # ファイル存在確認
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")
            
            # PyMuPDFでPDFを開く
            doc_fitz = fitz.open(str(pdf_path))
            total_pages = len(doc_fitz)
            
            # pdfplumberでも開く
            with pdfplumber.open(pdf_path) as pdf_plumber:
                # 各ページを処理
                for page_num in range(total_pages):
                    if page_num % 10 == 0 and page_num > 0:
                        print(f"  処理中: {page_num}/{total_pages} ページ...")
                    
                    page_fitz = doc_fitz[page_num]
                    page_plumber = pdf_plumber.pages[page_num]
                    
                    # 灰色矩形を検出
                    gray_rects = self._find_gray_rectangles(page_fitz)
                    
                    # デバッグ情報
                    if gray_rects:
                        print(f"    ページ {page_num + 1}: {len(gray_rects)} 個の灰色矩形を検出")
                    
                    # 各矩形でテキストオーバーフローをチェック
                    for rect in gray_rects:
                        if self._check_text_overflow(page_plumber, rect):
                            overflow_pages.append(page_num + 1)  # 1-indexed
                            break  # このページは既に検出済み
            
            self.end_time = datetime.now()
            
        except FileNotFoundError as e:
            self.errors.append(str(e))
            print(f"エラー: {e}")
            return []
            
        except Exception as e:
            self.errors.append(f"予期しないエラー: {str(e)}")
            print(f"エラー: PDFの処理中に問題が発生しました - {e}")
            return []
        
        finally:
            # リソースのクリーンアップ
            if doc_fitz:
                doc_fitz.close()
        
        return sorted(list(set(overflow_pages)))
    
    def _find_gray_rectangles(self, page_fitz) -> List[fitz.Rect]:
        """
        PyMuPDFで灰色背景の矩形を検出
        
        Args:
            page_fitz: PyMuPDFのページオブジェクト
            
        Returns:
            灰色矩形のリスト
        """
        gray_rects = []
        
        # 図形情報を取得
        drawings = page_fitz.get_drawings()
        
        for item in drawings:
            # 塗りつぶし図形のみ対象
            if item['type'] == 'f':  # 'f' = filled
                fill_color = item.get('fill')
                
                # 灰色かどうか判定
                if fill_color and self._is_gray_color(fill_color):
                    # fitz.Rectオブジェクトに変換
                    rect = fitz.Rect(item['rect'])
                    gray_rects.append(rect)
        
        return gray_rects
    
    def _is_gray_color(self, color: Tuple[float, ...]) -> bool:
        """
        色が灰色かどうか判定
        
        Args:
            color: 色情報のタプル（R, G, B）
            
        Returns:
            灰色の場合True
        """
        if not color or len(color) < 3:
            return False
        
        r, g, b = color[:3]
        
        # RGBが全て同じ値で、目標の灰色に近いか確認
        if r == g == b:
            return abs(r - self.GRAY_COLOR) <= self.COLOR_TOLERANCE
        
        return False
    
    def _check_text_overflow(self, page_plumber, rect: fitz.Rect) -> bool:
        """
        pdfplumberでテキストのはみ出しをチェック
        
        Args:
            page_plumber: pdfplumberのページオブジェクト
            rect: チェック対象の矩形（PyMuPDFのRect）
            
        Returns:
            はみ出しがある場合True
        """
        # 矩形の境界ボックスを取得
        bbox = (rect.x0, rect.y0, rect.x1, rect.y1)
        
        # 矩形内のテキストを抽出
        try:
            cropped = page_plumber.within_bbox(bbox)
            
            if cropped.chars:
                # 各文字の位置をチェック
                for char in cropped.chars:
                    # 右端の座標を確認
                    char_right = char['x1']
                    
                    # はみ出し幅を計算
                    overflow = char_right - rect.x1
                    
                    if overflow > self.MIN_OVERFLOW:
                        return True
        except Exception as e:
            # 個別ページのエラーは記録するが処理は継続
            self.errors.append(f"ページ内エラー: {str(e)}")
        
        return False
    
    def generate_report(self, pdf_path: Path, overflow_pages: List[int], 
                       output_path: Optional[Path] = None) -> str:
        """
        検出結果のレポート生成
        
        Args:
            pdf_path: 解析したPDFファイル
            overflow_pages: はみ出しが検出されたページ番号のリスト
            output_path: レポート出力先（省略時は標準出力のみ）
            
        Returns:
            レポート文字列
        """
        # 処理時間の計算
        if self.start_time and self.end_time:
            process_time = (self.end_time - self.start_time).total_seconds()
        else:
            process_time = 0
        
        # レポート作成
        report_lines = [
            "=== コードブロックはみ出し検出結果 ===",
            f"ファイル: {pdf_path.name}",
            f"検出日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
        
        if overflow_pages:
            report_lines.extend([
                "はみ出しが検出されたページ:",
                ", ".join(map(str, overflow_pages)),
                "",
                f"検出数: {len(overflow_pages)}ページ",
            ])
        else:
            report_lines.extend([
                "はみ出しは検出されませんでした。",
                "",
            ])
        
        report_lines.append(f"処理時間: {process_time:.1f}秒")
        
        # エラーがある場合は追記
        if self.errors:
            report_lines.extend([
                "",
                "警告:",
            ])
            for error in self.errors[:5]:  # 最初の5件のみ表示
                report_lines.append(f"  - {error}")
        
        report = "\n".join(report_lines)
        
        # ファイル出力（指定された場合）
        if output_path:
            output_path.write_text(report, encoding='utf-8')
            print(f"レポートを保存しました: {output_path}")
        
        return report


def main():
    """コマンドラインエントリーポイント"""
    parser = argparse.ArgumentParser(
        description="技術の泉シリーズPDFのコードブロックはみ出し検出"
    )
    parser.add_argument('pdf_file', help='検査対象のPDFファイル')
    parser.add_argument('-o', '--output', help='レポート出力先ファイル')
    
    args = parser.parse_args()
    
    # パスの準備
    pdf_path = Path(args.pdf_file)
    output_path = Path(args.output) if args.output else None
    
    # 検出器の初期化と実行
    detector = CodeBlockOverflowDetector()
    
    print(f"解析中: {pdf_path.name}")
    overflow_pages = detector.detect_file(pdf_path)
    
    # レポート生成と表示
    report = detector.generate_report(pdf_path, overflow_pages, output_path)
    print()
    print(report)
    
    # 終了コード（はみ出しがある場合は1）
    sys.exit(1 if overflow_pages else 0)


if __name__ == "__main__":
    main()