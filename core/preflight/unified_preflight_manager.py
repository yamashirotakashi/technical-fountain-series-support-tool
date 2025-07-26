"""統合Pre-flightマネージャー - 全機能の統合管理"""
import os
import time
import asyncio
from pathlib import Path
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from .verification_strategy import VerificationStrategyFactory, VerificationConfig, VerificationMode
from .job_state_manager import JobStateManager, JobStatus, JobPriority, get_job_manager
from .config_manager import ConfigManager, get_config_manager
from .performance_monitor import PerformanceMonitor, get_performance_monitor
from .file_validator import WordFileValidator, ValidationResult
from .word2xhtml_scraper import Word2XhtmlScrapingVerifier
from .enhanced_email_monitor import EnhancedEmailMonitor
from utils.logger import get_logger


class PreflightManager:
    """統合Pre-flight管理システム"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = get_logger(__name__)
        
        # コンポーネント初期化
        self.config_manager = get_config_manager(config_path)
        self.job_manager = get_job_manager()
        self.performance_monitor = get_performance_monitor()
        
        # 検証・送信コンポーネント
        self.scraper: Optional[Word2XhtmlScrapingVerifier] = None
        self.email_monitor: Optional[EnhancedEmailMonitor] = None
        
        # 実行状態
        self._is_running = False
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        # 統計情報
        self._session_start_time = datetime.now()
        self._total_files_processed = 0
        self._total_jobs_completed = 0
        self._total_errors = 0
        
        # 初期化完了
        self._initialize_components()
        self.logger.info("統合Pre-flightマネージャー初期化完了")
    
    def _initialize_components(self) -> None:
        """コンポーネントの初期化"""
        try:
            # パフォーマンス監視開始
            self.performance_monitor.start_monitoring()
            
            # アラートコールバック設定
            self.performance_monitor.add_alert_callback(self._handle_performance_alert)
            
            # ジョブマネージャーオブザーバー設定
            self.job_manager.add_observer(self._handle_job_state_change)
            
            # メール・スクレイパーコンポーネントの遅延初期化（実際の使用時）
            self.logger.info("統合マネージャーコンポーネント初期化完了")
            
        except Exception as e:
            self.logger.error(f"コンポーネント初期化エラー: {e}")
    
    def _ensure_email_monitor(self) -> EnhancedEmailMonitor:
        """メール監視の確実な初期化"""
        if not self.email_monitor:
            email_config = self.config_manager.get_email_config()
            if not email_config.is_valid():
                raise ValueError("メール設定が無効です。ユーザー名とパスワードを設定してください。")
            
            self.email_monitor = EnhancedEmailMonitor(
                email_config.username, 
                email_config.password
            )
            self.logger.info("メール監視システム初期化完了")
        
        return self.email_monitor
    
    def _ensure_scraper(self) -> Word2XhtmlScrapingVerifier:
        """スクレイパーの確実な初期化"""
        if not self.scraper:
            self.scraper = Word2XhtmlScrapingVerifier()
            self.logger.info("Word2XHTMLスクレイパー初期化完了")
        
        return self.scraper
    
    def _handle_performance_alert(self, alert) -> None:
        """パフォーマンスアラートの処理"""
        self.logger.warning(f"パフォーマンスアラート: {alert.message}")
        
        # 重大なアラートの場合は処理を一時停止
        if alert.severity == 'critical':
            self.logger.critical("重大なパフォーマンス問題を検出。処理を一時停止します。")
            # 必要に応じて処理の一時停止ロジックを実装
    
    def _handle_job_state_change(self, job_id: str, job_state) -> None:
        """ジョブ状態変更の処理"""
        # パフォーマンス監視にジョブ情報を更新
        active_jobs = len(self.job_manager.get_active_jobs())
        self.performance_monitor.update_custom_metric('active_jobs', active_jobs)
        
        # 統計情報更新
        if job_state.status == JobStatus.COMPLETED:
            self._total_jobs_completed += 1
        elif job_state.status == JobStatus.FAILED:
            self._total_errors += 1
    
    async def process_files_async(
        self, 
        file_paths: List[str], 
        email: str,
        verification_mode: VerificationMode = VerificationMode.STANDARD,
        priority: JobPriority = JobPriority.NORMAL
    ) -> Dict[str, str]:
        """非同期ファイル処理
        
        Args:
            file_paths: 処理対象ファイルパスのリスト
            email: 通知メールアドレス
            verification_mode: 検証モード
            priority: ジョブ優先度
            
        Returns:
            ファイルパス -> ジョブIDの辞書
        """
        self.logger.info(f"非同期ファイル処理開始: {len(file_paths)}ファイル")
        
        # 処理時間測定
        with self.performance_monitor.measure_operation("async_file_processing"):
            # ジョブ作成
            file_to_job = {}
            
            for file_path in file_paths:
                job_id = f"preflight_{int(time.time() * 1000)}_{Path(file_path).stem}"
                job_state = self.job_manager.create_job(job_id, file_path, email, priority)
                file_to_job[file_path] = job_id
            
            # 検証フェーズ
            await self._validate_files_async(file_to_job, verification_mode)
            
            # 送信フェーズ（有効なファイルのみ）
            valid_jobs = {}
            for file_path, job_id in file_to_job.items():
                job_state = self.job_manager.get_job(job_id)
                if job_state and job_state.status != JobStatus.FAILED:
                    valid_jobs[file_path] = job_id
            
            if valid_jobs:
                await self._submit_files_async(valid_jobs, email)
                
                # 結果監視フェーズ
                await self._monitor_results_async(list(valid_jobs.values()))
            
            self._total_files_processed += len(file_paths)
            return file_to_job
    
    async def _validate_files_async(self, file_to_job: Dict[str, str], mode: VerificationMode) -> None:
        """非同期ファイル検証"""
        self.logger.info(f"検証開始: {len(file_to_job)}ファイル, モード: {mode.value}")
        
        # 検証設定取得
        verification_config = self.config_manager.get_verification_strategy_config()
        verification_config.mode = mode
        
        # 検証戦略作成
        strategy = VerificationStrategyFactory.create_strategy(verification_config)
        
        # 各ジョブのステータス更新
        for job_id in file_to_job.values():
            self.job_manager.update_job_status(
                job_id, JobStatus.VALIDATING, 
                progress=0, phase="検証開始"
            )
        
        # パフォーマンス監視更新
        self.performance_monitor.update_custom_metric('pending_validations', len(file_to_job))
        
        # 検証実行（非同期）
        loop = asyncio.get_event_loop()
        verification_result = await loop.run_in_executor(
            self._executor, 
            strategy.execute, 
            list(file_to_job.keys())
        )
        
        # 結果をジョブに反映
        for file_path, job_id in file_to_job.items():
            file_result = verification_result.file_results.get(file_path)
            
            if file_result and file_result.is_valid:
                self.job_manager.update_job_status(
                    job_id, JobStatus.SUBMITTING,
                    progress=50, phase="検証完了",
                    validation_result=file_result.to_dict() if hasattr(file_result, 'to_dict') else None
                )
            else:
                error_msg = ', '.join(file_result.issues) if file_result else "検証失敗"
                self.job_manager.update_job_status(
                    job_id, JobStatus.FAILED,
                    progress=0, phase="検証失敗",
                    error_message=error_msg
                )
        
        self.performance_monitor.update_custom_metric('pending_validations', 0)
        self.logger.info(f"検証完了: 有効{verification_result.valid_files}, 無効{verification_result.invalid_files}")
    
    async def _submit_files_async(self, valid_jobs: Dict[str, str], email: str) -> None:
        """非同期ファイル送信"""
        self.logger.info(f"送信開始: {len(valid_jobs)}ファイル")
        
        scraper = self._ensure_scraper()
        
        # 送信実行
        loop = asyncio.get_event_loop()
        job_ids = await loop.run_in_executor(
            self._executor,
            scraper.submit_batch,
            list(valid_jobs.keys()),
            email
        )
        
        # 結果をジョブに反映
        for i, (file_path, job_id) in enumerate(valid_jobs.items()):
            server_job_id = job_ids[i] if i < len(job_ids) and job_ids[i] else None
            
            if server_job_id:
                self.job_manager.update_job_status(
                    job_id, JobStatus.SUBMITTED,
                    progress=75, phase="送信完了",
                    server_job_id=server_job_id
                )
            else:
                self.job_manager.update_job_status(
                    job_id, JobStatus.FAILED,
                    progress=0, phase="送信失敗",
                    error_message="サーバー送信失敗"
                )
        
        self.logger.info(f"送信完了: {len([j for j in job_ids if j])}件成功")
    
    async def _monitor_results_async(self, job_ids: List[str]) -> None:
        """非同期結果監視"""
        self.logger.info(f"結果監視開始: {len(job_ids)}ジョブ")
        
        email_monitor = self._ensure_email_monitor()
        monitoring_config = self.config_manager.get_monitoring_config()
        
        # サーバージョブIDを取得
        server_job_ids = []
        job_id_mapping = {}
        
        for job_id in job_ids:
            job_state = self.job_manager.get_job(job_id)
            if job_state and job_state.server_job_id:
                server_job_ids.append(job_state.server_job_id)
                job_id_mapping[job_state.server_job_id] = job_id
                
                # 処理中ステータスに更新
                self.job_manager.update_job_status(
                    job_id, JobStatus.PROCESSING,
                    progress=80, phase="サーバー処理中"
                )
        
        if not server_job_ids:
            self.logger.warning("監視対象のサーバージョブIDがありません")
            return
        
        # 結果監視実行
        loop = asyncio.get_event_loop()
        search_results = await loop.run_in_executor(
            self._executor,
            email_monitor.search_results_enhanced,
            server_job_ids,
            monitoring_config.search_hours,
            monitoring_config.max_wait_minutes
        )
        
        # 結果をジョブに反映
        for server_job_id, email_result in search_results.items():
            job_id = job_id_mapping.get(server_job_id)
            if not job_id:
                continue
            
            if email_result.is_success and email_result.download_links:
                self.job_manager.update_job_status(
                    job_id, JobStatus.COMPLETED,
                    progress=100, phase="処理完了",
                    download_links=email_result.download_links
                )
            elif email_result.is_error:
                self.job_manager.update_job_status(
                    job_id, JobStatus.FAILED,
                    progress=0, phase="サーバーエラー",
                    error_message="サーバー側処理エラー"
                )
            else:
                self.job_manager.update_job_status(
                    job_id, JobStatus.TIMEOUT,
                    progress=80, phase="タイムアウト",
                    error_message="結果取得タイムアウト"
                )
        
        self.logger.info("結果監視完了")
    
    def process_files_sync(
        self,
        file_paths: List[str],
        email: str,
        verification_mode: VerificationMode = VerificationMode.STANDARD,
        priority: JobPriority = JobPriority.NORMAL
    ) -> Dict[str, str]:
        """同期ファイル処理（非同期版のラッパー）"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(
                self.process_files_async(file_paths, email, verification_mode, priority)
            )
        finally:
            loop.close()
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """ジョブ状態取得"""
        job_state = self.job_manager.get_job(job_id)
        if job_state:
            return {
                'job_id': job_state.job_id,
                'status': job_state.status.value,
                'progress': job_state.progress_percentage,
                'phase': job_state.current_phase,
                'file_path': job_state.file_path,
                'created_at': job_state.created_at.isoformat(),
                'updated_at': job_state.updated_at.isoformat(),
                'error_message': job_state.error_message,
                'download_links': job_state.download_links,
                'elapsed_time_seconds': job_state.elapsed_time.total_seconds()
            }
        return None
    
    def get_all_jobs_status(self) -> List[Dict[str, Any]]:
        """全ジョブ状態取得"""
        jobs = self.job_manager.get_all_jobs()
        return [self.get_job_status(job.job_id) for job in jobs]
    
    def get_system_status(self) -> Dict[str, Any]:
        """システム状態取得"""
        # 基本統計
        job_stats = self.job_manager.get_statistics()
        perf_stats = self.performance_monitor.get_statistics()
        
        # セッション統計
        session_duration = datetime.now() - self._session_start_time
        
        return {
            'system_info': {
                'session_start_time': self._session_start_time.isoformat(),
                'session_duration_seconds': session_duration.total_seconds(),
                'total_files_processed': self._total_files_processed,
                'total_jobs_completed': self._total_jobs_completed,
                'total_errors': self._total_errors
            },
            'job_statistics': job_stats,
            'performance_statistics': perf_stats,
            'configuration': {
                'verification_mode': self.config_manager.get_validation_config().mode.value,
                'email_configured': self.config_manager.get_email_config().is_valid(),
                'monitoring_interval': self.performance_monitor.collection_interval
            },
            'active_alerts': [
                {
                    'id': alert.alert_id,
                    'severity': alert.severity,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat()
                }
                for alert in self.performance_monitor.get_active_alerts()
            ]
        }
    
    def cancel_job(self, job_id: str) -> bool:
        """ジョブキャンセル"""
        return self.job_manager.cancel_job(job_id)
    
    def retry_job(self, job_id: str) -> bool:
        """ジョブ再試行"""
        return self.job_manager.retry_job(job_id)
    
    def cleanup_resources(self) -> None:
        """リソースクリーンアップ"""
        self.logger.info("リソースクリーンアップ開始")
        
        try:
            # パフォーマンス監視停止
            self.performance_monitor.stop_monitoring()
            
            # スクレイパークリーンアップ
            if self.scraper:
                self.scraper.cleanup()
            
            # メール監視クリーンアップ
            if self.email_monitor:
                self.email_monitor.disconnect()
            
            # エグゼキューター終了
            self._executor.shutdown(wait=True)
            
            self.logger.info("リソースクリーンアップ完了")
            
        except Exception as e:
            self.logger.error(f"クリーンアップエラー: {e}")
    
    def __enter__(self):
        """コンテキストマネージャー開始"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー終了"""
        self.cleanup_resources()


# ファクトリ関数
def create_preflight_manager(config_path: Optional[str] = None) -> PreflightManager:
    """Pre-flightマネージャーの作成"""
    return PreflightManager(config_path)