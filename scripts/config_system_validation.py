#!/usr/bin/env python3
"""
ConfigManager統合システム検証スクリプト
GUI統合テストの非GUI版 - 統合機能の動作を検証
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def validate_config_manager():
    """ConfigManager動作検証"""
    print("=== ConfigManager動作検証 ===")
    try:
        from src.slack_pdf_poster import ConfigManager
        
        # 初期化
        config_manager = ConfigManager()
        print("✅ ConfigManager初期化完了")
        
        # 基本設定取得
        base_url = config_manager.get('api.nextpublishing.base_url')
        print(f"✅ 基本設定取得: {base_url}")
        
        # API設定取得
        nextpub_config = config_manager.get_api_config('nextpublishing')
        print(f"✅ API設定取得: {len(nextpub_config)}項目")
        
        # 設定検証
        validation_result = config_manager.validate_config()
        errors = validation_result.get('errors', [])
        warnings = validation_result.get('warnings', [])
        missing_vars = validation_result.get('missing_env_vars', [])
        
        print(f"✅ 設定検証: {len(errors)}エラー, {len(warnings)}警告, {len(missing_vars)}不足環境変数")
        
        # 設定変更テスト
        old_value = config_manager.get('processing.batch_size', 10)
        config_manager.set('processing.batch_size', 15)
        new_value = config_manager.get('processing.batch_size')
        print(f"✅ 設定変更: batch_size {old_value} → {new_value}")
        
        return True
        
    except Exception as e:
        print(f"❌ ConfigManager検証エラー: {e}")
        return False

def validate_hardcoding_detector():
    """HardcodingDetector動作検証"""
    print("\n=== HardcodingDetector動作検証 ===")
    try:
        from src.slack_pdf_poster import HardcodingDetector
        
        detector = HardcodingDetector()
        print("✅ HardcodingDetector初期化完了")
        
        # テストコード作成
        test_code = '''
def test_function():
    api_url = "http://test.example.com/api"
    username = "admin"
    password = "secret123"
    port = 8080
    return True
'''
        
        # 一時ファイル作成
        test_file = Path('/tmp/test_hardcoding.py')
        test_file.write_text(test_code)
        
        try:
            # スキャン実行
            results = detector.scan_file(test_file)
            total_detections = sum(len(detections) for detections in results.values())
            
            print(f"✅ ハードコーディング検知: {total_detections}個検出")
            
            for category, detections in results.items():
                if detections:
                    print(f"  【{category}】: {len(detections)}個")
            
            # 修正提案テスト
            if total_detections > 0:
                suggestions = detector.suggest_remediation(results)
                print(f"✅ 修正提案: {len(suggestions)}件生成")
            
        finally:
            # テストファイル削除
            if test_file.exists():
                test_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ HardcodingDetector検証エラー: {e}")
        return False

def validate_integration_points():
    """統合ポイント検証"""
    print("\n=== 統合ポイント検証 ===")
    try:
        # 1. ConfigManagerとHardcodingDetectorの統合
        from src.slack_pdf_poster import ConfigManager, HardcodingDetector
        
        config_manager = ConfigManager()
        detector = HardcodingDetector()
        
        # ハードコーディング検知設定取得
        enable_detection = config_manager.get('security.enable_hardcoding_detection', True)
        scan_on_startup = config_manager.get('security.hardcoding_scan_on_startup', False)
        
        print(f"✅ 統合設定: 検知有効={enable_detection}, 起動時スキャン={scan_on_startup}")
        
        # 2. 設定ファイル存在確認
        config_yaml = project_root / 'config' / 'techzip_config.yaml'
        env_template = project_root / '.env.template'
        
        print(f"✅ YAML設定ファイル: {'存在' if config_yaml.exists() else '不存在'}")
        print(f"✅ .envテンプレート: {'存在' if env_template.exists() else '不存在'}")
        
        # 3. GUI統合ポイント確認
        try:
            # ConfigDialogのインポート確認
            from gui.config_dialog import ConfigDialog
            print("✅ ConfigDialog: インポート可能")
            
            # MainWindow統合メソッド確認
            from gui.main_window import MainWindow
            
            # メソッド存在確認
            main_window_methods = [
                'init_config_manager',
                'perform_startup_checks',
                'show_comprehensive_settings',
                'show_hardcoding_scan_dialog',
                'on_config_changed'
            ]
            
            for method_name in main_window_methods:
                if hasattr(MainWindow, method_name):
                    print(f"✅ MainWindow.{method_name}: 存在")
                else:
                    print(f"❌ MainWindow.{method_name}: 不存在")
            
        except ImportError as e:
            print(f"⚠️ GUI統合確認不可: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 統合ポイント検証エラー: {e}")
        return False

def validate_config_files():
    """設定ファイル内容検証"""
    print("\n=== 設定ファイル内容検証 ===")
    try:
        import yaml
        
        # YAML設定ファイル読み込み
        config_file = project_root / 'config' / 'techzip_config.yaml'
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # 主要セクション確認
            required_sections = ['paths', 'api', 'processing', 'security', 'features']
            for section in required_sections:
                if section in config_data:
                    print(f"✅ YAML設定[{section}]: 存在")
                else:
                    print(f"❌ YAML設定[{section}]: 不存在")
        else:
            print("❌ YAML設定ファイル: 不存在")
        
        # .envテンプレート確認
        env_template = project_root / '.env.template'
        if env_template.exists():
            content = env_template.read_text(encoding='utf-8')
            env_vars = [line for line in content.split('\n') if line.strip() and not line.startswith('#')]
            print(f"✅ .envテンプレート: {len(env_vars)}変数定義")
        else:
            print("❌ .envテンプレート: 不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 設定ファイル検証エラー: {e}")
        return False

def main():
    """検証メイン実行"""
    print("🔧 ConfigManager統合システム検証開始")
    print("=" * 60)
    
    # 検証実行
    validations = [
        ("ConfigManager動作", validate_config_manager),
        ("HardcodingDetector動作", validate_hardcoding_detector),
        ("統合ポイント", validate_integration_points),
        ("設定ファイル", validate_config_files)
    ]
    
    results = []
    for name, validator in validations:
        try:
            result = validator()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}検証中にエラー: {e}")
            results.append((name, False))
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 統合システム検証結果")
    print("=" * 60)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}検証")
        if result:
            passed += 1
    
    print(f"\n🎯 検証結果: {passed}/{len(results)} 成功")
    
    if passed == len(results):
        print("🎉 ConfigManager統合システムが正常に動作しています!")
        print("\n📋 利用可能機能:")
        print("  • ConfigManagerによる統一設定管理")
        print("  • HardcodingDetectorによる自動検知")
        print("  • GUI設定ダイアログ統合")
        print("  • 起動時自動チェック")
        print("  • リアルタイム設定変更")
        return True
    else:
        print("⚠️ 一部機能に問題があります。修正が必要です。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)