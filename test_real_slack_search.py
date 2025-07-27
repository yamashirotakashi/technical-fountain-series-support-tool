#!/usr/bin/env python3
"""
実際のSlack環境でのチャネル検索テスト
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# 環境変数を読み込み
load_dotenv()

from src.slack_pdf_poster import SlackPDFPoster

def test_real_slack_channel_search():
    """実際のSlack環境でのチャネル検索テスト"""
    
    # 環境変数の確認
    slack_token = os.getenv('SLACK_BOT_TOKEN')
    if not slack_token:
        print("❌ SLACK_BOT_TOKEN環境変数が設定されていません")
        return
    
    print("=== 実際のSlack環境でのチャネル検索テスト ===")
    print(f"Bot Token: {slack_token[:10]}...")
    
    try:
        # SlackPDFPosterを初期化
        poster = SlackPDFPoster()
        
        print("\n1. Botが参加しているチャネル一覧:")
        channels = poster.slack_integration.get_bot_channels()
        
        # チャネル一覧を表示
        target_found = False
        for i, channel in enumerate(channels[:20]):  # 最初の20個まで表示
            channel_name = channel.get('name', '')
            print(f"  {i+1:2d}. {channel_name}")
            
            # z1798-nuxt3-tailwindcssがあるか確認
            if '1798' in channel_name:
                print(f"      ✓ 1798を含むチャネル発見!")
                target_found = True
        
        if len(channels) > 20:
            print(f"  ... (他{len(channels)-20}個のチャネル)")
        
        print(f"\n総チャネル数: {len(channels)}")
        
        # N01798の検索テスト
        print(f"\n2. N01798でのチャネル検索:")
        result = poster.find_slack_channel("1798")
        
        if result:
            print(f"✅ 検索成功: {result}")
        else:
            print("❌ 検索失敗")
            
            # 1798を含むチャネルがあるか手動確認
            channels_with_1798 = [ch['name'] for ch in channels if '1798' in ch.get('name', '')]
            if channels_with_1798:
                print(f"   ただし、1798を含むチャネルは存在します:")
                for ch in channels_with_1798:
                    print(f"     - {ch}")
            else:
                print("   1798を含むチャネルは見つかりませんでした")
        
        # z1798-nuxt3-tailwindcssの直接確認
        print(f"\n3. z1798-nuxt3-tailwindcssの直接確認:")
        z1798_exists = any(ch.get('name', '') == 'z1798-nuxt3-tailwindcss' for ch in channels)
        print(f"z1798-nuxt3-tailwindcss存在: {z1798_exists}")
        
        # Botがz1798チャネルに招待されているか確認
        if not z1798_exists:
            print("\n⚠️  z1798-nuxt3-tailwindcssチャネルにBotが招待されていない可能性があります")
            print("   以下を確認してください:")
            print("   1. チャネルが存在するか")
            print("   2. Botがチャネルに招待されているか")
            print("   3. /invite @TechZip PDF投稿Bot をチャネルで実行")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_slack_channel_search()