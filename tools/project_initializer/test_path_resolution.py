#!/usr/bin/env python3
"""
パス解決テストスクリプト
開発環境とEXE環境でのパス解決をテスト
"""

import sys
from pathlib import Path

# path_resolverをインポート
try:
    from path_resolver import get_config_path, get_exe_dir, print_debug_paths
    print("✅ path_resolver module loaded successfully")
except ImportError as e:
    print(f"❌ Failed to import path_resolver: {e}")
    sys.exit(1)

def test_path_resolution():
    """パス解決のテスト"""
    print("=" * 60)
    print("Path Resolution Test")
    print("=" * 60)
    
    # デバッグ情報表示
    print_debug_paths()
    
    # 具体的なファイルパステスト
    print("\n" + "=" * 60)
    print("File Path Tests")
    print("=" * 60)
    
    # service_account.json パス
    service_account_path = get_config_path("service_account.json")
    print(f"Service Account Path: {service_account_path}")
    print(f"Service Account Exists: {service_account_path.exists()}")
    
    if service_account_path.exists():
        print(f"  - File Size: {service_account_path.stat().st_size} bytes")
        try:
            # ファイルの最初の数行を読んでみる（JSONファイルかチェック）
            with open(service_account_path, 'r') as f:
                first_line = f.readline().strip()
                if first_line.startswith('{'):
                    print("  - ✅ Valid JSON format detected")
                else:
                    print("  - ⚠️ File doesn't appear to be JSON")
        except Exception as e:
            print(f"  - ❌ Error reading file: {e}")
    
    # 親ディレクトリ config の存在確認
    exe_dir = get_exe_dir()
    parent_config = exe_dir.parent / "config"
    if parent_config.exists():
        print(f"\nParent Config Directory: {parent_config}")
        print(f"Parent Config Contents:")
        for item in parent_config.iterdir():
            print(f"  - {item.name} ({'file' if item.is_file() else 'dir'})")
    
    # 開発環境特有のパス確認
    if not getattr(sys, 'frozen', False):
        dev_config = Path(__file__).parent.parent.parent / "config"
        print(f"\nDev Config Path: {dev_config}")
        print(f"Dev Config Exists: {dev_config.exists()}")
        if dev_config.exists():
            print("Dev Config Contents:")
            for item in dev_config.iterdir():
                print(f"  - {item.name}")

if __name__ == "__main__":
    test_path_resolution()