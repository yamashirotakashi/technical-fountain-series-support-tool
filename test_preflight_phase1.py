"""Phase 1実装テスト: 横書き専用フォーム機能の基本動作確認"""
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from core.preflight.form_settings import Word2XhtmlFormSettings
from core.preflight.word2xhtml_scraper import Word2XhtmlScrapingVerifier
from utils.logger import get_logger


def test_form_settings():
    """フォーム設定のテスト"""
    print("=== フォーム設定テスト ===")
    
    # デフォルト設定のテスト
    settings = Word2XhtmlFormSettings.create_default("test@example.com")
    print(f"デフォルト設定: {settings}")
    
    # バリデーションテスト
    assert settings.validate(), "設定バリデーションが失敗"
    print("✓ バリデーション成功")
    
    # フォームデータ取得テスト
    form_data = settings.get_form_data()
    expected_keys = ['project_name', 'direction', 'tobira', 
                    'tombo', 'syoko', 'index', 'mail', 'mailconf']
    
    for key in expected_keys:
        assert key in form_data, f"フォームデータに{key}が不足"
    
    print("✓ フォームデータ生成成功")
    
    # 横書き専用設定の確認
    assert form_data['direction'] == -10, "横書きレイアウトが正しくない"
    assert form_data['syoko'] == 2, "横書きスタイルが正しくない"
    print("✓ 横書き専用設定確認")
    
    print("フォーム設定テスト完了\n")


def test_scraper_initialization():
    """スクレイパー初期化テスト"""
    print("=== スクレイパー初期化テスト ===")
    
    try:
        scraper = Word2XhtmlScrapingVerifier()
        assert scraper.SERVICE_URL == "http://trial.nextpublishing.jp/upload_46tate/"
        print("✓ スクレイパー初期化成功")
        
        # クリーンアップ
        scraper.cleanup()
        print("✓ クリーンアップ成功")
        
    except Exception as e:
        print(f"✗ スクレイパー初期化エラー: {e}")
        return False
    
    print("スクレイパー初期化テスト完了\n")
    return True


def test_form_validation_edge_cases():
    """フォームバリデーションのエッジケーステスト"""
    print("=== フォームバリデーション エッジケーステスト ===")
    
    # 無効なメールアドレスのテスト
    invalid_emails = ["", "invalid", "no@", "@domain.com", "test@"]
    
    for email in invalid_emails:
        settings = Word2XhtmlFormSettings(email=email)
        assert not settings.validate(), f"無効なメール{email}がバリデーションを通過"
        print(f"✓ 無効メール拒否: {email}")
    
    # 有効なメールアドレスのテスト
    valid_emails = ["test@example.com", "user@domain.co.jp", "yamashiro.takashi@gmail.com"]
    
    for email in valid_emails:
        settings = Word2XhtmlFormSettings(email=email)
        assert settings.validate(), f"有効なメール{email}がバリデーション失敗"
        print(f"✓ 有効メール通過: {email}")
    
    print("フォームバリデーション エッジケーステスト完了\n")


def test_environment_variable_integration():
    """環境変数統合テスト"""
    print("=== 環境変数統合テスト ===")
    
    # 現在の環境変数を保持
    original_email = os.getenv('GMAIL_ADDRESS')
    
    try:
        # テスト用環境変数設定
        test_email = "env_test@example.com"
        os.environ['GMAIL_ADDRESS'] = test_email
        
        # 環境変数からの自動取得テスト
        settings = Word2XhtmlFormSettings.create_default()
        assert settings.email == test_email, "環境変数からのメール取得失敗"
        print(f"✓ 環境変数からメール取得: {test_email}")
        
        # メール確認の自動設定テスト
        assert settings.email_confirm == test_email, "メール確認の自動設定失敗"
        print("✓ メール確認自動設定成功")
        
    finally:
        # 環境変数復元
        if original_email:
            os.environ['GMAIL_ADDRESS'] = original_email
        else:
            os.environ.pop('GMAIL_ADDRESS', None)
    
    print("環境変数統合テスト完了\n")


def main():
    """メインテスト実行"""
    print("Phase 1実装テスト開始: 横書き専用フォーム機能\n")
    
    tests = [
        test_form_settings,
        test_scraper_initialization,
        test_form_validation_edge_cases,
        test_environment_variable_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            result = test()
            if result is not False:  # None or True は成功
                passed += 1
                print("✅ テスト成功")
            else:
                failed += 1
                print("❌ テスト失敗")
        except Exception as e:
            failed += 1
            print(f"❌ テスト例外: {e}")
        print("-" * 50)
    
    print(f"\nテスト結果: 成功 {passed}/{len(tests)}, 失敗 {failed}")
    
    if failed == 0:
        print("🎉 すべてのテストが成功しました！")
        print("Phase 1: 基本機能修正 - 完了")
        return True
    else:
        print("⚠️  一部のテストが失敗しました。修正が必要です。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)