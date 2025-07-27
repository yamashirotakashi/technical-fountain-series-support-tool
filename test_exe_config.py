"""EXE環境でのConfig動作を直接テスト"""

import sys
import os
from pathlib import Path
import json

print("=== EXE環境 Config直接テスト ===\n")

# 基本情報
print("1. 実行環境:")
print(f"   frozen: {getattr(sys, 'frozen', False)}")
print(f"   実行ファイル: {sys.executable}")
print(f"   現在のディレクトリ: {os.getcwd()}")

# ユーザーディレクトリの設定ファイルを直接読む
print("\n2. 設定ファイルの直接読み込み:")
user_home = Path.home()
settings_path = user_home / '.techzip' / 'config' / 'settings.json'

if settings_path.exists():
    with open(settings_path, 'r', encoding='utf-8') as f:
        settings = json.load(f)
    
    gs_config = settings.get('google_sheet', {})
    creds_path = gs_config.get('credentials_path', 'なし')
    print(f"   settings.json の credentials_path: {creds_path}")
    
    # パスの解析
    if creds_path and creds_path != 'なし':
        print(f"\n3. パス解析:")
        print(f"   元のパス: {creds_path}")
        print(f"   絶対パスか: {os.path.isabs(creds_path)}")
        print(f"   'config'で始まるか: {creds_path.startswith('config')}")
        
        # 実際のファイルパス
        if not os.path.isabs(creds_path):
            if creds_path.startswith('config'):
                full_path = user_home / '.techzip' / creds_path
            else:
                full_path = user_home / '.techzip' / 'config' / creds_path
        else:
            full_path = Path(creds_path)
        
        print(f"   完全パス: {full_path}")
        print(f"   ファイル存在: {full_path.exists()}")
        
        # ファイル名のみ
        filename = Path(creds_path).name
        print(f"   ファイル名: {filename}")
        
        # 期待されるファイルの確認
        expected_path = user_home / '.techzip' / 'config' / filename
        print(f"   期待されるパス: {expected_path}")
        print(f"   期待されるパスに存在: {expected_path.exists()}")
else:
    print(f"   設定ファイルが存在しません: {settings_path}")

# デフォルト値の問題を確認
print("\n4. デフォルト値の確認:")
print(f"   'google_service_account.json'が含まれているか確認")

# config.pyのデフォルト値をチェック
default_path = Path("config/google_service_account.json")
print(f"   デフォルトPath: {default_path}")
print(f"   デフォルトPathの文字列: {str(default_path)}")

print("\n完了。")
input("Enterキーを押して終了...")