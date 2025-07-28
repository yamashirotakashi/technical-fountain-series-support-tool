#!/usr/bin/env python3
"""
技術検証プロトタイプ
PDFから灰色背景の矩形とテキストを検出できるか検証
"""

import pdfplumber
import fitz  # PyMuPDF
import sys
from pathlib import Path


def test_with_pdfplumber(pdf_path):
    """pdfplumberでの検証"""
    print("=== pdfplumberでの検証 ===")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"総ページ数: {len(pdf.pages)}")
            
            # 48ページ（サンプルのはみ出しページ）を確認
            if len(pdf.pages) >= 48:
                page = pdf.pages[47]  # 0-indexed
                print(f"\nページ48の解析:")
                
                # 矩形を確認
                if hasattr(page, 'rects'):
                    print(f"矩形数: {len(page.rects) if page.rects else 0}")
                    
                    # 灰色の矩形を探す
                    gray_rects = []
                    for rect in (page.rects or []):
                        # rectの構造を確認
                        print(f"矩形情報: {rect}")
                        
                        # fill属性があるか確認
                        if isinstance(rect, dict) and 'fill' in rect:
                            fill = rect['fill']
                            if fill and len(fill) == 3:
                                r, g, b = fill
                                # 灰色判定（R≈G≈B かつ 0.85-0.95）
                                if abs(r - g) < 0.05 and abs(g - b) < 0.05 and 0.85 < r < 0.95:
                                    gray_rects.append(rect)
                    
                    print(f"灰色矩形数: {len(gray_rects)}")
                
                # テキストを確認
                chars = page.chars
                print(f"文字数: {len(chars) if chars else 0}")
                
                if chars and len(chars) > 0:
                    # 最初の数文字を表示
                    print("最初の5文字:")
                    for i, char in enumerate(chars[:5]):
                        print(f"  {char}")
                
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()


def test_with_pymupdf(pdf_path):
    """PyMuPDFでの検証"""
    print("\n=== PyMuPDFでの検証 ===")
    
    try:
        doc = fitz.open(pdf_path)
        print(f"総ページ数: {doc.page_count}")
        
        if doc.page_count >= 48:
            page = doc[47]  # 0-indexed
            print(f"\nページ48の解析:")
            
            # 図形を取得
            drawings = page.get_drawings()
            print(f"図形数: {len(drawings)}")
            
            # 灰色の矩形を探す
            gray_rects = []
            for item in drawings:
                if item['type'] == 'f':  # filled rectangle
                    # 塗りつぶし色を確認
                    if 'fill' in item and item['fill']:
                        color = item['fill']
                        if color and len(color) == 3:
                            r, g, b = color
                            # 灰色判定
                            if abs(r - g) < 0.05 and abs(g - b) < 0.05 and 0.85 < r < 0.95:
                                gray_rects.append(item)
                                print(f"灰色矩形発見: {item['rect']}")
            
            print(f"灰色矩形数: {len(gray_rects)}")
            
            # テキストを取得
            text_page = page.get_textpage()
            text_dict = text_page.extractDICT()
            
            char_count = 0
            for block in text_dict['blocks']:
                if block['type'] == 0:  # text block
                    for line in block['lines']:
                        for span in line['spans']:
                            char_count += len(span['text'])
            
            print(f"文字数: {char_count}")
            
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'doc' in locals():
            doc.close()


def main():
    if len(sys.argv) != 2:
        # デフォルトでsample.pdfを使用
        pdf_path = Path(__file__).parent / "sample.pdf"
        if not pdf_path.exists():
            print("使用方法: python technical_validation.py <PDFファイル>")
            sys.exit(1)
    else:
        pdf_path = Path(sys.argv[1])
    
    if not pdf_path.exists():
        print(f"エラー: ファイルが見つかりません: {pdf_path}")
        sys.exit(1)
    
    print(f"検証対象: {pdf_path}")
    print("=" * 50)
    
    # pdfplumberで検証
    test_with_pdfplumber(pdf_path)
    
    # PyMuPDFで検証
    test_with_pymupdf(pdf_path)


if __name__ == "__main__":
    main()