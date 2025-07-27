"""Configクラスの問題を詳細にデバッグ"""

import sys
import os
from pathlib import Path
import json

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

print("=== Config問題デバッグツール ===\n")

# 1. 環境確認
print("1. 環境確認:")
print(f"   Python実行ファイル: {sys.executable}")
print(f"   frozen属性: {getattr(sys, 'frozen', False)}")
print(f"   TECHZIP_IS_EXE: {os.environ.get('TECHZIP_IS_EXE', '未設定')}")

# 2. PathResolverの確認
try:
    from utils.path_resolver import PathResolver
    print(f"\n2. PathResolver:")
    print(f"   is_exe_environment: {PathResolver.is_exe_environment()}")
    print(f"   get_user_dir: {PathResolver.get_user_dir()}")
    print(f"   get_config_path: {PathResolver.get_config_path()}")
except Exception as e:
    print(f"\n2. PathResolver エラー: {e}")

# 3. 設定ファイルの直接読み込み
print(f"\n3. 設定ファイルの直接読み込み:")
user_dir = Path.home() / '.techzip'
settings_file = user_dir / 'config' / 'settings.json'

if settings_file.exists():
    with open(settings_file, 'r', encoding='utf-8') as f:
        settings = json.load(f)
    
    if 'google_sheet' in settings:
        print(f"   sheet_id: {settings['google_sheet'].get('sheet_id', 'なし')}")
        print(f"   credentials_path: {settings['google_sheet'].get('credentials_path', 'なし')}")
else:
    print(f"   設定ファイルが存在しません: {settings_file}")

# 4. Configクラスの確認
print(f"\n4. Configクラスの動作確認:")
try:
    # 環境変数を初期化
    from utils.env_manager import EnvManager
    EnvManager.initialize()
    
    # Configクラスをインポート
    from utils.config import Config, get_config, reset_config
    
    # リセットを試みる
    print("   reset_config()を実行...")
    reset_config()
    
    # 新しいインスタンスを作成
    print("   新しいConfigインスタンスを作成...")
    config = get_config()
    
    # 設定値を確認
    print(f"   config.config_path: {config.config_path}")
    print(f"   config.get('google_sheet.sheet_id'): {config.get('google_sheet.sheet_id')}")
    print(f"   config.get('google_sheet.credentials_path'): {config.get('google_sheet.credentials_path')}")
    
    # get_credentials_pathメソッドの確認
    print(f"\n5. get_credentials_pathメソッド:")
    creds_path = config.get_credentials_path()
    print(f"   返り値: {creds_path}")
    if creds_path:
        print(f"   存在: {creds_path.exists()}")
    
except Exception as e:
    print(f"   エラー: {e}")
    import traceback
    traceback.print_exc()

# 6. モジュールの場所確認
print(f"\n6. モジュールの場所:")
try:
    import utils.config
    print(f"   utils.config: {utils.config.__file__}")
    
    # Configクラスのソースコードの一部を確認
    import inspect
    get_credentials_path_source = inspect.getsource(config.get_credentials_path)
    print(f"\n   get_credentials_pathメソッドのソース（最初の5行）:")
    for i, line in enumerate(get_credentials_path_source.split('\n')[:5]):
        print(f"   {i+1}: {line}")
        
except Exception as e:
    print(f"   エラー: {e}")

print("\nデバッグ完了。")
input("Enterキーを押して終了...")