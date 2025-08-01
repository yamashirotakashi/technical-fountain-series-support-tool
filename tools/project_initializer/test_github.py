#!/usr/bin/env python3
"""
GitHub連携のテストスクリプト
組織リポジトリの作成とコラボレーター追加
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from github_client import GitHubClient

# 環境変数読み込み
load_dotenv()

async def test_github_functions():
    """GitHub機能のテスト"""
    
    # 設定
    GITHUB_TOKEN = os.getenv("GITHUB_ORG_TOKEN")
    if not GITHUB_TOKEN:
        print("✗ GITHUB_ORG_TOKEN環境変数が設定されていません")
        return
    
    print(f"Token from env: {GITHUB_TOKEN[:10]}...")
    
    TEST_N_CODE = "N09999"
    TEST_REPO_NAME = "zn9999-test"
    TEST_GITHUB_USER = "yamashirotakashi"  # テスト用コラボレーター
    
    print("=== GitHub連携テスト ===\n")
    
    # クライアント初期化
    print("1. GitHubクライアント初期化")
    client = GitHubClient(GITHUB_TOKEN)
    print("   ✓ クライアント初期化完了")
    print(f"   組織: {client.ORG_NAME}\n")
    
    # リポジトリの存在確認
    print(f"2. 既存リポジトリ {TEST_REPO_NAME} を確認")
    existing_repo = await client.get_repository(TEST_REPO_NAME)
    
    if existing_repo:
        print(f"   ✓ リポジトリが既に存在: {existing_repo['html_url']}")
        print(f"   - Private: {existing_repo['private']}")
        print(f"   - Created: {existing_repo['created_at']}")
    else:
        print("   → リポジトリが存在しません")
    
    # ユーザーの存在確認
    print(f"\n3. GitHubユーザー {TEST_GITHUB_USER} の存在確認")
    user_exists = await client.check_user_exists(TEST_GITHUB_USER)
    
    if user_exists:
        print(f"   ✓ ユーザーが存在します")
    else:
        print(f"   ✗ ユーザーが見つかりません")
    
    # リポジトリ作成テスト
    print(f"\n4. リポジトリ作成テスト")
    
    if existing_repo:
        print("   → 既存のリポジトリを使用します")
        print("   （新規作成をテストする場合は別のリポジトリ名を使用してください）")
    else:
        print(f"   新規リポジトリ {TEST_REPO_NAME} を作成中...")
        
        repo_info = await client.create_repository(
            TEST_REPO_NAME,
            f"テストリポジトリ - {TEST_N_CODE}",
            private=True
        )
        
        if repo_info:
            print(f"   ✓ リポジトリ作成成功")
            print(f"   - URL: {repo_info['html_url']}")
            print(f"   - Clone URL: {repo_info['clone_url']}")
        else:
            print("   ✗ リポジトリ作成失敗")
            return
    
    # 初期ファイル作成テスト（コメントアウト - 実行時は慎重に）
    # print(f"\n5. 初期ファイル作成テスト")
    # if input("README.mdと.gitignoreを作成しますか？ (y/N): ").lower() == 'y':
    #     success = await client.create_initial_files(TEST_REPO_NAME, TEST_N_CODE)
    #     if success:
    #         print("   ✓ 初期ファイル作成成功")
    #     else:
    #         print("   ✗ 初期ファイル作成失敗")
    
    # コラボレーター追加テスト
    print(f"\n6. コラボレーター追加テスト")
    
    if user_exists:
        print(f"   {TEST_GITHUB_USER} をコラボレーターとして追加中...")
        success = await client.add_collaborator(
            TEST_REPO_NAME,
            TEST_GITHUB_USER,
            permission="push"
        )
        
        if success:
            print("   ✓ コラボレーター追加成功")
            print("   → ユーザーには招待メールが送信されます")
        else:
            print("   ✗ コラボレーター追加失敗")
    else:
        print("   → ユーザーが存在しないためスキップ")
    
    # 完全セットアップのテスト（コメントアウト）
    print(f"\n7. 完全セットアップ機能")
    print("   setup_repository()は以下を一括実行:")
    print("   - リポジトリ作成")
    print("   - 初期ファイル作成")
    print("   - コラボレーター追加")
    print("   → 本番環境での使用を推奨")
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    asyncio.run(test_github_functions())