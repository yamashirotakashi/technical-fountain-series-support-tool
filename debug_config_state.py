#!/usr/bin/env python3
"""ConfigManager設定状態のデバッグ"""

import sys
import os
sys.path.append('.')

from src.slack_pdf_poster import ConfigManager

def debug_config_state():
    """現在のConfigManager設定状態を詳細表示"""
    print("=== ConfigManager設定状態デバッグ ===")
    
    try:
        config_manager = ConfigManager()
        print("[SUCCESS] ConfigManager initialized")
        
        # API設定関連を詳しく確認
        print("\n--- API NextPublishing 関連設定 ---")
        print(f"api.nextpublishing.api_base_url: {config_manager.get('api.nextpublishing.api_base_url', 'NOT_SET')}")
        print(f"api.nextpublishing.base_url: {config_manager.get('api.nextpublishing.base_url', 'NOT_SET')}")
        print(f"defaults.api_base_url: {config_manager.get('defaults.api_base_url', 'NOT_SET')}")
        
        print("\n--- 環境変数確認 ---")
        print(f"NEXTPUB_API_BASE_URL: {os.getenv('NEXTPUB_API_BASE_URL', 'NOT_SET')}")
        print(f"NEXTPUB_BASE_URL: {os.getenv('NEXTPUB_BASE_URL', 'NOT_SET')}")
        
        print("\n--- NextPublishing API設定 ---")
        nextpub_config = config_manager.get_api_config('nextpublishing')
        print(f"NextPublishing API Config: {nextpub_config}")
        
        print("\n--- 全設定ダンプ ---")
        # ConfigManagerの全設定を表示（可能であれば）
        if hasattr(config_manager, 'config') or hasattr(config_manager, '_config'):
            config_attr = getattr(config_manager, 'config', None) or getattr(config_manager, '_config', None)
            if config_attr:
                import json
                print("Full config:")
                print(json.dumps(config_attr, indent=2, default=str))
        
        print("\n=== デバッグ完了 ===")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_config_state()