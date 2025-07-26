"""Phase 1基本テスト: フォーム設定のみのテスト（Selenium不使用）"""
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# Seleniumなしでテスト可能な部分のみ
try:
    from core.preflight.form_settings import Word2XhtmlFormSettings
    print("✓ form_settings.py インポート成功")
except ImportError as e:
    print(f"✗ form_settings.py インポートエラー: {e}")
    sys.exit(1)


def test_form_settings():
    """フォーム設定のテスト"""
    print("\n=== フォーム設定テスト ===")
    
    # デフォルト設定のテスト
    settings = Word2XhtmlFormSettings.create_default("test@example.com")
    print(f"デフォルト設定:\n{settings}")
    
    # バリデーションテスト
    if settings.validate():
        print("✓ バリデーション成功")
    else:
        print("✗ バリデーション失敗")
        return False
    
    # フォームデータ取得テスト
    form_data = settings.get_form_data()
    expected_keys = ['project_name', 'direction', 'tobira', 
                    'tombo', 'syoko', 'index', 'mail', 'mailconf']
    
    for key in expected_keys:
        if key not in form_data:
            print(f"✗ フォームデータに{key}が不足")
            return False
    
    print("✓ フォームデータ生成成功")
    print(f"フォームデータ: {form_data}")
    
    # 横書き専用設定の確認
    if form_data['direction'] != -10:
        print(f"✗ 横書きレイアウトが正しくない: {form_data['direction']}")
        return False
    print("✓ 横書きレイアウト設定確認")
    
    if form_data['syoko'] != 2:
        print(f"✗ 横書きスタイルが正しくない: {form_data['syoko']}")
        return False
    print("✓ 横書きスタイル設定確認")
    
    return True


def test_form_validation_edge_cases():
    """フォームバリデーションのエッジケーステスト"""
    print("\n=== フォームバリデーション エッジケーステスト ===")
    
    # 無効なメールアドレスのテスト
    invalid_emails = ["", "invalid", "no@", "@domain.com", "test@"]
    
    for email in invalid_emails:
        settings = Word2XhtmlFormSettings(email=email)
        if settings.validate():
            print(f"✗ 無効なメール{email}がバリデーションを通過")
            return False
        print(f"✓ 無効メール拒否: {email}")
    
    # 有効なメールアドレスのテスト
    valid_emails = ["test@example.com", "user@domain.co.jp", "yamashiro.takashi@gmail.com"]
    
    for email in valid_emails:
        settings = Word2XhtmlFormSettings(email=email)
        if not settings.validate():
            print(f"✗ 有効なメール{email}がバリデーション失敗")
            return False
        print(f"✓ 有効メール通過: {email}")
    
    return True


def test_environment_variable_integration():
    """環境変数統合テスト"""
    print("\n=== 環境変数統合テスト ===")
    
    # 現在の環境変数を保持
    original_email = os.getenv('GMAIL_ADDRESS')
    
    try:
        # テスト用環境変数設定
        test_email = "env_test@example.com"
        os.environ['GMAIL_ADDRESS'] = test_email
        
        # 環境変数からの自動取得テスト
        settings = Word2XhtmlFormSettings.create_default()
        if settings.email != test_email:
            print(f"✗ 環境変数からのメール取得失敗: 期待値{test_email}, 実際{settings.email}")
            return False
        print(f"✓ 環境変数からメール取得: {test_email}")
        
        # メール確認の自動設定テスト
        if settings.email_confirm != test_email:
            print(f"✗ メール確認の自動設定失敗: 期待値{test_email}, 実際{settings.email_confirm}")
            return False
        print("✓ メール確認自動設定成功")
        
        return True
        
    finally:
        # 環境変数復元
        if original_email:
            os.environ['GMAIL_ADDRESS'] = original_email
        elif 'GMAIL_ADDRESS' in os.environ:
            del os.environ['GMAIL_ADDRESS']


def test_form_settings_values():
    """フォーム設定値の詳細テスト"""
    print("\n=== フォーム設定値詳細テスト ===")
    
    settings = Word2XhtmlFormSettings.create_default("yamashiro.takashi@gmail.com")
    
    # 各設定値の確認
    expected_values = {
        'project_name': '山城技術の泉',
        'layout_orientation': -10,  # 横（B5技術書）
        'cover_page': 0,           # 扉なし
        'crop_marks': 0,           # トンボなし
        'style_selection': 2,      # 本文（ソースコード）※実際の値
        'index_page': 0,           # 索引なし
    }
    
    for key, expected in expected_values.items():
        actual = getattr(settings, key)
        if actual != expected:
            print(f"✗ {key}: 期待値{expected}, 実際{actual}")
            return False
        print(f"✓ {key}: {actual}")
    
    return True


def main():
    """メインテスト実行"""
    print("Phase 1基本テスト開始: フォーム設定機能（Selenium不使用）")
    
    tests = [
        ("フォーム設定基本テスト", test_form_settings),
        ("フォーム設定値詳細テスト", test_form_settings_values),
        ("バリデーションエッジケーステスト", test_form_validation_edge_cases),
        ("環境変数統合テスト", test_environment_variable_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'-'*50}")
        print(f"実行中: {test_name}")
        
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"✅ {test_name} 成功")
            else:
                failed += 1
                print(f"❌ {test_name} 失敗")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} 例外: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'-'*50}")
    print(f"テスト結果: 成功 {passed}/{len(tests)}, 失敗 {failed}")
    
    if failed == 0:
        print("🎉 すべての基本テストが成功しました！")
        print("Phase 1: 基本機能修正（フォーム設定部分） - 完了")
        return True
    else:
        print("⚠️  一部のテストが失敗しました。修正が必要です。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)