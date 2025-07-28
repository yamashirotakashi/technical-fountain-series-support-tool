#!/usr/bin/env python3
"""
コードブロックはみ出し検出システム（シンプル版）
画像処理による直接的なアプローチ
"""

import argparse
import sys
import io
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Tuple
import cv2
import numpy as np
import fitz  # PyMuPDF
from PIL import Image


class SimpleOverflowDetector:
    """シンプルなはみ出し検出クラス"""
    
    # 定数定義
    DPI = 150  # 処理速度重視で低めのDPI
    
    # 技術の泉シリーズの標準的なマージン（実測値ベース）
    TYPICAL_RIGHT_MARGIN_RATIO = 0.12  # ページ幅の約12%が右マージン
    
    def __init__(self):
        """初期化"""
        self.results = []
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
        
        try:
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")
            
            print("PDFを解析中...")
            
            # PyMuPDFでPDFを開く
            doc = fitz.open(str(pdf_path))
            total_pages = len(doc)
            
            # 各ページを処理
            for page_num in range(total_pages):
                if page_num % 10 == 0 and page_num > 0:
                    print(f"  処理中: {page_num}/{total_pages} ページ...")
                
                # ページを画像に変換
                page = doc[page_num]
                mat = fitz.Matrix(self.DPI/72, self.DPI/72)
                pix = page.get_pixmap(matrix=mat)
                
                # OpenCV形式に変換
                img_data = pix.pil_tobytes(format="PNG")
                image = Image.open(io.BytesIO(img_data))
                img_array = np.array(image)
                img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # はみ出しチェック
                if self._detect_overflow(img_cv):
                    overflow_pages.append(page_num + 1)
            
            doc.close()
            self.end_time = datetime.now()
            
        except Exception as e:
            print(f"エラー: {e}")
            return []
        
        return sorted(list(set(overflow_pages)))
    
    def _detect_overflow(self, image: np.ndarray) -> bool:
        """
        シンプルなはみ出し検出
        
        Args:
            image: OpenCV形式の画像
            
        Returns:
            はみ出しがある場合True
        """
        height, width = image.shape[:2]
        
        # 右マージンエリアを定義（ページ幅の右側12%）
        right_margin_start = int(width * (1 - self.TYPICAL_RIGHT_MARGIN_RATIO))
        
        # グレースケール変換
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 右マージンエリアを抽出
        margin_area = gray[:, right_margin_start:]
        
        # 二値化（テキストを検出）
        _, binary = cv2.threshold(margin_area, 200, 255, cv2.THRESH_BINARY_INV)
        
        # コードブロック領域の検出（連続した暗い領域）
        # 灰色背景は二値化後も検出される
        
        # 各行で黒ピクセルをカウント
        black_pixels_per_row = np.sum(binary == 255, axis=1)
        
        # 連続してテキストがある行をカウント
        consecutive_text_rows = 0
        max_consecutive = 0
        
        for pixel_count in black_pixels_per_row:
            if pixel_count > 5:  # 5ピクセル以上のテキストがある
                consecutive_text_rows += 1
                max_consecutive = max(max_consecutive, consecutive_text_rows)
            else:
                consecutive_text_rows = 0
        
        # 5行以上連続してテキストがあれば、はみ出しと判定
        # これにより単独の図やノイズを除外
        return max_consecutive >= 5
    
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
        
        report = "\n".join(report_lines)
        
        if output_path:
            output_path.write_text(report, encoding='utf-8')
            print(f"レポートを保存しました: {output_path}")
        
        return report


def main():
    """コマンドラインエントリーポイント"""
    parser = argparse.ArgumentParser(
        description="技術の泉シリーズPDFのコードブロックはみ出し検出（シンプル版）"
    )
    parser.add_argument('pdf_file', help='検査対象のPDFファイル')
    parser.add_argument('-o', '--output', help='レポート出力先ファイル')
    parser.add_argument('--visualize', action='store_true', 
                       help='検出結果を可視化（最初の10ページ）')
    
    args = parser.parse_args()
    
    pdf_path = Path(args.pdf_file)
    output_path = Path(args.output) if args.output else None
    
    # 検出器の初期化と実行
    detector = SimpleOverflowDetector()
    
    print(f"解析中: {pdf_path.name}")
    overflow_pages = detector.detect_file(pdf_path)
    
    # レポート生成と表示
    report = detector.generate_report(pdf_path, overflow_pages, output_path)
    print()
    print(report)
    
    # 可視化オプション
    if args.visualize and overflow_pages:
        print("\n検出結果の可視化...")
        visualize_results(pdf_path, overflow_pages[:10], detector)
    
    sys.exit(1 if overflow_pages else 0)


def visualize_results(pdf_path: Path, pages: List[int], detector: SimpleOverflowDetector):
    """検出結果を可視化"""
    doc = fitz.open(str(pdf_path))
    
    for page_num in pages[:3]:  # 最初の3ページのみ
        page = doc[page_num - 1]
        mat = fitz.Matrix(detector.DPI/72, detector.DPI/72)
        pix = page.get_pixmap(matrix=mat)
        
        # OpenCV形式に変換
        img_data = pix.pil_tobytes(format="PNG")
        image = Image.open(io.BytesIO(img_data))
        img_array = np.array(image)
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        height, width = img_cv.shape[:2]
        right_margin_start = int(width * (1 - detector.TYPICAL_RIGHT_MARGIN_RATIO))
        
        # 右マージンラインを描画
        cv2.line(img_cv, (right_margin_start, 0), (right_margin_start, height), (0, 0, 255), 2)
        cv2.putText(img_cv, "Text Width Limit", (right_margin_start - 150, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # 保存
        output_file = f"page_{page_num}_overflow.png"
        cv2.imwrite(output_file, img_cv)
        print(f"  {output_file} を保存しました")
    
    doc.close()


if __name__ == "__main__":
    main()