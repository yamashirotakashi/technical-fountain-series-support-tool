#!/usr/bin/env python3
"""
zn9999-testチャンネルのIDを探す
"""

import asyncio
import os
from dotenv import load_dotenv
from slack_sdk.web.async_client import AsyncWebClient

load_dotenv()

async def find_test_channel():
    """テストチャンネルを探す"""
    
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    if not bot_token:
        print("SLACK_BOT_TOKEN not found")
        return
    
    client = AsyncWebClient(token=bot_token)
    
    try:
        # 公開・プライベート両方のチャンネルを検索
        print("Searching for channels...")
        response = await client.conversations_list(
            types="public_channel,private_channel",
            limit=1000
        )
        
        # zn9999-testを探す
        found = False
        for channel in response["channels"]:
            if "zn9999" in channel["name"]:
                print(f"Channel: {channel['name']} - ID: {channel['id']} - Private: {channel.get('is_private', False)}")
                found = True
                
                # 詳細情報を取得
                info = await client.conversations_info(channel=channel['id'])
                if info["ok"]:
                    ch = info["channel"]
                    print(f"  Members: {ch.get('num_members', 'N/A')}")
                    print(f"  Creator: {ch.get('creator', 'N/A')}")
                    print(f"  Created: {ch.get('created', 'N/A')}")
        
        if not found:
            print("\nzn9999-test channel not found.")
            print("\nAll private channels Bot is member of:")
            for channel in response["channels"]:
                if channel.get("is_private", False) and channel.get("is_member", False):
                    print(f"- {channel['name']} ({channel['id']})")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(find_test_channel())