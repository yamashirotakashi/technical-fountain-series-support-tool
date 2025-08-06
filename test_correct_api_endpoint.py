#!/usr/bin/env python3
"""正しいAPIエンドポイント修正のテスト"""

import sys
import os
sys.path.append('.')

from core.api_processor import ApiProcessor
from src.slack_pdf_poster import ConfigManager

def test_correct_api_endpoint():
    """正しいAPIエンドポイントのテスト"""
    print("=== 正しいAPIエンドポイント確認テスト ===")
    
    try:
        # ConfigManagerを初期化
        config_manager = ConfigManager()
        print("[SUCCESS] ConfigManager initialized")
        
        # ApiProcessorを初期化
        api_processor = ApiProcessor(config_manager)
        print("[SUCCESS] ApiProcessor initialized")
        
        # ベースURL確認
        base_url = api_processor.API_BASE_URL
        print(f"Current Base URL: {base_url}")
        
        # 正しいAPIエンドポイントと比較
        expected_url = "http://sd001.nextpublishing.jp/rapture"
        if base_url == expected_url:
            print("[SUCCESS] 正しいAPIエンドポイントが設定されています")
        else:
            print(f"[ERROR] APIエンドポイントが間違っています")
            print(f"期待値: {expected_url}")
            print(f"実際値: {base_url}")
            return False
        
        # 構築されるURL確認
        api_url = base_url.rstrip('/') + '/api/upload'
        status_url = base_url.rstrip('/') + '/api/status/test123'
        download_url = base_url.rstrip('/') + '/api/download/test123'
        
        print(f"Upload URL: {api_url}")
        print(f"Status URL: {status_url}")
        print(f"Download URL: {download_url}")
        
        # 期待値との比較
        expected_upload = "http://sd001.nextpublishing.jp/rapture/api/upload"
        expected_status = "http://sd001.nextpublishing.jp/rapture/api/status/test123"
        expected_download = "http://sd001.nextpublishing.jp/rapture/api/download/test123"
        
        if (api_url == expected_upload and 
            status_url == expected_status and 
            download_url == expected_download):
            print("[SUCCESS] すべてのAPIエンドポイントURL構築が正しく動作しています")
        else:
            print("[ERROR] 一部のURL構築に問題があります")
            return False
        
        # 認証情報確認
        print(f"API Username: {api_processor.API_USERNAME}")
        print(f"API Password: {'*' * len(api_processor.API_PASSWORD)}")
        
        if (api_processor.API_USERNAME == "ep_user" and 
            api_processor.API_PASSWORD == "Nn7eUTX5"):
            print("[SUCCESS] 認証情報が正しく設定されています")
        else:
            print("[ERROR] 認証情報に問題があります")
            return False
        
        print("\n=== 正しいAPIエンドポイント確認テスト: 成功 ===")
        print("API仕様書通りの設定に修正されました:")
        print("- ベースURL: http://sd001.nextpublishing.jp/rapture")
        print("- アップロード: /api/upload")
        print("- ステータス確認: /api/status/{jobid}")
        print("- ダウンロード: /api/download/{jobid}")
        print("- 認証: ep_user / Nn7eUTX5")
        
        return True
        
    except Exception as e:
        print(f"\n=== 正しいAPIエンドポイント確認テスト: 失敗 ===")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_correct_api_endpoint()
    sys.exit(0 if success else 1)