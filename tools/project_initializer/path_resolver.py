"""
EXE環境対応パス解決ユーティリティ
PyInstallerでパッケージ化された際のファイルパス解決を行う
"""

import sys
import os
from pathlib import Path

def get_exe_dir() -> Path:
    """EXE実行時の基準ディレクトリを取得"""
    if getattr(sys, 'frozen', False):
        # EXE実行時: 実行ファイルのディレクトリ
        return Path(sys.executable).parent
    else:
        # 開発環境: スクリプトファイルのディレクトリ
        return Path(__file__).parent

def get_config_path(filename: str = "service_account.json") -> Path:
    """設定ファイルのパスを取得"""
    exe_dir = get_exe_dir()
    
    # EXE実行時の候補パス
    if getattr(sys, 'frozen', False):
        candidates = [
            exe_dir / "config" / filename,
            exe_dir / "_internal" / "config" / filename,
            exe_dir.parent / "config" / filename
        ]
    else:
        # 開発環境の候補パス
        candidates = [
            exe_dir / "config" / filename,
            exe_dir.parent / "config" / filename,
            exe_dir.parent.parent / "config" / filename
        ]
    
    # 存在するファイルを探す
    for candidate in candidates:
        if candidate.exists():
            return candidate
    
    # 見つからない場合は最初の候補を返す（エラーメッセージ用）
    return candidates[0]

def get_env_path() -> Path:
    """.envファイルのパスを取得"""
    exe_dir = get_exe_dir()
    
    if getattr(sys, 'frozen', False):
        candidates = [
            exe_dir / ".env",
            exe_dir / "_internal" / ".env",
        ]
    else:
        candidates = [
            exe_dir / ".env",
            exe_dir.parent / ".env"
        ]
    
    for candidate in candidates:
        if candidate.exists():
            return candidate
    
    return candidates[0]

def get_resource_path(relative_path: str) -> Path:
    """リソースファイルのパスを取得（汎用）"""
    exe_dir = get_exe_dir()
    
    if getattr(sys, 'frozen', False):
        # PyInstallerの_MEIPASSを使用
        if hasattr(sys, '_MEIPASS'):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = exe_dir / "_internal"
    else:
        base_path = exe_dir
    
    return base_path / relative_path

def print_debug_paths():
    """デバッグ用パス情報表示"""
    print("=" * 50)
    print("Path Resolution Debug Info")
    print("=" * 50)
    print(f"Frozen (EXE): {getattr(sys, 'frozen', False)}")
    print(f"Executable: {sys.executable}")
    print(f"EXE Dir: {get_exe_dir()}")
    print(f"Config Path: {get_config_path()}")
    print(f"Config Exists: {get_config_path().exists()}")
    print(f"ENV Path: {get_env_path()}")
    print(f"ENV Exists: {get_env_path().exists()}")
    
    if hasattr(sys, '_MEIPASS'):
        print(f"_MEIPASS: {sys._MEIPASS}")
    
    print("=" * 50)