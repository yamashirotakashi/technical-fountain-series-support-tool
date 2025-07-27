#!/usr/bin/env python3
"""
nn2136-pysimpleguzチャネルへの招待
"""
import os
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# 設定
BOT_USER_ID = "U098ADT46E4"
ADMIN_TOKEN = os.environ.get("SLACK_USER_TOKEN")

def main():
    client = WebClient(token=ADMIN_TOKEN)
    target_channel = "nn2136-pysimpleguz"
    
    print(f"🎯 {target_channel} への招待")
    
    try:
        # チャネル情報を取得
        response = client.conversations_list(
            types="private_channel",
            limit=1000
        )
        
        channel_info = None
        for ch in response['channels']:
            if ch['name'] == target_channel:
                channel_info = ch
                break
        
        if not channel_info:
            print(f"❌ {target_channel} が見つかりません")
            return
        
        channel_id = channel_info['id']
        
        # 招待実行
        try:
            response = client.conversations_invite(
                channel=channel_id,
                users=BOT_USER_ID
            )
            print(f"✅ {target_channel} への招待が成功しました！")
            
        except SlackApiError as e:
            if "already_in_channel" in str(e):
                print(f"⏭️  {target_channel} - 既に参加済みです")
            else:
                print(f"❌ エラー: {e}")
                
    except Exception as e:
        print(f"❌ エラー: {e}")
    
    # 最終確認
    print("\n📊 最終確認...")
    bot_client = WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))
    
    try:
        response = bot_client.conversations_list(
            types="private_channel",
            limit=1000
        )
        
        bot_channels = [ch['name'] for ch in response['channels']]
        if target_channel in bot_channels:
            print(f"✅ 確認: {target_channel} に参加しています")
        else:
            print(f"❌ 確認: {target_channel} に参加していません")
            
        # n2218も探す
        n2218_channels = [ch for ch in bot_channels if "2218" in ch]
        if n2218_channels:
            print(f"\n💡 2218を含むチャネル: {', '.join(n2218_channels)}")
        else:
            print("\n💡 n2218-Linux-Container-Book4 は存在しないようです")
            
    except Exception as e:
        print(f"確認エラー: {e}")

if __name__ == "__main__":
    main()