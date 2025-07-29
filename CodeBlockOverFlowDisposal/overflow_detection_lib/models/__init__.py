#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data models for overflow detection results and settings
"""

from .result import DetectionResult, OverflowDetail, ConfidenceLevel
from .settings import PDFSize, MarginSettings

__all__ = [
    'DetectionResult',
    'OverflowDetail', 
    'ConfidenceLevel',
    'PDFSize',
    'MarginSettings',
]