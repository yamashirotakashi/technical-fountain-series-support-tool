#!/usr/bin/env python3
"""
Bot参加チャネルの再確認（キャッシュクリア付き）
"""
import os
from src.slack_integration import SlackIntegration

def main():
    bot_token = os.environ.get('SLACK_BOT_TOKEN', os.environ.get('SLACK_BOT_TOKEN'))
    slack = SlackIntegration(bot_token)
    
    # キャッシュをクリア
    slack._channel_cache.clear()
    
    print("🔄 チャネル情報を再取得中...\n")
    
    # 参加チャネル一覧を取得
    channels = slack.get_bot_channels()
    
    print(f"📊 Bot参加チャネル: {len(channels)}個")
    print("-" * 50)
    
    # n で始まるチャネルを優先表示
    n_channels = [ch for ch in channels if ch['name'].startswith(('n', 'N'))]
    other_channels = [ch for ch in channels if not ch['name'].startswith(('n', 'N'))]
    
    if n_channels:
        print("\n技術の泉シリーズチャネル:")
        for ch in sorted(n_channels, key=lambda x: x['name']):
            print(f"  ✅ {ch['name']}")
    
    if other_channels:
        print("\nその他のチャネル:")
        for ch in sorted(other_channels, key=lambda x: x['name']):
            print(f"  ✅ {ch['name']}")
    
    # n9999-bottest の確認
    print("\n" + "=" * 50)
    if any(ch['name'] == 'n9999-bottest' for ch in channels):
        print("✅ n9999-bottest チャネルへの参加を確認しました！")
        print("テスト投稿の準備ができています。")
    else:
        print("⚠️  n9999-bottest チャネルがまだ見つかりません")
        print("\n考えられる原因:")
        print("1. Bot招待の反映に時間がかかっている")
        print("2. チャネル名が異なる")
        print("3. 異なるワークスペースのBotを使用している")

if __name__ == "__main__":
    main()