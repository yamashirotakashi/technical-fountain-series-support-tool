#!/usr/bin/env python3
"""
Gmail API モード HTTP 404 エラー修正のテストスクリプト
処理方式に応じた正しいベースURL選択をテストする
"""

import sys
from pathlib import Path
from services.nextpublishing_service import NextPublishingService, UploadSettings
from core.configuration_provider import get_unified_config

def test_url_selection():
    """各処理方式で正しいベースURLが選択されることをテスト"""
    
    print("=== Gmail API 404エラー修正テスト ===")
    print()
    
    config_provider = get_unified_config()
    settings = UploadSettings()
    
    modes = [
        ("api", "http://sd001.nextpublishing.jp/rapture"),
        ("traditional", "http://trial.nextpublishing.jp/rapture"),
        ("gmail_api", "http://trial.nextpublishing.jp/rapture")
    ]
    
    for mode, expected_url in modes:
        print(f"テスト: {mode} モード")
        try:
            service = NextPublishingService(settings, config_provider, process_mode=mode)
            actual_url = service.base_url
            
            print(f"  予想URL: {expected_url}")
            print(f"  実際URL: {actual_url}")
            
            if actual_url == expected_url:
                print(f"  ✅ PASS: 正しいURLが選択されました")
            else:
                print(f"  ❌ FAIL: URLが一致しません")
                return False
            
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            return False
        
        print()
    
    return True

def test_api_endpoint_construction():
    """API エンドポイントの構築をテスト"""
    
    print("=== API エンドポイント構築テスト ===")
    print()
    
    config_provider = get_unified_config()
    settings = UploadSettings()
    
    # Gmail API モードでサービスを初期化
    service = NextPublishingService(settings, config_provider, process_mode="gmail_api")
    
    # API エンドポイントを構築（実際の upload_single_file 内の処理と同様）
    api_endpoint = f"{service.base_url}/api/upload"
    expected_endpoint = "http://trial.nextpublishing.jp/rapture/api/upload"
    
    print(f"Gmail APIモードのエンドポイント:")
    print(f"  予想: {expected_endpoint}")
    print(f"  実際: {api_endpoint}")
    
    if api_endpoint == expected_endpoint:
        print(f"  ✅ PASS: 正しいエンドポイントが構築されました")
        return True
    else:
        print(f"  ❌ FAIL: エンドポイントが一致しません")
        return False

def test_authentication():
    """Basic認証の設定をテスト"""
    
    print("=== Basic認証設定テスト ===")
    print()
    
    config_provider = get_unified_config()
    settings = UploadSettings()
    
    service = NextPublishingService(settings, config_provider, process_mode="gmail_api")
    
    # Basic認証の設定を確認
    if hasattr(service.session, 'auth') and service.session.auth:
        username = service.session.auth.username
        password = service.session.auth.password
        print(f"認証設定:")
        print(f"  Username: {username}")
        print(f"  Password: {'*' * len(password) if password else 'None'}")
        print(f"  ✅ PASS: Basic認証が正しく設定されています")
        return True
    else:
        print(f"  ❌ FAIL: Basic認証が設定されていません")
        return False

def main():
    """メインテスト実行"""
    print("Technical Fountain Series Support Tool")
    print("Gmail API モード HTTP 404 エラー修正テスト")
    print("=" * 60)
    print()
    
    tests_passed = 0
    total_tests = 3
    
    # テスト1: URL選択
    if test_url_selection():
        tests_passed += 1
    
    # テスト2: エンドポイント構築
    if test_api_endpoint_construction():
        tests_passed += 1
    
    # テスト3: 認証設定
    if test_authentication():
        tests_passed += 1
    
    # 結果サマリー
    print()
    print("=" * 60)
    print(f"テスト結果: {tests_passed}/{total_tests} 通過")
    
    if tests_passed == total_tests:
        print("✅ 全てのテストが通過しました。修正が正しく適用されています。")
        return 0
    else:
        print("❌ 一部のテストが失敗しました。修正を確認してください。")
        return 1

if __name__ == "__main__":
    sys.exit(main())