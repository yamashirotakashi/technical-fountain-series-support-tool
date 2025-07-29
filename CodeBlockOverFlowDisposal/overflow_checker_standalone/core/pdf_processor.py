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

# 既存のOCR検出器をインポート
sys.path.append(str(Path(__file__).parent.parent.parent))
from overflow_detection_lib.core.detector import OCRBasedOverflowDetector

import utils.windows_utils as wu
ensure_utf8_encoding = wu.ensure_utf8_encoding
is_windows = wu.is_windows

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
        
        # OCR検出器の初期化
        self.detector = OCRBasedOverflowDetector()
        
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
            overflow_data = self.detector.detect_overflow_pages(str(pdf_path))
            
            if overflow_data:
                # 総ページ数の取得
                result.total_pages = overflow_data.get('total_pages', 0)
                
                # 検出された溢れページの処理
                detected_pages = overflow_data.get('overflow_pages', [])
                
                for i, page_data in enumerate(detected_pages):
                    # 進捗コールバック実行
                    if progress_callback:
                        progress_callback(i + 1, len(detected_pages), i + 1)
                    
                    # 溢れページを結果に追加
                    result.add_overflow_page(
                        page_data.get('page_number', i + 1),
                        page_data
                    )
                    
                    self.logger.debug(f"溢れ検出: ページ {page_data.get('page_number', i + 1)}")
                
                # 最終進捗更新
                if progress_callback:
                    progress_callback(
                        len(detected_pages), 
                        len(detected_pages), 
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
    
    def _get_total_pages_fallback(self, pdf_path: Path) -> int:
        """総ページ数の取得（フォールバック）"""
        try:
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