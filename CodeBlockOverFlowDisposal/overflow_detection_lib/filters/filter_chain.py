#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Filter chain implementation
"""

from typing import List, Optional
from .base_filter import BaseFilter, FilterResult

class FilterChain:
    """フィルタチェーン実装"""
    
    def __init__(self, filters: Optional[List[BaseFilter]] = None):
        self.filters = filters or []
    
    def add_filter(self, filter_instance: BaseFilter) -> 'FilterChain':
        """フィルタを追加（メソッドチェーン対応）"""
        self.filters.append(filter_instance)
        return self
    
    def apply(self, overflow_text: str, overflow_amount: float, y_position: float) -> FilterResult:
        """
        全フィルタを順次適用し、最初に誤検知と判定したフィルタの結果を返す
        すべてのフィルタが通過した場合は有効なはみ出しと判定
        """
        if not self.filters:
            return FilterResult(
                is_false_positive=False,
                confidence=0.5,
                reason="フィルタなし",
                filter_name="NoFilter"
            )
        
        # フィルタを順次適用
        for filter_instance in self.filters:
            try:
                result = filter_instance.apply(overflow_text, overflow_amount, y_position)
                if result.is_false_positive:
                    return result
            except Exception as e:
                # フィルタエラーは記録するが処理を継続
                continue
        
        # すべてのフィルタを通過した場合
        return FilterResult(
            is_false_positive=False,
            confidence=0.8,
            reason="全フィルタ通過",
            filter_name="FilterChain"
        )
    
    def get_filter_names(self) -> List[str]:
        """登録されているフィルタ名一覧を取得"""
        return [f.name for f in self.filters]