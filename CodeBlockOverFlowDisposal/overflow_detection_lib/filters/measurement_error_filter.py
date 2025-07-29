#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Measurement error filter - 測定誤差によるはみ出しをフィルタ
"""

from .base_filter import BaseFilter, FilterResult

class MeasurementErrorFilter(BaseFilter):
    """測定誤差フィルタ"""
    
    def __init__(self, threshold_pt: float = 0.5):
        self.threshold_pt = threshold_pt
    
    @property
    def name(self) -> str:
        return "MeasurementError"
    
    def apply(self, overflow_text: str, overflow_amount: float, y_position: float) -> FilterResult:
        """微小なはみ出しを測定誤差として判定"""
        if overflow_amount <= self.threshold_pt:
            return self._create_result(
                is_false_positive=True,
                confidence=0.95,
                reason=f"測定誤差範囲内 ({overflow_amount:.2f}pt <= {self.threshold_pt}pt)"
            )
        
        return self._create_result(
            is_false_positive=False,
            confidence=0.8,
            reason=f"有効なはみ出し ({overflow_amount:.2f}pt)"
        )