"""EXE環境での設定キャッシュ問題を修正"""

import json
from pathlib import Path
import os

def fix_config_cache():
    """設定ファイルのキャッシュ問題を修正"""
    
    # ユーザーディレクトリの設定ファイルを確認
    user_dir = Path.home() / '.techzip'
    settings_file = user_dir / 'config' / 'settings.json'
    
    print(f"設定ファイル: {settings_file}")
    
    if settings_file.exists():
        # 現在の設定を読み込み
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        print("\n現在の設定:")
        if 'google_sheet' in settings:
            print(f"  sheet_id: {settings['google_sheet'].get('sheet_id', 'なし')}")
            print(f"  credentials_path: {settings['google_sheet'].get('credentials_path', 'なし')}")
        
        # パスが相対パスであることを確認
        if 'google_sheet' in settings and 'credentials_path' in settings['google_sheet']:
            creds_path = settings['google_sheet']['credentials_path']
            
            # 絶対パスの場合は相対パスに変換
            if os.path.isabs(creds_path):
                filename = os.path.basename(creds_path)
                settings['google_sheet']['credentials_path'] = f"config/{filename}"
                
                # 設定を保存
                with open(settings_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
                
                print(f"\n✅ 絶対パスを相対パスに変換しました: config/{filename}")
            else:
                print(f"\n✅ すでに相対パスです: {creds_path}")
        
        # 認証ファイルの存在確認
        if 'google_sheet' in settings and 'credentials_path' in settings['google_sheet']:
            creds_relative = settings['google_sheet']['credentials_path']
            creds_full = user_dir / creds_relative.replace('\\', '/')
            
            if creds_full.exists():
                print(f"\n✅ 認証ファイルが存在します: {creds_full}")
            else:
                print(f"\n❌ 認証ファイルが存在しません: {creds_full}")
                
                # 代替パスを確認
                alt_path = user_dir / 'config' / os.path.basename(creds_relative)
                if alt_path.exists():
                    print(f"   代替パスで発見: {alt_path}")
    else:
        print("❌ 設定ファイルが存在しません")

if __name__ == "__main__":
    print("=== EXE設定キャッシュ修正ツール ===\n")
    fix_config_cache()
    print("\n完了しました。")
    input("Enterキーを押して終了...")