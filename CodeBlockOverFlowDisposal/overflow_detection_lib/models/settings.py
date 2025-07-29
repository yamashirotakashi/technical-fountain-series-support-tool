#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Settings and configuration data models
"""

from dataclasses import dataclass
from typing import List


@dataclass
class PDFSize:
    """PDF サイズ設定"""
    width_pt: float
    height_pt: float
    
    @classmethod
    def b5(cls) -> 'PDFSize':
        """B5 判型の標準サイズ"""
        return cls(width_pt=515.9, height_pt=728.5)
    
    @classmethod
    def a4(cls) -> 'PDFSize':
        """A4 判型の標準サイズ"""
        return cls(width_pt=595.2, height_pt=841.8)


@dataclass
class MarginSettings:
    """マージン設定"""
    
    @dataclass
    class PageMargin:
        """ページ別マージン設定"""
        left_mm: float
        right_mm: float
        
        @property
        def left_pt(self) -> float:
            """左マージン (pt)"""
            return self.left_mm * 2.83465
            
        @property
        def right_pt(self) -> float:
            """右マージン (pt)"""
            return self.right_mm * 2.83465
    
    odd_page: PageMargin
    even_page: PageMargin
    
    @classmethod
    def techbook_standard(cls) -> 'MarginSettings':
        """技術書典標準マージン設定"""
        return cls(
            odd_page=cls.PageMargin(left_mm=18.0, right_mm=10.0),
            even_page=cls.PageMargin(left_mm=10.0, right_mm=18.0)
        )