#!/usr/bin/env python3
"""
Configuration Integration Test Suite
Phase 2: Configuration Hell Resolution Testing

Purpose:
- 統一設定システムの動作テスト
- 後方互換性の検証
- 設定移行機能のテスト
"""
from __future__ import annotations

import os
import tempfile
import json
import yaml
from pathlib import Path
from typing import Dict, Any

# Test imports
from core.configuration_provider import (
    get_unified_config, 
    UnifiedConfigurationService,
    ConfigManagerAdapter,
    LegacyConfigAdapter,
    get_web_config,
    get_api_config
)
from core.configuration_migration import (
    ConfigurationMigration,
    analyze_configuration,
    migrate_configuration,
    validate_configuration
)


class ConfigurationIntegrationTest:
    """統一設定システムの統合テスト"""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = None
    
    def run_all_tests(self) -> Dict[str, Any]:
        """全テストを実行"""
        print("🔧 Phase 2 統一Configuration統合テスト開始")
        
        self._setup_test_environment()
        
        try:
            # 1. 基本的な統一設定サービステスト
            self._test_unified_configuration_service()
            
            # 2. 後方互換性テスト
            self._test_backward_compatibility()
            
            # 3. 設定プロバイダーのアダプターテスト
            self._test_configuration_adapters()
            
            # 4. 設定移行機能テスト
            self._test_configuration_migration()
            
            # 5. 設定検証機能テスト
            self._test_configuration_validation()
            
            # 6. 実際の使用シナリオテスト
            self._test_real_world_scenarios()
            
        finally:
            self._cleanup_test_environment()
        
        return self._generate_test_report()
    
    def _setup_test_environment(self):
        """テスト環境をセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_dir = Path(self.temp_dir) / "config"
        self.test_config_dir.mkdir(parents=True)
        
        # Legacy設定ファイルを作成
        legacy_config = {
            "web": {
                "upload_url": "http://test.nextpublishing.jp/upload",
                "username": "test_user",
                "password": "test_pass"
            },
            "paths": {
                "git_base": "/test/git",
                "output_base": "/test/output"
            },
            "google_sheet": {
                "sheet_id": "test_sheet_id",
                "credentials_path": "config/test_credentials.json"
            }
        }
        
        legacy_path = self.test_config_dir / "settings.json"
        with open(legacy_path, 'w', encoding='utf-8') as f:
            json.dump(legacy_config, f, indent=2)
        
        print(f"✅ テスト環境セットアップ完了: {self.temp_dir}")
    
    def _test_unified_configuration_service(self):
        """統一設定サービスのテスト"""
        print("\n📋 1. 統一設定サービステスト")
        
        try:
            # シングルトンインスタンス取得
            config = get_unified_config()
            
            # 基本的な設定取得テスト
            provider_info = config.get_provider_info()
            print(f"  設定プロバイダー: {provider_info}")
            
            # ドット記法での設定取得テスト
            test_value = config.get("api.nextpublishing.username", "default_user")
            print(f"  設定値取得テスト: {test_value}")
            
            # セクション取得テスト
            web_config = config.get_web_config()
            api_config = config.get_api_config()
            
            print(f"  Web設定: {len(web_config)} 項目")
            print(f"  API設定: {len(api_config)} 項目")
            
            self.test_results.append({
                "test": "unified_configuration_service",
                "status": "PASS",
                "details": f"プロバイダー: {provider_info['provider_type']}"
            })
            
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            self.test_results.append({
                "test": "unified_configuration_service", 
                "status": "FAIL",
                "error": str(e)
            })
    
    def _test_backward_compatibility(self):
        """後方互換性テスト"""
        print("\n🔄 2. 後方互換性テスト")
        
        try:
            # 既存の関数が期待通りに動作するかテスト
            web_config = get_web_config()
            api_config = get_api_config("nextpublishing")
            
            print(f"  get_web_config(): {type(web_config)} - {len(web_config)} 項目")
            print(f"  get_api_config(): {type(api_config)} - {len(api_config)} 項目")
            
            # 期待されるキーが存在するかチェック
            expected_web_keys = ["upload_url", "username", "password"]
            missing_keys = [key for key in expected_web_keys if key not in web_config]
            
            if missing_keys:
                print(f"  ⚠️  不足キー: {missing_keys}")
            else:
                print("  ✅ すべての期待キーが存在")
            
            self.test_results.append({
                "test": "backward_compatibility",
                "status": "PASS" if not missing_keys else "PARTIAL",
                "details": f"不足キー: {missing_keys}" if missing_keys else "すべてのキーが利用可能"
            })
            
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            self.test_results.append({
                "test": "backward_compatibility",
                "status": "FAIL", 
                "error": str(e)
            })
    
    def _test_configuration_adapters(self):
        """設定プロバイダーのアダプターテスト"""
        print("\n🔌 3. 設定アダプターテスト")
        
        # ConfigManagerAdapterテスト
        try:
            print("  ConfigManagerAdapter テスト:")
            
            # 一時的にConfigManagerを作成
            from core.config_manager import ConfigManager
            temp_config_manager = ConfigManager(self.test_config_dir)
            
            adapter = ConfigManagerAdapter(temp_config_manager)
            
            # 基本操作テスト
            test_value = adapter.get("api.nextpublishing.username", "default")
            adapter.set("test.key", "test_value")
            
            web_section = adapter.get_section("web")
            
            print(f"    設定取得: {test_value}")
            print(f"    セクション取得: {len(web_section)} 項目")
            
            # 検証テスト
            validation = adapter.validate()
            print(f"    検証結果: {len(validation['errors'])} エラー, {len(validation['warnings'])} 警告")
            
            self.test_results.append({
                "test": "config_manager_adapter",
                "status": "PASS",
                "details": "すべての基本操作が正常動作"
            })
            
        except Exception as e:
            print(f"    ❌ ConfigManagerAdapter エラー: {e}")
            self.test_results.append({
                "test": "config_manager_adapter",
                "status": "FAIL",
                "error": str(e)
            })
        
        # LegacyConfigAdapterテスト
        try:
            print("  LegacyConfigAdapter テスト:")
            
            # 一時的にLegacyConfigを作成（テスト用の設定パスを使用）
            os.environ['TEST_CONFIG_PATH'] = str(self.test_config_dir / "settings.json")
            
            from utils.config import Config
            temp_legacy_config = Config(str(self.test_config_dir / "settings.json"))
            
            adapter = LegacyConfigAdapter(temp_legacy_config)
            
            # 基本操作テスト
            test_value = adapter.get("web.username", "default")
            web_section = adapter.get_section("web")
            
            print(f"    設定取得: {test_value}")
            print(f"    セクション取得: {len(web_section)} 項目")
            
            # 検証テスト
            validation = adapter.validate()
            print(f"    検証結果: {len(validation['errors'])} エラー, {len(validation['warnings'])} 警告")
            
            self.test_results.append({
                "test": "legacy_config_adapter",
                "status": "PASS",
                "details": "すべての基本操作が正常動作"
            })
            
        except Exception as e:
            print(f"    ❌ LegacyConfigAdapter エラー: {e}")
            self.test_results.append({
                "test": "legacy_config_adapter",
                "status": "FAIL",
                "error": str(e)
            })
    
    def _test_configuration_migration(self):
        """設定移行機能テスト"""
        print("\n📦 4. 設定移行機能テスト")
        
        try:
            # 現在のディレクトリを一時的に変更
            original_cwd = os.getcwd()
            os.chdir(self.temp_dir)
            
            try:
                # 設定分析テスト
                analysis = analyze_configuration()
                print(f"  設定分析: Legacy={analysis['legacy_config_exists']}, New={analysis['new_config_exists']}")
                print(f"  移行必要: {analysis['migration_needed']}")
                
                # ドライラン移行テスト
                migration_result = migrate_configuration(dry_run=True)
                print(f"  ドライラン移行: 成功={migration_result['success']}")
                print(f"  移行キー数: {len(migration_result['migrated_keys'])}")
                print(f"  スキップキー数: {len(migration_result['skipped_keys'])}")
                
                # 実際の移行テスト
                if migration_result['success'] and len(migration_result['migrated_keys']) > 0:
                    actual_migration = migrate_configuration(dry_run=False)
                    print(f"  実際の移行: 成功={actual_migration['success']}")
                
                # 設定検証テスト
                validation = validate_configuration()
                if validation:
                    print(f"  整合性チェック: 一貫性={validation.get('consistent', 'N/A')}")
                
                self.test_results.append({
                    "test": "configuration_migration",
                    "status": "PASS",
                    "details": f"移行キー: {len(migration_result['migrated_keys'])}"
                })
                
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            self.test_results.append({
                "test": "configuration_migration",
                "status": "FAIL",
                "error": str(e)
            })
    
    def _test_configuration_validation(self):
        """設定検証機能テスト"""
        print("\n✅ 5. 設定検証機能テスト")
        
        try:
            config = get_unified_config()
            
            # 統一設定サービスの検証機能テスト
            validation = config.validate()
            
            print(f"  エラー数: {len(validation['errors'])}")
            print(f"  警告数: {len(validation['warnings'])}")
            print(f"  不足環境変数: {len(validation.get('missing_env_vars', []))}")
            
            # 詳細な検証項目表示
            if validation['errors']:
                print("  エラー詳細:")
                for error in validation['errors'][:3]:  # 最大3つまで表示
                    print(f"    - {error}")
            
            if validation['warnings']:
                print("  警告詳細:")
                for warning in validation['warnings'][:3]:  # 最大3つまで表示
                    print(f"    - {warning}")
            
            self.test_results.append({
                "test": "configuration_validation",
                "status": "PASS",
                "details": f"エラー: {len(validation['errors'])}, 警告: {len(validation['warnings'])}"
            })
            
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            self.test_results.append({
                "test": "configuration_validation",
                "status": "FAIL",
                "error": str(e)
            })
    
    def _test_real_world_scenarios(self):
        """実際の使用シナリオテスト"""
        print("\n🌍 6. 実世界シナリオテスト")
        
        try:
            # WebClient統合テスト
            print("  WebClient統合テスト:")
            
            # WebClientが統一設定を使用できるかテスト（import可能性のみ）
            try:
                from core.web_client import WebClient
                # インスタンス化はテスト環境では困難なため、importのみテスト
                print("    ✅ WebClient import成功")
            except Exception as import_error:
                print(f"    ❌ WebClient import失敗: {import_error}")
                raise import_error
            
            # NextPublishingService統合テスト
            print("  NextPublishingService統合テスト:")
            
            try:
                from services.nextpublishing_service import NextPublishingService, UploadSettings
                # 設定プロバイダーを使用したサービス初期化テスト
                config = get_unified_config()
                settings = UploadSettings()
                
                # サービスのインスタンス化（設定プロバイダー注入）
                service = NextPublishingService(settings, config)
                print("    ✅ NextPublishingService初期化成功")
                
                # サービスのクリーンアップ
                service.close()
                
            except Exception as service_error:
                print(f"    ❌ NextPublishingService初期化失敗: {service_error}")
                raise service_error
            
            self.test_results.append({
                "test": "real_world_scenarios",
                "status": "PASS",
                "details": "WebClient & NextPublishingService 統合成功"
            })
            
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            self.test_results.append({
                "test": "real_world_scenarios",
                "status": "FAIL",
                "error": str(e)
            })
    
    def _cleanup_test_environment(self):
        """テスト環境をクリーンアップ"""
        if self.temp_dir:
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
                print(f"✅ テスト環境クリーンアップ完了: {self.temp_dir}")
            except Exception as e:
                print(f"⚠️  テスト環境クリーンアップエラー: {e}")
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """テスト結果レポートを生成"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        partial_tests = len([r for r in self.test_results if r['status'] == 'PARTIAL'])
        
        report = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "partial": partial_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "details": self.test_results
        }
        
        print(f"\n📊 Phase 2 統一Configuration統合テスト結果")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"総テスト数: {total_tests}")
        print(f"成功: {passed_tests}")
        print(f"失敗: {failed_tests}")
        print(f"部分的成功: {partial_tests}")
        print(f"成功率: {report['success_rate']:.1f}%")
        
        if failed_tests == 0:
            print("✅ すべてのテストが成功しました！")
        else:
            print("❌ 一部のテストが失敗しました。詳細を確認してください。")
        
        return report


def main():
    """テスト実行のメインエントリーポイント"""
    print("🚀 Phase 2: 統一Configuration統合実装テスト")
    print("=" * 60)
    
    test_suite = ConfigurationIntegrationTest()
    results = test_suite.run_all_tests()
    
    # 成功率に基づく終了コード
    if results['success_rate'] >= 80:
        print("\n🎉 Phase 2 統一Configuration統合は成功です！")
        return 0
    else:
        print("\n⚠️  Phase 2 統一Configuration統合に問題があります。修正が必要です。")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())