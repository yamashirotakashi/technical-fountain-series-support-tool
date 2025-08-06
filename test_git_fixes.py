#!/usr/bin/env python3
"""
Git修正のテスト
GitHub認証とWindows権限問題の修正確認
"""
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from core.git_repository_manager import GitRepositoryManager
from core.config_manager import ConfigManager

def test_git_fixes():
    """Git修正のテスト実行"""
    print("=== Git修正テスト開始 ===")
    
    # ConfigManagerをテスト
    try:
        config_manager = ConfigManager()
        validation = config_manager.validate_config()
        print(f"ConfigManager: {len(validation['errors'])} errors, {len(validation['missing_env_vars'])} missing vars")
    except Exception as e:
        print(f"ConfigManager error: {e}")
        return False
    
    # GitRepositoryManagerをテスト
    try:
        git_manager = GitRepositoryManager(config_manager)
        print(f"GitRepositoryManager initialized with cache: {git_manager.cache_dir}")
        
        # GitHub Token確認
        token = os.environ.get('GITHUB_TOKEN')
        if token:
            print(f"GitHub Token found: {token[:10]}...{token[-4:]}")
        else:
            print("No GitHub Token found")
        
        # n2360-2361-chatgptリポジトリをテスト取得
        print("\nTesting repository fetch: n2360-2361-chatgpt")
        repo_path = git_manager.get_repository("n2360-2361-chatgpt")
        
        if repo_path:
            print(f"Repository fetch successful: {repo_path}")
            print(f"Repository exists: {repo_path.exists()}")
            if repo_path.exists():
                print(f"Contents: {list(repo_path.iterdir())[:5]}")  # Show first 5 items
        else:
            print("Repository fetch failed")
            
        # キャッシュ情報を表示
        cache_info = git_manager.get_cache_info()
        print(f"\nCache info: {cache_info['repository_count']} repositories, {cache_info['total_size']} bytes")
        
        return True
        
    except Exception as e:
        print(f"GitRepositoryManager error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_git_fixes()
    if success:
        print("\n=== Git修正テスト完了: 成功 ===")
    else:
        print("\n=== Git修正テスト完了: 失敗 ===")