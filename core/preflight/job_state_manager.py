"""ジョブ状態管理システム"""
from __future__ import annotations

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

from utils.logger import get_logger

# ConfigManagerのインポート（try-except ImportErrorパターン）
try:
    from .config_manager import ConfigManager
except ImportError:
    ConfigManager = None


class JobStatus(Enum):
    """ジョブステータス"""
    PENDING = "pending"           # 待機中
    VALIDATING = "validating"     # 検証中
    SUBMITTING = "submitting"     # 送信中
    SUBMITTED = "submitted"       # 送信完了
    PROCESSING = "processing"     # 処理中（サーバー側）
    COMPLETED = "completed"       # 完了
    FAILED = "failed"            # 失敗
    TIMEOUT = "timeout"          # タイムアウト
    CANCELLED = "cancelled"      # キャンセル


class JobPriority(Enum):
    """ジョブ優先度"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class JobState:
    """ジョブ状態"""
    job_id: str
    file_path: str
    status: JobStatus
    priority: JobPriority
    created_at: datetime
    updated_at: datetime
    email: str
    
    # 進捗情報
    progress_percentage: int = 0
    current_phase: str = ""
    
    # 結果情報
    server_job_id: Optional[str] = None
    download_links: List[str] = None
    error_message: Optional[str] = None
    completion_time: Optional[datetime] = None
    
    # メタデータ
    file_size: int = 0
    validation_result: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.download_links is None:
            self.download_links = []
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
        if isinstance(self.completion_time, str) and self.completion_time:
            self.completion_time = datetime.fromisoformat(self.completion_time)
    
    @property
    def is_active(self) -> bool:
        """アクティブなジョブかどうか"""
        return self.status in [
            JobStatus.PENDING, JobStatus.VALIDATING, 
            JobStatus.SUBMITTING, JobStatus.SUBMITTED, JobStatus.PROCESSING
        ]
    
    @property
    def is_completed(self) -> bool:
        """完了状態かどうか"""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.TIMEOUT, JobStatus.CANCELLED]
    
    @property
    def can_retry(self) -> bool:
        """再試行可能かどうか"""
        return self.status == JobStatus.FAILED and self.retry_count < self.max_retries
    
    @property
    def elapsed_time(self) -> timedelta:
        """経過時間を取得"""
        end_time = self.completion_time or datetime.now()
        return end_time - self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        data = asdict(self)
        # datetime オブジェクトを文字列に変換
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        if self.completion_time:
            data['completion_time'] = self.completion_time.isoformat()
        # Enum を文字列に変換
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobState':
        """辞書から復元"""
        # Enum を復元
        data['status'] = JobStatus(data['status'])
        data['priority'] = JobPriority(data['priority'])
        return cls(**data)


class JobStateManager:
    """ジョブ状態の一元管理システム"""
    
    def __init__(self, storage_path: Optional[str] = None, config_manager: Optional['ConfigManager'] = None):
        self.logger = get_logger(__name__)
        self.config_manager = config_manager
        self._jobs: Dict[str, JobState] = {}
        self._lock = threading.RLock()
        self._observers: List[Callable[[str, JobState], None]] = []
        
        # 永続化設定
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            # ConfigManagerから設定値を取得（デフォルト値付き）
            default_base_dir = str(Path.home() / ".techzip")
            base_dir = self.config_manager.get("paths.cache_directory", default_base_dir) if self.config_manager else default_base_dir
            self.storage_path = Path(base_dir) / "job_states.json"
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 既存の状態を読み込み
        self._load_states()
        
        # 定期クリーンアップのスレッド開始
        self._start_cleanup_thread()
    
    def create_job(
        self, 
        job_id: str, 
        file_path: str, 
        email: str, 
        priority: JobPriority = JobPriority.NORMAL
    ) -> JobState:
        """新しいジョブを作成
        
        Args:
            job_id: ジョブID
            file_path: ファイルパス
            email: 通知先メールアドレス
            priority: 優先度
            
        Returns:
            作成されたジョブ状態
        """
        with self._lock:
            if job_id in self._jobs:
                raise ValueError(f"ジョブID '{job_id}' は既に存在します")
            
            # ファイルサイズを取得
            file_size = 0
            try:
                file_size = Path(file_path).stat().st_size
            except:
                pass
            
            job_state = JobState(
                job_id=job_id,
                file_path=file_path,
                status=JobStatus.PENDING,
                priority=priority,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                email=email,
                file_size=file_size
            )
            
            self._jobs[job_id] = job_state
            self._save_states()
            self._notify_observers(job_id, job_state)
            
            self.logger.info(f"ジョブ作成: {job_id} ({file_path})")
            return job_state
    
    def update_job_status(
        self, 
        job_id: str, 
        status: JobStatus, 
        progress: Optional[int] = None,
        phase: Optional[str] = None,
        error_message: Optional[str] = None,
        server_job_id: Optional[str] = None,
        download_links: Optional[List[str]] = None,
        validation_result: Optional[Dict[str, Any]] = None
    ) -> bool:
        """ジョブ状態を更新
        
        Args:
            job_id: ジョブID
            status: 新しいステータス
            progress: 進捗パーセンテージ
            phase: 現在のフェーズ
            error_message: エラーメッセージ
            server_job_id: サーバー側のジョブID
            download_links: ダウンロードリンク
            validation_result: 検証結果の詳細
            
        Returns:
            更新成功の場合True
        """
        with self._lock:
            if job_id not in self._jobs:
                self.logger.warning(f"未知のジョブID: {job_id}")
                return False
            
            job_state = self._jobs[job_id]
            old_status = job_state.status
            
            # 状態更新
            job_state.status = status
            job_state.updated_at = datetime.now()
            
            if progress is not None:
                job_state.progress_percentage = max(0, min(100, progress))
            
            if phase is not None:
                job_state.current_phase = phase
            
            if error_message is not None:
                job_state.error_message = error_message
            
            if server_job_id is not None:
                job_state.server_job_id = server_job_id
            
            if download_links is not None:
                job_state.download_links = download_links
            
            if validation_result is not None:
                job_state.validation_result = validation_result
            
            # 完了時の処理
            if status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.TIMEOUT, JobStatus.CANCELLED]:
                job_state.completion_time = datetime.now()
                if status == JobStatus.COMPLETED:
                    job_state.progress_percentage = 100
            
            self._save_states()
            self._notify_observers(job_id, job_state)
            
            self.logger.info(f"ジョブ状態更新: {job_id} {old_status.value} -> {status.value}")
            return True
    
    def get_job(self, job_id: str) -> Optional[JobState]:
        """ジョブ状態を取得"""
        with self._lock:
            return self._jobs.get(job_id)
    
    def get_jobs_by_status(self, status: JobStatus) -> List[JobState]:
        """指定ステータスのジョブ一覧を取得"""
        with self._lock:
            return [job for job in self._jobs.values() if job.status == status]
    
    def get_active_jobs(self) -> List[JobState]:
        """アクティブなジョブ一覧を取得"""
        with self._lock:
            return [job for job in self._jobs.values() if job.is_active]
    
    def get_jobs_by_priority(self, priority: JobPriority) -> List[JobState]:
        """指定優先度のジョブ一覧を取得"""
        with self._lock:
            return [job for job in self._jobs.values() if job.priority == priority]
    
    def get_all_jobs(self) -> List[JobState]:
        """全ジョブ一覧を取得"""
        with self._lock:
            return list(self._jobs.values())
    
    def retry_job(self, job_id: str) -> bool:
        """ジョブを再試行
        
        Args:
            job_id: ジョブID
            
        Returns:
            再試行開始成功の場合True
        """
        with self._lock:
            job_state = self._jobs.get(job_id)
            if not job_state:
                return False
            
            if not job_state.can_retry:
                self.logger.warning(f"ジョブ再試行不可: {job_id} (retry: {job_state.retry_count}/{job_state.max_retries})")
                return False
            
            # 再試行設定
            job_state.retry_count += 1
            job_state.status = JobStatus.PENDING
            job_state.updated_at = datetime.now()
            job_state.error_message = None
            job_state.progress_percentage = 0
            job_state.current_phase = ""
            
            self._save_states()
            self._notify_observers(job_id, job_state)
            
            self.logger.info(f"ジョブ再試行: {job_id} (試行回数: {job_state.retry_count})")
            return True
    
    def cancel_job(self, job_id: str) -> bool:
        """ジョブをキャンセル"""
        return self.update_job_status(job_id, JobStatus.CANCELLED, progress=0, phase="キャンセル済み")
    
    def remove_job(self, job_id: str) -> bool:
        """ジョブを削除"""
        with self._lock:
            if job_id in self._jobs:
                del self._jobs[job_id]
                self._save_states()
                self.logger.info(f"ジョブ削除: {job_id}")
                return True
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """統計情報を取得"""
        with self._lock:
            status_counts = defaultdict(int)
            priority_counts = defaultdict(int)
            total_files_size = 0
            total_jobs = len(self._jobs)
            
            completed_jobs = []
            failed_jobs = []
            
            for job in self._jobs.values():
                status_counts[job.status.value] += 1
                priority_counts[job.priority.value] += 1
                total_files_size += job.file_size
                
                if job.status == JobStatus.COMPLETED:
                    completed_jobs.append(job)
                elif job.status == JobStatus.FAILED:
                    failed_jobs.append(job)
            
            # 平均処理時間を計算
            avg_processing_time = None
            if completed_jobs:
                total_time = sum(job.elapsed_time.total_seconds() for job in completed_jobs)
                avg_processing_time = total_time / len(completed_jobs)
            
            return {
                'total_jobs': total_jobs,
                'status_counts': dict(status_counts),
                'priority_counts': dict(priority_counts),
                'total_files_size_mb': round(total_files_size / (1024 * 1024), 2),
                'active_jobs': len([j for j in self._jobs.values() if j.is_active]),
                'completed_jobs': len(completed_jobs),
                'failed_jobs': len(failed_jobs),
                'success_rate': round(len(completed_jobs) / total_jobs * 100, 1) if total_jobs > 0 else 0,
                'average_processing_time_seconds': round(avg_processing_time, 1) if avg_processing_time else None
            }
    
    def add_observer(self, observer: Callable[[str, JobState], None]) -> None:
        """状態変更の監視者を追加"""
        self._observers.append(observer)
    
    def remove_observer(self, observer: Callable[[str, JobState], None]) -> None:
        """監視者を削除"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify_observers(self, job_id: str, job_state: JobState) -> None:
        """監視者に状態変更を通知"""
        for observer in self._observers:
            try:
                observer(job_id, job_state)
            except Exception as e:
                self.logger.error(f"監視者通知エラー: {e}")
    
    def _save_states(self) -> None:
        """状態をファイルに保存"""
        try:
            data = {
                'jobs': {job_id: job.to_dict() for job_id, job in self._jobs.items()},
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"状態保存エラー: {e}")
    
    def _load_states(self) -> None:
        """ファイルから状態を読み込み"""
        try:
            if not self.storage_path.exists():
                return
            
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            jobs_data = data.get('jobs', {})
            for job_id, job_data in jobs_data.items():
                try:
                    job_state = JobState.from_dict(job_data)
                    self._jobs[job_id] = job_state
                except Exception as e:
                    self.logger.error(f"ジョブ状態復元エラー {job_id}: {e}")
            
            self.logger.info(f"ジョブ状態読み込み: {len(self._jobs)}件")
            
        except Exception as e:
            self.logger.error(f"状態読み込みエラー: {e}")
    
    def _start_cleanup_thread(self) -> None:
        """定期クリーンアップスレッドを開始"""
        def cleanup_worker():
            # ConfigManagerから設定値を取得
            cleanup_interval = self.config_manager.get("job_state.cleanup_interval_hours", 1) if self.config_manager else 1
            
            while True:
                try:
                    time.sleep(cleanup_interval * 3600)  # 時間を秒に変換
                    self._cleanup_old_jobs()
                except Exception as e:
                    self.logger.error(f"クリーンアップエラー: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_old_jobs(self, max_age_days: Optional[int] = None) -> None:
        """古いジョブをクリーンアップ"""
        # ConfigManagerから設定値を取得
        if max_age_days is None:
            max_age_days = self.config_manager.get("job_state.max_age_days", 7) if self.config_manager else 7
            
        with self._lock:
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            jobs_to_remove = []
            
            for job_id, job_state in self._jobs.items():
                if job_state.is_completed and job_state.updated_at < cutoff_time:
                    jobs_to_remove.append(job_id)
            
            for job_id in jobs_to_remove:
                del self._jobs[job_id]
            
            if jobs_to_remove:
                self._save_states()
                self.logger.info(f"古いジョブをクリーンアップ: {len(jobs_to_remove)}件")


# グローバルインスタンス（シングルトンパターン）
_job_manager_instance: Optional[JobStateManager] = None

def get_job_manager(storage_path: Optional[str] = None) -> JobStateManager:
    """ジョブ管理システムのグローバルインスタンスを取得"""
    global _job_manager_instance
    if _job_manager_instance is None:
        _job_manager_instance = JobStateManager(storage_path)
    return _job_manager_instance