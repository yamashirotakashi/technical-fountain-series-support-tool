#!/usr/bin/env python3
"""
現在のワークスペースで利用可能なGitHub関連のアプリ/ボットを探すスクリプト
conversations.members APIを使用してチャンネルメンバーから探す
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from slack_sdk.web.async_client import AsyncWebClient

async def find_github_apps():
    """GitHub関連のアプリを探す"""
    
    # .envファイルを読み込み
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ .envファイルを読み込み: {env_file}")
    
    # Slack User Tokenを取得
    user_token = os.getenv("SLACK_USER_TOKEN")
    if not user_token:
        print("❌ SLACK_USER_TOKEN not found")
        return
    
    client = AsyncWebClient(token=user_token)
    
    try:
        print("\n🔍 チャンネル一覧からGitHub関連アプリを探します:")
        print("=" * 60)
        
        # チャンネル一覧を取得
        channels_response = await client.conversations_list(
            types="public_channel,private_channel",
            limit=100
        )
        
        github_apps_found = set()
        
        if channels_response["ok"]:
            for channel in channels_response["channels"]:
                channel_name = channel["name"]
                channel_id = channel["id"]
                
                # GitHubに関連しそうなチャンネルをチェック
                if any(keyword in channel_name.lower() for keyword in ["github", "git"]):
                    print(f"\n📋 チャンネル: #{channel_name} ({channel_id})")
                    
                    try:
                        # チャンネルメンバーを取得
                        members_response = await client.conversations_members(channel=channel_id)
                        
                        if members_response["ok"]:
                            print(f"   メンバー数: {len(members_response['members'])}人")
                            
                            # メンバーの詳細を確認（GitHub関連のボット/アプリを探す）
                            for member_id in members_response["members"]:
                                if member_id.startswith("U") and len(member_id) == 11:  # ユーザーIDの形式
                                    # ユーザー情報を取得する代わりに、IDパターンを記録
                                    if "github" in channel_name.lower():
                                        github_apps_found.add(member_id)
                                        print(f"   - 候補ID: {member_id}")
                        
                    except Exception as e:
                        print(f"   ⚠️ メンバー取得エラー: {e}")
        
        # 管理チャンネルもチェック
        admin_channel_id = "C0980EXAZD1"  # -管理channel
        print(f"\n📋 管理チャンネル ({admin_channel_id}) をチェック:")
        
        try:
            members_response = await client.conversations_members(channel=admin_channel_id)
            
            if members_response["ok"]:
                print(f"   メンバー数: {len(members_response['members'])}人")
                
                for member_id in members_response["members"]:
                    if member_id.startswith("U") and len(member_id) == 11:
                        github_apps_found.add(member_id)
                        print(f"   - 管理チャンネルメンバー: {member_id}")
                        
        except Exception as e:
            print(f"   ⚠️ 管理チャンネルメンバー取得エラー: {e}")
        
        print(f"\n🔍 発見されたユーザー/アプリID一覧:")
        print("=" * 60)
        for app_id in sorted(github_apps_found):
            print(f"   ID: {app_id}")
            
            # 招待テストを実行
            try:
                # テストチャンネル作成
                test_channel_response = await client.conversations_create(
                    name=f"test-invite-{app_id.lower()}",
                    is_private=True
                )
                
                if test_channel_response["ok"]:
                    test_channel_id = test_channel_response["channel"]["id"]
                    
                    # 招待テスト
                    invite_response = await client.conversations_invite(
                        channel=test_channel_id,
                        users=app_id
                    )
                    
                    if invite_response["ok"]:
                        print(f"      ✅ 招待可能: {app_id}")
                    else:
                        error = invite_response.get("error", "Unknown")
                        print(f"      ❌ 招待失敗: {app_id} ({error})")
                    
                    # テストチャンネル削除
                    await client.conversations_archive(channel=test_channel_id)
                    
            except Exception as e:
                print(f"      ⚠️ テストエラー: {app_id} - {e}")
        
        print(f"\n💡 GitHub App更新の提案:")
        print("=" * 60)
        print("1. 招待可能なIDが見つかった場合:")
        print("   - slack_client.py の GITHUB_APP_ID を更新")
        print("2. 招待可能なIDが見つからない場合:")
        print("   - GitHub Appをワークスペースに再インストール")
        print("   - または GitHub App招待を一時的に無効化")
        
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    asyncio.run(find_github_apps())