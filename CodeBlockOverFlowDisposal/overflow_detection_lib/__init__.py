#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF Overflow Detection Library
OCRベースPDF右端はみ出し検出ライブラリ

This library provides tools for detecting text overflow at the right margin
of PDF documents using OCR-based analysis.
"""

__version__ = "1.0.0"
__author__ = "Claude Code"
__email__ = "noreply@anthropic.com"

# Main API exports
from .core.detector import OCRBasedOverflowDetector, FalsePositiveFilters
from .core.config import DetectionConfig, ConfigManager
from .models.result import DetectionResult, OverflowDetail, ConfidenceLevel
from .models.settings import PDFSize, MarginSettings

__all__ = [
    # Core classes
    'OCRBasedOverflowDetector',
    'FalsePositiveFilters', 
    'DetectionConfig',
    'ConfigManager',
    
    # Data models
    'DetectionResult',
    'OverflowDetail',
    'ConfidenceLevel',
    'PDFSize',
    'MarginSettings',
    
    # Version info
    '__version__',
]