"""Pre-flight Checkバッチ処理管理モジュール"""
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from .verifier_base import PreflightVerifier
from .word2xhtml_scraper import Word2XhtmlScrapingVerifier
from .state_manager import PreflightStateManager
from utils.logger import get_logger


@dataclass
class BatchJob:
    """バッチジョブの情報"""
    file_path: str
    job_id: Optional[str] = None
    status: str = "pending"  # pending, uploading, uploaded, checking, success, error
    error_message: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class BatchProcessor:
    """Pre-flight Checkのバッチ処理を管理"""
    
    def __init__(self, verifier: Optional[PreflightVerifier] = None):
        """
        Args:
            verifier: 使用するVerifier（Noneの場合はデフォルト）
        """
        self.logger = get_logger(__name__)
        self.verifier = verifier or Word2XhtmlScrapingVerifier()
        self.state_manager = PreflightStateManager()
        self.jobs: Dict[str, BatchJob] = {}
        self._lock = threading.Lock()
        self._cancelled = False
        
        # コールバック
        self.on_job_updated: Optional[Callable[[BatchJob], None]] = None
        self.on_progress_updated: Optional[Callable[[int, int], None]] = None
        
    def add_files(self, file_paths: List[str]):
        """処理対象ファイルを追加
        
        Args:
            file_paths: Wordファイルパスのリスト
        """
        with self._lock:
            for file_path in file_paths:
                if file_path not in self.jobs:
                    self.jobs[file_path] = BatchJob(file_path=file_path)
                    self.logger.info(f"ジョブ追加: {Path(file_path).name}")
                    
    def process_batch(self, email: str, max_parallel: int = 1) -> Dict[str, BatchJob]:
        """バッチ処理を実行
        
        Args:
            email: 結果送信先メールアドレス
            max_parallel: 並列処理数（デフォルト1でシーケンシャル）
            
        Returns:
            処理結果（file_path -> BatchJob）
        """
        self._cancelled = False
        
        # 状態を保存
        self._save_current_state()
        
        # アップロード処理
        self._upload_files(email)
        
        if self._cancelled:
            return self.jobs
            
        # 結果確認処理（Phase 4で実装）
        self._check_results()
        
        # 最終状態を保存
        self._save_current_state()
        
        return self.jobs
        
    def _upload_files(self, email: str):
        """ファイルをアップロード"""
        pending_jobs = [job for job in self.jobs.values() if job.status == "pending"]
        total = len(pending_jobs)
        
        self.logger.info(f"アップロード開始: {total}ファイル")
        
        file_paths = []
        for i, job in enumerate(pending_jobs):
            if self._cancelled:
                break
                
            job.status = "uploading"
            job.start_time = datetime.now()
            self._notify_job_updated(job)
            
            file_paths.append(job.file_path)
            
        # バッチアップロード
        if file_paths and not self._cancelled:
            job_ids = self.verifier.submit_batch(file_paths, email)
            
            # ジョブIDを更新
            for job, job_id in zip(pending_jobs, job_ids):
                if job_id:
                    job.job_id = job_id
                    job.status = "uploaded"
                else:
                    job.status = "error"
                    job.error_message = "アップロード失敗"
                    
                job.end_time = datetime.now()
                self._notify_job_updated(job)
                self._notify_progress(len([j for j in self.jobs.values() 
                                         if j.status in ["uploaded", "success", "error"]]), 
                                    len(self.jobs))
                
    def _check_results(self):
        """結果を確認（Phase 4で実装）"""
        uploaded_jobs = [job for job in self.jobs.values() if job.status == "uploaded"]
        
        if not uploaded_jobs:
            return
            
        self.logger.info(f"結果確認開始: {len(uploaded_jobs)}ファイル")
        
        # TODO: Phase 4でメール監視と連携
        # 現時点では仮実装
        job_ids = [job.job_id for job in uploaded_jobs if job.job_id]
        results = self.verifier.check_all_status(job_ids)
        
        for job in uploaded_jobs:
            if self._cancelled:
                break
                
            if job.job_id and job.job_id in results:
                status, error_msg = results[job.job_id]
                if status == "success":
                    job.status = "success"
                elif status == "error":
                    job.status = "error"
                    job.error_message = error_msg or "PDF変換エラー"
                else:
                    job.status = "checking"
                    
                self._notify_job_updated(job)
                
    def cancel(self):
        """処理をキャンセル"""
        self._cancelled = True
        self.logger.info("バッチ処理をキャンセルしました")
        
    def resume_from_state(self) -> bool:
        """保存された状態から再開
        
        Returns:
            再開できた場合True
        """
        state = self.state_manager.load_state()
        if not state or 'jobs' not in state:
            return False
            
        # ジョブを復元
        self.jobs.clear()
        for file_path, job_data in state['jobs'].items():
            job = BatchJob(
                file_path=job_data['file_path'],
                job_id=job_data.get('job_id'),
                status=job_data.get('status', 'pending'),
                error_message=job_data.get('error_message')
            )
            if job_data.get('start_time'):
                job.start_time = datetime.fromisoformat(job_data['start_time'])
            if job_data.get('end_time'):
                job.end_time = datetime.fromisoformat(job_data['end_time'])
                
            self.jobs[file_path] = job
            
        self.logger.info(f"状態を復元: {len(self.jobs)}ジョブ")
        return True
        
    def _save_current_state(self):
        """現在の状態を保存"""
        state = {
            'jobs': {}
        }
        
        for file_path, job in self.jobs.items():
            state['jobs'][file_path] = {
                'file_path': job.file_path,
                'job_id': job.job_id,
                'status': job.status,
                'error_message': job.error_message,
                'start_time': job.start_time.isoformat() if job.start_time else None,
                'end_time': job.end_time.isoformat() if job.end_time else None
            }
            
        self.state_manager.save_state(state)
        
    def _notify_job_updated(self, job: BatchJob):
        """ジョブ更新を通知"""
        if self.on_job_updated:
            self.on_job_updated(job)
            
    def _notify_progress(self, completed: int, total: int):
        """進捗を通知"""
        if self.on_progress_updated:
            self.on_progress_updated(completed, total)
            
    def get_summary(self) -> Dict[str, int]:
        """処理結果のサマリーを取得"""
        summary = {
            'total': len(self.jobs),
            'pending': 0,
            'uploading': 0,
            'uploaded': 0,
            'checking': 0,
            'success': 0,
            'error': 0
        }
        
        for job in self.jobs.values():
            summary[job.status] = summary.get(job.status, 0) + 1
            
        return summary