#!/usr/bin/env python3
"""
コードブロックはみ出し検出システム（画像ベース版）
OpenCVを使用した画像処理アプローチ

対応するコードブロック：
1. 灰色背景タイプ
2. 白背景・罫線囲みタイプ
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


class ImageBasedOverflowDetector:
    """画像ベースのコードブロックはみ出し検出クラス"""
    
    # 定数定義
    DPI = 300  # PDF→画像変換の解像度
    GRAY_THRESHOLD = (200, 230)  # 灰色の閾値範囲（RGB値）
    MIN_BLOCK_WIDTH = 100  # 最小コードブロック幅（ピクセル）
    MIN_BLOCK_HEIGHT = 50  # 最小コードブロック高さ（ピクセル）
    
    # 本文幅の定義（NextPublishing標準）
    # B4: 257mm × 364mm（JIS B4）
    # 左右マージン各20mm = 本文幅217mm
    # 300DPIでの計算: 
    # - ページ幅: 257mm * 300/25.4 ≈ 3035ピクセル
    # - 本文幅: 217mm * 300/25.4 ≈ 2563ピクセル
    PAGE_LEFT_MARGIN = 236  # 20mm @ 300DPI
    PAGE_RIGHT_MARGIN = 236  # 20mm @ 300DPI
    
    def __init__(self):
        """初期化"""
        self.results = []
        self.errors = []
        self.start_time = None
        self.end_time = None
    
    def detect_file(self, pdf_path: Path) -> List[int]:
        """
        PDFファイルを画像化して、はみ出しページを検出
        
        Args:
            pdf_path: 解析対象のPDFファイルパス
            
        Returns:
            はみ出しが検出されたページ番号のリスト（1-indexed）
        """
        self.start_time = datetime.now()
        overflow_pages = []
        
        try:
            # ファイル存在確認
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")
            
            print("PDFを画像に変換中...")
            
            # PyMuPDFでPDFを開く
            doc = fitz.open(str(pdf_path))
            total_pages = len(doc)
            
            # 各ページを処理
            for page_num in range(total_pages):
                if page_num % 10 == 0 and page_num > 0:
                    print(f"  処理中: {page_num}/{total_pages} ページ...")
                
                # ページを画像に変換
                page = doc[page_num]
                mat = fitz.Matrix(self.DPI/72, self.DPI/72)  # 72 DPI → 指定DPIに変換
                pix = page.get_pixmap(matrix=mat)
                
                # PILイメージに変換
                img_data = pix.pil_tobytes(format="PNG")
                image = Image.open(io.BytesIO(img_data))
                
                # OpenCV形式に変換
                img_array = np.array(image)
                img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    
                # ページの本文幅を計算
                page_width = img_cv.shape[1]
                text_area_right = page_width - self.PAGE_RIGHT_MARGIN
                
                # コードブロックを検出
                code_blocks = self._detect_code_blocks(img_cv)
                
                # 各ブロックでテキストオーバーフローをチェック
                for block in code_blocks:
                    if self._check_text_overflow_from_page(img_cv, block, text_area_right):
                        overflow_pages.append(page_num + 1)  # 1-indexed
                        break  # このページは既に検出済み
            
            doc.close()
            
            self.end_time = datetime.now()
            
        except Exception as e:
            self.errors.append(f"エラー: {str(e)}")
            print(f"エラー: {e}")
            return []
        
        return sorted(list(set(overflow_pages)))
    
    def _detect_code_blocks(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        画像からコードブロック領域を検出
        
        Args:
            image: OpenCV形式の画像
            
        Returns:
            コードブロックの矩形リスト [(x, y, w, h), ...]
        """
        blocks = []
        
        # 1. 灰色背景のコードブロックを検出
        gray_blocks = self._detect_gray_blocks(image)
        blocks.extend(gray_blocks)
        
        # 2. 罫線で囲まれたコードブロックを検出
        bordered_blocks = self._detect_bordered_blocks(image)
        blocks.extend(bordered_blocks)
        
        return blocks
    
    def _detect_gray_blocks(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        灰色背景のコードブロックを検出
        
        Args:
            image: OpenCV形式の画像
            
        Returns:
            灰色矩形のリスト [(x, y, w, h), ...]
        """
        blocks = []
        
        # グレースケールに変換
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 灰色の範囲を指定してマスクを作成
        lower_gray = self.GRAY_THRESHOLD[0]
        upper_gray = self.GRAY_THRESHOLD[1]
        mask = cv2.inRange(gray, lower_gray, upper_gray)
        
        # 輪郭を検出
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 大きな矩形のみを抽出
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # 最小サイズ以上の矩形のみ
            if w >= self.MIN_BLOCK_WIDTH and h >= self.MIN_BLOCK_HEIGHT:
                blocks.append((x, y, w, h))
        
        return blocks
    
    def _detect_bordered_blocks(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        罫線で囲まれたコードブロックを検出
        
        Args:
            image: OpenCV形式の画像
            
        Returns:
            罫線矩形のリスト [(x, y, w, h), ...]
        """
        blocks = []
        
        # グレースケールに変換
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # エッジ検出
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # ハフ変換で直線を検出
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
        if lines is not None:
            # 水平線と垂直線を分類
            h_lines = []
            v_lines = []
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                
                # 水平線
                if abs(y2 - y1) < 5:
                    h_lines.append((min(x1, x2), y1, max(x1, x2), y1))
                # 垂直線
                elif abs(x2 - x1) < 5:
                    v_lines.append((x1, min(y1, y2), x1, max(y1, y2)))
            
            # 矩形を形成する線の組み合わせを探す
            # （簡易的な実装：より正確な検出は Phase 2 で実装）
            # ここでは白背景の大きな矩形領域を検出
            
            # 白い領域を検出
            _, white_mask = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)
            
            # 輪郭を検出
            contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # 最小サイズ以上で、罫線が近くにある矩形
                if w >= self.MIN_BLOCK_WIDTH and h >= self.MIN_BLOCK_HEIGHT:
                    # 矩形の周囲に罫線があるかチェック（簡易版）
                    if self._has_border_lines(x, y, w, h, h_lines, v_lines):
                        blocks.append((x, y, w, h))
        
        return blocks
    
    def _has_border_lines(self, x: int, y: int, w: int, h: int, 
                         h_lines: List, v_lines: List, tolerance: int = 10) -> bool:
        """
        矩形の周囲に罫線があるかチェック（簡易版）
        """
        # 上下左右に線があるかチェック
        has_top = any(abs(ly - y) < tolerance and lx1 <= x and lx2 >= x + w 
                     for lx1, ly, lx2, _ in h_lines)
        has_bottom = any(abs(ly - (y + h)) < tolerance and lx1 <= x and lx2 >= x + w 
                        for lx1, ly, lx2, _ in h_lines)
        has_left = any(abs(lx - x) < tolerance and ly1 <= y and ly2 >= y + h 
                      for lx, ly1, _, ly2 in v_lines)
        has_right = any(abs(lx - (x + w)) < tolerance and ly1 <= y and ly2 >= y + h 
                       for lx, ly1, _, ly2 in v_lines)
        
        # 4辺のうち3辺以上に線があれば罫線囲みと判定
        return sum([has_top, has_bottom, has_left, has_right]) >= 3
    
    def _check_text_overflow_from_page(self, image: np.ndarray, block: Tuple[int, int, int, int], 
                                       text_area_right: int) -> bool:
        """
        コードブロック内のテキストが本文幅を超えているかチェック
        
        Args:
            image: OpenCV形式の画像
            block: コードブロックの矩形 (x, y, w, h)
            text_area_right: 本文領域の右端のX座標
            
        Returns:
            本文幅を超えている場合True
        """
        x, y, w, h = block
        
        # ブロック内の画像を切り出し
        block_img = image[y:y+h, x:x+w]
        
        # グレースケールに変換
        gray = cv2.cvtColor(block_img, cv2.COLOR_BGR2GRAY)
        
        # 二値化（テキストを黒、背景を白に）
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        # 本文幅を超える部分があるかチェック
        block_right = x + w
        
        # コードブロックの右端が本文幅を超えている場合
        if block_right > text_area_right:
            # 超過部分にテキストがあるかチェック
            overflow_start = text_area_right - x
            if overflow_start < w and overflow_start > 0:
                overflow_region = binary[:, overflow_start:]
                
                # 超過部分にテキストがあるか
                text_pixels = np.sum(overflow_region == 255)
                
                # テキストがある場合は、はみ出しと判定
                if text_pixels > 50:  # 50ピクセル以上のテキスト
                    return True
        
        return False
    
    def _check_text_overflow(self, image: np.ndarray, block: Tuple[int, int, int, int]) -> bool:
        """
        コードブロック内のテキストがはみ出しているかチェック
        
        Args:
            image: OpenCV形式の画像
            block: コードブロックの矩形 (x, y, w, h)
            
        Returns:
            はみ出しがある場合True
        """
        x, y, w, h = block
        
        # ブロック内の画像を切り出し
        block_img = image[y:y+h, x:x+w]
        
        # グレースケールに変換
        gray = cv2.cvtColor(block_img, cv2.COLOR_BGR2GRAY)
        
        # 二値化（テキストを黒、背景を白に）
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        # 右端付近のピクセルをチェック
        right_margin = self.TEXT_MARGIN
        right_edge_region = binary[:, -right_margin:]
        
        # 右端にテキスト（黒いピクセル）があるかチェック
        text_pixels = np.sum(right_edge_region == 255)  # 黒いピクセルの数
        
        # より厳密な判定：連続した黒ピクセルの行数をカウント
        rows_with_text = 0
        for row in right_edge_region:
            if np.sum(row == 255) > 3:  # 行に3ピクセル以上の黒がある
                rows_with_text += 1
        
        # 複数行にわたってテキストがある場合のみ、はみ出しと判定
        if rows_with_text >= 3:  # 3行以上
            return True
        
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
            "=== コードブロックはみ出し検出結果（画像ベース） ===",
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
        description="技術の泉シリーズPDFのコードブロックはみ出し検出（画像ベース版）"
    )
    parser.add_argument('pdf_file', help='検査対象のPDFファイル')
    parser.add_argument('-o', '--output', help='レポート出力先ファイル')
    
    args = parser.parse_args()
    
    # パスの準備
    pdf_path = Path(args.pdf_file)
    output_path = Path(args.output) if args.output else None
    
    # 検出器の初期化と実行
    detector = ImageBasedOverflowDetector()
    
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