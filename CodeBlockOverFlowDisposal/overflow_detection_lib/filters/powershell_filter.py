#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PowerShell filter - PowerShellスクリプト検出フィルタ
"""

from .base_filter import BaseFilter, FilterResult

class PowerShellFilter(BaseFilter):
    """PowerShellスクリプトフィルタ"""
    
    def __init__(self, min_length: int = 10):
        self.min_length = min_length
        self.powershell_indicators = {'.ps1', 'PowerShell', 'Get-', 'Set-', 'New-', '$_'}
    
    @property
    def name(self) -> str:
        return "PowerShell"
    
    def apply(self, overflow_text: str, overflow_amount: float, y_position: float) -> FilterResult:
        """PowerShellスクリプト関連をフィルタ"""
        text_content = overflow_text.strip()
        
        # PowerShell指標を含む長いテキストを除外
        has_powershell_indicator = any(indicator in text_content for indicator in self.powershell_indicators)
        
        if has_powershell_indicator and len(text_content) >= self.min_length:
            return self._create_result(
                is_false_positive=True,
                confidence=0.9,
                reason=f"PowerShellスクリプト関連: '{text_content[:20]}...'"
            )
        
        return self._create_result(
            is_false_positive=False,
            confidence=0.3,
            reason=f"PowerShellフィルタ対象外: '{text_content}'"
        )