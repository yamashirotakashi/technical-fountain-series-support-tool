#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration management for overflow detection
"""

import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..models.settings import PDFSize, MarginSettings
from ..utils.validation import ValidationError, validate_config

logger = logging.getLogger(__name__)


@dataclass
class DetectionConfig:
    """検出設定データクラス"""
    
    # PDF 設定
    pdf_size: PDFSize
    margins: MarginSettings
    
    # 検出設定
    overflow_threshold_pt: float = 0.1
    measurement_error_threshold_pt: float = 0.5
    max_page_number_digits: int = 3
    
    # フィルタ設定  
    protected_symbols: List[str] = None
    excluded_extensions: List[str] = None
    powershell_min_length: int = 10
    
    # 品質設定
    max_function_complexity: int = 15
    min_test_coverage_percent: int = 80
    
    def __post_init__(self):
        """デフォルト値の設定"""
        if self.protected_symbols is None:
            self.protected_symbols = [
                '"', "'", '(', ')', '[', ']', '{', '}', '<', '>', 
                '=', '+', '-', '*', '/', '\\', '|', '&', '%', 
                '$', '#', '@', '!', '?', '.', ',', ';', ':'
            ]
        
        if self.excluded_extensions is None:
            self.excluded_extensions = [".ps1"]
    
    @classmethod
    def default(cls) -> 'DetectionConfig':
        """デフォルト設定を作成"""
        return cls(
            pdf_size=PDFSize.b5(),
            margins=MarginSettings.techbook_standard()
        )
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'DetectionConfig':
        """設定ファイルから読み込み"""
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return cls.default()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # 設定の検証
            validate_config(config_dict)
            
            return cls.from_dict(config_dict)
            
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Invalid config file {config_path}: {e}")
            raise ValidationError(f"Cannot load config file: {e}", "config_file")
        except Exception as e:
            logger.error(f"Unexpected error loading config: {e}")
            raise ValidationError(f"Cannot load config file: {e}", "config_file")
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'DetectionConfig':
        """辞書から設定を作成"""
        # PDF設定の変換
        pdf_settings = config_dict['pdf_settings']
        pdf_size = PDFSize(
            width_pt=pdf_settings['b5_size']['width_pt'],
            height_pt=pdf_settings['b5_size']['height_pt']
        )
        
        margins_dict = pdf_settings['margins']
        margins = MarginSettings(
            odd_page=MarginSettings.PageMargin(
                left_mm=margins_dict['odd_page']['left_mm'],
                right_mm=margins_dict['odd_page']['right_mm']
            ),
            even_page=MarginSettings.PageMargin(
                left_mm=margins_dict['even_page']['left_mm'],
                right_mm=margins_dict['even_page']['right_mm']
            )
        )
        
        # 検出設定の変換
        detection_settings = config_dict['detection_settings']
        
        # フィルタ設定の変換
        filter_settings = config_dict.get('filter_settings', {})
        
        # 品質設定の変換
        quality_settings = config_dict.get('quality_settings', {})
        
        return cls(
            pdf_size=pdf_size,
            margins=margins,
            overflow_threshold_pt=detection_settings['overflow_threshold_pt'],
            measurement_error_threshold_pt=detection_settings['measurement_error_threshold_pt'],
            max_page_number_digits=detection_settings.get('max_page_number_digits', 3),
            protected_symbols=filter_settings.get('protected_symbols', None),
            excluded_extensions=filter_settings.get('excluded_extensions', None),
            powershell_min_length=filter_settings.get('powershell_min_length', 10),
            max_function_complexity=quality_settings.get('max_function_complexity', 15),
            min_test_coverage_percent=quality_settings.get('min_test_coverage_percent', 80)
        )
    
    def to_file(self, config_path: Path) -> None:
        """設定ファイルに保存"""
        config_dict = self.to_dict()
        
        try:
            # ディレクトリが存在しない場合は作成
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Config saved to: {config_path}")
            
        except Exception as e:
            logger.error(f"Cannot save config file: {e}")
            raise ValidationError(f"Cannot save config file: {e}", "config_file")
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "pdf_settings": {
                "b5_size": {
                    "width_pt": self.pdf_size.width_pt,
                    "height_pt": self.pdf_size.height_pt
                },
                "margins": {
                    "odd_page": {
                        "left_mm": self.margins.odd_page.left_mm,
                        "right_mm": self.margins.odd_page.right_mm
                    },
                    "even_page": {
                        "left_mm": self.margins.even_page.left_mm,
                        "right_mm": self.margins.even_page.right_mm
                    }
                }
            },
            "detection_settings": {
                "overflow_threshold_pt": self.overflow_threshold_pt,
                "measurement_error_threshold_pt": self.measurement_error_threshold_pt,
                "max_page_number_digits": self.max_page_number_digits
            },
            "filter_settings": {
                "protected_symbols": self.protected_symbols,
                "excluded_extensions": self.excluded_extensions,
                "powershell_min_length": self.powershell_min_length
            },
            "quality_settings": {
                "max_function_complexity": self.max_function_complexity,
                "min_test_coverage_percent": self.min_test_coverage_percent
            }
        }


class ConfigManager:
    """設定管理クラス"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Args:
            config_path: 設定ファイルのパス（デフォルト: ./config.json）
        """
        if config_path is None:
            config_path = Path("config.json")
        
        self.config_path = config_path
        self._config: Optional[DetectionConfig] = None
    
    @property 
    def config(self) -> DetectionConfig:
        """現在の設定を取得"""
        if self._config is None:
            self.load()
        return self._config
    
    def load(self) -> DetectionConfig:
        """設定を読み込み"""
        try:
            self._config = DetectionConfig.from_file(self.config_path)
            logger.info(f"Config loaded from: {self.config_path}")
        except ValidationError:
            logger.warning("Using default config due to load error")
            self._config = DetectionConfig.default()
        
        return self._config
    
    def save(self, config: Optional[DetectionConfig] = None) -> None:
        """設定を保存"""
        if config is not None:
            self._config = config
        
        if self._config is None:
            raise ValueError("No config to save")
        
        self._config.to_file(self.config_path)
    
    def reset_to_default(self) -> DetectionConfig:
        """デフォルト設定にリセット"""
        self._config = DetectionConfig.default()
        return self._config
    
    def update_detection_settings(self, **kwargs) -> None:
        """検出設定の部分更新"""
        config = self.config
        
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                raise ValueError(f"Unknown config parameter: {key}")
        
        self._config = config
    
    def get_margin_for_page(self, page_number: int) -> float:
        """指定ページの右マージンを取得 (pt)"""
        config = self.config
        
        if page_number % 2 == 1:  # 奇数ページ
            return config.margins.odd_page.right_pt
        else:  # 偶数ページ
            return config.margins.even_page.right_pt
    
    def validate_current_config(self) -> bool:
        """現在の設定の妥当性を検証"""
        try:
            config_dict = self.config.to_dict()
            validate_config(config_dict)
            return True
        except ValidationError as e:
            logger.error(f"Config validation failed: {e}")
            return False