#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Japanese text filter - 日本語テキストによるフィルタ
"""

import re
from .base_filter import BaseFilter, FilterResult

class JapaneseTextFilter(BaseFilter):
    """日本語テキストフィルタ"""
    
    def __init__(self):
        # 日本語文字範囲の正規表現
        self.japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]')
    
    @property
    def name(self) -> str:
        return "JapaneseText"
    
    def apply(self, overflow_text: str, overflow_amount: float, y_position: float) -> FilterResult:
        """日本語テキストを誤検知として判定"""
        text_content = overflow_text.strip()
        
        # 日本語テキストの短いはみ出しは除外（完全な文字でない可能性）
        if self.japanese_pattern.search(text_content) and len(text_content) <= 2:
            return self._create_result(
                is_false_positive=True,
                confidence=0.85,
                reason=f"短い日本語テキスト: '{text_content}'"
            )
        
        return self._create_result(
            is_false_positive=False,
            confidence=0.6,
            reason=f"日本語フィルタ対象外: '{text_content}'"
        )