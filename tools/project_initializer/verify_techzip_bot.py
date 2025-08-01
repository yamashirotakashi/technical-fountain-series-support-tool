#!/usr/bin/env python3
"""
TechZipワークスペースのBot情報を確認
"""

import asyncio
import os
from dotenv import load_dotenv
from slack_sdk.web.async_client import AsyncWebClient

# techzipプロジェクトの.envファイルを読み込み
techzip_env_path = "/mnt/c/Users/tky99/DEV/technical-fountain-series-support-tool/.env"
load_dotenv(techzip_env_path)

async def verify_techzip_bot():
    """TechZipワークスペースのBot情報を確認"""
    
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    if not bot_token:
        print("SLACK_BOT_TOKEN not found")
        return
    
    print(f"Using token: {bot_token[:20]}...")
    
    client = AsyncWebClient(token=bot_token)
    
    try:
        # Botの基本情報を取得
        auth_info = await client.auth_test()
        print(f"\n=== Bot基本情報 ===")
        print(f"Bot User ID: {auth_info['user_id']}")
        print(f"Bot Name: {auth_info.get('user', 'N/A')}")
        print(f"Team: {auth_info.get('team', 'N/A')}")
        print(f"Team ID: {auth_info.get('team_id', 'N/A')}")
        print(f"URL: {auth_info.get('url', 'N/A')}")
        
        # Botの詳細情報を取得
        user_info = await client.users_info(user=auth_info['user_id'])
        if user_info["ok"]:
            user = user_info["user"]
            profile = user.get("profile", {})
            print(f"\n=== Bot詳細情報 ===")
            print(f"Display Name: {profile.get('display_name', 'N/A')}")
            print(f"Real Name: {profile.get('real_name', 'N/A')}")
            print(f"Status: {profile.get('status_text', 'N/A')}")
        
        # 管理チャンネルC0980EXAZD1を確認
        print(f"\n=== 管理チャンネル確認 ===")
        try:
            channel_info = await client.conversations_info(channel="C0980EXAZD1")
            if channel_info["ok"]:
                channel = channel_info["channel"]
                print(f"Channel: {channel['name']} ({channel['id']})")
                print(f"Is Member: {channel.get('is_member', False)}")
                
                # メンバーリストを取得
                members = await client.conversations_members(channel="C0980EXAZD1")
                if members["ok"] and auth_info['user_id'] in members['members']:
                    print("✓ Botは管理チャンネルのメンバーです")
                else:
                    print("✗ Botは管理チャンネルのメンバーではありません")
        except Exception as e:
            print(f"管理チャンネル確認エラー: {e}")
        
        # zn9999-testチャンネルを検索
        print(f"\n=== zn9999-testチャンネル検索 ===")
        response = await client.conversations_list(
            types="public_channel,private_channel",
            limit=1000
        )
        
        found = False
        for channel in response["channels"]:
            if "zn9999" in channel["name"] or "9999" in channel["name"]:
                print(f"- {channel['name']} ({channel['id']}) - Member: {channel.get('is_member', False)}")
                found = True
        
        if not found:
            print("zn9999関連のチャンネルが見つかりません")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_techzip_bot())