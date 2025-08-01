#!/usr/bin/env python3
"""
GitHubトークンの権限と組織アクセスを確認
"""

import asyncio
import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def check_github_access():
    """GitHubアクセス権限を確認"""
    
    token = os.getenv("GITHUB_ORG_TOKEN")
    if not token:
        print("GITHUB_ORG_TOKEN not found")
        return
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    print("=== GitHubトークン権限確認 ===\n")
    
    async with aiohttp.ClientSession() as session:
        # 1. 認証ユーザー情報
        print("1. 認証ユーザー情報")
        async with session.get("https://api.github.com/user", headers=headers) as response:
            if response.status == 200:
                user_data = await response.json()
                print(f"   ✓ ユーザー: {user_data['login']}")
                print(f"   - Name: {user_data.get('name', 'N/A')}")
                print(f"   - Email: {user_data.get('email', 'N/A')}")
            else:
                print(f"   ✗ 認証エラー: {response.status}")
                return
        
        # 2. 組織へのアクセス
        print("\n2. 組織アクセス確認")
        async with session.get("https://api.github.com/user/orgs", headers=headers) as response:
            if response.status == 200:
                orgs = await response.json()
                print(f"   アクセス可能な組織: {len(orgs)}個")
                for org in orgs:
                    print(f"   - {org['login']}")
                    
                # irdtechbook組織が含まれているか確認
                if any(org['login'] == 'irdtechbook' for org in orgs):
                    print("\n   ✓ irdtechbook組織へのアクセス確認")
                else:
                    print("\n   ✗ irdtechbook組織へのアクセスがありません")
        
        # 3. irdtechbook組織の詳細確認
        print("\n3. irdtechbook組織の詳細")
        async with session.get("https://api.github.com/orgs/irdtechbook", headers=headers) as response:
            if response.status == 200:
                org_data = await response.json()
                print(f"   ✓ 組織名: {org_data['name']}")
                print(f"   - リポジトリ数: {org_data['public_repos'] + org_data.get('total_private_repos', 0)}")
            else:
                print(f"   ✗ 組織情報取得エラー: {response.status}")
        
        # 4. リポジトリ作成権限の確認
        print("\n4. irdtechbook組織でのメンバーシップ確認")
        async with session.get("https://api.github.com/user/memberships/orgs/irdtechbook", headers=headers) as response:
            if response.status == 200:
                membership = await response.json()
                print(f"   ✓ ロール: {membership['role']}")
                print(f"   - 状態: {membership['state']}")
                
                if membership['role'] == 'admin':
                    print("   ✓ 管理者権限があります（リポジトリ作成可能）")
                else:
                    print("   ⚠ メンバー権限です（組織設定によってはリポジトリ作成不可）")
            else:
                print(f"   ✗ メンバーシップ確認エラー: {response.status}")
        
        # 5. スコープの確認
        print("\n5. トークンのスコープ確認")
        # rate limitエンドポイントでヘッダーからスコープを取得
        async with session.get("https://api.github.com/rate_limit", headers=headers) as response:
            if response.status == 200:
                scopes = response.headers.get('X-OAuth-Scopes', '').split(', ')
                print("   付与されているスコープ:")
                for scope in scopes:
                    if scope:
                        print(f"   - {scope}")
                
                # 必要なスコープの確認
                required_scopes = ['repo', 'admin:org']
                missing_scopes = [s for s in required_scopes if not any(scope.startswith(s) for scope in scopes)]
                
                if missing_scopes:
                    print(f"\n   ⚠ 不足しているスコープ: {', '.join(missing_scopes)}")
                else:
                    print("\n   ✓ 必要なスコープはすべて付与されています")

if __name__ == "__main__":
    asyncio.run(check_github_access())