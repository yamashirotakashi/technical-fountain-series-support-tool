#!/usr/bin/env python3
"""
設定値をデバッグ表示するスクリプト
"""

from core.configuration_provider import get_unified_config

def debug_config():
    config = get_unified_config()
    
    print("=== 設定デバッグ ===")
    print(f"Provider info: {config.get_provider_info()}")
    print()
    
    keys_to_check = [
        "api.nextpublishing.base_url",
        "api.nextpublishing.gmail_base_url", 
        "api.nextpublishing.username",
        "api.nextpublishing.password"
    ]
    
    for key in keys_to_check:
        value = config.get(key, "NOT SET")
        print(f"{key}: {value}")
    
    print()
    print("API section:")
    api_section = config.get_section("api")
    print(api_section)

if __name__ == "__main__":
    debug_config()