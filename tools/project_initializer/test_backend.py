#!/usr/bin/env python3
"""
バックエンド機能のテスト（GUI無し）
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# 環境変数を読み込み（ローカル優先）
local_env = Path(__file__).parent / ".env"
parent_env = Path(__file__).parent.parent.parent / ".env"

if local_env.exists():
    load_dotenv(local_env)
    print(f"✅ ローカル.envファイルを読み込み: {local_env}")
elif parent_env.exists():
    load_dotenv(parent_env)
    print(f"✅ 親ディレクトリ.envファイルを読み込み: {parent_env}")
else:
    print("⚠️ .envファイルが見つかりません")

from google_sheets import GoogleSheetsClient
from slack_client import SlackClient
from github_client import GitHubClient

async def test_google_sheets():
    """Google Sheets連携テスト"""
    print("=== Google Sheets テスト ===")
    
    try:
        # サービスアカウントファイルパス
        service_account_path = Path(__file__).parent.parent.parent / "config" / "service_account.json"
        
        if not service_account_path.exists():
            print(f"❌ サービスアカウントファイルが見つかりません: {service_account_path}")
            return False
            
        client = GoogleSheetsClient(str(service_account_path))
        
        # テスト用のNコード
        test_n_code = "N09999"
        planning_sheet_id = "17DKsMGQ6krbhY7GIcX0iaeN-y8HcGGVkXt3d4oOckyQ"
        purchase_sheet_id = "1JJ_C3z0txlJWiyEDl0c6OoVD5Ym_IoZJMMf5o76oV4c"
        
        # プロジェクト情報取得テスト
        print(f"プロジェクト情報を取得中: {test_n_code}")
        project_info = await client.get_project_info(planning_sheet_id, test_n_code)
        
        if project_info:
            print("✅ プロジェクト情報取得成功:")
            for key, value in project_info.items():
                print(f"   {key}: {value}")
        else:
            print(f"❌ プロジェクト情報が見つかりません: {test_n_code}")
            return False
            
        # 購入リストから書籍URL取得テスト
        print(f"購入リストから書籍URL取得中: {test_n_code}")
        book_url = await client.get_book_url_from_purchase_list(purchase_sheet_id, test_n_code)
        
        if book_url:
            print(f"✅ 書籍URL取得成功: {book_url}")
        else:
            print(f"⚠️ 書籍URLが見つかりません: {test_n_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ Google Sheetsテストエラー: {e}")
        return False

async def test_slack():
    """Slack連携テスト"""
    print("\n=== Slack テスト ===")
    
    try:
        bot_token = os.getenv("SLACK_BOT_TOKEN")
        user_token = os.getenv("SLACK_USER_TOKEN")
        
        if not bot_token:
            print("❌ SLACK_BOT_TOKENが設定されていません")
            return False
            
        if not user_token:
            print("❌ SLACK_USER_TOKENが設定されていません")
            return False
            
        client = SlackClient(bot_token, user_token)
        
        # テストチャンネルの存在確認
        test_channel = "zn9999-test"
        print(f"テストチャンネル確認中: #{test_channel}")
        
        # チャンネル情報取得（存在確認）
        channel_info = await client._get_channel_info(test_channel)
        if channel_info:
            print(f"✅ テストチャンネル確認成功: #{test_channel}")
            print(f"   チャンネルID: {channel_info['id']}")
        else:
            print(f"❌ テストチャンネルが見つかりません: #{test_channel}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Slackテストエラー: {e}")
        return False

async def test_github():
    """GitHub連携テスト"""
    print("\n=== GitHub テスト ===")
    
    try:
        token = os.getenv("GITHUB_ORG_TOKEN")
        if not token:
            print("❌ GITHUB_ORG_TOKENが設定されていません")
            return False
            
        client = GitHubClient(token)
        
        # 認証テスト（組織リポジトリ一覧取得）
        print("GitHub認証テスト中...")
        
        import aiohttp
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.github.com/user", headers=headers) as response:
                if response.status == 200:
                    user_data = await response.json()
                    print(f"✅ GitHub認証成功: {user_data['login']}")
                else:
                    print(f"❌ GitHub認証失敗: {response.status}")
                    return False
                    
        return True
        
    except Exception as e:
        print(f"❌ GitHubテストエラー: {e}")
        return False

async def main():
    """メインテスト関数"""
    print("技術の泉シリーズプロジェクト初期化ツール - バックエンドテスト\n")
    
    # 環境変数確認
    print("=== 環境変数確認 ===")
    env_vars = [
        "SLACK_BOT_TOKEN",
        "SLACK_USER_TOKEN", 
        "GITHUB_ORG_TOKEN"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✅ {var}: {masked_value}")
        else:
            print(f"❌ {var}: 未設定")
    
    print()
    
    # 各機能のテスト実行
    tests = [
        ("Google Sheets", test_google_sheets),
        ("Slack", test_slack),
        ("GitHub", test_github)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ {test_name}テストで予期しないエラー: {e}")
            results[test_name] = False
    
    # 結果サマリー
    print("\n" + "="*50)
    print("テスト結果サマリー")
    print("="*50)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 すべてのテストが成功しました！")
        print("アプリケーションの準備が完了しています。")
    else:
        print("⚠️ 一部のテストが失敗しました。")
        print("設定を確認して再度テストしてください。")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())