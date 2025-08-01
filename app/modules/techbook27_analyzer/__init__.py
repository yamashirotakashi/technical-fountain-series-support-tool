# TechDisposal Analyzer Module
"""
TechImgFile - 画像・文書処理ツール
画像の最適化とWord文書の前処理を行います。
"""

__version__ = "1.0.0"
__author__ = "TechGate Team"

from .core.models import ProcessingOptions, ProcessingResult, ImageInfo
from .processors.image_processor import ImageProcessor

__all__ = [
    'ProcessingOptions',
    'ProcessingResult', 
    'ImageInfo',
    'ImageProcessor'
]