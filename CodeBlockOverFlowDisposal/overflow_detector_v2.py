#!/usr/bin/env python3
"""
コードブロックはみ出し検出システム v2
本文幅を基準とした厳密な判定
"""

import argparse
import sys
import io
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Tuple
import cv2
import numpy as np
import fitz  # PyMuPDF
from PIL import Image


class TextWidthBasedOverflowDetector:
    """本文幅基準のコードブロックはみ出し検出クラス"""
    
    # 定数定義
    DPI = 300  # PDF→画像変換の解像度
    
    # NextPublishingの標準レイアウト（実測値）
    LEFT_MARGIN = 45  # 左マージン（pt）
    RIGHT_MARGIN = 45  # 右マージン（pt）
    PAGE_WIDTH = 515.91  # ページ幅（pt）
    TEXT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN  # 本文幅
    
    # 画像処理用の定数
    GRAY_THRESHOLD = (200, 230)  # 灰色の閾値範囲
    MIN_BLOCK_HEIGHT = 30  # 最小コードブロック高さ（ピクセル）
    
    def __init__(self):
        """初期化"""
        self.results = []
        self.errors = []
        self.start_time = None
        self.end_time = None
        
        # ピクセル単位での本文幅を計算
        self.text_width_px = int(self.TEXT_WIDTH * self.DPI / 72)
        self.left_margin_px = int(self.LEFT_MARGIN * self.DPI / 72)
        self.right_margin_px = int(self.RIGHT_MARGIN * self.DPI / 72)
    
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
                
                # 本文幅の右端位置を計算
                page_width_px = int(page.rect.width * self.DPI / 72)
                text_right_edge = page_width_px - self.right_margin_px
                
                # ページを画像化
                mat = fitz.Matrix(self.DPI/72, self.DPI/72)
                pix = page.get_pixmap(matrix=mat)
                
                # OpenCV形式に変換
                img_data = pix.pil_tobytes(format="PNG")
                image = Image.open(io.BytesIO(img_data))
                img_array = np.array(image)
                img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # コードブロックを検出してはみ出しチェック
                if self._check_code_overflow(img_cv, text_right_edge):
                    overflow_pages.append(page_num + 1)
                    
                    # デバッグ情報
                    print(f"    ページ {page_num + 1}: 本文幅からのはみ出しを検出")
            
            doc.close()
            self.end_time = datetime.now()
            
        except Exception as e:
            self.errors.append(f"エラー: {str(e)}")
            print(f"エラー: {e}")
            return []
        
        return sorted(list(set(overflow_pages)))
    
    def _check_code_overflow(self, image: np.ndarray, text_right_edge: int) -> bool:
        """
        コードブロック内のテキストが本文幅を超えているかチェック
        
        Args:
            image: OpenCV形式の画像
            text_right_edge: 本文幅の右端位置（ピクセル）
            
        Returns:
            はみ出しがある場合True
        """
        # グレースケールに変換
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 1. 灰色背景のコードブロックを検出
        gray_blocks = self._detect_gray_code_blocks(gray)
        
        # 2. 罫線で囲まれたコードブロックを検出
        bordered_blocks = self._detect_bordered_code_blocks(image, gray)
        
        # すべてのコードブロックをチェック
        all_blocks = gray_blocks + bordered_blocks
        
        for block in all_blocks:
            x, y, w, h = block
            
            # コードブロック内のテキストを検出
            block_img = gray[y:y+h, x:x+w]
            
            # 二値化
            _, binary = cv2.threshold(block_img, 200, 255, cv2.THRESH_BINARY_INV)
            
            # 各行をチェック
            for row_idx in range(h):
                row = binary[row_idx]
                
                # 行内の最右端のテキストピクセルを検出
                text_pixels = np.where(row == 255)[0]
                
                if len(text_pixels) > 0:
                    # ブロック内での最右端位置
                    rightmost_in_block = text_pixels[-1]
                    
                    # ページ全体での位置
                    rightmost_in_page = x + rightmost_in_block
                    
                    # 本文幅を超えているかチェック
                    if rightmost_in_page > text_right_edge:
                        return True
        
        return False
    
    def _detect_gray_code_blocks(self, gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        灰色背景のコードブロックを検出
        
        Args:
            gray: グレースケール画像
            
        Returns:
            コードブロックの矩形リスト [(x, y, w, h), ...]
        """
        blocks = []
        
        # 灰色の範囲でマスクを作成
        mask = cv2.inRange(gray, self.GRAY_THRESHOLD[0], self.GRAY_THRESHOLD[1])
        
        # モルフォロジー処理でノイズ除去
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # 輪郭を検出
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # 本文エリア内にあり、最小高さ以上の矩形のみ
            if (x >= self.left_margin_px - 10 and 
                h >= self.MIN_BLOCK_HEIGHT and
                w > 100):  # 幅も考慮
                blocks.append((x, y, w, h))
        
        return blocks
    
    def _detect_bordered_code_blocks(self, image: np.ndarray, gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        罫線で囲まれた白背景のコードブロックを検出
        
        Args:
            image: カラー画像
            gray: グレースケール画像
            
        Returns:
            コードブロックの矩形リスト [(x, y, w, h), ...]
        """
        blocks = []
        
        # エッジ検出で罫線を検出
        edges = cv2.Canny(gray, 50, 150)
        
        # 輪郭を検出
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # 輪郭を矩形で近似
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # 4点で構成される矩形のみ
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                
                # 本文エリア内にあり、適切なサイズの矩形
                if (x >= self.left_margin_px - 10 and 
                    h >= self.MIN_BLOCK_HEIGHT and
                    w > 100):
                    
                    # 内部が白背景かチェック
                    roi = gray[y+5:y+h-5, x+5:x+w-5]
                    mean_color = np.mean(roi)
                    
                    # 白背景（明るい）場合
                    if mean_color > 240:
                        blocks.append((x, y, w, h))
        
        return blocks
    
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
            "=== コードブロックはみ出し検出結果 v2 ===",
            f"ファイル: {pdf_path.name}",
            f"検出日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"本文幅: {self.TEXT_WIDTH:.1f}pt",
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
        
        report = "\n".join(report_lines)
        
        if output_path:
            output_path.write_text(report, encoding='utf-8')
            print(f"レポートを保存しました: {output_path}")
        
        return report


def main():
    """コマンドラインエントリーポイント"""
    parser = argparse.ArgumentParser(
        description="技術の泉シリーズPDFの本文幅基準コードブロックはみ出し検出"
    )
    parser.add_argument('pdf_file', help='検査対象のPDFファイル')
    parser.add_argument('-o', '--output', help='レポート出力先ファイル')
    
    args = parser.parse_args()
    
    pdf_path = Path(args.pdf_file)
    output_path = Path(args.output) if args.output else None
    
    # 検出器の初期化と実行
    detector = TextWidthBasedOverflowDetector()
    
    print(f"解析中: {pdf_path.name}")
    overflow_pages = detector.detect_file(pdf_path)
    
    # レポート生成と表示
    report = detector.generate_report(pdf_path, overflow_pages, output_path)
    print()
    print(report)
    
    sys.exit(1 if overflow_pages else 0)


if __name__ == "__main__":
    main()