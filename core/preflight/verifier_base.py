"""Pre-flight Verifierの抽象基底クラス"""
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional


class PreflightVerifier(ABC):
    """Pre-flight検証の抽象基底クラス
from __future__ import annotations
    
    Strategy Patternで実装方式を切り替え可能にする
    """
    
    @abstractmethod
    def submit_batch(self, file_paths: List[str], email: str) -> List[str]:
        """複数ファイルを送信してジョブIDリストを返す
        
        Args:
            file_paths: 検証対象のWordファイルパスリスト
            email: 結果送信先のメールアドレス
            
        Returns:
            ジョブIDのリスト（ファイルパスと同じ順序）
        """
        pass
    
    @abstractmethod
    def check_all_status(self, job_ids: List[str]) -> Dict[str, Tuple[str, Optional[str]]]:
        """全ジョブのステータスを確認
        
        Args:
            job_ids: チェック対象のジョブIDリスト
            
        Returns:
            {job_id: (status, error_message)} の辞書
            status: "success", "error", "pending"
            error_message: エラーの場合のメッセージ（successの場合はNone）
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """リソースのクリーンアップ"""
        pass