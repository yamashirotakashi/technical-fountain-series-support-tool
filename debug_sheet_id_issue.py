"""Google Sheet ID問題の詳細デバッグ"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

print("=== Google Sheet ID デバッグ ===\n")

# 1. 環境変数の確認
print("1. 環境変数:")
print(f"   GOOGLE_SHEETS_ID: {os.environ.get('GOOGLE_SHEETS_ID', '未設定')}")
print(f"   TECHZIP_IS_EXE: {os.environ.get('TECHZIP_IS_EXE', '未設定')}")

# 2. PathResolverの動作確認
from utils.path_resolver import PathResolver
print(f"\n2. PathResolver:")
print(f"   is_exe_environment: {PathResolver.is_exe_environment()}")
print(f"   config_path: {PathResolver.get_config_path()}")

# 3. EnvManagerの動作確認
from utils.env_manager import EnvManager
EnvManager.initialize()
print(f"\n3. EnvManager:")
print(f"   GOOGLE_SHEETS_ID: {EnvManager.get('GOOGLE_SHEETS_ID')}")
print(f"   .envファイル: {EnvManager._env_file}")

# 4. Configの動作確認
from utils.config import get_config, reset_config
reset_config()  # キャッシュをクリア
config = get_config()

print(f"\n4. Config:")
print(f"   config_path: {config.config_path}")
print(f"   google_sheet.sheet_id: {config.get('google_sheet.sheet_id')}")

# 設定ファイルの内容を直接確認
import json
if config.config_path.exists():
    with open(config.config_path, 'r', encoding='utf-8') as f:
        raw_config = json.load(f)
    print(f"   設定ファイル内のsheet_id: {raw_config.get('google_sheet', {}).get('sheet_id')}")

# 5. GoogleSheetClientの初期化をシミュレート
print(f"\n5. GoogleSheetClient初期化シミュレーション:")
try:
    from core.google_sheet import GoogleSheetClient
    # 初期化を試みる（エラーが発生する可能性あり）
    client = GoogleSheetClient()
    print(f"   初期化成功 - sheet_id: {client.sheet_id}")
except Exception as e:
    print(f"   初期化エラー: {e}")

# 6. 問題の診断
print(f"\n6. 診断結果:")

# 環境変数優先の問題をチェック
env_sheet_id = EnvManager.get('GOOGLE_SHEETS_ID')
config_sheet_id = config.get('google_sheet.sheet_id')

if env_sheet_id and env_sheet_id != config_sheet_id:
    print(f"   ⚠️ 環境変数とConfigで異なるSheet IDが設定されています")
    print(f"      環境変数: {env_sheet_id}")
    print(f"      Config: {config_sheet_id}")

if env_sheet_id == "your-sheet-id":
    print(f"   ⚠️ 環境変数にプレースホルダーが設定されています")
    print(f"      .envファイルを確認してください")

print("\n完了。")
input("Enterキーを押して終了...")