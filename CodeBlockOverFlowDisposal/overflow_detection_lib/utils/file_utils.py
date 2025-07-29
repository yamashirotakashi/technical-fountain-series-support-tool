#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File handling utilities for PDF processing
"""

from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from .validation import ValidationError, validate_pdf_path

logger = logging.getLogger(__name__)


def validate_pdf_file(pdf_path: Path) -> bool:
    """
    PDF ファイルの妥当性を検証
    
    Args:
        pdf_path: PDF ファイルのパス
        
    Returns:
        bool: 有効な PDF ファイルの場合 True
        
    Raises:
        ValidationError: ファイルが無効な場合
    """
    # 基本的なパス検証
    validate_pdf_path(pdf_path)
    
    # pdfplumber が利用可能かチェック
    if pdfplumber is None:
        raise ValidationError("pdfplumber library is not available", "dependencies")
    
    # PDF として読み込み可能かチェック
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) == 0:
                raise ValidationError("PDF file contains no pages", "pdf_content")
            
            # 最初のページが読み込めるかテスト
            first_page = pdf.pages[0]
            if first_page.width <= 0 or first_page.height <= 0:
                raise ValidationError("PDF page has invalid dimensions", "pdf_content")
                
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f"Cannot read PDF file: {str(e)}", "pdf_content")
    
    return True


def get_pdf_info(pdf_path: Path) -> Dict[str, any]:
    """
    PDF ファイルの基本情報を取得
    
    Args:
        pdf_path: PDF ファイルのパス
        
    Returns:
        Dict: PDF 情報（ページ数、サイズ等）
        
    Raises:
        ValidationError: ファイルが読み込めない場合
    """
    validate_pdf_file(pdf_path)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            
            # 最初のページから基本情報を取得
            first_page = pdf.pages[0]
            page_width = first_page.width
            page_height = first_page.height
            
            # ファイルサイズ
            file_size = pdf_path.stat().st_size
            
            return {
                'file_path': str(pdf_path),
                'file_name': pdf_path.name,
                'file_size_bytes': file_size,
                'file_size_mb': file_size / (1024 * 1024),
                'total_pages': total_pages,
                'page_width_pt': page_width,
                'page_height_pt': page_height,
                'is_b5_format': abs(page_width - 515.9) < 5.0 and abs(page_height - 728.5) < 5.0,
                'is_a4_format': abs(page_width - 595.2) < 5.0 and abs(page_height - 841.8) < 5.0,
            }
            
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f"Cannot extract PDF info: {str(e)}", "pdf_analysis")


def estimate_processing_time(pdf_path: Path) -> float:
    """
    PDF 処理時間の推定
    
    Args:
        pdf_path: PDF ファイルのパス
        
    Returns:
        float: 推定処理時間（秒）
    """
    try:
        pdf_info = get_pdf_info(pdf_path)
        total_pages = pdf_info['total_pages']
        
        # 経験則に基づく処理時間推定
        # 平均 10ページ/秒 の処理速度を想定
        base_time_per_page = 0.1  # 秒
        estimated_time = total_pages * base_time_per_page
        
        # ファイルサイズによる補正
        file_size_mb = pdf_info['file_size_mb']
        if file_size_mb > 10:
            # 大きなファイルは若干時間がかかる
            estimated_time *= (1 + (file_size_mb - 10) * 0.1)
        
        return max(estimated_time, 1.0)  # 最低1秒
        
    except Exception as e:
        logger.warning(f"Cannot estimate processing time: {e}")
        return 10.0  # デフォルト値


def get_safe_filename(pdf_path: Path, suffix: str = "") -> str:
    """
    安全なファイル名を生成（結果出力用）
    
    Args:
        pdf_path: 元の PDF ファイルパス
        suffix: 追加するサフィックス
        
    Returns:
        str: 安全なファイル名
    """
    # ファイル名から拡張子を除去
    base_name = pdf_path.stem
    
    # 安全でない文字を置換
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    safe_name = ''.join(c if c in safe_chars else '_' for c in base_name)
    
    # あまりに長い場合は切り詰める
    if len(safe_name) > 50:
        safe_name = safe_name[:50]
    
    # サフィックスを追加
    if suffix:
        safe_name += f"_{suffix}"
    
    return safe_name