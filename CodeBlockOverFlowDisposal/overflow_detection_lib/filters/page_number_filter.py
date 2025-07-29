#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Page number filter - ページ番号によるフィルタ
"""

import re
from .base_filter import BaseFilter, FilterResult

class PageNumberFilter(BaseFilter):
    """ページ番号フィルタ"""
    
    def __init__(self, max_digits: int = 3):
        self.max_digits = max_digits
        self.page_number_pattern = re.compile(r'^\d{1,' + str(max_digits) + r'}$')
    
    @property
    def name(self) -> str:
        return "PageNumber"
    
    def apply(self, overflow_text: str, overflow_amount: float, y_position: float) -> FilterResult:
        """ページ番号を誤検知として判定"""
        text_content = overflow_text.strip()
        
        if self.page_number_pattern.match(text_content):
            return self._create_result(
                is_false_positive=True,
                confidence=0.9,
                reason=f"ページ番号と判定: '{text_content}'"
            )
        
        return self._create_result(
            is_false_positive=False,
            confidence=0.7,
            reason=f"ページ番号ではない: '{text_content}'"
        )