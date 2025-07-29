#!/usr/bin/env python3
"""
シンプルなOCRテスト - 1ページだけ処理
"""

import sys
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import numpy as np
import io


def test_single_page(pdf_path: str, page_num: int = 0):
    """1ページだけOCRテスト"""
    print(f"PDFファイル: {pdf_path}")
    print(f"ページ番号: {page_num + 1}")
    
    try:
        # PDFを開く
        doc = fitz.open(pdf_path)
        if page_num >= len(doc):
            print(f"エラー: ページ番号が範囲外です（総ページ数: {len(doc)}）")
            return
        
        # ページを画像化
        page = doc[page_num]
        mat = fitz.Matrix(300/72, 300/72)  # 300 DPI
        pix = page.get_pixmap(matrix=mat)
        
        # PIL形式に変換
        img_data = pix.pil_tobytes(format="PNG")
        image = Image.open(io.BytesIO(img_data))
        
        print(f"画像サイズ: {image.size}")
        
        # OCRテスト
        print("\nOCR実行中...")
        img_array = np.array(image)
        
        # OCRデータを取得
        ocr_data = pytesseract.image_to_data(
            img_array, 
            lang='jpn+eng',
            output_type=pytesseract.Output.DICT
        )
        
        # 右端の位置を計算（B5判想定）
        img_width = image.size[0]
        # 奇数ページなら右マージン20mm、偶数ページなら15mm
        page_number = page_num + 1
        if page_number % 2 == 1:  # 奇数ページ
            right_margin_px = 20 * (300 / 25.4)  # 20mm
        else:  # 偶数ページ
            right_margin_px = 15 * (300 / 25.4)  # 15mm
        
        text_right_edge = img_width - right_margin_px
        print(f"本文右端位置: {text_right_edge:.1f}px")
        
        # はみ出しチェック
        overflow_count = 0
        for i in range(len(ocr_data['text'])):
            if int(ocr_data['conf'][i]) < 30:  # 信頼度30%以上
                continue
            
            text = ocr_data['text'][i].strip()
            if not text:
                continue
            
            box_right = ocr_data['left'][i] + ocr_data['width'][i]
            
            if box_right > text_right_edge + 5:  # 5px以上はみ出し
                overflow_amount = box_right - text_right_edge
                overflow_count += 1
                print(f"\nはみ出し検出 {overflow_count}:")
                print(f"  テキスト: '{text[:30]}...'")
                print(f"  右端位置: {box_right:.1f}px")
                print(f"  はみ出し量: {overflow_amount:.1f}px")
        
        if overflow_count == 0:
            print("\nはみ出しは検出されませんでした。")
        else:
            print(f"\n合計 {overflow_count} 件のはみ出しを検出しました。")
        
        doc.close()
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用法: python ocr_test_simple.py PDFファイル [ページ番号]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    page_num = int(sys.argv[2]) - 1 if len(sys.argv) > 2 else 0
    
    test_single_page(pdf_path, page_num)