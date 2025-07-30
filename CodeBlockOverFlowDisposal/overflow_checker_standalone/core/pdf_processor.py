# -*- coding: utf-8 -*-
"""
PDF処理メインクラス

Phase 2C-1 実装
既存のOCR検出器を統合した独立アプリ用のPDF処理
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable
import logging

# 既存の検出器をインポート
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

# ハイブリッド検出器（矩形ベース）を優先使用
try:
    from rect_based_detector import RectBasedOverflowDetector
    USE_RECT_BASED = True
except ImportError:
    # フォールバック: OCRベース検出器
    from overflow_detector_ocr import OCRBasedOverflowDetector
    USE_RECT_BASED = False

from utils.windows_utils import ensure_utf8_encoding, is_windows
from utils.tesseract_config import configure_tesseract
# Functions now imported directly above

class ProcessingResult:
    """処理結果を格納するクラス"""
    
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.pdf_name = pdf_path.name
        self.overflow_pages: List[Dict] = []
        self.total_pages = 0
        self.processing_time = 0.0
        self.detection_count = 0
        self.error_message = None
        self.timestamp = datetime.now()
        
    def add_overflow_page(self, page_number: int, overflow_data: Dict):
        """溢れページを追加"""
        page_data = {
            'page_number': page_number,
            'overflow_text': overflow_data.get('overflow_text', ''),
            'overflow_amount': overflow_data.get('overflow_amount', 0.0),
            'confidence': overflow_data.get('confidence', 0.0),
            'y_position': overflow_data.get('y_position', 0.0)
        }
        self.overflow_pages.append(page_data)
        self.detection_count = len(self.overflow_pages)
    
    def get_summary(self) -> Dict:
        """処理結果サマリーを取得"""
        return {
            'pdf_name': self.pdf_name,
            'total_pages': self.total_pages,
            'overflow_count': self.detection_count,
            'processing_time': self.processing_time,
            'timestamp': self.timestamp.isoformat(),
            'has_errors': self.error_message is not None
        }

class PDFOverflowProcessor:
    """PDF溢れ処理メインクラス"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Tesseract OCRの設定
        configure_tesseract()
        
        # 検出器の初期化
        try:
            if USE_RECT_BASED:
                self.detector = RectBasedOverflowDetector()
                self.logger.info(f"検出器初期化成功: RectBasedOverflowDetector（ハイブリッド検出）")
                self.logger.info("検出方式: コードブロック（グレー背景）からのはみ出し + 英数字の本文幅突出")
            else:
                self.detector = OCRBasedOverflowDetector()
                self.logger.info(f"検出器初期化成功: OCRBasedOverflowDetector")
                
                # Tesseract OCRの確認
                try:
                    import pytesseract
                    tesseract_version = pytesseract.get_tesseract_version()
                    self.logger.info(f"Tesseract OCR バージョン: {tesseract_version}")
                except Exception as ocr_error:
                    self.logger.warning(f"Tesseract OCR確認エラー: {ocr_error}")
                    self.logger.warning("Tesseract OCRが正しくインストールされていない可能性があります")
                    self.logger.warning("https://github.com/UB-Mannheim/tesseract/wiki からインストールしてください")
                
        except Exception as e:
            self.logger.error(f"検出器初期化エラー: {e}")
            raise
        
        # Windows環境対応
        if config.get('windows_environment', False):
            self.logger.info("Windows環境での処理を開始")
    
    def process_pdf(self, pdf_path: Path, progress_callback: Optional[Callable] = None) -> ProcessingResult:
        """PDFファイルを処理
        
        Args:
            pdf_path: 処理対象PDFファイルパス
            progress_callback: 進捗コールバック関数
            
        Returns:
            ProcessingResult: 処理結果
        """
        start_time = datetime.now()
        result = ProcessingResult(pdf_path)
        
        try:
            self.logger.info(f"PDF処理開始: {pdf_path}")
            
            # PDFファイルの存在確認
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")
            
            # OCR検出器での処理実行
            # detect_overflowsメソッドはページごとの処理なので、PDF全体処理用のラッパーを使用
            overflow_data = self._process_pdf_with_detector(pdf_path, progress_callback)
            
            if overflow_data:
                # 総ページ数の取得
                result.total_pages = overflow_data.get('total_pages', 0)
                
                # 検出された溢れページの処理
                detected_pages = overflow_data.get('overflow_pages', [])
                
                for i, page_data in enumerate(detected_pages):
                    # 進捗コールバック実行（総ページ数を使用）
                    if progress_callback:
                        progress_callback(i + 1, result.total_pages, i + 1)
                    
                    # 溢れページを結果に追加
                    result.add_overflow_page(
                        page_data.get('page_number', i + 1),
                        page_data
                    )
                    
                    self.logger.debug(f"溢れ検出: ページ {page_data.get('page_number', i + 1)}")
                
                # 最終進捗更新（総ページ数を使用）
                if progress_callback:
                    progress_callback(
                        result.total_pages, 
                        result.total_pages, 
                        result.detection_count
                    )
            
            else:
                # 溢れが検出されなかった場合
                result.total_pages = self._get_total_pages_fallback(pdf_path)
                if progress_callback:
                    progress_callback(result.total_pages, result.total_pages, 0)
            
            # 処理時間の計算
            result.processing_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(
                f"PDF処理完了: {pdf_path.name} - "
                f"{result.detection_count}件検出, {result.processing_time:.2f}秒"
            )
            
            return result
            
        except Exception as e:
            # エラーハンドリング
            result.error_message = str(e)
            result.processing_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.error(f"PDF処理エラー ({pdf_path}): {e}", exc_info=True)
            
            return result
    
    def _process_pdf_with_detector(self, pdf_path: Path, progress_callback=None) -> Dict:
        """既存のOCR検出器を使用してPDF全体を処理
        
        Args:
            pdf_path: PDFファイルパス
            progress_callback: 進捗コールバック
            
        Returns:
            処理結果辞書
        """
        try:
            self.logger.info(f"検出器でPDF処理開始: {pdf_path}")
            
            # OCRBasedOverflowDetectorのdetect_fileメソッドを使用
            overflow_page_numbers = self.detector.detect_file(pdf_path)
            
            self.logger.info(f"検出結果: {len(overflow_page_numbers)}ページで溢れを検出")
            if overflow_page_numbers:
                self.logger.info(f"検出ページ: {overflow_page_numbers}")
            
            # PDFの総ページ数を取得
            try:
                import pypdf
                with open(pdf_path, 'rb') as file:
                    reader = pypdf.PdfReader(file)
                    total_pages = len(reader.pages)
            except ImportError:
                import PyPDF2
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    total_pages = len(reader.pages)
            
            # 検出結果を辞書形式に変換
            overflow_pages = []
            for page_num in overflow_page_numbers:
                overflow_pages.append({
                    'page_number': page_num,
                    'overflow_text': '検出済み',
                    'overflow_amount': 0.0,
                    'confidence': 100.0,
                    'y_position': 0.0
                })
            
            return {
                'total_pages': total_pages,
                'overflow_pages': overflow_pages
            }
            
        except Exception as e:
            self.logger.error(f"PDF処理エラー: {e}")
            return {
                'total_pages': 0,
                'overflow_pages': []
            }
    
    def _get_total_pages_fallback(self, pdf_path: Path) -> int:
        """総ページ数の取得（フォールバック）"""
        try:
            try:
                import pypdf
                with open(pdf_path, 'rb') as file:
                    reader = pypdf.PdfReader(file)
                    return len(reader.pages)
            except ImportError:
                import PyPDF2
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    return len(reader.pages)
        except Exception as e:
            self.logger.warning(f"総ページ数取得失敗: {e}")
            return 0
    
    def validate_pdf(self, pdf_path: Path) -> tuple[bool, str]:
        """PDFファイルの妥当性検証
        
        Args:
            pdf_path: 検証対象PDFファイルパス
            
        Returns:
            tuple[bool, str]: (妥当性, エラーメッセージ)
        """
        try:
            # ファイル存在確認
            if not pdf_path.exists():
                return False, f"ファイルが存在しません: {pdf_path}"
            
            # ファイル拡張子確認
            if pdf_path.suffix.lower() != '.pdf':
                return False, f"PDFファイルではありません: {pdf_path.suffix}"
            
            # ファイルサイズ確認
            file_size = pdf_path.stat().st_size
            if file_size == 0:
                return False, "ファイルサイズが0バイトです"
            
            # 最大ファイルサイズ確認（100MB）
            max_size = 100 * 1024 * 1024  # 100MB
            if file_size > max_size:
                return False, f"ファイルサイズが大きすぎます: {file_size / (1024*1024):.1f}MB"
            
            # PDFファイルとしての妥当性確認
            try:
                try:
                    import pypdf
                    with open(pdf_path, 'rb') as file:
                        reader = pypdf.PdfReader(file)
                        if len(reader.pages) == 0:
                            return False, "PDFにページが含まれていません"
                except ImportError:
                    import PyPDF2
                    with open(pdf_path, 'rb') as file:
                        reader = PyPDF2.PdfReader(file)
                        if len(reader.pages) == 0:
                            return False, "PDFにページが含まれていません"
            except Exception as e:
                return False, f"PDFファイルが破損している可能性があります: {str(e)}"
            
            return True, ""
            
        except Exception as e:
            return False, f"検証中にエラーが発生しました: {str(e)}"