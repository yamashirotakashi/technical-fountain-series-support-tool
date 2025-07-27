#!/usr/bin/env python3
"""
Bot プロファイルの詳細確認と更新
"""
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json
import os
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ SLACK_BOT_TOKEN環境変数が設定されていません")
    exit(1)

def main():
    client = WebClient(token=BOT_TOKEN)
    
    print("=== Bot プロファイル詳細確認 ===\n")
    
    # 1. auth.test
    auth_info = client.auth_test()
    bot_user_id = auth_info['user_id']
    print(f"Bot User ID: {bot_user_id}")
    print(f"Username: {auth_info['user']}")
    
    # 2. users.info で詳細取得
    try:
        user_info = client.users_info(user=bot_user_id)
        user = user_info['user']
        profile = user['profile']
        
        print(f"\n--- 現在のプロファイル ---")
        print(f"is_bot: {user.get('is_bot', False)}")
        print(f"name: {user.get('name', 'なし')}")
        print(f"real_name: {user.get('real_name', 'なし')}")
        print(f"display_name: {profile.get('display_name', 'なし')}")
        print(f"display_name_normalized: {profile.get('display_name_normalized', 'なし')}")
        print(f"real_name: {profile.get('real_name', 'なし')}")
        print(f"real_name_normalized: {profile.get('real_name_normalized', 'なし')}")
        print(f"title: {profile.get('title', 'なし')}")
        
    except SlackApiError as e:
        print(f"エラー: {e}")
    
    # 3. プロファイル更新を試みる
    print(f"\n=== プロファイル更新テスト ===")
    try:
        # users.profile.set は Bot Token では使えない可能性が高い
        response = client.users_profile_set(
            profile={
                "display_name": "技術の泉シリーズ",
                "real_name": "技術の泉シリーズ"
            }
        )
        print("✅ プロファイル更新成功")
        print(json.dumps(response['profile'], indent=2, ensure_ascii=False))
    except SlackApiError as e:
        print(f"❌ プロファイル更新失敗: {e}")
        print("\n💡 Bot Tokenではプロファイル更新ができません")
        print("   Slack App設定ページでの変更が必要です")

if __name__ == "__main__":
    main()