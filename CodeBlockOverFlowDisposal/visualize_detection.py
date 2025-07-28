#!/usr/bin/env python3
"""
検出結果の可視化スクリプト
特定ページの検出結果を画像として保存
"""

import cv2
import numpy as np
import fitz
from pathlib import Path
import sys
from overflow_detector_image import ImageBasedOverflowDetector


def visualize_page(pdf_path: Path, page_num: int, output_path: Path):
    """特定ページの検出結果を可視化"""
    
    # 検出器の初期化
    detector = ImageBasedOverflowDetector()
    
    # PDFを開く
    doc = fitz.open(str(pdf_path))
    
    if page_num > len(doc):
        print(f"エラー: PDFは {len(doc)} ページしかありません")
        return
    
    # ページを画像に変換
    page = doc[page_num - 1]  # 0-indexed
    mat = fitz.Matrix(detector.DPI/72, detector.DPI/72)
    pix = page.get_pixmap(matrix=mat)
    
    # OpenCV形式に変換
    img_data = pix.pil_tobytes(format="PNG")
    import io
    from PIL import Image
    image = Image.open(io.BytesIO(img_data))
    img_array = np.array(image)
    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    # コピーを作成（描画用）
    img_result = img_cv.copy()
    
    # コードブロックを検出
    code_blocks = detector._detect_code_blocks(img_cv)
    
    print(f"ページ {page_num} で {len(code_blocks)} 個のコードブロックを検出")
    
    # 各ブロックを描画
    for i, block in enumerate(code_blocks):
        x, y, w, h = block
        
        # ブロックの枠を描画（緑）
        cv2.rectangle(img_result, (x, y), (x+w, y+h), (0, 255, 0), 3)
        
        # はみ出しチェック
        if detector._check_text_overflow(img_cv, block):
            # はみ出している場合は赤い線を右端に描画
            cv2.line(img_result, (x+w-10, y), (x+w-10, y+h), (0, 0, 255), 5)
            cv2.putText(img_result, "OVERFLOW", (x+w-100, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # ブロック番号を表示
        cv2.putText(img_result, f"Block {i}", (x, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # 結果を保存
    cv2.imwrite(str(output_path), img_result)
    print(f"可視化結果を保存: {output_path}")
    
    doc.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使用方法: python visualize_detection.py <PDFファイル> <ページ番号>")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    page_num = int(sys.argv[2])
    output_path = Path(f"page_{page_num}_visualization.png")
    
    visualize_page(pdf_path, page_num, output_path)