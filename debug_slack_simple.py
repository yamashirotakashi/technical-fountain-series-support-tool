#!/usr/bin/env python3
"""
Slack APIチャネル取得の詳細デバッグ（dotenv依存なし）
"""
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

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
        
        if not connection_test.get('success'):
            print("❌ 接続失敗のため、チャネル検索をスキップ")
            return
        
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
                    print(f"    - {ch['name']} (ID: {ch['id']}, Member: {ch.get('is_member', 'N/A')})")
            else:
                print("  1798を含むプライベートチャネルなし")
                
        except Exception as e:
            print(f"プライベートチャネル取得エラー: {e}")
        
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
        
        print("\n4. z1798-nuxt3-tailwindcssの直接確認:")
        # 全チャネルから直接検索
        all_channels = []
        try:
            # パブリック
            response = slack.client.conversations_list(types="public_channel", limit=1000)
            all_channels.extend(response.get('channels', []))
            
            # プライベート
            response = slack.client.conversations_list(types="private_channel", limit=1000)
            all_channels.extend(response.get('channels', []))
            
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
            else:
                print("  ❌ z1798-nuxt3-tailwindcssが見つかりません")
                
        except Exception as e:
            print(f"  チャネル確認エラー: {e}")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_slack_channels()