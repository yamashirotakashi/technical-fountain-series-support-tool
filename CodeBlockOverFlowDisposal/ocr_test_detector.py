#!/usr/bin/env python3
"""
OCRによるはみ出し検出テスト実装
右端のみ検出、左端は無視
奇数ページと偶数ページでマージンが異なることを考慮
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import numpy as np
import io


class OCRTestDetector:
    """OCRベースのはみ出し検出テストクラス"""
    
    # 定数定義
    DPI = 300  # PDF→画像変換の解像度
    
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
    
    # OCRパラメータ（調整対象）
    MIN_CONFIDENCE = 30      # OCR信頼度閾値
    OVERFLOW_THRESHOLD_PX = 5  # はみ出し判定閾値（ピクセル）
    
    def __init__(self):
        """初期化"""
        self.mm_to_px = self.DPI / 25.4
        self.results = {}
        
    def get_page_margins(self, page_number: int) -> Tuple[float, float]:
        """ページ番号に応じたマージンを取得（ピクセル単位）"""
        if page_number % 2 == 0:  # 偶数ページ
            left_margin_px = self.EVEN_PAGE_LEFT_MARGIN_MM * self.mm_to_px
            right_margin_px = self.EVEN_PAGE_RIGHT_MARGIN_MM * self.mm_to_px
        else:  # 奇数ページ
            left_margin_px = self.ODD_PAGE_LEFT_MARGIN_MM * self.mm_to_px
            right_margin_px = self.ODD_PAGE_RIGHT_MARGIN_MM * self.mm_to_px
        
        return left_margin_px, right_margin_px
    
    def detect_overflow_in_page(self, image: Image.Image, page_number: int) -> List[Dict]:
        """ページ画像からはみ出しを検出"""
        # 画像サイズ取得
        img_width, img_height = image.size
        
        # ページマージン取得
        left_margin_px, right_margin_px = self.get_page_margins(page_number)
        
        # 本文右端の位置
        text_right_edge = img_width - right_margin_px
        
        # NumPy配列に変換
        img_array = np.array(image)
        
        # OCRでテキスト位置を検出
        ocr_data = pytesseract.image_to_data(
            img_array, 
            lang='jpn+eng',
            output_type=pytesseract.Output.DICT
        )
        
        overflows = []
        
        # 各テキストボックスをチェック
        for i in range(len(ocr_data['text'])):
            # 信頼度チェック
            if int(ocr_data['conf'][i]) < self.MIN_CONFIDENCE:
                continue
                
            # テキストが空でないことを確認
            text = ocr_data['text'][i].strip()
            if not text:
                continue
            
            # テキストボックスの右端位置
            box_left = ocr_data['left'][i]
            box_width = ocr_data['width'][i]
            box_right = box_left + box_width
            
            # 右端からのはみ出しをチェック（左端は無視）
            if box_right > text_right_edge + self.OVERFLOW_THRESHOLD_PX:
                overflow_amount = box_right - text_right_edge
                overflows.append({
                    'text': text,
                    'position': (box_left, ocr_data['top'][i]),
                    'overflow_px': overflow_amount,
                    'confidence': ocr_data['conf'][i]
                })
        
        return overflows
    
    def process_pdf(self, pdf_path: Path) -> Dict[int, List[Dict]]:
        """PDFファイル全体を処理"""
        print(f"処理開始: {pdf_path}")
        print(f"OCR信頼度閾値: {self.MIN_CONFIDENCE}%")
        print(f"はみ出し判定閾値: {self.OVERFLOW_THRESHOLD_PX}px")
        print("右端のみ検出（左端は無視）\n")
        
        doc = fitz.open(str(pdf_path))
        total_pages = len(doc)
        overflow_pages = {}
        
        for page_num in range(total_pages):
            page_number = page_num + 1
            
            if page_num % 10 == 0:
                print(f"処理中: {page_number}/{total_pages}ページ...")
            
            # ページを画像化
            page = doc[page_num]
            mat = fitz.Matrix(self.DPI/72, self.DPI/72)
            pix = page.get_pixmap(matrix=mat)
            
            # PIL形式に変換
            img_data = pix.pil_tobytes(format="PNG")
            image = Image.open(io.BytesIO(img_data))
            
            # はみ出し検出
            overflows = self.detect_overflow_in_page(image, page_number)
            
            if overflows:
                overflow_pages[page_number] = overflows
        
        doc.close()
        return overflow_pages
    
    def save_results(self, results: Dict[str, Dict], output_path: Path):
        """結果をtestresult.mdに保存"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# OCRはみ出し検出テスト結果\n")
            f.write(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"検出パラメータ:\n")
            f.write(f"- OCR信頼度閾値: {self.MIN_CONFIDENCE}%\n")
            f.write(f"- はみ出し判定閾値: {self.OVERFLOW_THRESHOLD_PX}px\n")
            f.write(f"- 検出対象: 右端のみ（左端は無視）\n\n")
            
            if not results:
                f.write("はみ出しは検出されませんでした。\n")
                return
            
            # ファイルごとに結果を出力
            for pdf_name, overflow_pages in results.items():
                if overflow_pages:
                    page_list = sorted(overflow_pages.keys())
                    page_str = ", ".join(map(str, page_list))
                    f.write(f"## {pdf_name}: {page_str}\n\n")
                    
                    # 詳細情報
                    for page_num in page_list:
                        f.write(f"### ページ {page_num}\n")
                        overflows = overflow_pages[page_num]
                        for i, overflow in enumerate(overflows, 1):
                            f.write(f"- 検出 {i}:\n")
                            f.write(f"  - テキスト: `{overflow['text'][:50]}...`\n")
                            f.write(f"  - はみ出し量: {overflow['overflow_px']:.1f}px\n")
                            f.write(f"  - OCR信頼度: {overflow['confidence']}%\n")
                        f.write("\n")
                else:
                    f.write(f"## {pdf_name}: はみ出しなし\n\n")


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='OCRによるはみ出し検出テスト')
    parser.add_argument('pdf_files', nargs='+', help='検査するPDFファイル')
    parser.add_argument('--confidence', type=int, default=30, 
                       help='OCR信頼度閾値 (default: 30)')
    parser.add_argument('--threshold', type=int, default=5,
                       help='はみ出し判定閾値px (default: 5)')
    
    args = parser.parse_args()
    
    # 検出器を初期化
    detector = OCRTestDetector()
    detector.MIN_CONFIDENCE = args.confidence
    detector.OVERFLOW_THRESHOLD_PX = args.threshold
    
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
                print(f"\n{pdf_path.name}: はみ出し検出ページ: {page_list}")
            else:
                print(f"\n{pdf_path.name}: はみ出しなし")
                
        except Exception as e:
            print(f"エラー: {pdf_path.name} の処理中にエラー: {e}")
            all_results[pdf_path.name] = {}
    
    # 結果を保存
    output_path = Path("testresult.md")
    detector.save_results(all_results, output_path)
    print(f"\n結果を {output_path} に保存しました。")
    print("PDFを目視確認して、実際のはみ出しと比較してください。")


if __name__ == "__main__":
    main()