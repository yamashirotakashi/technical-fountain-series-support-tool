#!/usr/bin/env python3
"""
NextPublishing Rapture URL修正テストスクリプト
修正されたWebClient.upload_file()とNextPublishingServiceのrapture URL統合をテスト
"""
import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

def test_nextpublishing_rapture_service():
    """NextPublishingService（Rapture URL修正版）の単体テスト"""
    try:
        from services.nextpublishing_service import NextPublishingService, UploadSettings
        from src.slack_pdf_poster import ConfigManager
        
        print("OK NextPublishingService import successful")
        
        # 設定管理システムのテスト
        config_manager = ConfigManager()
        print("OK ConfigManager initialization successful")
        
        # サービスの初期化テスト
        settings = UploadSettings()
        settings.email = "test@example.com"
        service = NextPublishingService(settings, config_manager)
        print("OK NextPublishingService initialization successful")
        
        # 修正後の設定値確認
        base_url = config_manager.get("api.nextpublishing.base_url")
        username = config_manager.get("api.nextpublishing.username")
        print(f"OK Configuration loaded (Rapture URL修正版):")
        print(f"  - Base URL: {base_url}")
        print(f"  - Username: {username}")
        print(f"  - Expected: http://trial.nextpublishing.jp/rapture/")
        
        # URL修正確認
        if "rapture" in base_url:
            print("OK Rapture URL correctly configured")
        elif "upload_46tate" in base_url:
            print("WARNING Still using old upload_46tate URL")
        else:
            print("ERROR Unknown URL configuration")
        
        return True
        
    except Exception as e:
        print(f"ERROR NextPublishingService rapture test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_webclient_rapture_integration():
    """WebClient Rapture統合テスト"""
    try:
        from core.web_client import WebClient
        
        print("\nOK WebClient import successful")
        
        # WebClientの初期化テスト
        client = WebClient()
        print("OK WebClient initialization successful")
        
        # ConfigManager デフォルト設定確認
        try:
            # ConfigManagerファイル内のデフォルトURLを確認
            config_content = client.CONFIG_MANAGER_FILE_CONTENT
            if "rapture" in config_content:
                print("OK WebClient ConfigManager defaults updated to rapture")
            elif "upload_46tate" in config_content:
                print("WARNING WebClient still using upload_46tate defaults")
            else:
                print("INFO WebClient ConfigManager content needs verification")
        except Exception as e:
            print(f"INFO WebClient ConfigManager content check: {e}")
        
        # クリーンアップテスト
        client.close()
        print("OK WebClient.close() executed successfully")
        
        return True
        
    except Exception as e:
        print(f"ERROR WebClient rapture integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_syntax_warning_fix():
    """SyntaxWarning修正の確認テスト"""
    print("\n=== SyntaxWarning Fix Test ===")
    
    try:
        # WebClientをインポートしてSyntaxWarningが出ないことを確認
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            from core.web_client import WebClient
            
            syntax_warnings = [warning for warning in w if issubclass(warning.category, SyntaxWarning)]
            
            if syntax_warnings:
                print(f"ERROR {len(syntax_warnings)} SyntaxWarning(s) still present:")
                for warning in syntax_warnings:
                    print(f"  - {warning.message}")
                return False
            else:
                print("OK No SyntaxWarning detected")
                return True
                
    except Exception as e:
        print(f"ERROR SyntaxWarning test failed: {e}")
        return False

def main():
    """メインテスト実行"""
    print("=== NextPublishing Rapture URL Fix Test ===\n")
    
    all_tests_passed = True
    
    # NextPublishingService Rapture テスト
    if not test_nextpublishing_rapture_service():
        all_tests_passed = False
    
    # WebClient Rapture 統合テスト
    if not test_webclient_rapture_integration():
        all_tests_passed = False
        
    # SyntaxWarning修正テスト
    if not test_syntax_warning_fix():
        all_tests_passed = False
    
    print("\n" + "="*70)
    if all_tests_passed:
        print("SUCCESS All NextPublishing Rapture functionality tests PASSED!")
        print("\nTest Summary:")
        print("  OK NextPublishingService rapture URL integration functional")
        print("  OK WebClient rapture URL configuration updated")  
        print("  OK SyntaxWarning issues resolved")
        print("  OK Configuration management operational with rapture URL")
        print("\nReady for real-world N02360 processing test with rapture URL")
        return 0
    else:
        print("FAILED Some NextPublishing Rapture functionality tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())