#!/usr/bin/env python3
"""
User Tokenを使用した一括招待スクリプト
OAuth認証後に実行
"""
import json
import time
import sys
import os
from pathlib import Path
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

def load_user_token():
    """保存されたUser Tokenを読み込み"""
    token_file = Path('.slack_user_token')
    if not token_file.exists():
        print("❌ User Tokenが見つかりません")
        print("先に python src/oauth_server.py を実行してください")
        sys.exit(1)
    
    with open(token_file, 'r') as f:
        data = json.load(f)
        return data['user_token']

def main():
    # Bot情報
    BOT_USER_ID = "U098ADT46E4"
    
    # User Tokenを読み込み
    user_token = load_user_token()
    client = WebClient(token=user_token)
    
    print("🔍 プライベートチャネル一覧を取得中...")
    
    try:
        # 全プライベートチャネルを取得（User Tokenなら可能）
        response = client.conversations_list(
            types="private_channel",
            limit=1000,
            exclude_archived=True
        )
        
        all_channels = response.get('channels', [])
        print(f"📊 {len(all_channels)}個のプライベートチャネルが見つかりました")
        
        # 技術の泉チャネルをフィルタ
        tech_channels = [ch for ch in all_channels if ch['name'].startswith(('n', 'N'))]
        print(f"🎯 技術の泉シリーズのチャネル: {len(tech_channels)}個")
        
        # Botの現在の参加状況を確認
        slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
        if not slack_bot_token:
            print("❌ SLACK_BOT_TOKEN環境変数が設定されていません")
            sys.exit(1)
        
        bot_client = WebClient(token=slack_bot_token)
        bot_response = bot_client.conversations_list(types="private_channel", limit=1000)
        bot_channels = {ch['name'] for ch in bot_response.get('channels', [])}
        
        # 未参加のチャネルを特定
        new_channels = [ch for ch in tech_channels if ch['name'] not in bot_channels]
        print(f"🆕 Botが未参加のチャネル: {len(new_channels)}個")
        
        if len(new_channels) == 0:
            print("✅ 全てのチャネルに参加済みです")
            return
        
        print("\n以下のチャネルにBotを招待します:")
        for ch in new_channels[:10]:
            print(f"  - {ch['name']}")
        if len(new_channels) > 10:
            print(f"  ... 他 {len(new_channels) - 10}個")
        
        confirm = input("\n続行しますか？ (y/N): ")
        if confirm.lower() != 'y':
            print("キャンセルしました")
            return
        
        success_count = 0
        error_count = 0
        
        # 各チャネルにBotを招待
        for i, channel in enumerate(new_channels):
            channel_name = channel['name']
            channel_id = channel['id']
            
            try:
                response = client.conversations_invite(
                    channel=channel_id,
                    users=BOT_USER_ID
                )
                print(f"[{i+1}/{len(new_channels)}] ✅ {channel_name}")
                success_count += 1
                time.sleep(1)  # Rate limit対策
                
            except SlackApiError as e:
                error_msg = str(e)
                if "already_in_channel" in error_msg:
                    print(f"[{i+1}/{len(new_channels)}] ⏭️  {channel_name} (既に参加済み)")
                else:
                    print(f"[{i+1}/{len(new_channels)}] ❌ {channel_name}: {error_msg}")
                    error_count += 1
                time.sleep(0.5)
        
        # 結果サマリー
        print("\n" + "="*50)
        print("📊 実行結果サマリー")
        print("="*50)
        print(f"✅ 成功: {success_count}個")
        print(f"❌ エラー: {error_count}個")
        print(f"📊 合計: {len(new_channels)}個")
        
    except SlackApiError as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()