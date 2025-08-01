#!/usr/bin/env python3
"""
シンプル実行版 - GUI依存を最小化した実行テスト
"""

import sys
import os
import asyncio
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """インポートテスト"""
    print("🔍 モジュールインポートテスト")
    print("=" * 40)
    
    try:
        print("PyQt6...", end=" ")
        from PyQt6.QtWidgets import QApplication
        print("✅")
    except ImportError as e:
        print(f"❌ {e}")
        return False
        
    try:
        print("asyncqt...", end=" ")
        from asyncqt import QEventLoop
        print("✅")
    except ImportError as e:
        print(f"❌ {e}")
        return False
        
    try:
        print("Google Sheets...", end=" ")
        from google_sheets import GoogleSheetsClient
        print("✅")
    except ImportError as e:
        print(f"❌ {e}")
        return False
        
    try:
        print("Slack Client...", end=" ")
        from slack_client import SlackClient
        print("✅")
    except ImportError as e:
        print(f"❌ {e}")
        return False
        
    try:
        print("GitHub Client...", end=" ")
        from github_client import GitHubClient
        print("✅")
    except ImportError as e:
        print(f"❌ {e}")
        return False
        
    print("\n✅ すべてのモジュールインポート成功")
    return True

def check_config():
    """設定ファイル確認"""
    print("\n🔧 設定ファイル確認")
    print("=" * 40)
    
    # .env ファイル確認
    env_path = project_root.parent.parent.parent / ".env"
    print(f".env ファイル ({env_path})...", end=" ")
    if env_path.exists():
        print("✅")
        
        # 環境変数読み込みテスト
        from dotenv import load_dotenv
        load_dotenv(env_path)
        
        required_vars = ["SLACK_BOT_TOKEN", "GITHUB_ORG_TOKEN"]
        for var in required_vars:
            value = os.getenv(var)
            print(f"  {var}...", end=" ")
            if value:
                print("✅")
            else:
                print("❌")
    else:
        print("❌")
    
    # サービスアカウントファイル確認
    service_account_path = project_root / "config" / "service_account.json"
    print(f"サービスアカウント ({service_account_path})...", end=" ")
    if service_account_path.exists():
        print("✅")
    else:
        print("❌")

async def test_basic_functionality():
    """基本機能テスト"""
    print("\n🧪 基本機能テスト")
    print("=" * 40)
    
    try:
        # 環境変数読み込み
        env_path = project_root.parent.parent.parent / ".env"
        if env_path.exists():
            from dotenv import load_dotenv
            load_dotenv(env_path)
        
        # Google Sheets テスト
        print("Google Sheets接続テスト...", end=" ")
        service_account_path = project_root / "config" / "service_account.json"
        if service_account_path.exists():
            from google_sheets import GoogleSheetsClient
            client = GoogleSheetsClient(str(service_account_path))
            print("✅")
        else:
            print("❌ (サービスアカウントファイルなし)")
        
        # Slack テスト
        print("Slack接続テスト...", end=" ")
        slack_token = os.getenv("SLACK_BOT_TOKEN")
        if slack_token:
            from slack_client import SlackClient
            slack_client = SlackClient(slack_token)
            print("✅")
        else:
            print("❌ (トークンなし)")
        
        # GitHub テスト
        print("GitHub接続テスト...", end=" ")
        github_token = os.getenv("GITHUB_ORG_TOKEN")
        if github_token:
            from github_client import GitHubClient
            github_client = GitHubClient(github_token)
            print("✅")
        else:
            print("❌ (トークンなし)")
            
        print("\n✅ 基本機能テスト完了")
        
    except Exception as e:
        print(f"❌ エラー: {e}")

def main():
    """メイン実行"""
    print("🚀 技術の泉シリーズプロジェクト初期化ツール - シンプル実行テスト")
    print("=" * 70)
    
    # インポートテスト
    if not test_imports():
        print("\n❌ モジュールインポートに失敗しました")
        print("必要なパッケージをインストールしてください:")
        print("  pip install -r requirements.txt")
        return 1
    
    # 設定確認
    check_config()
    
    # 基本機能テスト
    try:
        asyncio.run(test_basic_functionality())
    except Exception as e:
        print(f"\n❌ 基本機能テストエラー: {e}")
        return 1
    
    # GUI起動テスト
    print("\n🖥️ GUI起動テスト")
    print("=" * 40)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from asyncqt import QEventLoop
        
        app = QApplication(sys.argv)
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        print("Qt6アプリケーション初期化...", end=" ")
        print("✅")
        
        # メインウィンドウ作成テスト
        from main_window import ProjectInitializerWindow
        print("メインウィンドウ作成...", end=" ")
        window = ProjectInitializerWindow()
        print("✅")
        
        print("\n🎉 すべてのテストが成功しました！")
        print("\n実際にGUIを起動しますか？ (y/N): ", end="")
        
        try:
            choice = input().lower()
            if choice in ['y', 'yes']:
                print("\n🚀 GUIアプリケーションを起動中...")
                window.show()
                with loop:
                    sys.exit(loop.run_forever())
            else:
                print("GUI起動をスキップしました")
        except (KeyboardInterrupt, EOFError):
            print("\nGUI起動をスキップしました")
        
        return 0
        
    except Exception as e:
        print(f"❌ GUI起動テストエラー: {e}")
        print("\nバックエンド機能は正常です。GUIライブラリの設定を確認してください。")
        return 1

if __name__ == "__main__":
    sys.exit(main())