"""EXE環境での設定読み込み問題を診断"""

import json
import os
from pathlib import Path

def diagnose():
    """設定の読み込み状況を詳細に診断"""
    
    print("=== EXE環境設定診断ツール ===\n")
    
    # 1. ユーザーディレクトリの確認
    user_dir = Path.home() / '.techzip'
    print(f"1. ユーザーディレクトリ: {user_dir}")
    print(f"   存在: {user_dir.exists()}")
    
    # 2. settings.jsonの確認
    settings_file = user_dir / 'config' / 'settings.json'
    print(f"\n2. 設定ファイル: {settings_file}")
    print(f"   存在: {settings_file.exists()}")
    
    if settings_file.exists():
        # 設定を読み込む
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        # Google Sheets設定を表示
        if 'google_sheet' in settings:
            gs_config = settings['google_sheet']
            print(f"\n3. Google Sheets設定:")
            print(f"   sheet_id: {gs_config.get('sheet_id', 'なし')}")
            print(f"   credentials_path: {gs_config.get('credentials_path', 'なし')}")
            
            # 認証ファイルの存在確認
            creds_path = gs_config.get('credentials_path', '')
            if creds_path:
                # 相対パスの場合
                if not os.path.isabs(creds_path):
                    # config/ファイル名形式
                    if creds_path.startswith('config'):
                        full_path = user_dir / creds_path
                    else:
                        full_path = user_dir / 'config' / creds_path
                else:
                    full_path = Path(creds_path)
                
                print(f"\n4. 認証ファイルの確認:")
                print(f"   期待されるパス: {full_path}")
                print(f"   ファイル存在: {full_path.exists()}")
                
                # configディレクトリ内のJSONファイルを列挙
                config_dir = user_dir / 'config'
                print(f"\n5. configディレクトリ内のJSONファイル:")
                if config_dir.exists():
                    for json_file in config_dir.glob('*.json'):
                        print(f"   - {json_file.name} ({json_file.stat().st_size} bytes)")
    
    # 6. 環境変数の確認
    print(f"\n6. 環境変数:")
    print(f"   TECHZIP_IS_EXE: {os.environ.get('TECHZIP_IS_EXE', '未設定')}")
    print(f"   GOOGLE_SHEETS_CREDENTIALS_PATH: {os.environ.get('GOOGLE_SHEETS_CREDENTIALS_PATH', '未設定')}")
    
    # 7. 実行環境の確認
    print(f"\n7. 実行環境:")
    print(f"   現在のディレクトリ: {os.getcwd()}")
    print(f"   スクリプトの場所: {__file__}")
    
    # 8. Pythonパスの確認
    import sys
    print(f"\n8. Pythonパス:")
    for i, path in enumerate(sys.path[:5]):  # 最初の5つだけ表示
        print(f"   [{i}] {path}")

if __name__ == "__main__":
    diagnose()
    print("\n診断完了。")
    input("Enterキーを押して終了...")