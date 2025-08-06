"""
HardcodingDetector独立モジュール
ハードコーディング検知システム
リファクタリング時に設定すべき値をスキャンして検出

分離元: src/slack_pdf_poster.py
作成日: 2025-08-03
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional


class HardcodingDetector:
    """
    ハードコーディング検知システム
    リファクタリング時に設定すべき値をスキャンして検出
    """
    
    HARDCODE_PATTERNS = {
        "file_paths": [
            r"G:\\.*",
            r"G:/.*",
            r"C:\\.*",
            r"C:/.*",
            r"/mnt/.*",
            r"Path\(\".*\"\)",
        ],
        "urls": [
            r"https?://[^\s\"\']+",
            r"localhost:\d+",
            r"127\.0\.0\.1:\d+",
        ],
        "credentials": [
            r"ep_user",
            r"Nn7eUTX5",
            r"password\s*=\s*[\"\'][^\"\'][\"\']",
            r"username\s*=\s*[\"\'][^\"\'][\"\']",
        ],
        "api_endpoints": [
            r"trial\.nextpublishing\.jp",
            r"upload_46tate",
            r"do_download_pdf",
            r"api\.slack\.com",
        ],
        "magic_numbers": [
            r":\d{4,5}",  # ポート番号
            r"timeout\s*=\s*\d+",
            r"sleep\(\d+\)",
        ]
    }
    
    def __init__(self, config_manager=None):
        """HardcodingDetectorを初期化"""
        # 循環インポートを避けるため、config_managerは任意
        self.config_manager = config_manager
    
    def scan_file(self, file_path: Path) -> Dict[str, list]:
        """
        ファイル内のハードコーディングをスキャン
        
        Args:
            file_path: スキャン対象ファイル
            
        Returns:
            検出されたハードコーディングの分類別リスト
        """
        return self.scan_hardcoding(str(file_path))
    
    def scan_multiple_files(self, file_paths: list) -> Dict[str, Dict[str, list]]:
        """
        複数ファイルの一括スキャン
        
        Args:
            file_paths: スキャン対象ファイルのリスト
            
        Returns:
            ファイル別の検出結果
        """
        results = {}
        for file_path in file_paths:
            results[str(file_path)] = self.scan_file(Path(file_path))
        return results
    
    def suggest_remediation(self, scan_results: Dict[str, list]) -> list:
        """
        修正提案を生成
        
        Args:
            scan_results: スキャン結果
            
        Returns:
            修正提案のリスト
        """
        suggestions = []
        
        for category, detections in scan_results.items():
            if not detections:
                continue
                
            if category == "file_paths":
                suggestions.append("ファイルパスを設定ファイル（config.yaml）に外部化してください")
            elif category == "urls":
                suggestions.append("URLを環境変数（.env）または設定ファイルに移動してください")
            elif category == "credentials":
                suggestions.append("認証情報を環境変数（.env）に移動し、コードから削除してください")
            elif category == "api_endpoints":
                suggestions.append("APIエンドポイントを設定ファイルに外部化してください")
            elif category == "magic_numbers":
                suggestions.append("数値設定を設定ファイルの定数として定義してください")
                
        return suggestions
    
    @classmethod
    def scan_hardcoding(cls, file_path: str) -> Dict[str, list]:
        """
        ファイル内のハードコーディングをスキャン
        
        Args:
            file_path: スキャン対象ファイル
            
        Returns:
            検出されたハードコーディングの分類別リスト
        """
        detected = {category: [] for category in cls.HARDCODE_PATTERNS.keys()}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for category, patterns in cls.HARDCODE_PATTERNS.items():
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        detected[category].extend(matches)
                        
        except Exception as e:
            print(f"ハードコーディングスキャンエラー: {e}")
            
        return detected