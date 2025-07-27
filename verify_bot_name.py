#!/usr/bin/env python3
"""
Bot名変更の最終確認
"""
from slack_sdk import WebClient
from datetime import datetime

BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

def main():
    client = WebClient(token=BOT_TOKEN)
    
    print("=== Bot名変更の確認 ===\n")
    
    # Bot情報を再取得（トークンが変わっている可能性があるため注意）
    try:
        auth_info = client.auth_test()
        print(f"✅ 接続成功")
        print(f"Team: {auth_info['team']}")
        print(f"Bot Username: {auth_info['user']}")
        
        # 詳細情報
        user_info = client.users_info(user=auth_info['user_id'])
        profile = user_info['user']['profile']
        
        print(f"\n--- 表示名情報 ---")
        print(f"display_name: {profile.get('display_name', '(未設定)')}")
        print(f"real_name: {profile.get('real_name', '(未設定)')}")
        
        # テストメッセージ
        print(f"\n--- テストメッセージ投稿 ---")
        response = client.chat_postMessage(
            channel="C097H72S49H",
            text=f"Bot名確認テスト - {datetime.now().strftime('%H:%M:%S')}\n表示名は「技術の泉シリーズ」になっていますか？"
        )
        print(f"✅ 投稿成功")
        print(f"\nSlackで表示名を確認してください")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        print("\n⚠️  注意: 再インストール後はBot Tokenが変わる可能性があります")
        print("その場合は新しいBot Tokenを取得してください")

if __name__ == "__main__":
    main()