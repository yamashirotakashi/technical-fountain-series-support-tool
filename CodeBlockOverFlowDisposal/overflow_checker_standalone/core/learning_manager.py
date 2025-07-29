# -*- coding: utf-8 -*-
"""
学習データ管理（Windows対応版）

Phase 2C-1 実装
SQLiteベースの学習データ管理システム
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

import utils.windows_utils as wu
normalize_path = wu.normalize_path
ensure_utf8_encoding = wu.ensure_utf8_encoding
get_default_db_path = wu.get_default_db_path

class WindowsLearningDataManager:
    """Windows環境対応学習データ管理"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        
        if db_path is None:
            db_path = get_default_db_path()
        
        self.db_path = normalize_path(str(db_path))
        self.init_database()
    
    def init_database(self):
        """データベース初期化（Windows文字コード対応）"""
        try:
            # Windows環境でのUTF-8対応
            with sqlite3.connect(
                str(self.db_path),
                isolation_level=None,  # autocommit
                check_same_thread=False
            ) as conn:
                # UTF-8エンコーディング強制
                conn.execute("PRAGMA encoding = 'UTF-8'")
                conn.execute("PRAGMA journal_mode = WAL")  # Windows環境でのパフォーマンス向上
                
                cursor = conn.cursor()
                
                # 学習データテーブル（Windows対応）
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS learning_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pdf_path TEXT NOT NULL,
                        pdf_name TEXT NOT NULL,
                        detected_pages TEXT,  -- JSON配列
                        confirmed_pages TEXT, -- JSON配列
                        additional_pages TEXT, -- JSON配列
                        false_positives TEXT, -- JSON配列
                        timestamp TEXT NOT NULL,
                        os_info TEXT,         -- Windows環境情報
                        app_version TEXT,
                        user_notes TEXT,
                        processing_time REAL
                    )
                """)
                
                # インデックス作成
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_pdf_name ON learning_data(pdf_name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON learning_data(timestamp)")
                
                # 統計情報テーブル
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS learning_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stat_date TEXT NOT NULL,
                        total_cases INTEGER,
                        total_detected INTEGER,
                        total_confirmed INTEGER,
                        total_false_positives INTEGER,
                        total_additional INTEGER,
                        precision_rate REAL,
                        recall_rate REAL,
                        f1_score REAL
                    )
                """)
                
                conn.commit()
                self.logger.info(f"学習データベース初期化完了: {self.db_path}")
                
        except Exception as e:
            self.logger.error(f"データベース初期化エラー: {e}", exc_info=True)
            raise
    
    def save_learning_data(self, learning_data: Dict) -> bool:
        """学習データ保存（Windows環境対応）"""
        try:
            # Windows環境情報を追加
            import platform
            os_info = {
                'system': platform.system(),
                'version': platform.version(),
                'machine': platform.machine(),
                'python_version': platform.python_version(),
                'powershell_version': self._get_powershell_version()
            }
            
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO learning_data (
                        pdf_path, pdf_name, detected_pages, confirmed_pages, 
                        additional_pages, false_positives, timestamp, 
                        os_info, app_version, user_notes, processing_time
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ensure_utf8_encoding(str(learning_data['pdf_path'])),
                    ensure_utf8_encoding(learning_data['pdf_name']),
                    json.dumps(learning_data['detected_pages'], ensure_ascii=False),
                    json.dumps(learning_data['confirmed_pages'], ensure_ascii=False),
                    json.dumps(learning_data['additional_pages'], ensure_ascii=False),
                    json.dumps(learning_data['false_positives'], ensure_ascii=False),
                    datetime.now().isoformat(),
                    json.dumps(os_info, ensure_ascii=False),
                    learning_data.get('app_version', '1.0.0'),
                    ensure_utf8_encoding(learning_data.get('user_notes', '')),
                    learning_data.get('processing_time', 0.0)
                ))
                
                conn.commit()
                self.logger.info(f"学習データ保存完了: {learning_data['pdf_name']}")
                
                # 統計情報の更新
                self._update_statistics()
                
                return True
                
        except Exception as e:
            self.logger.error(f"学習データ保存エラー: {e}", exc_info=True)
            return False
    
    def get_learning_statistics(self) -> Dict:
        """学習統計取得（Windows環境対応）"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # 基本統計
                cursor.execute("SELECT COUNT(*) FROM learning_data")
                total_cases = cursor.fetchone()[0]
                
                if total_cases == 0:
                    return {
                        'total_cases': 0,
                        'database_path': str(self.db_path),
                        'database_size_mb': 0,
                        'last_updated': None
                    }
                
                # 詳細統計計算
                cursor.execute("""
                    SELECT detected_pages, confirmed_pages, false_positives, additional_pages
                    FROM learning_data
                """)
                
                total_detected = 0
                total_confirmed = 0
                total_false_positives = 0
                total_additional = 0
                
                for row in cursor.fetchall():
                    detected = json.loads(row[0]) if row[0] else []
                    confirmed = json.loads(row[1]) if row[1] else []
                    false_pos = json.loads(row[2]) if row[2] else []
                    additional = json.loads(row[3]) if row[3] else []
                    
                    total_detected += len(detected)
                    total_confirmed += len(confirmed)
                    total_false_positives += len(false_pos)
                    total_additional += len(additional)
                
                # 精度計算
                precision = total_confirmed / total_detected if total_detected > 0 else 0
                recall = total_confirmed / (total_confirmed + total_additional) if (total_confirmed + total_additional) > 0 else 0
                f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                
                # データベースサイズ
                db_size_mb = self.db_path.stat().st_size / (1024 * 1024)
                
                # 最終更新日時
                cursor.execute("SELECT MAX(timestamp) FROM learning_data")
                last_updated = cursor.fetchone()[0]
                
                return {
                    'total_cases': total_cases,
                    'total_detected': total_detected,
                    'total_confirmed': total_confirmed,
                    'total_false_positives': total_false_positives,
                    'total_additional': total_additional,
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1_score,
                    'database_path': str(self.db_path),
                    'database_size_mb': round(db_size_mb, 2),
                    'last_updated': last_updated
                }
                
        except Exception as e:
            self.logger.error(f"統計取得エラー: {e}", exc_info=True)
            return {'error': str(e)}
    
    def get_recent_learning_data(self, limit: int = 10) -> List[Dict]:
        """最近の学習データを取得"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT pdf_name, timestamp, detected_pages, confirmed_pages, 
                           false_positives, additional_pages, user_notes
                    FROM learning_data 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
                
                results = []
                for row in cursor.fetchall():
                    data = {
                        'pdf_name': row[0],
                        'timestamp': row[1],
                        'detected_count': len(json.loads(row[2])) if row[2] else 0,
                        'confirmed_count': len(json.loads(row[3])) if row[3] else 0,
                        'false_positive_count': len(json.loads(row[4])) if row[4] else 0,
                        'additional_count': len(json.loads(row[5])) if row[5] else 0,
                        'has_notes': bool(row[6] and row[6].strip())
                    }
                    results.append(data)
                
                return results
                
        except Exception as e:
            self.logger.error(f"最近のデータ取得エラー: {e}", exc_info=True)
            return []
    
    def _update_statistics(self):
        """統計情報を更新"""
        try:
            stats = self.get_learning_statistics()
            if 'error' in stats:
                return
            
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO learning_stats (
                        stat_date, total_cases, total_detected, total_confirmed,
                        total_false_positives, total_additional, precision_rate,
                        recall_rate, f1_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    stats['total_cases'],
                    stats['total_detected'],
                    stats['total_confirmed'],
                    stats['total_false_positives'],
                    stats['total_additional'],
                    stats['precision'],
                    stats['recall'],
                    stats['f1_score']
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.warning(f"統計更新エラー: {e}")
    
    def _get_powershell_version(self) -> str:
        """PowerShellバージョンを取得"""
        try:
            import subprocess
            result = subprocess.run(
                ['powershell', '-Command', '$PSVersionTable.PSVersion'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "Unknown"
    
    def export_learning_data(self, export_path: Path) -> bool:
        """学習データをJSONファイルにエクスポート"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM learning_data ORDER BY timestamp DESC
                """)
                
                columns = [description[0] for description in cursor.description]
                data = []
                
                for row in cursor.fetchall():
                    row_dict = dict(zip(columns, row))
                    # JSON文字列をパース
                    for json_field in ['detected_pages', 'confirmed_pages', 'additional_pages', 'false_positives', 'os_info']:
                        if row_dict[json_field]:
                            row_dict[json_field] = json.loads(row_dict[json_field])
                    data.append(row_dict)
                
                # ファイルに書き込み
                from utils.windows_utils import safe_file_write
                export_content = json.dumps(data, ensure_ascii=False, indent=2)
                safe_file_write(export_path, export_content)
                
                self.logger.info(f"学習データエクスポート完了: {export_path}")
                return True
                
        except Exception as e:
            self.logger.error(f"エクスポートエラー: {e}", exc_info=True)
            return False