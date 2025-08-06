#!/usr/bin/env python3
"""API設定を正しい値にリセット"""

import sys
import os
sys.path.append('.')

from src.slack_pdf_poster import ConfigManager

def reset_api_config():
    """API設定をリセットして正しい値を設定"""
    print("=== API設定リセット開始 ===")
    
    try:
        config_manager = ConfigManager()
        print("[SUCCESS] ConfigManager initialized")
        
        # 現在の設定を表示
        print(f"現在のAPI Base URL: {config_manager.get('api.nextpublishing.base_url', 'NOT_SET')}")
        
        # 正しいAPI設定を強制的に適用
        correct_api_settings = {
            'api.nextpublishing.base_url': 'http://sd001.nextpublishing.jp/rapture',
            'api.nextpublishing.username': 'ep_user',
            'api.nextpublishing.password': 'Nn7eUTX5',
            'api.nextpublishing.timeout': 60,
            'api.nextpublishing.review_endpoint': 'do_download_review',
            'api.nextpublishing.epub_endpoint': 'do_download_epub',
            'api.nextpublishing.gcf_endpoint': 'do_download_gcf',
        }
        
        # 設定を一つずつ適用
        for key, value in correct_api_settings.items():
            config_manager.set(key, value)
            print(f"設定適用: {key} = {value}")
        
        # 設定後の値を確認
        print("\n--- 設定後の確認 ---")
        for key in correct_api_settings.keys():
            current_value = config_manager.get(key)
            print(f"{key}: {current_value}")
        
        # ApiProcessorで使用される値を確認
        from core.api_processor import ApiProcessor
        api_processor = ApiProcessor(config_manager)
        print(f"\nApiProcessorのベースURL: {api_processor.API_BASE_URL}")
        
        if api_processor.API_BASE_URL == 'http://sd001.nextpublishing.jp/rapture':
            print("[SUCCESS] API設定が正しく適用されました！")
        else:
            print(f"[ERROR] まだ正しくありません: {api_processor.API_BASE_URL}")
            return False
        
        print("\n=== API設定リセット完了: 成功 ===")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = reset_api_config()
    sys.exit(0 if success else 1)