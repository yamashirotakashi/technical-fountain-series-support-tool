#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Input validation utilities
"""

from pathlib import Path
from typing import Any, Dict


class ValidationError(Exception):
    """バリデーションエラー"""
    def __init__(self, message: str, field_name: str = None):
        self.message = message
        self.field_name = field_name
        super().__init__(self.message)
    
    def __str__(self):
        if self.field_name:
            return f"Validation error in '{self.field_name}': {self.message}"
        return f"Validation error: {self.message}"


def validate_pdf_path(pdf_path: Path) -> None:
    """PDF ファイルパスの検証"""
    if not isinstance(pdf_path, Path):
        raise ValidationError("PDF path must be a Path object", "pdf_path")
    
    if not pdf_path.exists():
        raise ValidationError(f"PDF file does not exist: {pdf_path}", "pdf_path")
    
    if not pdf_path.is_file():
        raise ValidationError(f"PDF path is not a file: {pdf_path}", "pdf_path")
    
    if pdf_path.suffix.lower() != '.pdf':
        raise ValidationError(f"File is not a PDF: {pdf_path}", "pdf_path")
    
    # ファイルサイズチェック (100MB制限)
    file_size = pdf_path.stat().st_size
    max_size = 100 * 1024 * 1024  # 100MB
    if file_size > max_size:
        raise ValidationError(
            f"PDF file too large: {file_size / 1024 / 1024:.1f}MB (max: 100MB)", 
            "pdf_path"
        )


def validate_config(config_dict: Dict[str, Any]) -> None:
    """設定辞書の検証"""
    required_sections = ['pdf_settings', 'detection_settings', 'filter_settings']
    
    for section in required_sections:
        if section not in config_dict:
            raise ValidationError(f"Missing required config section: {section}", section)
    
    # PDF設定の検証
    pdf_settings = config_dict['pdf_settings']
    if 'b5_size' not in pdf_settings:
        raise ValidationError("Missing 'b5_size' in pdf_settings", "pdf_settings")
    
    b5_size = pdf_settings['b5_size']
    if not isinstance(b5_size.get('width_pt'), (int, float)):
        raise ValidationError("Invalid width_pt in b5_size", "pdf_settings")
    if not isinstance(b5_size.get('height_pt'), (int, float)):
        raise ValidationError("Invalid height_pt in b5_size", "pdf_settings")
    
    # 検出設定の検証
    detection_settings = config_dict['detection_settings']
    required_detection_keys = ['overflow_threshold_pt', 'measurement_error_threshold_pt']
    
    for key in required_detection_keys:
        if key not in detection_settings:
            raise ValidationError(f"Missing '{key}' in detection_settings", "detection_settings")
        if not isinstance(detection_settings[key], (int, float)):
            raise ValidationError(f"Invalid {key} value", "detection_settings")
    
    # 閾値の妥当性チェック
    if detection_settings['overflow_threshold_pt'] <= 0:
        raise ValidationError("overflow_threshold_pt must be positive", "detection_settings")
    
    if detection_settings['measurement_error_threshold_pt'] <= 0:
        raise ValidationError("measurement_error_threshold_pt must be positive", "detection_settings")


def validate_processing_params(total_pages: int, page_number: int) -> None:
    """処理パラメータの検証"""
    if not isinstance(total_pages, int) or total_pages <= 0:
        raise ValidationError("total_pages must be a positive integer", "total_pages")
    
    if not isinstance(page_number, int) or page_number < 1:
        raise ValidationError("page_number must be a positive integer", "page_number")
    
    if page_number > total_pages:
        raise ValidationError(
            f"page_number ({page_number}) exceeds total_pages ({total_pages})", 
            "page_number"
        )