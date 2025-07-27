#!/usr/bin/env python3
"""
全チャネルの詳細確認（プライベート・パブリック）
"""
from slack_sdk import WebClient
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
    
    print("🔍 チャネル情報を取得中...\n")
    
    # Botが参加しているチャネルのみ取得できる
    print("=== Bot参加済みチャネル ===")
    
    # パブリックチャネル
    try:
        response = client.conversations_list(
            types="public_channel",
            limit=1000
        )
        public_channels = [ch for ch in response['channels'] if ch.get('is_member', False)]
        
        if public_channels:
            print(f"\n📢 パブリックチャネル ({len(public_channels)}個):")
            for ch in sorted(public_channels, key=lambda x: x['name']):
                print(f"  - {ch['name']}")
    except Exception as e:
        print(f"パブリックチャネル取得エラー: {e}")
    
    # プライベートチャネル
    try:
        response = client.conversations_list(
            types="private_channel",
            limit=1000
        )
        private_channels = response.get('channels', [])
        
        print(f"\n🔒 プライベートチャネル ({len(private_channels)}個):")
        
        # n で始まるチャネル
        n_channels = [ch for ch in private_channels if ch['name'].startswith(('n', 'N'))]
        other_channels = [ch for ch in private_channels if not ch['name'].startswith(('n', 'N'))]
        
        if n_channels:
            print("\n【技術の泉シリーズ】")
            for ch in sorted(n_channels, key=lambda x: x['name']):
                print(f"  ✅ {ch['name']}")
        
        if other_channels:
            print("\n【その他】")
            for ch in sorted(other_channels, key=lambda x: x['name']):
                print(f"  - {ch['name']}")
                
    except Exception as e:
        print(f"プライベートチャネル取得エラー: {e}")
    
    print("\n" + "="*60)
    print("📝 一括招待について:")
    print("1. Bot Tokenでは未参加のプライベートチャネルは見えません")
    print("2. 一括招待には以下の方法があります:")
    print("   a) Slack CLIを使用（~/.slack/bin/slack login）")
    print("   b) 管理者がSlack上で手動招待")
    print("   c) OAuth認証でUser Token取得")
    print("\n💡 推奨: Slack CLIまたは手動招待")

if __name__ == "__main__":
    main()