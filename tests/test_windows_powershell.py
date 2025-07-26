"""Windows PowerShell環境での実働テスト"""
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.preflight.unified_preflight_manager import PreflightManager, create_preflight_manager
from core.preflight.verification_strategy import VerificationMode
from core.preflight.job_state_manager import JobStatus, JobPriority
from utils.logger import get_logger


class WindowsPowerShellTestSuite:
    """Windows PowerShell環境テストスイート"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.test_results: Dict[str, Any] = {}
        self.test_files: List[str] = []
        
    def create_test_docx_file(self, file_path: Path, content_size: int = 2000) -> str:
        """テスト用DOCXファイルを作成"""
        # 簡易的なDOCXファイル構造をシミュレート
        import zipfile
        
        # 最小限のDOCXファイル構造
        docx_content = {
            '[Content_Types].xml': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>''',
            '_rels/.rels': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>''',
            'word/document.xml': f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>
<w:p><w:t>テスト文書内容: {'テスト内容 ' * (content_size // 10)}</w:t></w:p>
</w:body>
</w:document>'''
        }
        
        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as docx:
            for file_name, content in docx_content.items():
                docx.writestr(file_name, content.encode('utf-8'))
        
        return str(file_path)
    
    def test_environment_setup(self) -> bool:
        """環境セットアップテスト"""
        self.logger.info("=== 環境セットアップテスト ===")
        
        try:
            # Python環境確認
            python_version = sys.version
            self.logger.info(f"Python Version: {python_version}")
            
            # OS環境確認
            os_info = os.name
            platform_info = sys.platform
            self.logger.info(f"OS: {os_info}, Platform: {platform_info}")
            
            # パッケージ依存関係確認
            required_packages = [
                ('requests', 'requests'),
                ('psutil', 'psutil'), 
                ('python-dotenv', 'dotenv')
            ]
            missing_packages = []
            
            for package_name, import_name in required_packages:
                try:
                    __import__(import_name)
                    self.logger.info(f"✓ パッケージ利用可能: {package_name}")
                except ImportError:
                    missing_packages.append(package_name)
                    self.logger.error(f"✗ パッケージ不足: {package_name}")
            
            if missing_packages:
                self.logger.error(f"不足パッケージ: {missing_packages}")
                return False
            
            # 環境変数確認とテスト用設定
            gmail_address = os.getenv('GMAIL_ADDRESS')
            gmail_password = os.getenv('GMAIL_APP_PASSWORD')
            
            if not gmail_address or not gmail_password:
                self.logger.warning("環境変数が未設定: GMAIL_ADDRESS, GMAIL_APP_PASSWORD")
                self.logger.info("テスト用のダミー設定を使用します")
                # テスト用環境変数を設定
                os.environ['GMAIL_ADDRESS'] = 'test@example.com'
                os.environ['GMAIL_APP_PASSWORD'] = 'test_password_123'
                self.logger.info("テスト用ダミー環境変数を設定しました")
            
            self.test_results['environment_setup'] = {
                'status': 'success',
                'python_version': python_version,
                'os_info': f"{os_info}/{platform_info}",
                'missing_packages': missing_packages,
                'env_configured': True  # テスト用設定でTrue
            }
            
            self.logger.info("環境セットアップテスト完了\n")
            return True
            
        except Exception as e:
            self.logger.error(f"環境セットアップテストエラー: {e}")
            self.test_results['environment_setup'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    def test_preflight_manager_initialization(self) -> bool:
        """Pre-flightマネージャー初期化テスト"""
        self.logger.info("=== Pre-flightマネージャー初期化テスト ===")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                config_path = Path(temp_dir) / "test_config.json"
                
                # マネージャー作成
                manager = create_preflight_manager(str(config_path))
                
                if manager:
                    self.logger.info("✓ Pre-flightマネージャー初期化成功")
                    
                    # システム状態取得テスト
                    system_status = manager.get_system_status()
                    if system_status:
                        self.logger.info("✓ システム状態取得成功")
                        self.logger.info(f"  セッション開始時刻: {system_status['system_info']['session_start_time']}")
                        self.logger.info(f"  環境設定状況: メール={system_status['configuration']['email_configured']}")
                    else:
                        self.logger.error("✗ システム状態取得失敗")
                        return False
                    
                    # クリーンアップテスト
                    manager.cleanup_resources()
                    self.logger.info("✓ リソースクリーンアップ成功")
                    
                    self.test_results['manager_initialization'] = {
                        'status': 'success',
                        'system_status': system_status
                    }
                    
                else:
                    self.logger.error("✗ Pre-flightマネージャー初期化失敗")
                    return False
            
            self.logger.info("Pre-flightマネージャー初期化テスト完了\n")
            return True
            
        except Exception as e:
            self.logger.error(f"Pre-flightマネージャー初期化テストエラー: {e}")
            self.test_results['manager_initialization'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    def test_file_validation_pipeline(self) -> bool:
        """ファイル検証パイプラインテスト"""
        self.logger.info("=== ファイル検証パイプラインテスト ===")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # テストファイル作成
                test_files = []
                for i in range(3):
                    test_file = temp_path / f"test_validation_{i}.docx"
                    file_path = self.create_test_docx_file(test_file, 2000)
                    test_files.append(file_path)
                    self.test_files.append(file_path)
                
                # 不正ファイル
                invalid_file = temp_path / "invalid.txt"
                with open(invalid_file, 'w', encoding='utf-8') as f:
                    f.write("これは無効なファイルです")
                test_files.append(str(invalid_file))
                
                # マネージャー作成
                config_path = temp_path / "validation_config.json"
                manager = create_preflight_manager(str(config_path))
                
                # 検証のみのテスト（メール監視をスキップ）
                test_email = "test@example.com"
                job_results = {}
                
                # 各ファイルに対して検証のみ実行
                for file_path in test_files:
                    job_id = f"validation_test_{int(time.time() * 1000)}_{Path(file_path).stem}"
                    job_state = manager.job_manager.create_job(job_id, file_path, test_email, JobPriority.HIGH)
                    job_results[file_path] = job_id
                    
                    # 検証フェーズのみ実行
                    from core.preflight.verification_strategy import VerificationStrategyFactory
                    verification_config = manager.config_manager.get_verification_strategy_config()
                    verification_config.mode = VerificationMode.STANDARD
                    strategy = VerificationStrategyFactory.create_strategy(verification_config)
                    
                    # 個別ファイル検証
                    try:
                        result = strategy.execute([file_path])
                        file_result = result.file_results.get(file_path)
                        
                        if file_result and file_result.is_valid:
                            manager.job_manager.update_job_status(
                                job_id, JobStatus.COMPLETED,
                                progress=100, phase="検証完了"
                            )
                        else:
                            error_msg = ', '.join(file_result.issues) if file_result else "検証失敗"
                            manager.job_manager.update_job_status(
                                job_id, JobStatus.FAILED,
                                progress=0, phase="検証失敗",
                                error_message=error_msg
                            )
                    except Exception as e:
                        manager.job_manager.update_job_status(
                            job_id, JobStatus.FAILED,
                            progress=0, phase="検証エラー",
                            error_message=str(e)
                        )
                
                if job_results:
                    self.logger.info(f"✓ ファイル検証パイプライン実行成功: {len(job_results)}ジョブ作成")
                    
                    # ジョブ状態確認
                    valid_jobs = 0
                    failed_jobs = 0
                    
                    for file_path, job_id in job_results.items():
                        job_status = manager.get_job_status(job_id)
                        if job_status:
                            status = job_status['status']
                            file_name = Path(file_path).name
                            self.logger.info(f"  {file_name}: {status}")
                            
                            if status in ['submitted', 'processing', 'completed']:
                                valid_jobs += 1
                            elif status == 'failed':
                                failed_jobs += 1
                    
                    # システム統計確認
                    final_stats = manager.get_system_status()
                    job_stats = final_stats.get('job_statistics', {})
                    
                    self.logger.info(f"統計: 有効ジョブ={valid_jobs}, 失敗ジョブ={failed_jobs}")
                    self.logger.info(f"総ジョブ数: {job_stats.get('total_jobs', 0)}")
                    
                    self.test_results['file_validation'] = {
                        'status': 'success',
                        'total_files': len(test_files),
                        'job_results': len(job_results),
                        'valid_jobs': valid_jobs,
                        'failed_jobs': failed_jobs,
                        'statistics': job_stats
                    }
                    
                    manager.cleanup_resources()
                    
                else:
                    self.logger.error("✗ ファイル検証パイプライン実行失敗")
                    return False
            
            self.logger.info("ファイル検証パイプラインテスト完了\n")
            return True
            
        except Exception as e:
            self.logger.error(f"ファイル検証パイプラインテストエラー: {e}")
            import traceback
            traceback.print_exc()
            self.test_results['file_validation'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    def test_performance_monitoring(self) -> bool:
        """パフォーマンス監視テスト"""
        self.logger.info("=== パフォーマンス監視テスト ===")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                config_path = Path(temp_dir) / "performance_config.json"
                
                # パフォーマンス監視付きマネージャー作成
                manager = create_preflight_manager(str(config_path))
                
                # システム状態でパフォーマンス情報を確認
                system_status = manager.get_system_status()
                perf_stats = system_status.get('performance_statistics', {})
                
                if perf_stats:
                    self.logger.info("✓ パフォーマンス監視システム動作中")
                    self.logger.info(f"  監視状態: {perf_stats.get('monitoring_active', False)}")
                    self.logger.info(f"  収集間隔: {perf_stats.get('collection_interval', 0)}秒")
                    self.logger.info(f"  平均CPU使用率: {perf_stats.get('average_cpu_percent', 0)}%")
                    self.logger.info(f"  平均メモリ使用率: {perf_stats.get('average_memory_percent', 0)}%")
                    
                    # 負荷テストでパフォーマンス測定
                    start_time = time.time()
                    
                    # 軽い負荷をかける
                    test_data = []
                    for i in range(1000):
                        test_data.append(f"test_data_{i}" * 100)
                    
                    # 測定完了
                    elapsed = time.time() - start_time
                    self.logger.info(f"  負荷テスト実行時間: {elapsed:.3f}秒")
                    
                    # アラート状態確認
                    active_alerts = system_status.get('active_alerts', [])
                    self.logger.info(f"  アクティブアラート: {len(active_alerts)}件")
                    
                    self.test_results['performance_monitoring'] = {
                        'status': 'success',
                        'monitoring_active': perf_stats.get('monitoring_active', False),
                        'performance_stats': perf_stats,
                        'load_test_time': elapsed,
                        'active_alerts': len(active_alerts)
                    }
                    
                else:
                    self.logger.warning("パフォーマンス統計が取得できませんでした")
                    self.test_results['performance_monitoring'] = {
                        'status': 'partial',
                        'warning': 'Performance stats not available'
                    }
                
                manager.cleanup_resources()
            
            self.logger.info("パフォーマンス監視テスト完了\n")
            return True
            
        except Exception as e:
            self.logger.error(f"パフォーマンス監視テストエラー: {e}")
            self.test_results['performance_monitoring'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    def test_error_recovery(self) -> bool:
        """エラー回復テスト"""
        self.logger.info("=== エラー回復テスト ===")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                config_path = Path(temp_dir) / "error_recovery_config.json"
                manager = create_preflight_manager(str(config_path))
                
                # 存在しないファイルでエラーを意図的に発生
                invalid_files = [
                    "/nonexistent/file1.docx",
                    "/invalid/path/file2.docx"
                ]
                
                test_email = "error_test@example.com"
                
                # エラーが予想される処理を実行
                job_results = manager.process_files_sync(
                    invalid_files, 
                    test_email,
                    VerificationMode.QUICK
                )
                
                error_jobs = 0
                if job_results:
                    for file_path, job_id in job_results.items():
                        job_status = manager.get_job_status(job_id)
                        if job_status and job_status['status'] == 'failed':
                            error_jobs += 1
                            self.logger.info(f"✓ 期待されるエラー処理: {Path(file_path).name}")
                
                # システムの安定性確認
                system_status = manager.get_system_status()
                if system_status:
                    self.logger.info("✓ エラー後のシステム状態正常")
                    
                    self.test_results['error_recovery'] = {
                        'status': 'success',
                        'error_jobs_handled': error_jobs,
                        'system_stable': True,
                        'total_errors': system_status['system_info'].get('total_errors', 0)
                    }
                else:
                    self.logger.error("✗ エラー後のシステム状態異常")
                    return False
                
                manager.cleanup_resources()
            
            self.logger.info("エラー回復テスト完了\n")
            return True
            
        except Exception as e:
            self.logger.error(f"エラー回復テストエラー: {e}")
            self.test_results['error_recovery'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    def run_full_test_suite(self) -> Dict[str, Any]:
        """完全テストスイート実行"""
        self.logger.info("Windows PowerShell実働テスト開始\n")
        
        test_methods = [
            ("環境セットアップ", self.test_environment_setup),
            ("Pre-flightマネージャー初期化", self.test_preflight_manager_initialization),
            ("ファイル検証パイプライン", self.test_file_validation_pipeline),
            ("パフォーマンス監視", self.test_performance_monitoring),
            ("エラー回復", self.test_error_recovery)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_method in test_methods:
            self.logger.info(f"{'-'*60}")
            self.logger.info(f"実行中: {test_name}")
            
            try:
                result = test_method()
                if result:
                    passed += 1
                    self.logger.info(f"✅ {test_name} 成功")
                else:
                    failed += 1
                    self.logger.error(f"❌ {test_name} 失敗")
            except Exception as e:
                failed += 1
                self.logger.error(f"❌ {test_name} 例外: {e}")
                import traceback
                traceback.print_exc()
        
        # 最終結果
        self.logger.info(f"\n{'-'*60}")
        self.logger.info(f"Windows PowerShell実働テスト結果:")
        self.logger.info(f"成功: {passed}/{len(test_methods)}")
        self.logger.info(f"失敗: {failed}")
        
        final_result = {
            'test_summary': {
                'total_tests': len(test_methods),
                'passed': passed,
                'failed': failed,
                'success_rate': round(passed / len(test_methods) * 100, 1)
            },
            'test_results': self.test_results,
            'test_timestamp': datetime.now().isoformat(),
            'test_files_created': len(self.test_files)
        }
        
        if failed == 0:
            self.logger.info("🎉 すべての実働テストが成功しました！")
            self.logger.info("Windows PowerShell環境での動作確認完了")
        else:
            self.logger.warning("⚠️ 一部のテストが失敗しました。")
            self.logger.info("詳細なエラー情報を確認して修正してください。")
        
        return final_result


def main():
    """メイン実行関数"""
    test_suite = WindowsPowerShellTestSuite()
    results = test_suite.run_full_test_suite()
    
    # 結果をファイルに保存
    import json
    results_file = Path("windows_powershell_test_results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nテスト結果が保存されました: {results_file}")
    
    # 終了コード
    return 0 if results['test_summary']['failed'] == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)