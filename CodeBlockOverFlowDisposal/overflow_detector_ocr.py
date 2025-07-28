#!/usr/bin/env python3
"""
コードブロックはみ出し検出システム - OCRベース版
本文幅を逸脱しているテキストをOCRで検出
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Tuple
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import numpy as np
import io


class OCRBasedOverflowDetector:
    """OCRベースの本文幅逸脱検出クラス"""
    
    # 定数定義
    DPI = 300  # PDF→画像変換の解像度
    
    # はみ出し検出パラメータ（調整可能）
    MIN_CONFIDENCE = 30      # OCR信頼度閾値（0-100）
    MARGIN_TOLERANCE_PX = 20  # 右マージン許容範囲（px）
    MIN_OVERFLOW_PX = 1      # 最小はみ出し検出量（px）- 1pxでも不良品
    LEFT_MARGIN_TOLERANCE_PX = 15  # 左マージン許容範囲（px）
    
    # B5判のレイアウト（技術の泉シリーズ標準）
    # ページサイズ: 182mm × 257mm (B5)
    PAGE_WIDTH_MM = 182
    PAGE_HEIGHT_MM = 257
    
    # 本文エリアのマージン（mm）
    # 左右ページで異なる（見開きを考慮）
    LEFT_PAGE_LEFT_MARGIN_MM = 20    # 左ページ（偶数ページ）の左マージン
    LEFT_PAGE_RIGHT_MARGIN_MM = 15   # 左ページ（偶数ページ）の右マージン
    RIGHT_PAGE_LEFT_MARGIN_MM = 15   # 右ページ（奇数ページ）の左マージン
    RIGHT_PAGE_RIGHT_MARGIN_MM = 20  # 右ページ（奇数ページ）の右マージン
    
    TOP_MARGIN_MM = 20
    BOTTOM_MARGIN_MM = 20
    
    def __init__(self):
        """初期化"""
        self.results = []
        self.errors = []
        self.start_time = None
        self.end_time = None
        
        # mm to pixel conversion (at 300 DPI)
        self.mm_to_px = self.DPI / 25.4
        
    def detect_file(self, pdf_path: Path) -> List[int]:
        """
        PDFファイルを解析して、本文幅からのはみ出しページを検出
        
        Args:
            pdf_path: 解析対象のPDFファイルパス
            
        Returns:
            はみ出しが検出されたページ番号のリスト（1-indexed）
        """
        self.start_time = datetime.now()
        overflow_pages = []
        
        try:
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")
            
            print("PDFをOCR解析中...")
            print("注意: B5判（182×257mm）、左右ページでマージンが異なります")
            
            # PyMuPDFでPDFを開く
            doc = fitz.open(str(pdf_path))
            total_pages = len(doc)
            
            # 各ページを処理
            for page_num in range(total_pages):
                if page_num % 10 == 0 and page_num > 0:
                    print(f"  処理中: {page_num}/{total_pages} ページ...")
                
                # ページを画像に変換
                page = doc[page_num]
                
                # ページ番号（1-indexed）
                page_number = page_num + 1
                
                # 左右ページの判定（奇数ページ=右ページ、偶数ページ=左ページ）
                is_right_page = (page_number % 2 == 1)
                
                # ページを画像化
                mat = fitz.Matrix(self.DPI/72, self.DPI/72)
                pix = page.get_pixmap(matrix=mat)
                
                # PIL形式に変換
                img_data = pix.pil_tobytes(format="PNG")
                image = Image.open(io.BytesIO(img_data))
                
                # OCRでテキストと位置情報を取得
                if self._check_text_overflow_ocr(image, is_right_page, page_number):
                    overflow_pages.append(page_number)
            
            doc.close()
            self.end_time = datetime.now()
            
        except Exception as e:
            self.errors.append(f"エラー: {str(e)}")
            print(f"エラー: {e}")
            return []
        
        return sorted(list(set(overflow_pages)))
    
    def _check_text_overflow_ocr(self, image: Image.Image, is_right_page: bool, page_number: int) -> bool:
        """
        OCRでテキストを認識し、本文幅を超えているかチェック
        
        Args:
            image: PIL形式の画像
            is_right_page: 右ページかどうか（True=右ページ=奇数ページ）
            page_number: ページ番号（デバッグ用）
            
        Returns:
            はみ出しがある場合True
        """
        # 画像サイズを取得
        img_width, img_height = image.size
        
        # マージンをピクセルに変換（左右ページで異なる）
        if is_right_page:
            left_margin_px = int(self.RIGHT_PAGE_LEFT_MARGIN_MM * self.mm_to_px)
            right_margin_px = int(self.RIGHT_PAGE_RIGHT_MARGIN_MM * self.mm_to_px)
        else:
            left_margin_px = int(self.LEFT_PAGE_LEFT_MARGIN_MM * self.mm_to_px)
            right_margin_px = int(self.LEFT_PAGE_RIGHT_MARGIN_MM * self.mm_to_px)
        
        # 本文エリアの右端位置
        text_right_edge = img_width - right_margin_px
        
        # OCRでテキストの位置情報を取得
        try:
            # Tesseractの詳細データを取得
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang='jpn+eng')
            
            # 各テキスト要素をチェック
            n_boxes = len(data['text'])
            overflow_detected = False
            
            for i in range(n_boxes):
                # 空白でないテキストかつ信頼度が高いもののみ処理
                if data['text'][i].strip() and int(data['conf'][i]) >= self.MIN_CONFIDENCE:
                    # テキストボックスの右端位置
                    text_left = data['left'][i]
                    text_width = data['width'][i]
                    text_right = text_left + text_width
                    
                    # 本文エリア内のテキストのみチェック（左マージンより右にある）
                    if text_left >= left_margin_px - self.LEFT_MARGIN_TOLERANCE_PX:
                        # 右端が本文幅を超えているかチェック
                        overflow_threshold = text_right_edge + self.MARGIN_TOLERANCE_PX
                        if text_right > overflow_threshold:
                            overflow_amount = text_right - text_right_edge
                            
                            # 最小はみ出し量の確認（小さなはみ出しは無視）
                            if overflow_amount >= self.MIN_OVERFLOW_PX:
                                # デバッグ情報
                                print(f"    ページ {page_number} ({'右' if is_right_page else '左'}ページ): "
                                      f"はみ出し検出 - {overflow_amount:.1f}px超過")
                                print(f"      テキスト: '{data['text'][i][:30]}...'")
                                print(f"      位置: left={text_left}, right={text_right}, "
                                      f"本文右端={text_right_edge}, 閾値={overflow_threshold}")
                                
                                overflow_detected = True
            
            return overflow_detected
            
        except Exception as e:
            print(f"    ページ {page_number}: OCRエラー - {e}")
            return False
    
    def generate_report(self, pdf_path: Path, overflow_pages: List[int], 
                       output_path: Optional[Path] = None) -> str:
        """
        検出結果のレポート生成
        """
        if self.start_time and self.end_time:
            process_time = (self.end_time - self.start_time).total_seconds()
        else:
            process_time = 0
        
        report_lines = [
            "=== コードブロックはみ出し検出結果 (OCR版) ===",
            f"ファイル: {pdf_path.name}",
            f"検出日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"ページサイズ: B5 ({self.PAGE_WIDTH_MM}×{self.PAGE_HEIGHT_MM}mm)",
            f"左ページマージン: 左{self.LEFT_PAGE_LEFT_MARGIN_MM}mm / 右{self.LEFT_PAGE_RIGHT_MARGIN_MM}mm",
            f"右ページマージン: 左{self.RIGHT_PAGE_LEFT_MARGIN_MM}mm / 右{self.RIGHT_PAGE_RIGHT_MARGIN_MM}mm",
            "",
        ]
        
        if overflow_pages:
            report_lines.extend([
                "本文幅からはみ出しているページ:",
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
        
        if self.errors:
            report_lines.extend([
                "",
                "エラー:",
                *self.errors
            ])
        
        report = "\n".join(report_lines)
        
        if output_path:
            output_path.write_text(report, encoding='utf-8')
            print(f"レポートを保存しました: {output_path}")
        
        return report


def main():
    """コマンドラインエントリーポイント"""
    parser = argparse.ArgumentParser(
        description="技術の泉シリーズPDFのOCRベース本文幅逸脱検出"
    )
    parser.add_argument('pdf_file', help='検査対象のPDFファイル')
    parser.add_argument('-o', '--output', help='レポート出力先ファイル')
    parser.add_argument('--lang', default='jpn+eng', help='OCR言語設定（デフォルト: jpn+eng）')
    parser.add_argument('--min-confidence', type=int, default=30, 
                       help='OCR信頼度閾値（0-100、デフォルト: 30）')
    parser.add_argument('--margin-tolerance', type=int, default=20,
                       help='右マージン許容範囲（px、デフォルト: 20）')
    parser.add_argument('--min-overflow', type=int, default=1,
                       help='最小はみ出し検出量（px、デフォルト: 1）')
    
    args = parser.parse_args()
    
    pdf_path = Path(args.pdf_file)
    output_path = Path(args.output) if args.output else None
    
    # Tesseractの確認
    try:
        pytesseract.get_tesseract_version()
    except Exception as e:
        print("エラー: Tesseract OCRがインストールされていません")
        print("インストール方法:")
        print("  Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-jpn")
        print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        sys.exit(1)
    
    # 検出器の初期化と実行
    detector = OCRBasedOverflowDetector()
    
    # コマンドライン引数でパラメータを上書き
    detector.MIN_CONFIDENCE = args.min_confidence
    detector.MARGIN_TOLERANCE_PX = args.margin_tolerance
    detector.MIN_OVERFLOW_PX = args.min_overflow
    
    print(f"解析中: {pdf_path.name}")
    print(f"設定 - 信頼度閾値: {detector.MIN_CONFIDENCE}, マージン許容: {detector.MARGIN_TOLERANCE_PX}px, 最小はみ出し: {detector.MIN_OVERFLOW_PX}px")
    overflow_pages = detector.detect_file(pdf_path)
    
    # レポート生成と表示
    report = detector.generate_report(pdf_path, overflow_pages, output_path)
    print()
    print(report)
    
    sys.exit(1 if overflow_pages else 0)


if __name__ == "__main__":
    main()