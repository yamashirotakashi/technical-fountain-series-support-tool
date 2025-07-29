#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Symbol only filter - 記号のみのテキストフィルタ
"""

from .base_filter import BaseFilter, FilterResult

class SymbolOnlyFilter(BaseFilter):
    """記号のみフィルタ"""
    
    def __init__(self):
        # 保護すべき重要な記号（プログラミング関連）
        self.protected_symbols = {
            '"', "'", '(', ')', '[', ']', '{', '}', '<', '>', 
            '=', '+', '-', '*', '/', '\\', '|', '&', '%', 
            '$', '#', '@', '!', '?', '.', ',', ';', ':'
        }
    
    @property
    def name(self) -> str:
        return "SymbolOnly"
    
    def apply(self, overflow_text: str, overflow_amount: float, y_position: float) -> FilterResult:
        """記号のみのテキストをフィルタ（保護対象は除く）"""
        text_content = overflow_text.strip()
        text_length = len(text_content)
        
        # 単一文字の場合の判定
        if text_length == 1:
            char = text_content[0]
            if char in self.protected_symbols or char.isalnum():
                return self._create_result(
                    is_false_positive=False,
                    confidence=0.8,
                    reason=f"保護対象文字: '{char}'"
                )
            else:
                return self._create_result(
                    is_false_positive=True,
                    confidence=0.9,
                    reason=f"保護対象外の記号: '{char}'"
                )
        
        # 短いテキストで記号のみの場合（保護対象の組み合わせは除く）
        if text_length <= 2 and all(not c.isalnum() for c in text_content):
            # 全文字が保護対象記号かチェック
            if all(c in self.protected_symbols for c in text_content):
                return self._create_result(
                    is_false_positive=False,
                    confidence=0.7,
                    reason=f"保護対象記号組み合わせ: '{text_content}'"
                )
            else:
                return self._create_result(
                    is_false_positive=True,
                    confidence=0.85,
                    reason=f"非保護記号組み合わせ: '{text_content}'"
                )
        
        return self._create_result(
            is_false_positive=False,
            confidence=0.5,
            reason=f"記号フィルタ対象外: '{text_content}'"
        )