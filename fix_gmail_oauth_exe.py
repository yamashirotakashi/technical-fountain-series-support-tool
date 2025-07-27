#!/usr/bin/env python3
"""
Gmail OAuth EXE環境修正スクリプト
EXE環境でGmail OAuth認証が正しく動作するように修正
"""

import os
import sys
import shutil
from pathlib import Path


def fix_gmail_oauth_exe():
    """EXE環境でのGmail OAuth認証を修正"""
    
    # ユーザーディレクトリの確認
    user_dir = Path.home() / '.techzip'
    config_dir = user_dir / 'config'
    
    print(f"ユーザーディレクトリ: {user_dir}")
    print(f"設定ディレクトリ: {config_dir}")
    
    # ディレクトリが存在しない場合は作成
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ 設定ディレクトリを作成しました: {config_dir}")
    
    # 開発環境の認証ファイルを探す
    dev_paths = [
        Path("C:/Users/tky99/dev/technical-fountain-series-support-tool/config/gmail_oauth_credentials.json"),
        Path("config/gmail_oauth_credentials.json"),
        Path(__file__).parent / "config" / "gmail_oauth_credentials.json"
    ]
    
    source_file = None
    for path in dev_paths:
        if path.exists():
            source_file = path
            break
    
    if not source_file:
        print("❌ Gmail OAuth認証ファイルが見つかりません")
        print("以下のいずれかの場所に gmail_oauth_credentials.json を配置してください:")
        for path in dev_paths:
            print(f"  - {path}")
        return False
    
    # 認証ファイルをコピー
    target_file = config_dir / 'gmail_oauth_credentials.json'
    if not target_file.exists():
        shutil.copy2(source_file, target_file)
        print(f"✓ 認証ファイルをコピーしました:")
        print(f"  元: {source_file}")
        print(f"  先: {target_file}")
    else:
        print(f"✓ 認証ファイルは既に存在します: {target_file}")
    
    # トークンファイルもコピー（存在する場合）
    token_source = source_file.parent / 'gmail_token.pickle'
    if token_source.exists():
        token_target = config_dir / 'gmail_token.pickle'
        if not token_target.exists():
            shutil.copy2(token_source, token_target)
            print(f"✓ トークンファイルもコピーしました: {token_target}")
    
    # 環境変数の設定（必要に応じて）
    print("\n環境情報:")
    print(f"  Python: {sys.executable}")
    print(f"  作業ディレクトリ: {os.getcwd()}")
    print(f"  EXE実行: {'_MEIPASS' in dir(sys)}")
    
    return True


def test_import():
    """必要なモジュールのインポートテスト"""
    print("\nモジュールインポートテスト:")
    
    try:
        from core.gmail_oauth_monitor import GmailOAuthMonitor
        print("✓ GmailOAuthMonitor のインポート成功")
    except Exception as e:
        print(f"❌ GmailOAuthMonitor のインポート失敗: {e}")
        return False
    
    try:
        from core.gmail_oauth_exe_helper import gmail_oauth_helper
        print("✓ gmail_oauth_helper のインポート成功")
        print(f"  - EXE環境: {gmail_oauth_helper.is_exe}")
        print(f"  - 認証ファイル存在: {gmail_oauth_helper.check_credentials_exist()}")
    except Exception as e:
        print(f"❌ gmail_oauth_helper のインポート失敗: {e}")
        return False
    
    return True


def main():
    """メイン処理"""
    print("Gmail OAuth EXE環境修正ツール")
    print("="*50)
    
    # 修正実行
    if fix_gmail_oauth_exe():
        print("\n✓ 修正が完了しました")
        
        # インポートテスト
        if test_import():
            print("\n✓ すべてのテストが成功しました")
            print("\nTechZip GUIを再起動してGmail API方式を試してください。")
        else:
            print("\n⚠ 一部のテストが失敗しました")
    else:
        print("\n❌ 修正に失敗しました")


if __name__ == "__main__":
    main()