#!/usr/bin/env python3
"""
Bot情報とチャネル検索の詳細デバッグ
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# 環境変数を読み込み
load_dotenv()

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def debug_bot_and_channels():
    """Bot情報とチャネル検索の詳細デバッグ"""
    
    # 環境変数の確認
    slack_token = os.getenv('SLACK_BOT_TOKEN')
    if not slack_token:
        print("❌ SLACK_BOT_TOKEN環境変数が設定されていません")
        return
    
    print("=== Bot情報とチャネル検索デバッグ ===")
    print(f"Bot Token: {slack_token[:10]}...")
    
    try:
        client = WebClient(token=slack_token)
        
        print("\n1. Bot認証情報:")
        try:
            auth_response = client.auth_test()
            print(f"  Bot User ID: {auth_response.get('user_id')}")
            print(f"  Bot User: {auth_response.get('user')}")
            print(f"  Team: {auth_response.get('team')}")
            print(f"  Team ID: {auth_response.get('team_id')}")
            
            bot_user_id = auth_response.get('user_id')
            
        except SlackApiError as e:
            print(f"  認証エラー: {e}")
            return
        
        print("\n2. Bot詳細情報:")
        try:
            bot_info = client.users_info(user=bot_user_id)
            bot_data = bot_info.get('user', {})
            print(f"  Real Name: {bot_data.get('real_name', 'N/A')}")
            print(f"  Display Name: {bot_data.get('profile', {}).get('display_name', 'N/A')}")
            print(f"  Name: {bot_data.get('name', 'N/A')}")
            print(f"  Is Bot: {bot_data.get('is_bot', False)}")
            
        except SlackApiError as e:
            print(f"  Bot情報取得エラー: {e}")
        
        print("\n3. チャネル一覧（Bot参加済み）:")
        
        # 全タイプのチャネルを取得
        all_channels = []
        
        # パブリックチャネル
        try:
            response = client.conversations_list(
                types="public_channel",
                limit=1000,
                exclude_archived=True
            )
            public_channels = response.get('channels', [])
            all_channels.extend(public_channels)
            print(f"  パブリックチャネル: {len(public_channels)}個")
            
        except SlackApiError as e:
            print(f"  パブリックチャネル取得エラー: {e}")
        
        # プライベートチャネル（Botが参加しているもののみ）
        try:
            response = client.conversations_list(
                types="private_channel",
                limit=1000,
                exclude_archived=True
            )
            private_channels = response.get('channels', [])
            all_channels.extend(private_channels)
            print(f"  プライベートチャネル: {len(private_channels)}個")
            
        except SlackApiError as e:
            print(f"  プライベートチャネル取得エラー: {e}")
        
        print(f"  総チャネル数: {len(all_channels)}個")
        
        print("\n4. 1798を含むチャネル検索:")
        channels_with_1798 = []
        
        for channel in all_channels:
            channel_name = channel.get('name', '')
            if '1798' in channel_name:
                channels_with_1798.append(channel)
                print(f"  ✓ {channel_name} (ID: {channel.get('id')}, Type: {'Private' if channel.get('is_private') else 'Public'})")
        
        if not channels_with_1798:
            print("  ❌ 1798を含むチャネルが見つかりません")
            
            # z1798で始まるチャネルを検索
            z_channels = [ch for ch in all_channels if ch.get('name', '').startswith('z')]
            if z_channels:
                print(f"\n  参考: 'z'で始まるチャネル({len(z_channels)}個):")
                for ch in z_channels[:10]:  # 最初の10個まで
                    print(f"    - {ch.get('name')}")
        
        print("\n5. z1798-nuxt3-tailwindcssの直接確認:")
        target_channel = None
        for channel in all_channels:
            if channel.get('name') == 'z1798-nuxt3-tailwindcss':
                target_channel = channel
                break
        
        if target_channel:
            print(f"  ✅ z1798-nuxt3-tailwindcss発見!")
            print(f"    ID: {target_channel.get('id')}")
            print(f"    Private: {target_channel.get('is_private', False)}")
            print(f"    Member: {target_channel.get('is_member', False)}")
            print(f"    Archived: {target_channel.get('is_archived', False)}")
            
            # メンバーシップの詳細確認
            try:
                channel_info = client.conversations_info(channel=target_channel['id'])
                channel_detail = channel_info.get('channel', {})
                print(f"    詳細Member: {channel_detail.get('is_member', False)}")
                
            except SlackApiError as e:
                print(f"    チャネル詳細取得エラー: {e}")
                
        else:
            print("  ❌ z1798-nuxt3-tailwindcssが見つかりません")
            
            # 類似名のチャネルを検索
            similar_channels = [ch for ch in all_channels 
                             if 'nuxt' in ch.get('name', '').lower() or 
                                'tailwind' in ch.get('name', '').lower() or
                                'z1798' in ch.get('name', '')]
            
            if similar_channels:
                print(f"  類似チャネル({len(similar_channels)}個):")
                for ch in similar_channels:
                    print(f"    - {ch.get('name')}")
        
        print("\n6. チャネル名の完全一致テスト:")
        test_names = [
            'z1798-nuxt3-tailwindcss',
            'Z1798-nuxt3-tailwindcss', 
            'z1798-nuxt3-tailwindcss ',  # 末尾スペース
            ' z1798-nuxt3-tailwindcss',  # 先頭スペース
        ]
        
        for test_name in test_names:
            found = any(ch.get('name') == test_name for ch in all_channels)
            print(f"  '{test_name}': {found}")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_bot_and_channels()