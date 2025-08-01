#!/usr/bin/env python3
"""
別Bot（技術の泉シリーズ招待Bot）を使用したGitHub App招待テスト
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from slack_sdk.web.async_client import AsyncWebClient

async def test_alternative_bot_invitation():
    """別BotでのGitHub App招待をテスト"""
    
    # .envファイルを読み込み
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ .envファイルを読み込み: {env_file}")
    
    # 環境変数から取得
    invitation_bot_token = os.getenv("SLACK_INVITATION_BOT_TOKEN")
    user_token = os.getenv("SLACK_USER_TOKEN")
    
    if not invitation_bot_token:
        print("❌ SLACK_INVITATION_BOT_TOKEN が設定されていません")
        print("💡 設定方法:")
        print("   1. .envファイルに以下を追加:")
        print("      SLACK_INVITATION_BOT_TOKEN=xoxb-your-invitation-bot-token")
        print("   2. 技術の泉シリーズ招待BotのBot Tokenを設定")
        return
    
    if not user_token:
        print("❌ SLACK_USER_TOKEN が設定されていません")
        return
    
    print(f"🔍 別Bot Token: {invitation_bot_token[:20]}...")
    print(f"🔍 User Token: {user_token[:20]}...")
    
    # 別BotでのGitHub App招待テスト
    github_app_id = "UA8BZ8ENT"
    
    try:
        # User Tokenでテストチャンネル作成
        user_client = AsyncWebClient(token=user_token)
        
        test_channel_name = "test-alt-bot-invite"
        print(f"\n📝 テストチャンネル '{test_channel_name}' を作成中...")
        
        channel_response = await user_client.conversations_create(
            name=test_channel_name,
            is_private=True
        )
        
        if channel_response["ok"]:
            test_channel_id = channel_response["channel"]["id"]
            print(f"✅ テストチャンネル作成成功: {test_channel_id}")
            
            # 別BotでGitHub App招待
            print(f"\n🤖 別Bot ({invitation_bot_token[:20]}...) でGitHub App招待テスト:")
            
            alt_client = AsyncWebClient(token=invitation_bot_token)
            
            # 別Botの認証確認
            bot_auth = await alt_client.auth_test()
            if bot_auth["ok"]:
                print(f"✅ 別Bot認証成功: {bot_auth['user']} (ID: {bot_auth['user_id']})")
            else:
                print(f"❌ 別Bot認証失敗: {bot_auth.get('error')}")
                return
            
            # GitHub App招待実行
            try:
                invite_response = await alt_client.conversations_invite(
                    channel=test_channel_id,
                    users=github_app_id
                )
                
                if invite_response["ok"]:
                    print(f"✅ 別BotによるGitHub App招待成功!")
                    print(f"   - 解決策が見つかりました")
                else:
                    error = invite_response.get("error", "Unknown")
                    print(f"❌ 別BotによるGitHub App招待失敗: {error}")
                    
                    # 詳細エラー情報
                    if "errors" in invite_response:
                        print(f"   - 詳細: {invite_response['errors']}")
                    
                    if error == "cant_invite":
                        print(f"   - 結論: 別Botでも同じ制限が適用されている")
                        print(f"   - GitHub App特有の制限の可能性が高い")
                    elif error == "not_in_channel":
                        print(f"   - 別Botもチャンネルのメンバーでない")
                        print(f"   - 別Botをチャンネルに招待してから再試行が必要")
                        
            except Exception as e:
                print(f"❌ 別Bot招待実行エラー: {e}")
            
            # テストチャンネル削除
            try:
                await user_client.conversations_archive(channel=test_channel_id)
                print(f"🧹 テストチャンネル削除完了")
            except:
                print(f"⚠️ テストチャンネル削除失敗")
                
        else:
            error = channel_response.get("error", "Unknown")
            print(f"❌ テストチャンネル作成失敗: {error}")
            
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
    
    print(f"\n💡 まとめ:")
    print("=" * 50)
    print("1. 手動招待(/invite @GitHub)は成功している")
    print("2. User TokenによるAPI招待は失敗")
    print("3. 別BotによるAPI招待の結果により判断:")
    print("   - 成功 → 別Botを使用した実装を採用")
    print("   - 失敗 → GitHub App特有の制限のため手動招待を推奨")

if __name__ == "__main__":
    asyncio.run(test_alternative_bot_invitation())