#!/usr/bin/env python3
"""
Slack APIチャネル取得の詳細デバッグ
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# 環境変数を読み込み
load_dotenv()

from src.slack_integration import SlackIntegration

def debug_slack_channels():
    """Slack APIでの詳細なチャネル取得デバッグ"""
    
    # 環境変数の確認
    slack_token = os.getenv('SLACK_BOT_TOKEN')
    if not slack_token:
        print("❌ SLACK_BOT_TOKEN環境変数が設定されていません")
        return
    
    print("=== Slack APIチャネル取得デバッグ ===")
    print(f"Bot Token: {slack_token[:10]}...")
    
    try:
        # SlackIntegrationを直接使用
        slack = SlackIntegration()
        
        print("\n1. 接続テスト:")
        connection_test = slack.test_connection()
        print(f"接続状態: {connection_test}")
        
        print("\n2. 全チャネルタイプの取得:")
        
        # パブリックチャネル
        try:
            response = slack.client.conversations_list(
                types="public_channel",
                limit=1000,
                exclude_archived=True
            )
            public_channels = response.get('channels', [])
            print(f"パブリックチャネル数: {len(public_channels)}")
            
            z1798_in_public = [ch for ch in public_channels if '1798' in ch.get('name', '')]
            if z1798_in_public:
                print("  1798を含むパブリックチャネル:")
                for ch in z1798_in_public:
                    print(f"    - {ch['name']} (ID: {ch['id']})")
                    
        except Exception as e:
            print(f"パブリックチャネル取得エラー: {e}")
        
        # プライベートチャネル
        try:
            response = slack.client.conversations_list(
                types="private_channel",
                limit=1000,
                exclude_archived=True
            )
            private_channels = response.get('channels', [])
            print(f"プライベートチャネル数: {len(private_channels)}")
            
            z1798_in_private = [ch for ch in private_channels if '1798' in ch.get('name', '')]
            if z1798_in_private:
                print("  1798を含むプライベートチャネル:")
                for ch in z1798_in_private:
                    print(f"    - {ch['name']} (ID: {ch['id']})")
            else:
                print("  1798を含むプライベートチャネルなし")
                
        except Exception as e:
            print(f"プライベートチャネル取得エラー: {e}")
        
        # IM/DM
        try:
            response = slack.client.conversations_list(
                types="im,mpim",
                limit=1000
            )
            im_channels = response.get('channels', [])
            print(f"IM/DM数: {len(im_channels)}")
            
        except Exception as e:
            print(f"IM/DM取得エラー: {e}")
        
        print("\n3. get_bot_channels()メソッドの結果:")
        bot_channels = slack.get_bot_channels()
        print(f"Bot参加チャネル数: {len(bot_channels)}")
        
        # z1798を含むチャネルを検索
        z1798_channels = [ch for ch in bot_channels if '1798' in ch.get('name', '')]
        
        if z1798_channels:
            print("  1798を含むBot参加チャネル:")
            for ch in z1798_channels:
                print(f"    - {ch['name']} (ID: {ch.get('id', 'N/A')})")
        else:
            print("  ❌ 1798を含むBot参加チャネルが見つかりません")
            
            # 全チャネル名を表示（デバッグ用）
            print("\n  Bot参加チャネル一覧（最初の30個）:")
            for i, ch in enumerate(bot_channels[:30]):
                channel_name = ch.get('name', 'Unknown')
                print(f"    {i+1:2d}. {channel_name}")
                
                # z1798-nuxt3-tailwindcssと完全一致を確認
                if channel_name == 'z1798-nuxt3-tailwindcss':
                    print("        ✓ z1798-nuxt3-tailwindcss 完全一致!")
                elif 'z1798' in channel_name:
                    print(f"        ✓ z1798を含む: {channel_name}")
                elif '1798' in channel_name:
                    print(f"        ✓ 1798を含む: {channel_name}")
            
            if len(bot_channels) > 30:
                print(f"    ... (他{len(bot_channels)-30}個)")
        
        print("\n4. 直接的なチャネル名検索:")
        # get_bot_channels()の実装を確認
        print("get_bot_channels()の詳細:")
        print(f"  戻り値の型: {type(bot_channels)}")
        if bot_channels:
            first_channel = bot_channels[0]
            print(f"  最初のチャネルの構造: {first_channel}")
            print(f"  最初のチャネルのキー: {list(first_channel.keys())}")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_slack_channels()