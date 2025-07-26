"""Phase 3実装テスト: アーキテクチャ改善機能の検証"""
import os
import sys
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from core.preflight.verification_strategy import (
    VerificationMode, VerificationConfig, VerificationStrategyFactory,
    QuickVerificationStrategy, StandardVerificationStrategy, ThoroughVerificationStrategy
)
from core.preflight.job_state_manager import (
    JobStateManager, JobStatus, JobPriority, JobState
)
from core.preflight.config_manager import (
    ConfigManager, PreflightConfig, EmailConfig, ServiceConfig, ValidationConfig
)
from utils.logger import get_logger


def create_test_file(file_path: Path, size_bytes: int = 1000) -> None:
    """テスト用ファイルを作成"""
    with open(file_path, 'w', encoding='utf-8') as f:
        content = "テスト内容 " * (size_bytes // 10)
        f.write(content)


def test_verification_strategy_factory():
    """検証戦略ファクトリのテスト"""
    print("=== 検証戦略ファクトリテスト ===")
    
    # 利用可能なモード確認
    available_modes = VerificationStrategyFactory.get_available_modes()
    expected_modes = [VerificationMode.QUICK, VerificationMode.STANDARD, 
                     VerificationMode.THOROUGH, VerificationMode.CUSTOM]
    
    for mode in expected_modes:
        if mode in available_modes:
            print(f"✓ モード利用可能: {mode.value}")
        else:
            print(f"✗ モード利用不可: {mode.value}")
            return False
    
    # 各モードの戦略作成テスト
    for mode in expected_modes:
        try:
            config = VerificationConfig(mode=mode)
            strategy = VerificationStrategyFactory.create_strategy(config)
            
            description = strategy.get_description()
            if description:
                print(f"✓ {mode.value}戦略作成成功: {description}")
            else:
                print(f"✗ {mode.value}戦略説明取得失敗")
                return False
                
        except Exception as e:
            print(f"✗ {mode.value}戦略作成エラー: {e}")
            return False
    
    print("検証戦略ファクトリテスト完了\n")
    return True


def test_verification_strategies():
    """各検証戦略のテスト"""
    print("=== 検証戦略実行テスト ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # テストファイル作成
        test_files = []
        for i in range(3):
            test_file = temp_path / f"test_{i}.docx"
            create_test_file(test_file, 1000)
            test_files.append(str(test_file))
        
        # 不正ファイル
        invalid_file = temp_path / "invalid.txt"
        create_test_file(invalid_file, 500)
        test_files.append(str(invalid_file))
        
        # 各戦略のテスト
        strategies_to_test = [
            (VerificationMode.QUICK, "高速検証"),
            (VerificationMode.STANDARD, "標準検証"),
            (VerificationMode.THOROUGH, "徹底検証")
        ]
        
        for mode, description in strategies_to_test:
            try:
                config = VerificationConfig(mode=mode)
                strategy = VerificationStrategyFactory.create_strategy(config)
                
                result = strategy.execute(test_files)
                
                if result.total_files == len(test_files):
                    print(f"✓ {description}実行成功: {result.total_files}ファイル処理")
                else:
                    print(f"✗ {description}実行失敗: 期待{len(test_files)}, 実際{result.total_files}")
                    return False
                
                # 実行時間確認
                if result.execution_time_seconds > 0:
                    print(f"  実行時間: {result.execution_time_seconds:.3f}秒")
                
                # 結果確認
                print(f"  有効ファイル: {result.valid_files}, 無効ファイル: {result.invalid_files}")
                
            except Exception as e:
                print(f"✗ {description}実行エラー: {e}")
                return False
    
    print("検証戦略実行テスト完了\n")
    return True


def test_job_state_manager():
    """ジョブ状態管理のテスト"""
    print("=== ジョブ状態管理テスト ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir) / "job_states.json"
        manager = JobStateManager(str(storage_path))
        
        # ジョブ作成テスト
        job_id = "test_job_001"
        file_path = "/tmp/test.docx"
        email = "test@example.com"
        
        job_state = manager.create_job(job_id, file_path, email, JobPriority.HIGH)
        
        if job_state.job_id == job_id and job_state.status == JobStatus.PENDING:
            print("✓ ジョブ作成成功")
        else:
            print(f"✗ ジョブ作成失敗: {job_state}")
            return False
        
        # ジョブ状態更新テスト
        success = manager.update_job_status(
            job_id, JobStatus.PROCESSING, 
            progress=50, phase="検証中"
        )
        
        if success:
            updated_job = manager.get_job(job_id)
            if updated_job.status == JobStatus.PROCESSING and updated_job.progress_percentage == 50:
                print("✓ ジョブ状態更新成功")
            else:
                print(f"✗ ジョブ状態更新確認失敗: {updated_job}")
                return False
        else:
            print("✗ ジョブ状態更新失敗")
            return False
        
        # 複数ジョブ作成
        for i in range(3):
            manager.create_job(f"batch_job_{i}", f"/tmp/batch_{i}.docx", email)
        
        # 統計情報テスト
        stats = manager.get_statistics()
        expected_total = 4  # test_job_001 + batch_job_0,1,2
        
        if stats['total_jobs'] == expected_total:
            print(f"✓ 統計情報取得成功: 総ジョブ数{stats['total_jobs']}")
        else:
            print(f"✗ 統計情報取得失敗: 期待{expected_total}, 実際{stats['total_jobs']}")
            return False
        
        # アクティブジョブ取得テスト
        active_jobs = manager.get_active_jobs()
        if len(active_jobs) == expected_total:
            print(f"✓ アクティブジョブ取得成功: {len(active_jobs)}件")
        else:
            print(f"✗ アクティブジョブ取得失敗: {len(active_jobs)}件")
            return False
        
        # ジョブ完了テスト
        manager.update_job_status(job_id, JobStatus.COMPLETED, progress=100, phase="完了")
        completed_job = manager.get_job(job_id)
        
        if completed_job.is_completed and completed_job.progress_percentage == 100:
            print("✓ ジョブ完了処理成功")
        else:
            print("✗ ジョブ完了処理失敗")
            return False
        
        # 永続化テスト
        if storage_path.exists():
            print("✓ ジョブ状態永続化成功")
        else:
            print("✗ ジョブ状態永続化失敗")
            return False
    
    print("ジョブ状態管理テスト完了\n")
    return True


def test_config_manager():
    """設定管理のテスト"""
    print("=== 設定管理テスト ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "test_config.json"
        manager = ConfigManager(str(config_path))
        
        # デフォルト設定確認
        config = manager.config
        if isinstance(config, PreflightConfig):
            print("✓ デフォルト設定読み込み成功")
        else:
            print("✗ デフォルト設定読み込み失敗")
            return False
        
        # 個別設定取得テスト
        email_config = manager.get_email_config()
        service_config = manager.get_service_config()
        validation_config = manager.get_validation_config()
        
        if all([isinstance(email_config, EmailConfig),
                isinstance(service_config, ServiceConfig),
                isinstance(validation_config, ValidationConfig)]):
            print("✓ 個別設定取得成功")
        else:
            print("✗ 個別設定取得失敗")
            return False
        
        # 設定更新テスト
        test_email = "updated@example.com"
        manager.update_email_config(username=test_email)
        
        updated_email_config = manager.get_email_config()
        if updated_email_config.username == test_email:
            print("✓ メール設定更新成功")
        else:
            print(f"✗ メール設定更新失敗: {updated_email_config.username}")
            return False
        
        # 検証モード変更テスト
        manager.set_verification_mode(VerificationMode.THOROUGH)
        
        updated_validation = manager.get_validation_config()
        if updated_validation.mode == VerificationMode.THOROUGH:
            print("✓ 検証モード変更成功")
        else:
            print(f"✗ 検証モード変更失敗: {updated_validation.mode}")
            return False
        
        # カスタムパターン追加テスト
        test_pattern = "test_pattern_*"
        manager.add_custom_pattern(test_pattern)
        
        validation_with_pattern = manager.get_validation_config()
        if test_pattern in validation_with_pattern.custom_patterns:
            print("✓ カスタムパターン追加成功")
        else:
            print("✗ カスタムパターン追加失敗")
            return False
        
        # 設定妥当性チェック
        issues = manager.validate_config()
        print(f"✓ 設定妥当性チェック完了: {len(issues)}件の問題")
        
        # 設定ファイル永続化確認
        if config_path.exists():
            print("✓ 設定ファイル保存成功")
        else:
            print("✗ 設定ファイル保存失敗")
            return False
    
    print("設定管理テスト完了\n")
    return True


def test_integration_architecture():
    """アーキテクチャ統合テスト"""
    print("=== アーキテクチャ統合テスト ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 設定管理の初期化
        config_manager = ConfigManager(str(temp_path / "config.json"))
        
        # ジョブ管理の初期化
        job_manager = JobStateManager(str(temp_path / "jobs.json"))
        
        # 設定から検証戦略設定を取得
        verification_config = config_manager.get_verification_strategy_config()
        
        # 検証戦略の作成
        strategy = VerificationStrategyFactory.create_strategy(verification_config)
        
        # テストファイル作成
        test_files = []
        for i in range(2):
            test_file = temp_path / f"integration_test_{i}.docx"
            create_test_file(test_file, 1000)
            test_files.append(str(test_file))
        
        # ジョブ作成
        job_ids = []
        for i, file_path in enumerate(test_files):
            job_id = f"integration_job_{i}"
            job_state = job_manager.create_job(
                job_id, file_path, 
                config_manager.get_email_config().username or "test@example.com"
            )
            job_ids.append(job_id)
        
        # 検証実行
        verification_result = strategy.execute(test_files)
        
        # ジョブ状態を検証結果で更新
        for i, job_id in enumerate(job_ids):
            file_path = test_files[i]
            file_result = verification_result.file_results.get(file_path)
            
            if file_result and file_result.is_valid:
                job_manager.update_job_status(job_id, JobStatus.SUBMITTED, progress=100)
            else:
                job_manager.update_job_status(
                    job_id, JobStatus.FAILED, 
                    error_message="検証失敗", progress=0
                )
        
        # 統合結果確認
        final_stats = job_manager.get_statistics()
        
        if final_stats['total_jobs'] == len(test_files):
            print(f"✓ 統合処理成功: {final_stats['total_jobs']}ジョブ処理")
        else:
            print(f"✗ 統合処理失敗: 期待{len(test_files)}, 実際{final_stats['total_jobs']}")
            return False
        
        # 設定と検証結果の整合性確認
        if verification_result.mode == config_manager.get_validation_config().mode:
            print("✓ 設定-検証戦略整合性確認")
        else:
            print("✗ 設定-検証戦略整合性失敗")
            return False
        
        print(f"統合テスト統計: 成功率{final_stats.get('success_rate', 0)}%")
    
    print("アーキテクチャ統合テスト完了\n")
    return True


def test_observer_pattern():
    """オブザーバーパターンのテスト"""
    print("=== オブザーバーパターンテスト ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = JobStateManager(str(Path(temp_dir) / "observer_test.json"))
        
        # 通知受信用リスト
        notifications = []
        
        def test_observer(job_id: str, job_state: JobState):
            notifications.append((job_id, job_state.status.value))
        
        # オブザーバー登録
        manager.add_observer(test_observer)
        
        # ジョブ作成と状態変更
        job_id = "observer_test_job"
        manager.create_job(job_id, "/tmp/test.docx", "test@example.com")
        manager.update_job_status(job_id, JobStatus.PROCESSING)
        manager.update_job_status(job_id, JobStatus.COMPLETED)
        
        # 通知確認
        expected_notifications = 3  # create, processing, completed
        
        if len(notifications) == expected_notifications:
            print(f"✓ オブザーバー通知成功: {len(notifications)}回通知")
            for job_id, status in notifications:
                print(f"  通知: {job_id} -> {status}")
        else:
            print(f"✗ オブザーバー通知失敗: 期待{expected_notifications}, 実際{len(notifications)}")
            return False
        
        # オブザーバー削除テスト
        manager.remove_observer(test_observer)
        
        # 新しいジョブでの通知確認（通知されないはず）
        old_count = len(notifications)
        manager.create_job("no_notify_job", "/tmp/test2.docx", "test@example.com")
        
        if len(notifications) == old_count:
            print("✓ オブザーバー削除成功")
        else:
            print("✗ オブザーバー削除失敗")
            return False
    
    print("オブザーバーパターンテスト完了\n")
    return True


def main():
    """メインテスト実行"""
    print("Phase 3実装テスト開始: アーキテクチャ改善機能\n")
    
    tests = [
        ("検証戦略ファクトリ", test_verification_strategy_factory),
        ("検証戦略実行", test_verification_strategies),
        ("ジョブ状態管理", test_job_state_manager),
        ("設定管理", test_config_manager),
        ("アーキテクチャ統合", test_integration_architecture),
        ("オブザーバーパターン", test_observer_pattern)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"{'-'*50}")
        print(f"実行中: {test_name}")
        
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"✅ {test_name} 成功")
            else:
                failed += 1
                print(f"❌ {test_name} 失敗")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} 例外: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'-'*50}")
    print(f"テスト結果: 成功 {passed}/{len(tests)}, 失敗 {failed}")
    
    if failed == 0:
        print("🎉 すべてのアーキテクチャ改善テストが成功しました！")
        print("Phase 3: アーキテクチャ改善 - 完了")
        return True
    else:
        print("⚠️  一部のテストが失敗しました。修正が必要です。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)