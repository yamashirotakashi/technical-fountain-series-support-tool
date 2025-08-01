#!/usr/bin/env python3
"""
Google Sheets連携のテストスクリプト
N09999でテスト実行
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from google_sheets import GoogleSheetsClient

# 環境変数読み込み
load_dotenv()

async def test_google_sheets():
    """Google Sheets機能のテスト"""
    
    # 設定
    SERVICE_ACCOUNT_PATH = Path(__file__).parent.parent.parent / "config" / "service_account.json"
    PLANNING_SHEET_ID = "17DKsMGQ6krbhY7GIcX0iaeN-y8HcGGVkXt3d4oOckyQ"
    PURCHASE_LIST_SHEET_ID = "1JJ_C3z0txlJWiyEDl0c6OoVD5Ym_IoZJMMf5o76oV4c"
    TEST_N_CODE = "N09999"
    
    print("=== Google Sheets連携テスト ===\n")
    
    # クライアント初期化
    print(f"1. サービスアカウント確認")
    if not SERVICE_ACCOUNT_PATH.exists():
        print(f"   ✗ サービスアカウントファイルが見つかりません: {SERVICE_ACCOUNT_PATH}")
        return
    print(f"   ✓ {SERVICE_ACCOUNT_PATH}")
    
    client = GoogleSheetsClient(str(SERVICE_ACCOUNT_PATH))
    print("   ✓ クライアント初期化完了\n")
    
    # 発行計画シートからデータ取得
    print(f"2. 発行計画シートから {TEST_N_CODE} を検索")
    project_info = await client.get_project_info(PLANNING_SHEET_ID, TEST_N_CODE)
    
    if project_info:
        print("   ✓ プロジェクト情報取得成功:")
        print(f"     - Nコード: {project_info['n_code']}")
        print(f"     - リポジトリ名: {project_info['repository_name']}")
        print(f"     - Slack ID (J列): {project_info['slack_user_id']}")
        print(f"     - GitHub (L列): {project_info['github_account']}")
        print(f"     - メール (S列): {project_info['author_email']}")
        print(f"     - 行番号: {project_info['row_number']}")
        print(f"     - 既存URL (E列): {project_info['book_url']}")
        
        # GitHubユーザー名抽出テスト
        if project_info['github_account']:
            github_username = client.extract_github_username(project_info['github_account'])
            print(f"     - GitHub名抽出: {github_username}")
    else:
        print(f"   ✗ {TEST_N_CODE} が見つかりません")
        print("   → 発行計画シートにN09999のテストデータを追加してください")
        return
    
    # 購入リストから書籍URL取得
    print(f"\n3. 購入リストシートから書籍URL検索")
    book_url = await client.get_book_url_from_purchase_list(PURCHASE_LIST_SHEET_ID, TEST_N_CODE)
    
    if book_url:
        print(f"   ✓ 書籍URL取得成功: {book_url}")
    else:
        print(f"   ✗ 書籍URLが見つかりません")
        print("   → 購入リストシートのM列にN09999、D列にURLを追加してください")
    
    # 手動タスク追加テスト
    print("\n4. 手動タスク管理シートへのテスト書き込み")
    from datetime import datetime
    
    task_id = f"TEST_{TEST_N_CODE}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    task_data = [
        task_id,
        TEST_N_CODE,
        "zn9999-test",
        "slack_invitation",
        "test@example.com",
        "pending",
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "",  # 完了日時
        "山城敬",
        "テスト実行"
    ]
    
    success = await client.append_manual_task(PLANNING_SHEET_ID, task_data)
    if success:
        print(f"   ✓ 手動タスク追加成功: {task_id}")
        print("   → 手動タスク管理シートを確認してください")
    else:
        print("   ✗ 手動タスク追加失敗")
    
    # URL更新テスト（コメントアウト - 実行時は慎重に）
    # print("\n5. E列への書籍URL転記テスト")
    # if book_url and input("E列を更新しますか？ (y/N): ").lower() == 'y':
    #     success = await client.update_book_url(PLANNING_SHEET_ID, TEST_N_CODE, book_url)
    #     if success:
    #         print("   ✓ URL転記成功")
    #     else:
    #         print("   ✗ URL転記失敗")
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    asyncio.run(test_google_sheets())