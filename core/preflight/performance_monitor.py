"""Pre-flightパフォーマンス監視システム"""
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import deque, defaultdict
from contextlib import contextmanager

from utils.logger import get_logger


@dataclass
class PerformanceMetrics:
    """パフォーマンス指標"""
    timestamp: datetime
    
    # CPU使用率
    cpu_percent: float
    cpu_count: int
    
    # メモリ使用量
    memory_used_mb: float
    memory_total_mb: float
    memory_percent: float
    
    # ディスク使用量
    disk_read_mb: float
    disk_write_mb: float
    
    # ネットワーク使用量
    network_sent_mb: float
    network_recv_mb: float
    
    # プロセス固有情報
    process_cpu_percent: float
    process_memory_mb: float
    process_threads: int
    
    # カスタム指標
    active_jobs: int = 0
    pending_validations: int = 0
    email_checks_per_minute: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_percent': self.cpu_percent,
            'cpu_count': self.cpu_count,
            'memory_used_mb': self.memory_used_mb,
            'memory_total_mb': self.memory_total_mb,
            'memory_percent': self.memory_percent,
            'disk_read_mb': self.disk_read_mb,
            'disk_write_mb': self.disk_write_mb,
            'network_sent_mb': self.network_sent_mb,
            'network_recv_mb': self.network_recv_mb,
            'process_cpu_percent': self.process_cpu_percent,
            'process_memory_mb': self.process_memory_mb,
            'process_threads': self.process_threads,
            'active_jobs': self.active_jobs,
            'pending_validations': self.pending_validations,
            'email_checks_per_minute': self.email_checks_per_minute
        }


@dataclass
class PerformanceAlert:
    """パフォーマンスアラート"""
    alert_id: str
    severity: str  # info, warning, critical
    metric_name: str
    current_value: float
    threshold_value: float
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class PerformanceThresholds:
    """パフォーマンス閾値設定"""
    cpu_warning: float = 70.0      # CPU使用率警告閾値（%）
    cpu_critical: float = 90.0     # CPU使用率重大閾値（%）
    memory_warning: float = 80.0   # メモリ使用率警告閾値（%）
    memory_critical: float = 95.0  # メモリ使用率重大閾値（%）
    disk_io_warning: float = 100.0 # ディスクI/O警告閾値（MB/s）
    disk_io_critical: float = 500.0# ディスクI/O重大閾値（MB/s）
    response_time_warning: float = 5.0    # レスポンス時間警告閾値（秒）
    response_time_critical: float = 10.0  # レスポンス時間重大閾値（秒）


class PerformanceMonitor:
    """パフォーマンス監視システム"""
    
    def __init__(self, collection_interval: int = 30, retention_hours: int = 24):
        self.logger = get_logger(__name__)
        self.collection_interval = collection_interval
        self.retention_hours = retention_hours
        
        # データ保存
        self._metrics_history: deque = deque(maxlen=int(retention_hours * 3600 / collection_interval))
        self._alerts: Dict[str, PerformanceAlert] = {}
        self._alert_callbacks: List[Callable[[PerformanceAlert], None]] = []
        
        # 設定
        self.thresholds = PerformanceThresholds()
        
        # 監視状態
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        
        # プロセス情報
        self._process = psutil.Process()
        self._last_disk_io = None
        self._last_network_io = None
        
        # カスタム指標
        self._custom_metrics: Dict[str, Any] = {}
        self._operation_times: deque = deque(maxlen=100)  # 最新100操作の実行時間
    
    def start_monitoring(self) -> None:
        """監視開始"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_worker, daemon=True)
        self._monitor_thread.start()
        
        self.logger.info(f"パフォーマンス監視開始: 間隔{self.collection_interval}秒")
    
    def stop_monitoring(self) -> None:
        """監視停止"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        
        self.logger.info("パフォーマンス監視停止")
    
    def _monitor_worker(self) -> None:
        """監視ワーカー"""
        while self._monitoring:
            try:
                metrics = self._collect_metrics()
                
                with self._lock:
                    self._metrics_history.append(metrics)
                
                # 閾値チェック
                self._check_thresholds(metrics)
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                self.logger.error(f"監視エラー: {e}")
                time.sleep(self.collection_interval)
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """メトリクス収集"""
        now = datetime.now()
        
        # システム情報
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        memory = psutil.virtual_memory()
        memory_used_mb = memory.used / (1024 * 1024)
        memory_total_mb = memory.total / (1024 * 1024)
        memory_percent = memory.percent
        
        # ディスクI/O
        disk_io = psutil.disk_io_counters()
        disk_read_mb = 0.0
        disk_write_mb = 0.0
        
        if self._last_disk_io and disk_io:
            read_bytes = disk_io.read_bytes - self._last_disk_io.read_bytes
            write_bytes = disk_io.write_bytes - self._last_disk_io.write_bytes
            disk_read_mb = read_bytes / (1024 * 1024) / self.collection_interval
            disk_write_mb = write_bytes / (1024 * 1024) / self.collection_interval
        
        self._last_disk_io = disk_io
        
        # ネットワークI/O
        network_io = psutil.net_io_counters()
        network_sent_mb = 0.0
        network_recv_mb = 0.0
        
        if self._last_network_io and network_io:
            sent_bytes = network_io.bytes_sent - self._last_network_io.bytes_sent
            recv_bytes = network_io.bytes_recv - self._last_network_io.bytes_recv
            network_sent_mb = sent_bytes / (1024 * 1024) / self.collection_interval
            network_recv_mb = recv_bytes / (1024 * 1024) / self.collection_interval
        
        self._last_network_io = network_io
        
        # プロセス情報
        try:
            process_cpu_percent = self._process.cpu_percent()
            process_memory_mb = self._process.memory_info().rss / (1024 * 1024)
            process_threads = self._process.num_threads()
        except:
            process_cpu_percent = 0.0
            process_memory_mb = 0.0
            process_threads = 0
        
        # カスタム指標
        active_jobs = self._custom_metrics.get('active_jobs', 0)
        pending_validations = self._custom_metrics.get('pending_validations', 0)
        email_checks_per_minute = self._custom_metrics.get('email_checks_per_minute', 0.0)
        
        return PerformanceMetrics(
            timestamp=now,
            cpu_percent=cpu_percent,
            cpu_count=cpu_count,
            memory_used_mb=memory_used_mb,
            memory_total_mb=memory_total_mb,
            memory_percent=memory_percent,
            disk_read_mb=disk_read_mb,
            disk_write_mb=disk_write_mb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            process_cpu_percent=process_cpu_percent,
            process_memory_mb=process_memory_mb,
            process_threads=process_threads,
            active_jobs=active_jobs,
            pending_validations=pending_validations,
            email_checks_per_minute=email_checks_per_minute
        )
    
    def _check_thresholds(self, metrics: PerformanceMetrics) -> None:
        """閾値チェックとアラート生成"""
        alerts_to_generate = []
        
        # CPU使用率チェック
        if metrics.cpu_percent >= self.thresholds.cpu_critical:
            alerts_to_generate.append(('cpu_critical', 'critical', 'CPU使用率', 
                                     metrics.cpu_percent, self.thresholds.cpu_critical))
        elif metrics.cpu_percent >= self.thresholds.cpu_warning:
            alerts_to_generate.append(('cpu_warning', 'warning', 'CPU使用率', 
                                     metrics.cpu_percent, self.thresholds.cpu_warning))
        
        # メモリ使用率チェック
        if metrics.memory_percent >= self.thresholds.memory_critical:
            alerts_to_generate.append(('memory_critical', 'critical', 'メモリ使用率', 
                                     metrics.memory_percent, self.thresholds.memory_critical))
        elif metrics.memory_percent >= self.thresholds.memory_warning:
            alerts_to_generate.append(('memory_warning', 'warning', 'メモリ使用率', 
                                     metrics.memory_percent, self.thresholds.memory_warning))
        
        # ディスクI/Oチェック
        total_disk_io = metrics.disk_read_mb + metrics.disk_write_mb
        if total_disk_io >= self.thresholds.disk_io_critical:
            alerts_to_generate.append(('disk_io_critical', 'critical', 'ディスクI/O', 
                                     total_disk_io, self.thresholds.disk_io_critical))
        elif total_disk_io >= self.thresholds.disk_io_warning:
            alerts_to_generate.append(('disk_io_warning', 'warning', 'ディスクI/O', 
                                     total_disk_io, self.thresholds.disk_io_warning))
        
        # アラート生成
        for alert_id, severity, metric_name, current_value, threshold_value in alerts_to_generate:
            self._generate_alert(alert_id, severity, metric_name, current_value, threshold_value)
    
    def _generate_alert(self, alert_id: str, severity: str, metric_name: str, 
                       current_value: float, threshold_value: float) -> None:
        """アラート生成"""
        with self._lock:
            # 既存のアラートが未解決の場合はスキップ
            if alert_id in self._alerts and not self._alerts[alert_id].resolved:
                return
            
            message = f"{metric_name}が閾値を超過: {current_value:.1f} >= {threshold_value:.1f}"
            
            alert = PerformanceAlert(
                alert_id=alert_id,
                severity=severity,
                metric_name=metric_name,
                current_value=current_value,
                threshold_value=threshold_value,
                message=message,
                timestamp=datetime.now()
            )
            
            self._alerts[alert_id] = alert
            
            # コールバック実行
            for callback in self._alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"アラートコールバックエラー: {e}")
            
            self.logger.warning(f"パフォーマンスアラート[{severity.upper()}]: {message}")
    
    def resolve_alert(self, alert_id: str) -> bool:
        """アラート解決"""
        with self._lock:
            if alert_id in self._alerts:
                alert = self._alerts[alert_id]
                if not alert.resolved:
                    alert.resolved = True
                    alert.resolved_at = datetime.now()
                    self.logger.info(f"アラート解決: {alert_id}")
                    return True
        return False
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]) -> None:
        """アラートコールバック追加"""
        self._alert_callbacks.append(callback)
    
    def update_custom_metric(self, key: str, value: Any) -> None:
        """カスタム指標更新"""
        self._custom_metrics[key] = value
    
    @contextmanager
    def measure_operation(self, operation_name: str = "operation"):
        """操作実行時間測定"""
        start_time = time.time()
        try:
            yield
        finally:
            execution_time = time.time() - start_time
            self._operation_times.append(execution_time)
            
            # レスポンス時間アラート
            if execution_time >= self.thresholds.response_time_critical:
                self._generate_alert(
                    f'response_time_critical_{int(time.time())}', 'critical', 
                    f'{operation_name}実行時間', execution_time, self.thresholds.response_time_critical
                )
            elif execution_time >= self.thresholds.response_time_warning:
                self._generate_alert(
                    f'response_time_warning_{int(time.time())}', 'warning', 
                    f'{operation_name}実行時間', execution_time, self.thresholds.response_time_warning
                )
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """現在のメトリクス取得"""
        with self._lock:
            if self._metrics_history:
                return self._metrics_history[-1]
        return None
    
    def get_metrics_history(self, hours: int = 1) -> List[PerformanceMetrics]:
        """メトリクス履歴取得"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        with self._lock:
            return [m for m in self._metrics_history if m.timestamp >= cutoff_time]
    
    def get_active_alerts(self) -> List[PerformanceAlert]:
        """アクティブなアラート取得"""
        with self._lock:
            return [alert for alert in self._alerts.values() if not alert.resolved]
    
    def get_statistics(self) -> Dict[str, Any]:
        """統計情報取得"""
        with self._lock:
            if not self._metrics_history:
                return {}
            
            recent_metrics = list(self._metrics_history)[-60:]  # 最新60データポイント
            
            if not recent_metrics:
                return {}
            
            # 平均値計算
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
            avg_process_cpu = sum(m.process_cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_process_memory = sum(m.process_memory_mb for m in recent_metrics) / len(recent_metrics)
            
            # 最大値
            max_cpu = max(m.cpu_percent for m in recent_metrics)
            max_memory = max(m.memory_percent for m in recent_metrics)
            
            # 操作実行時間統計
            operation_stats = {}
            if self._operation_times:
                times = list(self._operation_times)
                operation_stats = {
                    'avg_response_time': sum(times) / len(times),
                    'max_response_time': max(times),
                    'min_response_time': min(times),
                    'total_operations': len(times)
                }
            
            return {
                'monitoring_active': self._monitoring,
                'collection_interval': self.collection_interval,
                'data_points': len(recent_metrics),
                'average_cpu_percent': round(avg_cpu, 1),
                'average_memory_percent': round(avg_memory, 1),
                'average_process_cpu_percent': round(avg_process_cpu, 1),
                'average_process_memory_mb': round(avg_process_memory, 1),
                'peak_cpu_percent': round(max_cpu, 1),
                'peak_memory_percent': round(max_memory, 1),
                'active_alerts_count': len(self.get_active_alerts()),
                'total_alerts_count': len(self._alerts),
                'operation_statistics': operation_stats,
                'custom_metrics': dict(self._custom_metrics)
            }
    
    def export_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """メトリクスをエクスポート"""
        metrics_list = self.get_metrics_history(hours)
        return [m.to_dict() for m in metrics_list]
    
    def cleanup_old_data(self) -> None:
        """古いデータのクリーンアップ"""
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        
        with self._lock:
            # 古いアラートを削除
            old_alerts = [
                alert_id for alert_id, alert in self._alerts.items()
                if alert.resolved and alert.resolved_at and alert.resolved_at < cutoff_time
            ]
            
            for alert_id in old_alerts:
                del self._alerts[alert_id]
            
            if old_alerts:
                self.logger.info(f"古いアラートをクリーンアップ: {len(old_alerts)}件")


# グローバルインスタンス
_performance_monitor_instance: Optional[PerformanceMonitor] = None

def get_performance_monitor() -> PerformanceMonitor:
    """パフォーマンス監視システムのグローバルインスタンスを取得"""
    global _performance_monitor_instance
    if _performance_monitor_instance is None:
        _performance_monitor_instance = PerformanceMonitor()
    return _performance_monitor_instance