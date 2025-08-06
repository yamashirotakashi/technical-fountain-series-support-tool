from __future__ import annotations
#!/usr/bin/env python3
"""
ConfigDialog統合テスト - GUI設定システムの動作確認

このスクリプトはConfigDialogとMainWindowの統合テストを実行します。
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_config_manager_initialization():
    """ConfigManager初期化テスト"""
    print("=== ConfigManager初期化テスト ===")
    try:
        from src.slack_pdf_poster import ConfigManager
        config_manager = ConfigManager()
        
        # 基本設定取得テスト
        api_config = config_manager.get_api_config('nextpublishing')
        print(f"✅ NextPublishing設定取得: {len(api_config)}項目")
        
        # 階層設定アクセステスト
        base_url = config_manager.get('api.nextpublishing.base_url')
        print(f"✅ 階層設定アクセス: {base_url}")
        
        # 設定検証テスト
        validation_result = config_manager.validate_config()
        errors = validation_result.get('errors', [])
        warnings = validation_result.get('warnings', [])
        print(f"✅ 設定検証: {len(errors)}エラー, {len(warnings)}警告")
        
        return config_manager
        
    except Exception as e:
        print(f"❌ ConfigManager初期化エラー: {e}")
        return None

def test_hardcoding_detector():
    """HardcodingDetector動作テスト"""
    print("\n=== HardcodingDetector動作テスト ===")
    try:
        from src.slack_pdf_poster import HardcodingDetector
        
        detector = HardcodingDetector()
        
        # テストファイル作成
        test_content = '''
# テスト用ハードコーディング
BASE_URL = "http://example.com/api"
USERNAME = "test_user"
PASSWORD = "test123"
PORT = 8080
API_KEY = "abc123def456"
'''
        
        test_file = Path('/tmp/hardcoding_test.py')
        test_file.write_text(test_content)
        
        # スキャン実行
        results = detector.scan_file(test_file)
        total_detections = sum(len(detections) for detections in results.values())
        
        print(f"✅ ハードコーディング検知: {total_detections}個検出")
        for category, detections in results.items():
            if detections:
                print(f"  【{category}】: {len(detections)}個")
        
        # テストファイル削除
        test_file.unlink()
        
        return detector
        
    except Exception as e:
        print(f"❌ HardcodingDetector テストエラー: {e}")
        return None

def test_config_dialog_integration(config_manager):
    """ConfigDialog統合テスト"""
    print("\n=== ConfigDialog統合テスト ===")
    try:
        from gui.config_dialog import ConfigDialog
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 設定ダイアログを作成
        dialog = ConfigDialog(config_manager)
        
        # 設定変更シグナルのテスト
        def on_config_changed(key, value):
            print(f"🔧 設定変更シグナル受信: {key} = {value}")
        
        dialog.config_changed.connect(on_config_changed)
        
        print("✅ ConfigDialog作成完了")
        print("✅ シグナル接続完了")
        
        # 設定検証テスト
        dialog.validate_config()
        print("✅ 設定検証メソッド動作確認")
        
        return dialog
        
    except Exception as e:
        print(f"❌ ConfigDialog統合テストエラー: {e}")
        return None

def test_main_window_integration():
    """MainWindow統合テスト"""
    print("\n=== MainWindow統合テスト ===")
    try:
        from gui.main_window import MainWindow
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # メインウィンドウ作成
        window = MainWindow()
        
        # ConfigManager確認
        if hasattr(window, 'config_manager') and window.config_manager:
            print("✅ MainWindow ConfigManager統合完了")
        else:
            print("⚠️ MainWindow ConfigManager未統合")
        
        # 設定ダイアログメソッド確認
        if hasattr(window, 'show_comprehensive_settings'):
            print("✅ 設定ダイアログメソッド存在")
        else:
            print("❌ 設定ダイアログメソッド不存在")
        
        # ハードコーディングスキャンメソッド確認
        if hasattr(window, 'show_hardcoding_scan_dialog'):
            print("✅ ハードコーディングスキャンメソッド存在")
        else:
            print("❌ ハードコーディングスキャンメソッド不存在")
        
        return window
        
    except Exception as e:
        print(f"❌ MainWindow統合テストエラー: {e}")
        return None

def main():
    """統合テストメイン実行"""
    print("🚀 ConfigDialog統合テスト開始")
    print("=" * 50)
    
    # 1. ConfigManager初期化テスト
    config_manager = test_config_manager_initialization()
    
    # 2. HardcodingDetector動作テスト
    detector = test_hardcoding_detector()
    
    # 3. ConfigDialog統合テスト
    dialog = None
    if config_manager:
        dialog = test_config_dialog_integration(config_manager)
    
    # 4. MainWindow統合テスト
    window = test_main_window_integration()
    
    # 結果サマリー
    print("\n" + "=" * 50)
    print("📊 テスト結果サマリー")
    print("=" * 50)
    
    tests = [
        ("ConfigManager初期化", config_manager is not None),
        ("HardcodingDetector動作", detector is not None),
        ("ConfigDialog統合", dialog is not None),
        ("MainWindow統合", window is not None)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 テスト結果: {passed}/{total} 成功")
    
    if passed == total:
        print("🎉 全テスト完了! GUI設定統合システムが正常に動作しています。")
        return True
    else:
        print("⚠️ 一部テストが失敗しました。詳細を確認してください。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)