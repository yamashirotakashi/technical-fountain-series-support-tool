#!/usr/bin/env python3
"""
チャネルリストを処理して招待状況を確認
"""
from slack_sdk import WebClient
import sys
import os
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ SLACK_BOT_TOKEN環境変数が設定されていません")
    exit(1)

def main():
    print("=== チャネルリスト処理ツール ===\n")
    print("投稿予定チャネルのリストを入力してください。")
    print("入力が終わったらCtrl+D（Windows）またはCtrl+D（Linux/Mac）を押してください。")
    print("-" * 50)
    
    # 標準入力からチャネルリストを読み込み
    channel_list = []
    try:
        for line in sys.stdin:
            channel_name = line.strip()
            if channel_name:
                channel_list.append(channel_name)
    except EOFError:
        pass
    
    if not channel_list:
        print("\nチャネルリストが空です。")
        print("\n使用方法:")
        print("1. python process_channel_list.py と実行")
        print("2. チャネル名を1行ずつ入力")
        print("3. Ctrl+D で終了")
        print("\nまたは:")
        print("echo -e 'channel1\\nchannel2\\nchannel3' | python process_channel_list.py")
        return
    
    print(f"\n✅ {len(channel_list)}個のチャネルを確認します")
    
    # Slack接続
    client = WebClient(token=BOT_TOKEN)
    
    # 現在参加しているチャネルを取得
    try:
        response = client.conversations_list(
            types="private_channel",
            limit=1000
        )
        joined_channels = {ch['name']: ch['id'] for ch in response['channels'] if ch.get('is_member', False)}
    except Exception as e:
        print(f"❌ Slack接続エラー: {e}")
        return
    
    # 結果を分類
    already_joined = []
    need_invite = []
    
    for channel in channel_list:
        if channel in joined_channels:
            already_joined.append(channel)
        else:
            need_invite.append(channel)
    
    # 結果表示
    print(f"\n📊 チャネル参加状況")
    print("=" * 50)
    print(f"総チャネル数: {len(channel_list)}")
    print(f"参加済み: {len(already_joined)}")
    print(f"未参加: {len(need_invite)}")
    
    if already_joined:
        print(f"\n✅ 参加済みチャネル ({len(already_joined)}個):")
        for ch in sorted(already_joined):
            print(f"  - {ch}")
    
    if need_invite:
        print(f"\n❌ 招待が必要なチャネル ({len(need_invite)}個):")
        for ch in sorted(need_invite):
            print(f"  - {ch}")
        
        # 招待用コマンド生成
        print("\n📝 Slack招待コマンド（コピー用）:")
        print("-" * 50)
        for ch in sorted(need_invite):
            print(f"/invite @techzip_pdf_bot #{ch}")
        print("-" * 50)
        
        # 管理者向けメッセージ
        print("\n💌 管理者への依頼メッセージ（コピー用）:")
        print("-" * 50)
        print("以下のチャネルに @techzip_pdf_bot の招待をお願いします：")
        print("")
        for ch in sorted(need_invite):
            print(f"- #{ch}")
        print("")
        print("各チャネルで /invite @techzip_pdf_bot を実行してください。")
        print("-" * 50)

if __name__ == "__main__":
    main()