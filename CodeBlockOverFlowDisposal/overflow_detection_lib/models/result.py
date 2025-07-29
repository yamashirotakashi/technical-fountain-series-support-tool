#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Detection result data models
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional
import statistics


class ConfidenceLevel(Enum):
    """検出信頼度レベル"""
    LOW = "Low"
    MEDIUM = "Med"
    HIGH = "High"
    VERY_HIGH = "VHigh"


@dataclass
class OverflowDetail:
    """個別はみ出し詳細データ"""
    
    page_number: int
    overflow_text: str
    x_position: float
    y_position: float
    overflow_amount: float
    confidence: ConfidenceLevel
    char_count: int
    
    def __str__(self) -> str:
        """文字列表現（ログ出力用）"""
        return (f"Page {self.page_number}: '{self.overflow_text}' "
                f"at ({self.x_position:.1f}, {self.y_position:.1f}) "
                f"overflow +{self.overflow_amount:.2f}pt [{self.confidence.value}]")
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'page': self.page_number,
            'text': self.overflow_text,
            'x_pos': self.x_position,
            'y_pos': self.y_position,
            'overflow': self.overflow_amount,
            'confidence': self.confidence.value,
            'char_count': self.char_count
        }


@dataclass 
class DetectionResult:
    """検出結果データクラス"""
    
    # 基本情報
    pdf_path: Path
    total_pages: int
    processing_time: float
    detection_timestamp: datetime = field(default_factory=datetime.now)
    
    # 検出結果
    detected_pages: List[int] = field(default_factory=list)
    detection_details: List[OverflowDetail] = field(default_factory=list)
    
    # 品質情報
    processing_warnings: List[str] = field(default_factory=list)
    
    @property
    def detection_count(self) -> int:
        """検出ページ数"""
        return len(self.detected_pages)
    
    @property
    def detection_rate(self) -> float:
        """検出率 (%)"""
        if self.total_pages == 0:
            return 0.0
        return (self.detection_count / self.total_pages) * 100
    
    @property
    def avg_overflow_amount(self) -> float:
        """平均はみ出し量 (pt)"""
        if not self.detection_details:
            return 0.0
        amounts = [detail.overflow_amount for detail in self.detection_details]
        return statistics.mean(amounts)
    
    @property
    def max_overflow_amount(self) -> float:
        """最大はみ出し量 (pt)"""
        if not self.detection_details:
            return 0.0
        amounts = [detail.overflow_amount for detail in self.detection_details]
        return max(amounts)
    
    @property
    def confidence_scores(self) -> List[float]:
        """信頼度スコア一覧"""
        confidence_mapping = {
            ConfidenceLevel.LOW: 0.25,
            ConfidenceLevel.MEDIUM: 0.50,
            ConfidenceLevel.HIGH: 0.75,
            ConfidenceLevel.VERY_HIGH: 0.95
        }
        return [confidence_mapping.get(detail.confidence, 0.5) 
                for detail in self.detection_details]
    
    def to_page_list(self) -> str:
        """改行区切りのページリスト文字列を生成"""
        if not self.detected_pages:
            return "検出されたはみ出しページはありません。"
        
        return "\n".join(str(page) for page in sorted(self.detected_pages))
    
    def to_detailed_report(self) -> str:
        """詳細レポート文字列を生成"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"PDF はみ出し検出結果詳細レポート")
        lines.append("=" * 60)
        lines.append("")
        
        # ファイル情報
        lines.append("📄 ファイル情報")
        lines.append(f"ファイル名: {self.pdf_path.name}")
        lines.append(f"総ページ数: {self.total_pages}")
        lines.append(f"処理時間: {self.processing_time:.2f}秒")
        lines.append(f"処理日時: {self.detection_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # 検出統計
        lines.append("📊 検出統計")
        lines.append(f"検出ページ数: {self.detection_count} / {self.total_pages} ({self.detection_rate:.1f}%)")
        if self.detection_details:
            lines.append(f"平均はみ出し量: {self.avg_overflow_amount:.2f}pt")
            lines.append(f"最大はみ出し量: {self.max_overflow_amount:.2f}pt")
        lines.append("")
        
        # 詳細結果
        if self.detection_details:
            lines.append("📋 詳細結果")
            lines.append(f"{'Page':<5} {'はみ出し文字':<15} {'位置(pt)':<10} {'はみ出し量':<12} {'信頼度':<8}")
            lines.append("-" * 60)
            
            for detail in self.detection_details:
                text_preview = detail.overflow_text[:12] + "..." if len(detail.overflow_text) > 12 else detail.overflow_text
                lines.append(f"{detail.page_number:<5} {text_preview:<15} {detail.x_position:<10.1f} "
                           f"+{detail.overflow_amount:<11.2f} {detail.confidence.value:<8}")
        else:
            lines.append("📋 詳細結果: はみ出し検出なし")
        
        # 警告情報
        if self.processing_warnings:
            lines.append("")
            lines.append("⚠️ 処理警告")
            for warning in self.processing_warnings:
                lines.append(f"  - {warning}")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def to_csv(self) -> str:
        """CSV 形式の詳細データを生成"""
        if not self.detection_details:
            return "ページ,はみ出し文字,X座標,Y座標,はみ出し量,信頼度,文字数\n"
        
        lines = ["ページ,はみ出し文字,X座標,Y座標,はみ出し量,信頼度,文字数"]
        
        for detail in self.detection_details:
            # CSV用にテキストをエスケープ
            escaped_text = detail.overflow_text.replace('"', '""')
            if ',' in escaped_text or '"' in escaped_text or '\n' in escaped_text:
                escaped_text = f'"{escaped_text}"'
            
            lines.append(f"{detail.page_number},{escaped_text},{detail.x_position:.2f},"
                        f"{detail.y_position:.2f},{detail.overflow_amount:.2f},"
                        f"{detail.confidence.value},{detail.char_count}")
        
        return "\n".join(lines)
    
    def get_summary_stats(self) -> dict:
        """統計サマリーを辞書形式で取得"""
        return {
            'total_pages': self.total_pages,
            'detected_pages': self.detection_count,
            'detection_rate': self.detection_rate,
            'processing_time': self.processing_time,
            'avg_overflow': self.avg_overflow_amount,
            'max_overflow': self.max_overflow_amount,
            'warnings_count': len(self.processing_warnings)
        }