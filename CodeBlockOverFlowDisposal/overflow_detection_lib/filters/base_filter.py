#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base filter interface for overflow detection
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class FilterResult:
    """フィルタ結果データクラス"""
    is_false_positive: bool
    confidence: float  # 0.0-1.0
    reason: str
    filter_name: str

class BaseFilter(ABC):
    """フィルタリング基底クラス"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """フィルタ名"""
        pass
    
    @abstractmethod
    def apply(self, overflow_text: str, overflow_amount: float, y_position: float) -> FilterResult:
        """
        フィルタを適用
        
        Args:
            overflow_text: はみ出しテキスト
            overflow_amount: はみ出し量 (pt)
            y_position: Y座標
            
        Returns:
            FilterResult: フィルタ結果
        """
        pass
    
    def _create_result(self, is_false_positive: bool, confidence: float, reason: str) -> FilterResult:
        """結果生成ヘルパー"""
        return FilterResult(
            is_false_positive=is_false_positive,
            confidence=confidence,
            reason=reason,
            filter_name=self.name
        )