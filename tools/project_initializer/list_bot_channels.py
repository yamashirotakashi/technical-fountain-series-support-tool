#!/usr/bin/env python3
"""
Botが参加しているチャンネル一覧を表示
"""

import asyncio
import os
from dotenv import load_dotenv
from slack_sdk.web.async_client import AsyncWebClient

load_dotenv()

async def list_bot_channels():
    """Botが参加しているチャンネル一覧"""
    
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    if not bot_token:
        print("SLACK_BOT_TOKEN not found")
        return
    
    client = AsyncWebClient(token=bot_token)
    
    try:
        # Botの情報を取得
        auth_info = await client.auth_test()
        bot_user_id = auth_info["user_id"]
        print(f"Bot User ID: {bot_user_id}")
        print(f"Bot Name: {auth_info.get('user', 'N/A')}")
        print(f"Team: {auth_info.get('team', 'N/A')}\n")
        
        # 公開・プライベート両方のチャンネルを検索（Botがメンバーのもののみ）
        print("Channels Bot is member of:")
        response = await client.conversations_list(
            types="public_channel,private_channel",
            limit=1000
        )
        
        bot_channels = []
        for channel in response["channels"]:
            if channel.get("is_member", False):
                bot_channels.append(channel)
                print(f"- {channel['name']} ({channel['id']}) - Private: {channel.get('is_private', False)}")
        
        print(f"\nTotal channels: {len(bot_channels)}")
        
        # 管理チャンネルを探す
        print("\nLooking for admin channel C0980EXAZD1...")
        for ch in bot_channels:
            if ch['id'] == 'C0980EXAZD1':
                print(f"✓ Found: {ch['name']}")
                break
        else:
            print("✗ Admin channel not found in Bot's channel list")
            
        # スコープ情報を表示
        print(f"\nBot scopes: {auth_info.get('headers', {}).get('x-oauth-scopes', 'N/A')}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(list_bot_channels())