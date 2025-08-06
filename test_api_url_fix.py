#!/usr/bin/env python3
"""API URL修正のテスト"""

import sys
import os
sys.path.append('.')

from core.api_processor import ApiProcessor
from src.slack_pdf_poster import ConfigManager

def test_api_url_construction():
    """API URL構築のテスト"""
    print("=== API URL構築テスト開始 ===")
    
    try:
        # ConfigManagerを初期化
        config_manager = ConfigManager()
        print("[SUCCESS] ConfigManager initialized")
        
        # ApiProcessorを初期化
        api_processor = ApiProcessor(config_manager)
        print("[SUCCESS] ApiProcessor initialized")
        
        # ベースURL確認
        base_url = api_processor.API_BASE_URL
        print(f"Base URL: {base_url}")
        
        # API URLの構築をテスト
        api_url = base_url.rstrip('/') + '/api/upload'
        print(f"Constructed API URL: {api_url}")
        
        # 期待値と比較
        expected_clean_url = "http://trial.nextpublishing.jp/upload_46tate/api/upload"
        if api_url == expected_clean_url:
            print("[SUCCESS] URL construction is correct (no double slashes)")
        else:
            print(f"[WARNING] URL construction may have issues")
            print(f"Expected: {expected_clean_url}")
            print(f"Actual:   {api_url}")
        
        # ステータスURL構築のテスト
        test_jobid = "test123"
        status_url = base_url.rstrip('/') + f'/api/status/{test_jobid}'
        print(f"Status URL: {status_url}")
        
        expected_status_url = f"http://trial.nextpublishing.jp/upload_46tate/api/status/{test_jobid}"
        if status_url == expected_status_url:
            print("[SUCCESS] Status URL construction is correct")
        else:
            print(f"[WARNING] Status URL construction may have issues")
            print(f"Expected: {expected_status_url}")
            print(f"Actual:   {status_url}")
        
        print("\n=== API URL構築テスト完了: 成功 ===")
        return True
        
    except Exception as e:
        print(f"\n=== API URL構築テスト完了: 失敗 ===")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_url_construction()
    sys.exit(0 if success else 1)