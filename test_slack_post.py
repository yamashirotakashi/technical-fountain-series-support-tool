#!/usr/bin/env python3
"""
Slack投稿機能のテストスクリプト
"""

import os
from src.slack_integration import SlackIntegration

def main():
    # Slack統合の初期化
    slack = SlackIntegration()
    
    # 接続テスト
    print("=== 接続テスト ===")
    result = slack.test_connection()
    if not result['success']:
        print(f"❌ 接続失敗: {result['error']}")
        return
    
    print(f"✅ 接続成功: {result['team']} / {result['user']}")
    
    # 参加チャネル一覧
    print("\n=== 参加チャネル一覧 ===")
    channels = slack.get_bot_channels()
    if channels:
        print(f"📊 {len(channels)}個のチャネルに参加中:")
        for ch in channels[:5]:
            print(f"  - {ch['name']}")
    else:
        print("⚠️  まだどのチャネルにも参加していません")
        print("\nSlackアプリから手動でBotを招待してください:")
        print("1. プライベートチャネルを開く")
        print("2. チャネル名をクリック → メンバーを追加")
        print("3. @techzip_pdf_bot を検索して追加")
        return
    
    # テスト投稿（オプション）
    if channels:
        test_channel = input("\nテスト投稿を行うチャネル名を入力 (スキップはEnter): ")
        if test_channel:
            # テスト用PDFの存在確認
            test_pdf = "test.pdf"
            if not os.path.exists(test_pdf):
                print(f"⚠️  {test_pdf}が見つかりません")
                print("テスト用PDFを作成するか、既存のPDFパスを指定してください")
                return
            
            print(f"\n📤 {test_channel}にテスト投稿中...")
            result = slack.post_pdf_to_channel(
                pdf_path=test_pdf,
                repo_name=test_channel,
                book_title="テスト投稿"
            )
            
            if result['success']:
                print(f"✅ 投稿成功: {result['permalink']}")
            else:
                print(f"❌ 投稿失敗: {result['error']}")

if __name__ == "__main__":
    main()