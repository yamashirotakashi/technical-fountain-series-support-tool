#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Core module for overflow detection functionality
"""

from .detector import OCRBasedOverflowDetector, FalsePositiveFilters
from .config import DetectionConfig, ConfigManager

__all__ = [
    'OCRBasedOverflowDetector',
    'FalsePositiveFilters', 
    'DetectionConfig',
    'ConfigManager',
]