"""
統一ログ管理システム
Phase 1-3: 統合ログビューアとプラグイン別フィルタリング
"""
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import threading
import queue


class PluginLogFilter(logging.Filter):
    """プラグイン別のログフィルター"""
    
    def __init__(self, plugin_name: str):
        super().__init__()
        self.plugin_name = plugin_name
        
    def filter(self, record: logging.LogRecord) -> bool:
        """プラグイン名でフィルタリング"""
        return getattr(record, 'plugin', None) == self.plugin_name


class ColoredFormatter(logging.Formatter):
    """カラー対応のフォーマッター"""
    
    # ANSIカラーコード
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """カラー付きでフォーマット"""
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


class LogManager:
    """統一されたログ管理クラス"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """シングルトンパターンの実装"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        """初期化"""
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.project_root = Path(__file__).parent.parent.parent
        self.log_dir = self.project_root / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # ログ設定
        self.loggers: Dict[str, logging.Logger] = {}
        self.handlers: Dict[str, logging.Handler] = {}
        self.log_queue = queue.Queue()
        self.log_history: List[Dict[str, Any]] = []
        
        # メインログの設定
        self._setup_main_logger()
        
        # ログ監視スレッド
        self.monitor_thread = threading.Thread(
            target=self._monitor_logs,
            daemon=True
        )
        self.monitor_thread.start()
        
    def _setup_main_logger(self):
        """メインログの設定"""
        # ルートロガーの設定
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # メインログファイルハンドラー
        main_handler = RotatingFileHandler(
            self.log_dir / "techgate.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        main_handler.setLevel(logging.INFO)
        
        # フォーマッター
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        main_handler.setFormatter(formatter)
        
        # ハンドラーを追加
        root_logger.addHandler(main_handler)
        self.handlers['main'] = main_handler
        
        # コンソールハンドラー（開発用）
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        ))
        root_logger.addHandler(console_handler)
        self.handlers['console'] = console_handler
        
    def get_logger(self, name: str, plugin_name: Optional[str] = None) -> logging.Logger:
        """
        ロガーの取得
        
        Args:
            name: ロガー名
            plugin_name: プラグイン名（オプション）
            
        Returns:
            設定されたロガー
        """
        if name in self.loggers:
            return self.loggers[name]
            
        # 新しいロガーを作成
        logger = logging.getLogger(name)
        
        # プラグイン用の設定
        if plugin_name:
            # プラグイン専用ファイルハンドラー
            plugin_handler = RotatingFileHandler(
                self.log_dir / f"plugin_{plugin_name}.log",
                maxBytes=5 * 1024 * 1024,  # 5MB
                backupCount=3,
                encoding='utf-8'
            )
            plugin_handler.setLevel(logging.DEBUG)
            
            # フォーマッター
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            plugin_handler.setFormatter(formatter)
            
            # フィルターを追加
            plugin_filter = PluginLogFilter(plugin_name)
            plugin_handler.addFilter(plugin_filter)
            
            logger.addHandler(plugin_handler)
            self.handlers[f"plugin_{plugin_name}"] = plugin_handler
            
            # ログアダプターでプラグイン名を自動付与
            logger = logging.LoggerAdapter(logger, {'plugin': plugin_name})
            
        self.loggers[name] = logger
        return logger
        
    def _monitor_logs(self):
        """ログ監視スレッド"""
        while True:
            try:
                # キューからログを取得
                log_entry = self.log_queue.get(timeout=1)
                
                # 履歴に追加（最新1000件を保持）
                self.log_history.append(log_entry)
                if len(self.log_history) > 1000:
                    self.log_history.pop(0)
                    
            except queue.Empty:
                continue
                
    def add_log_entry(self, level: str, message: str, plugin: Optional[str] = None,
                     extra: Optional[Dict[str, Any]] = None):
        """
        ログエントリーの追加（UI表示用）
        
        Args:
            level: ログレベル
            message: メッセージ
            plugin: プラグイン名
            extra: 追加情報
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'plugin': plugin,
            'extra': extra or {}
        }
        self.log_queue.put(entry)
        
    def get_log_history(self, plugin: Optional[str] = None,
                       level: Optional[str] = None,
                       since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        ログ履歴の取得
        
        Args:
            plugin: フィルタリングするプラグイン名
            level: フィルタリングするログレベル
            since: この日時以降のログのみ取得
            
        Returns:
            フィルタリングされたログエントリーのリスト
        """
        filtered = self.log_history.copy()
        
        # プラグインでフィルタリング
        if plugin:
            filtered = [log for log in filtered if log.get('plugin') == plugin]
            
        # レベルでフィルタリング
        if level:
            filtered = [log for log in filtered if log.get('level') == level]
            
        # 日時でフィルタリング
        if since:
            since_str = since.isoformat()
            filtered = [log for log in filtered if log.get('timestamp', '') >= since_str]
            
        return filtered
        
    def export_logs(self, output_path: Path, plugin: Optional[str] = None,
                   since: Optional[datetime] = None) -> bool:
        """
        ログのエクスポート
        
        Args:
            output_path: 出力先パス
            plugin: エクスポートするプラグイン
            since: この日時以降のログのみ
            
        Returns:
            成功フラグ
        """
        try:
            logs = self.get_log_history(plugin=plugin, since=since)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for log in logs:
                    f.write(f"{log['timestamp']} - {log['level']} - ")
                    if log.get('plugin'):
                        f.write(f"[{log['plugin']}] ")
                    f.write(f"{log['message']}\n")
                    if log.get('extra'):
                        f.write(f"  Extra: {json.dumps(log['extra'])}\n")
                        
            return True
            
        except Exception as e:
            print(f"ログエクスポートエラー: {e}")
            return False
            
    def clear_old_logs(self, days: int = 30) -> int:
        """
        古いログファイルの削除
        
        Args:
            days: 保持する日数
            
        Returns:
            削除したファイル数
        """
        deleted = 0
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for log_file in self.log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                try:
                    log_file.unlink()
                    deleted += 1
                except Exception as e:
                    print(f"ログファイル削除エラー: {e}")
                    
        return deleted
        
    def set_log_level(self, level: str, handler_name: Optional[str] = None):
        """
        ログレベルの設定
        
        Args:
            level: ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）
            handler_name: ハンドラー名（指定しない場合は全て）
        """
        level_obj = getattr(logging, level.upper())
        
        if handler_name and handler_name in self.handlers:
            self.handlers[handler_name].setLevel(level_obj)
        else:
            for handler in self.handlers.values():
                handler.setLevel(level_obj)


# グローバルインスタンス
log_manager = LogManager()


# 便利な関数
def get_logger(name: str, plugin_name: Optional[str] = None) -> logging.Logger:
    """ロガーの取得"""
    return log_manager.get_logger(name, plugin_name)


# 使用例
if __name__ == "__main__":
    # 通常のロガー
    logger = get_logger(__name__)
    logger.info("ログマネージャーが初期化されました")
    
    # プラグイン用ロガー
    plugin_logger = get_logger("TechZipPlugin", plugin_name="TechZipPlugin")
    plugin_logger.info("プラグインが起動しました")
    plugin_logger.debug("デバッグ情報")
    plugin_logger.warning("警告メッセージ")
    plugin_logger.error("エラーが発生しました")
    
    # ログ履歴の取得
    history = log_manager.get_log_history(plugin="TechZipPlugin")
    for entry in history:
        print(f"{entry['timestamp']}: {entry['message']}")