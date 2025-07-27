#!/usr/bin/env python3
"""
管理者権限での一括招待スクリプト
※要管理者のUser Token
"""
import os
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# 設定
BOT_USER_ID = "U098ADT46E4"  # techzip_pdf_bot
ADMIN_TOKEN = os.environ.get("SLACK_USER_TOKEN")  # 技術の泉シリーズ招待アプリのUser Token

# チャネルリスト
CHANNELS = [
    "n2132-powershell",
    "n2136-pysimplegui",
    "n2140-ai-illust",
    "n2176-podman-advanced",
    "n2250-python-ai",
    "n2253-copilot",
    "n2257-amazonbedrock",
    "n2258-reactaria",
    "n2278-streamlit-ai",
    "n2279-python-sbrl",
    "n2280-digital-signage",
    "n2308-kubernetes-elasticsearch",
    "n2354-ai-efficiency",
    "n2355-react-apps",
    "n2356-Linux-Container-Book5",
    "n2357-snowflake-cortex",
    "n2358-prepomax",
    "n2359-novel-generative-ai",
    "n2360-2361-chatgpt",
    "n2363-gas-linebot",
    "n2364-github-guide",
    "n2365-local-llm",
    "n2366-graphrag",
    "n2367-github-pages",
    "n2368-gas-slack",
    "n2374-fedify",
    "n2375-graphdb",
    "n2376-folium",
    "n2385-mcp-agent",
    "n2399-practice-mcp",
    "n2412-aws-llm",
    "n2413-apache-iceberg",
    "n2421-winsows-sandbox"
]

def main():
    if ADMIN_TOKEN == "xoxp-YOUR-ADMIN-USER-TOKEN":
        print("❌ エラー: ADMIN_TOKENを設定してください")
        print("\n取得方法:")
        print("1. https://api.slack.com/apps/A097K6HTULW/oauth")
        print("2. User Token Scopesを追加（channels:read, groups:read, groups:write）")
        print("3. Reinstall to Workspace")
        print("4. User OAuth Tokenをコピー")
        return
    
    client = WebClient(token=ADMIN_TOKEN)
    
    print(f"🤖 Bot User ID: {BOT_USER_ID}")
    print(f"📊 招待対象: {len(CHANNELS)}チャネル")
    print("-" * 50)
    
    # まず全チャネルのIDを取得
    print("📍 チャネルID取得中...")
    channel_map = {}
    
    try:
        response = client.conversations_list(
            types="private_channel",
            limit=1000
        )
        
        for channel in response['channels']:
            if channel['name'] in CHANNELS:
                channel_map[channel['name']] = channel['id']
    except SlackApiError as e:
        print(f"❌ チャネル一覧取得エラー: {e}")
        return
    
    print(f"✅ {len(channel_map)}個のチャネルIDを取得")
    
    # 見つからないチャネル
    not_found = set(CHANNELS) - set(channel_map.keys())
    if not_found:
        print(f"\n⚠️  見つからないチャネル ({len(not_found)}個):")
        for ch in sorted(not_found):
            print(f"  - {ch}")
    
    # 招待実行
    print(f"\n🚀 招待開始...")
    success_count = 0
    already_count = 0
    error_count = 0
    
    for channel_name, channel_id in sorted(channel_map.items()):
        try:
            response = client.conversations_invite(
                channel=channel_id,
                users=BOT_USER_ID
            )
            print(f"✅ {channel_name}")
            success_count += 1
            time.sleep(1)  # Rate limit対策
            
        except SlackApiError as e:
            if "already_in_channel" in str(e):
                print(f"⏭️  {channel_name} (既に参加済み)")
                already_count += 1
            else:
                print(f"❌ {channel_name}: {e}")
                error_count += 1
            time.sleep(0.5)
    
    # サマリー
    print("\n" + "=" * 50)
    print("📊 実行結果")
    print("=" * 50)
    print(f"✅ 成功: {success_count}")
    print(f"⏭️  既に参加: {already_count}")
    print(f"❌ エラー: {error_count}")
    print(f"❓ チャネル未発見: {len(not_found)}")
    print(f"📊 合計: {len(CHANNELS)}")

if __name__ == "__main__":
    main()