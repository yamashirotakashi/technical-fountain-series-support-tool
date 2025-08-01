#!/usr/bin/env python3
"""
GitHub App ID確認スクリプト - Bot Tokenを使用したバージョン
Bot Tokenでアクセス可能な範囲でGitHub App存在を確認
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from slack_sdk.web.async_client import AsyncWebClient
import json

async def check_github_app():
    """GitHub AppのIDを確認"""
    
    # .envファイルを読み込み
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ .envファイルを読み込み: {env_file}")
    
    # Slack Bot Tokenを取得
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    user_token = os.getenv("SLACK_USER_TOKEN")
    
    if not bot_token:
        print("❌ SLACK_BOT_TOKEN not found")
        return
    
    print(f"🔍 GitHub App招待エラーの調査を実行中...")
    print("=" * 50)
    
    # 現在設定されているIDを確認
    current_github_app_id = "UA8BZ8ENT"
    print(f"🔍 現在設定されているGitHub App ID: {current_github_app_id}")
    
    # Bot Tokenでテスト
    print(f"\n📋 Bot Tokenでの調査:")
    bot_client = AsyncWebClient(token=bot_token)
    
    try:
        # Bot情報を取得
        bot_info = await bot_client.auth_test()
        if bot_info["ok"]:
            print(f"✅ Bot Token接続成功: {bot_info['user']}")
            print(f"   - Bot ID: {bot_info['user_id']}")
            print(f"   - Team: {bot_info['team']}")
        else:
            print(f"❌ Bot Token接続失敗: {bot_info.get('error')}")
    except Exception as e:
        print(f"❌ Bot Token エラー: {e}")
    
    # User Tokenでテスト（利用可能な場合）
    if user_token:
        print(f"\n📋 User Tokenでの調査:")
        user_client = AsyncWebClient(token=user_token)
        
        try:
            # User情報を取得
            user_info = await user_client.auth_test()
            if user_info["ok"]:
                print(f"✅ User Token接続成功: {user_info['user']}")
                print(f"   - User ID: {user_info['user_id']}")
                print(f"   - Team: {user_info['team']}")
            else:
                print(f"❌ User Token接続失敗: {user_info.get('error')}")
        except Exception as e:
            print(f"❌ User Token エラー: {e}")
    
    # 実際のchannelでの招待テスト（テストチャンネルを作成）
    print(f"\n🧪 GitHub App招待の実際のテスト:")
    print("=" * 50)
    
    if user_token:
        try:
            user_client = AsyncWebClient(token=user_token)
            
            # テストチャンネル作成
            test_channel_name = "test-github-app-invite"
            print(f"📝 テストチャンネル '{test_channel_name}' を作成中...")
            
            channel_response = await user_client.conversations_create(
                name=test_channel_name,
                is_private=True
            )
            
            if channel_response["ok"]:
                test_channel_id = channel_response["channel"]["id"]
                print(f"✅ テストチャンネル作成成功: {test_channel_id}")
                
                # GitHub App招待テスト
                print(f"🤖 GitHub App ({current_github_app_id}) の招待をテスト中...")
                
                try:
                    invite_response = await user_client.conversations_invite(
                        channel=test_channel_id,
                        users=current_github_app_id
                    )
                    
                    if invite_response["ok"]:
                        print(f"✅ GitHub App招待成功!")
                        print("   - 元のエラーは一時的なものだった可能性があります")
                    else:
                        error = invite_response.get("error", "Unknown")
                        print(f"❌ GitHub App招待失敗: {error}")
                        
                        if error == "cant_invite":
                            print("   - cant_inviteエラー: 該当ユーザー/アプリが招待できない状態")
                            print("   - 可能性:")
                            print("     1. GitHub Appが削除またはワークスペースから削除済み")
                            print("     2. アプリの権限設定に問題がある")
                            print("     3. 一時的なSlack APIの問題")
                        elif error == "user_not_found":
                            print("   - user_not_foundエラー: GitHub App IDが存在しない")
                            print("   - GitHub Appが削除された可能性が高い")
                            
                except Exception as e:
                    print(f"❌ 招待テスト実行エラー: {e}")
                
                # テストチャンネル削除
                print(f"🧹 テストチャンネルを削除中...")
                try:
                    await user_client.conversations_archive(channel=test_channel_id)
                    print(f"✅ テストチャンネル削除完了")
                except:
                    print(f"⚠️ テストチャンネル削除に失敗（手動削除が必要）")
                    
            else:
                print(f"❌ テストチャンネル作成失敗: {channel_response.get('error')}")
                
        except Exception as e:
            print(f"❌ 招待テスト準備エラー: {e}")
    else:
        print("❌ User Tokenが必要です（招待テストをスキップ）")
    
    print(f"\n💡 推奨対応:")
    print("=" * 50)
    print("1. GitHub App IDが無効な場合:")
    print("   - Slackワークスペースの設定でGitHub Appを確認")
    print("   - 必要に応じて再インストール")
    print("2. 一時的なエラーの場合:")
    print("   - しばらく時間をおいてから再試行")
    print("3. アプリの権限設定を確認:")
    print("   - Slack App設定でチャンネル招待権限を確認")

if __name__ == "__main__":
    asyncio.run(check_github_app())