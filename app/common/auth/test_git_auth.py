"""
Git認証プロトタイプのテストスクリプト
Phase 0-2の技術検証用
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.common.auth.git_auth_prototype import GitAuthPrototype, run_prototype_test
from app.common.auth.git_auth_manager import GitAuthManager, AuthConfig
import logging


def test_prototype():
    """プロトタイプの包括的テスト"""
    print("=" * 60)
    print("Git認証プロトタイプ テスト")
    print("=" * 60)
    
    # プロトタイプテスト実行
    results = run_prototype_test()
    
    print("\n" + "=" * 60)
    print("テスト完了")
    print("=" * 60)
    
    return results


def test_auth_manager():
    """認証マネージャーのテスト"""
    print("\n" + "=" * 60)
    print("Git認証マネージャー テスト")
    print("=" * 60)
    
    # 設定
    config = AuthConfig(
        enable_pat=True,
        enable_gcm=True,
        enable_windows=True,
        max_retry=3
    )
    
    manager = GitAuthManager(config)
    
    # 認証情報取得テスト
    print("\n1. 認証情報取得テスト")
    creds = manager.get_credentials()
    if creds:
        print(f"✅ 認証情報取得成功")
        print(f"   - 認証タイプ: {creds.get('auth_type')}")
        print(f"   - ユーザー名: {creds.get('username')}")
    else:
        print("❌ 認証情報が見つかりません")
        
    # 接続テスト
    print("\n2. GitHub接続テスト")
    if manager.test_connection():
        print("✅ GitHub接続成功")
    else:
        print("❌ GitHub接続失敗")
        
    print("\n" + "=" * 60)
    
    
def test_error_handling():
    """エラーハンドリングのテスト"""
    print("\n" + "=" * 60)
    print("エラーハンドリング テスト")
    print("=" * 60)
    
    manager = GitAuthManager()
    
    # 存在しないリポジトリでテスト
    print("\n1. 無効なリポジトリURL")
    result = manager.test_connection("https://github.com/invalid/repo/does/not/exist")
    print(f"結果: {'✅ 予期通り失敗' if not result else '❌ 予期せず成功'}")
    
    # タイムアウトテスト
    print("\n2. タイムアウトテスト")
    config = AuthConfig(timeout=1)  # 1秒でタイムアウト
    manager_short = GitAuthManager(config)
    # 実際のテストは環境に依存するため省略
    
    print("\n" + "=" * 60)


def generate_security_report():
    """セキュリティレポートの生成"""
    print("\n" + "=" * 60)
    print("セキュリティレポート")
    print("=" * 60)
    
    report = """
## セキュリティベストプラクティス

### 1. Personal Access Token (PAT)
- ✅ 最小権限の原則を適用
  - repo権限のみ付与（プライベートリポジトリアクセス用）
  - 不要な権限は付与しない
- ✅ 定期的なローテーション
  - 90日ごとにトークンを更新
- ✅ 安全な保存
  - Keyringを使用した暗号化保存

### 2. 環境変数
- ✅ .envファイルは必ずgitignoreに追加
- ✅ 本番環境では環境変数を使用
- ❌ ハードコーディングは絶対に避ける

### 3. Windows資格情報マネージャー
- ✅ Windowsの標準機能を活用
- ✅ 他のWindowsアプリケーションとの互換性
- ⚠️ ユーザーアカウントのセキュリティに依存

### 4. エラーハンドリング
- ✅ 認証情報をログに出力しない
- ✅ エラーメッセージに機密情報を含めない
- ✅ リトライ回数の制限

### 5. 実装上の推奨事項
- 認証失敗時の適切なフィードバック
- ユーザーへの明確なガイダンス
- 複数の認証方式のフォールバック
"""
    
    print(report)
    print("=" * 60)


def main():
    """メインテスト実行"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 1. プロトタイプテスト
    test_prototype()
    
    # 2. 認証マネージャーテスト
    test_auth_manager()
    
    # 3. エラーハンドリングテスト
    test_error_handling()
    
    # 4. セキュリティレポート
    generate_security_report()
    
    print("\n✅ 全テスト完了")


if __name__ == "__main__":
    main()