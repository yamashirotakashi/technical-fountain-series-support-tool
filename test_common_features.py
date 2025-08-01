"""
共通機能統合テスト
Phase 1-3: 設定管理、認証管理、ログ管理の動作確認
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.common import settings_manager, auth_manager, get_logger


def test_settings_manager():
    """設定管理のテスト"""
    print("\n=== 設定管理テスト ===")
    
    # 設定の取得
    theme = settings_manager.get("app.theme")
    print(f"現在のテーマ: {theme}")
    
    # 設定の更新
    settings_manager.set("app.log_level", "DEBUG")
    print(f"ログレベル: {settings_manager.get('app.log_level')}")
    
    # プラグイン設定
    plugin_settings = {
        "test_mode": True,
        "window_position": [100, 100]
    }
    settings_manager.save_plugin_settings("TestPlugin", plugin_settings)
    
    # プラグイン設定の取得
    loaded = settings_manager.get_plugin_settings("TestPlugin")
    print(f"プラグイン設定: {loaded}")
    
    print("✓ 設定管理テスト完了")


def test_auth_manager():
    """認証管理のテスト"""
    print("\n=== 認証管理テスト ===")
    
    # Git認証情報の保存（テスト用）
    success = auth_manager.store_git_credentials(
        "https://github.com/test/repo.git",
        "test_user",
        "test_token"
    )
    print(f"Git認証情報保存: {'成功' if success else '失敗'}")
    
    # Git認証情報の取得
    creds = auth_manager.get_git_credentials("https://github.com/test/repo.git")
    if creds:
        print(f"取得したユーザー名: {creds['username']}")
    
    # 保存されている認証情報のリスト
    stored = auth_manager.list_stored_credentials()
    print(f"保存されている認証情報: {len(stored)}件")
    
    # テスト用認証情報の削除
    auth_manager.delete_credentials(
        auth_manager.AUTH_TYPE_GIT,
        "https://github.com/test/repo.git"
    )
    
    print("✓ 認証管理テスト完了")


def test_log_manager():
    """ログ管理のテスト"""
    print("\n=== ログ管理テスト ===")
    
    # 通常のロガー
    logger = get_logger("test.common")
    logger.info("共通機能のテストを開始します")
    logger.debug("デバッグメッセージ")
    logger.warning("警告メッセージ")
    
    # プラグイン用ロガー
    plugin_logger = get_logger("test.plugin", plugin_name="TestPlugin")
    plugin_logger.info("プラグインロガーのテスト")
    plugin_logger.error("エラーメッセージのテスト")
    
    print("✓ ログ管理テスト完了")


def test_plugin_integration():
    """プラグインとの統合テスト"""
    print("\n=== プラグイン統合テスト ===")
    
    # プラグインローダーのインポート
    from app.launcher.plugin_loader import PluginLoader
    
    loader = PluginLoader()
    plugins = loader.discover_plugins()
    print(f"発見したプラグイン: {plugins}")
    
    # プラグインのロード
    for plugin_name in plugins[:1]:  # 最初の1つだけテスト
        plugin = loader.load_plugin(plugin_name)
        if plugin:
            print(f"ロード成功: {plugin.metadata.name}")
            
            # プラグインの設定を確認
            config = plugin.config
            print(f"プラグイン設定: {config}")
            
            # プラグインのログを確認
            plugin.logger.info("統合テストからのログ")
    
    print("✓ プラグイン統合テスト完了")


def main():
    """メイン処理"""
    print("=== 共通機能統合テスト ===")
    print("Phase 1-3: 設定管理、認証管理、ログ管理のテスト")
    
    # 各機能のテスト
    test_settings_manager()
    test_auth_manager()
    test_log_manager()
    test_plugin_integration()
    
    print("\n=== すべてのテストが完了しました ===")


if __name__ == "__main__":
    main()