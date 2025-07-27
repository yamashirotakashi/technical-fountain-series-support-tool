#!/usr/bin/env python3
"""
追加チャネルへの招待スクリプト
"""
import os
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# 設定
BOT_USER_ID = "U098ADT46E4"  # techzip_pdf_bot
ADMIN_TOKEN = os.environ.get("SLACK_USER_TOKEN")

# 追加で招待が必要なチャネル
ADDITIONAL_CHANNELS = [
    "n2360-2361-chatgpt",      # 既に招待済みのはずだが再確認
    "n2218-Linux-Container-Book4",  # 新規
    "n2136-pysimplegui"        # 元リストにあったが見つからなかった（typoを修正）
]

def main():
    client = WebClient(token=ADMIN_TOKEN)
    
    print("🤖 追加チャネルへの招待")
    print(f"Bot User ID: {BOT_USER_ID}")
    print(f"対象: {len(ADDITIONAL_CHANNELS)}チャネル")
    print("-" * 50)
    
    # チャネルIDを取得
    print("📍 チャネルID取得中...")
    channel_map = {}
    
    try:
        response = client.conversations_list(
            types="private_channel",
            limit=1000
        )
        
        all_channels = {ch['name']: ch for ch in response['channels']}
        
        # 対象チャネルの確認
        for channel_name in ADDITIONAL_CHANNELS:
            if channel_name in all_channels:
                ch_info = all_channels[channel_name]
                channel_map[channel_name] = ch_info['id']
                
                # 既に参加しているか確認
                is_member = ch_info.get('is_member', False)
                if is_member:
                    print(f"✅ {channel_name} - 既に参加済み")
                else:
                    print(f"📌 {channel_name} - 招待が必要")
            else:
                print(f"❌ {channel_name} - チャネルが見つかりません")
                
                # 類似チャネルを探す
                similar = [name for name in all_channels.keys() if channel_name[:5] in name]
                if similar:
                    print(f"   💡 類似チャネル: {', '.join(similar)}")
    
    except SlackApiError as e:
        print(f"❌ チャネル一覧取得エラー: {e}")
        return
    
    # 招待実行
    need_invite = [name for name, ch_id in channel_map.items() 
                   if not all_channels[name].get('is_member', False)]
    
    if need_invite:
        print(f"\n🚀 {len(need_invite)}個のチャネルに招待開始...")
        
        for channel_name in need_invite:
            channel_id = channel_map[channel_name]
            try:
                response = client.conversations_invite(
                    channel=channel_id,
                    users=BOT_USER_ID
                )
                print(f"✅ {channel_name} - 招待成功")
                time.sleep(1)
                
            except SlackApiError as e:
                if "already_in_channel" in str(e):
                    print(f"⏭️  {channel_name} - 既に参加済み")
                else:
                    print(f"❌ {channel_name} - エラー: {e}")
                time.sleep(0.5)
    else:
        print("\n✅ 全てのチャネルに既に参加済みです")
    
    # 最終確認
    print("\n" + "="*50)
    print("📊 現在のBot参加状況を確認中...")
    
    try:
        # Bot Tokenで参加チャネルを確認
        bot_client = WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))
        bot_response = bot_client.conversations_list(
            types="private_channel",
            limit=1000
        )
        
        bot_channels = sorted([ch['name'] for ch in bot_response['channels']])
        tech_channels = [ch for ch in bot_channels if ch.startswith('n')]
        
        print(f"✅ Bot参加チャネル数: {len(tech_channels)}個")
        
        # 対象チャネルの参加状況
        print("\n対象チャネルの状況:")
        for ch in ADDITIONAL_CHANNELS:
            if ch in bot_channels:
                print(f"  ✅ {ch}")
            else:
                print(f"  ❌ {ch} - 未参加")
                
    except Exception as e:
        print(f"確認エラー: {e}")

if __name__ == "__main__":
    main()