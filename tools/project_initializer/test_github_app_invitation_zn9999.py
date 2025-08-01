#!/usr/bin/env python3
"""
zn9999-testチャンネルでのGitHub App招待テスト
ChatGPT推奨のBot Token優先アプローチを検証
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

async def test_github_app_invitation_zn9999():
    """zn9999-testチャンネルでGitHub App招待をテスト"""
    
    # .envファイルを読み込み
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ .envファイルを読み込み: {env_file}")
    
    # 環境変数から取得
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    user_token = os.getenv("SLACK_USER_TOKEN")
    
    if not bot_token:
        print("❌ SLACK_BOT_TOKEN が設定されていません")
        return
        
    if not user_token:
        print("❌ SLACK_USER_TOKEN が設定されていません")
        return
    
    print(f"🔍 Bot Token: {bot_token[:20]}...")
    print(f"🔍 User Token: {user_token[:20]}...")
    
    # テスト対象チャンネル
    test_channel_id = "C097P9PFFAB"  # zn9999-test
    test_channel_name = "zn9999-test"
    github_app_id = "UA8BZ8ENT"
    
    print(f"\\n🎯 テスト対象: #{test_channel_name} ({test_channel_id})")
    print(f"GitHub App ID: {github_app_id}")
    
    try:
        # Bot Tokenクライアント
        bot_client = AsyncWebClient(token=bot_token)
        user_client = AsyncWebClient(token=user_token)
        
        # Bot認証確認
        print(f"\\n🤖 Bot認証確認:")
        bot_auth = await bot_client.auth_test()
        if bot_auth["ok"]:
            print(f"✅ Bot認証成功: {bot_auth['user']} (ID: {bot_auth['user_id']})")
        else:
            print(f"❌ Bot認証失敗: {bot_auth.get('error')}")
            return
        
        # User認証確認
        print(f"\\n👤 User認証確認:")
        user_auth = await user_client.auth_test()
        if user_auth["ok"]:
            print(f"✅ User認証成功: {user_auth['user']} (ID: {user_auth['user_id']})")
        else:
            print(f"❌ User認証失敗: {user_auth.get('error')}")
            return
        
        # チャンネル情報確認（User Tokenで試行）
        print(f"\\n📋 チャンネル情報確認:")
        try:
            channel_info = await user_client.conversations_info(channel=test_channel_id)
            if channel_info["ok"]:
                channel = channel_info["channel"]
                print(f"✅ チャンネル存在確認: #{channel['name']} (プライベート: {channel['is_private']})")
            else:
                print(f"❌ チャンネル情報取得失敗: {channel_info.get('error')}")
                # チャンネル情報取得失敗でもテストを続行
                print(f"⚠️ チャンネル情報取得失敗でもテストを続行します")
        except Exception as e:
            print(f"❌ チャンネル情報取得エラー: {e}")
            print(f"⚠️ チャンネル情報取得失敗でもテストを続行します")
        
        # GitHub App招待テスト（3段階アプローチ）
        print(f"\\n🚀 GitHub App招待テスト開始:")
        print("=" * 60)
        
        github_app_invite_success = False
        
        # 方法1: Bot Token招待（ChatGPT推奨アプローチ）
        print(f"\\n1️⃣ Bot Token招待テスト (ChatGPT推奨方式):")
        try:
            invite_response = await bot_client.conversations_invite(
                channel=test_channel_id,
                users=github_app_id
            )
            
            if invite_response["ok"]:
                print(f"✅ Bot Token招待成功! 🎉")
                print(f"   - 解決策: Bot Tokenアプローチが有効")
                github_app_invite_success = True
            else:
                error = invite_response.get("error", "Unknown")
                print(f"❌ Bot Token招待失敗: {error}")
                
                # ChatGPTの指摘に基づくエラー分析
                if error == "cant_invite":
                    print(f"   - 原因: Bot Token でも cant_invite エラー")
                    print(f"   - 分析: Botがチャンネルメンバーでない可能性")
                elif error == "not_in_channel":
                    print(f"   - 原因: Botがチャンネルのメンバーではない")
                elif error == "user_not_found":
                    print(f"   - 原因: GitHub App IDが無効")
                    
        except SlackApiError as e:
            error_code = e.response.get('error', 'Unknown')
            print(f"❌ Bot Token招待API エラー: {error_code}")
        except Exception as e:
            print(f"❌ Bot Token招待実行エラー: {e}")
        
        # 方法2: User Token招待（従来アプローチ）
        if not github_app_invite_success:
            print(f"\\n2️⃣ User Token招待テスト (従来方式):")
            try:
                invite_response = await user_client.conversations_invite(
                    channel=test_channel_id,
                    users=github_app_id
                )
                
                if invite_response["ok"]:
                    print(f"✅ User Token招待成功!")
                    print(f"   - 解決策: User Tokenアプローチが有効")
                    github_app_invite_success = True
                else:
                    error = invite_response.get("error", "Unknown")
                    print(f"❌ User Token招待失敗: {error}")
                    
                    if error == "cant_invite":
                        print(f"   - 原因: User Token でも cant_invite エラー")
                        print(f"   - 分析: GitHub App特有の制限")
                    elif error == "not_in_channel":
                        print(f"   - 原因: Userがチャンネルのメンバーではない")
                        
            except SlackApiError as e:
                error_code = e.response.get('error', 'Unknown')
                print(f"❌ User Token招待API エラー: {error_code}")
            except Exception as e:
                print(f"❌ User Token招待実行エラー: {e}")
        
        # 結果サマリー
        print(f"\\n📊 テスト結果サマリー:")
        print("=" * 60)
        if github_app_invite_success:
            print(f"🎉 成功! GitHub App招待が完了しました")
            print(f"✅ 実装で使用すべきアプローチが確認できました")
        else:
            print(f"❌ 全ての招待方法が失敗")
            print(f"💡 推奨対応:")
            print(f"   1. 手動招待: /invite @GitHub をチャンネルで実行")
            print(f"   2. GitHub App状態確認: App が有効か確認")
            print(f"   3. 別のテスト環境での確認")
        
        print(f"\\n📋 詳細分析:")
        print(f"   - Bot Token優先アプローチ (ChatGPT推奨): {'✅ 成功' if github_app_invite_success else '❌ 失敗'}")
        print(f"   - 手動招待 (/invite @GitHub): ✅ 確認済み (成功)")
        print(f"   - GitHub App ID (UA8BZ8ENT): 有効性要確認")
        
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")

if __name__ == "__main__":
    asyncio.run(test_github_app_invitation_zn9999())