#!/usr/bin/env python3
"""
Bot情報の確認とキャッシュクリア
"""
from slack_sdk import WebClient
from datetime import datetime

BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

def main():
    client = WebClient(token=BOT_TOKEN)
    
    print("=== Bot情報の確認 ===")
    
    # auth.testで基本情報を取得
    auth_info = client.auth_test()
    print(f"Bot ID: {auth_info['user_id']}")
    print(f"Bot名（内部）: {auth_info['user']}")
    print(f"Team: {auth_info['team']}")
    
    # users.infoでBot詳細情報を取得
    print("\n=== Bot詳細情報 ===")
    try:
        user_info = client.users_info(user=auth_info['user_id'])
        profile = user_info['user']['profile']
        print(f"表示名: {profile.get('display_name', 'なし')}")
        print(f"実名: {profile.get('real_name', 'なし')}")
        print(f"Bot名: {user_info['user'].get('name', 'なし')}")
        
        if profile.get('image_24'):
            print(f"アイコン: 設定済み")
    except Exception as e:
        print(f"詳細情報取得エラー: {e}")
    
    # メッセージ投稿時の表示を確認
    print("\n=== テストメッセージ投稿 ===")
    try:
        response = client.chat_postMessage(
            channel="C097H72S49H",  # n9999-bottest
            text=f"Bot名変更テスト - {datetime.now().strftime('%H:%M:%S')}"
        )
        print(f"✅ メッセージ投稿成功")
        print(f"タイムスタンプ: {response['ts']}")
    except Exception as e:
        print(f"❌ 投稿エラー: {e}")

if __name__ == "__main__":
    main()