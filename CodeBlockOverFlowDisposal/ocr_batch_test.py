#!/usr/bin/env python3
"""
バッチ処理版OCRテスト - 複数PDFを処理してtestresult.mdに出力
"""

import sys
from pathlib import Path
from datetime import datetime
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import numpy as np
import io


class BatchOCRTester:
    def __init__(self, confidence=30, threshold=5):
        self.MIN_CONFIDENCE = confidence
        self.OVERFLOW_THRESHOLD_PX = threshold
        self.DPI = 300
        self.mm_to_px = self.DPI / 25.4
        
    def process_page(self, doc, page_num):
        """1ページを処理してはみ出しを検出"""
        page = doc[page_num]
        page_number = page_num + 1
        
        # ページを画像化
        mat = fitz.Matrix(self.DPI/72, self.DPI/72)
        pix = page.get_pixmap(matrix=mat)
        
        # PIL形式に変換
        img_data = pix.pil_tobytes(format="PNG")
        image = Image.open(io.BytesIO(img_data))
        
        # 右端の位置を計算
        img_width = image.size[0]
        if page_number % 2 == 1:  # 奇数ページ
            right_margin_px = 20 * self.mm_to_px  # 20mm
        else:  # 偶数ページ
            right_margin_px = 15 * self.mm_to_px  # 15mm
        
        text_right_edge = img_width - right_margin_px
        
        # OCR実行
        img_array = np.array(image)
        ocr_data = pytesseract.image_to_data(
            img_array, 
            lang='jpn+eng',
            output_type=pytesseract.Output.DICT
        )
        
        # はみ出しチェック
        overflows = []
        for i in range(len(ocr_data['text'])):
            if int(ocr_data['conf'][i]) < self.MIN_CONFIDENCE:
                continue
            
            text = ocr_data['text'][i].strip()
            if not text:
                continue
            
            box_right = ocr_data['left'][i] + ocr_data['width'][i]
            
            if box_right > text_right_edge + self.OVERFLOW_THRESHOLD_PX:
                overflow_amount = box_right - text_right_edge
                overflows.append({
                    'text': text,
                    'amount': overflow_amount,
                    'position': box_right
                })
        
        return overflows
    
    def process_pdf(self, pdf_path):
        """PDFファイル全体を処理"""
        print(f"処理中: {pdf_path.name}")
        
        doc = fitz.open(str(pdf_path))
        total_pages = len(doc)
        overflow_pages = {}
        
        for page_num in range(total_pages):
            if page_num % 10 == 0 and page_num > 0:
                print(f"  {page_num}/{total_pages} ページ処理済み...")
            
            overflows = self.process_page(doc, page_num)
            if overflows:
                overflow_pages[page_num + 1] = overflows
        
        doc.close()
        return overflow_pages
    
    def save_results(self, all_results, output_path):
        """結果をtestresult.mdに保存"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# OCRはみ出し検出テスト結果\n\n")
            f.write(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## 検出パラメータ\n")
            f.write(f"- OCR信頼度閾値: {self.MIN_CONFIDENCE}%\n")
            f.write(f"- はみ出し判定閾値: {self.OVERFLOW_THRESHOLD_PX}px\n")
            f.write("- 検出対象: 右端のみ（左端は無視）\n")
            f.write("- 奇数ページ右マージン: 20mm\n")
            f.write("- 偶数ページ右マージン: 15mm\n\n")
            
            f.write("## 検出結果\n\n")
            
            for pdf_name, overflow_pages in all_results.items():
                if overflow_pages:
                    page_list = sorted(overflow_pages.keys())
                    page_str = ", ".join(map(str, page_list))
                    f.write(f"### {pdf_name}: ページ {page_str}\n\n")
                else:
                    f.write(f"### {pdf_name}: はみ出しなし\n\n")
            
            # 詳細情報
            f.write("\n## 詳細情報\n\n")
            for pdf_name, overflow_pages in all_results.items():
                if overflow_pages:
                    f.write(f"### {pdf_name}\n\n")
                    for page_num in sorted(overflow_pages.keys()):
                        f.write(f"#### ページ {page_num}\n")
                        overflows = overflow_pages[page_num]
                        f.write(f"検出数: {len(overflows)}件\n\n")
                        
                        for i, overflow in enumerate(overflows[:5], 1):  # 最初の5件のみ
                            f.write(f"{i}. テキスト: `{overflow['text'][:20]}...`\n")
                            f.write(f"   はみ出し量: {overflow['amount']:.1f}px\n\n")
                        
                        if len(overflows) > 5:
                            f.write(f"... 他 {len(overflows) - 5} 件\n\n")


def main():
    # テスト対象のPDFファイル
    pdf_files = [
        "sample.pdf",
        "sample2.pdf", 
        "sampleOverflow.pdf"
    ]
    
    tester = BatchOCRTester(confidence=30, threshold=5)
    all_results = {}
    
    for pdf_name in pdf_files:
        pdf_path = Path(pdf_name)
        if pdf_path.exists():
            try:
                overflow_pages = tester.process_pdf(pdf_path)
                all_results[pdf_name] = overflow_pages
            except Exception as e:
                print(f"エラー: {pdf_name} - {e}")
                all_results[pdf_name] = {}
        else:
            print(f"警告: {pdf_name} が見つかりません")
    
    # 結果を保存
    output_path = Path("testresult.md")
    tester.save_results(all_results, output_path)
    print(f"\n結果を {output_path} に保存しました。")


if __name__ == "__main__":
    main()