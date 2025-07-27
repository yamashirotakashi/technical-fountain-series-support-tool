#!/usr/bin/env python3
"""
全チャネルタイプをチェックするスクリプト
"""

from slack_sdk import WebClient
import os

BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')

def main():
    client = WebClient(token=BOT_TOKEN)
    
    print("🔍 チャネル情報を取得中...\n")
    
    # 1. パブリックチャネル
    try:
        response = client.conversations_list(
            types="public_channel",
            limit=1000
        )
        public_channels = response.get('channels', [])
        print(f"📢 パブリックチャネル: {len(public_channels)}個")
        
        # Botが参加しているパブリックチャネル
        member_public = [ch for ch in public_channels if ch.get('is_member', False)]
        print(f"   - Bot参加中: {len(member_public)}個")
        if member_public:
            for ch in member_public[:3]:
                print(f"     • {ch['name']}")
    except Exception as e:
        print(f"❌ パブリックチャネル取得エラー: {e}")
    
    print()
    
    # 2. プライベートチャネル（Bot参加済みのみ）
    try:
        response = client.conversations_list(
            types="private_channel",
            limit=1000
        )
        private_channels = response.get('channels', [])
        print(f"🔒 プライベートチャネル（Bot参加済み）: {len(private_channels)}個")
        
        if private_channels:
            for ch in private_channels[:5]:
                print(f"   • {ch['name']}")
        else:
            print("   ⚠️  Botはまだプライベートチャネルに参加していません")
    except Exception as e:
        print(f"❌ プライベートチャネル取得エラー: {e}")
    
    print()
    
    # 3. インバイトが必要な説明
    print("📝 プライベートチャネルへの参加方法:")
    print("1. Slackアプリで任意のプライベートチャネルを開く")
    print("2. チャネル名をクリック → 「メンバーを追加」")
    print("3. @techzip_pdf_bot を検索して追加")
    print("\n⚠️  注意: Bot Tokenではプライベートチャネルの一覧は取得できません")
    print("   Botは招待されたチャネルのみ表示・投稿可能です")

if __name__ == "__main__":
    main()