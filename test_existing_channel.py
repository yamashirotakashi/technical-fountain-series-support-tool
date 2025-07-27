#!/usr/bin/env python3
"""
既存チャネルでのSlack投稿テスト
"""
import os
from datetime import datetime
from src.slack_integration import SlackIntegration

def main():
    # 環境変数からBot Token取得
    bot_token = os.environ.get('SLACK_BOT_TOKEN')
    
    # Slack統合の初期化
    slack = SlackIntegration(bot_token)
    
    # 接続テスト
    print("=== Slack接続テスト ===")
    result = slack.test_connection()
    if not result['success']:
        print(f"❌ 接続失敗: {result['error']}")
        return
    
    print(f"✅ 接続成功")
    print(f"Team: {result['team']}")
    print(f"Bot: {result['user']}")
    print(f"Bot ID: {result['bot_id']}")
    
    # 参加チャネル一覧
    print("\n=== 参加済みチャネル ===")
    channels = slack.get_bot_channels()
    if not channels:
        print("❌ 参加チャネルがありません")
        return
    
    print(f"📊 {len(channels)}個のチャネルに参加中:")
    for i, ch in enumerate(channels):
        print(f"{i+1}. {ch['name']}")
    
    # テスト投稿
    print("\n=== テスト投稿 ===")
    print("テスト用のPDFファイルを作成します...")
    
    # テスト用PDFの作成（簡易的なテキストファイル）
    test_pdf_path = "test_techzip.pdf"
    with open(test_pdf_path, 'w', encoding='utf-8') as f:
        f.write(f"TechZip Slack統合テスト\n")
        f.write(f"生成日時: {datetime.now()}\n")
        f.write(f"これはテスト用のPDFファイルです。\n")
    
    # チャネル選択
    print("\nテスト投稿先を選択してください:")
    print("1. n-ネトコン作品検討")
    print("2. ----0-tb18通知")
    print("3. z-cursor連携")
    print("0. キャンセル")
    
    choice = input("\n番号を入力 (1-3): ")
    
    channel_map = {
        "1": "n-ネトコン作品検討",
        "2": "----0-tb18通知",
        "3": "z-cursor連携"
    }
    
    if choice not in channel_map:
        print("キャンセルしました")
        return
    
    target_channel = channel_map[choice]
    
    print(f"\n📤 {target_channel} にテスト投稿中...")
    
    # PDF投稿
    result = slack.post_pdf_to_channel(
        pdf_path=test_pdf_path,
        repo_name=target_channel,
        book_title="TechZip Slack統合テスト"
    )
    
    if result['success']:
        print(f"✅ 投稿成功！")
        print(f"URL: {result['permalink']}")
    else:
        print(f"❌ 投稿失敗: {result['error']}")
        if 'instruction' in result:
            print(result['instruction'])
    
    # テストファイルの削除
    if os.path.exists(test_pdf_path):
        os.remove(test_pdf_path)
        print("\nテストファイルを削除しました")

if __name__ == "__main__":
    main()