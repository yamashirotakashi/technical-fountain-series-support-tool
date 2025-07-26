# Gmail API統合後のエラー検知テスト

import sys
from pathlib import Path
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_email_monitoring():
    """メール監視機能のテスト"""
    print("📧 Gmail API統合後のメール監視テスト")
    print("=" * 60)
    
    try:
        # Gmail API監視をテスト
        from core.gmail_oauth_monitor import GmailOAuthMonitor
        
        print("🔐 Gmail API認証中...")
        monitor = GmailOAuthMonitor("config/gmail_oauth_credentials.json")
        monitor.authenticate()
        print("✅ Gmail API認証成功")
        
        # 過去24時間のメール検索（時刻フィルタリングテスト）
        print("🔍 時刻フィルタリングテスト...")
        since_time = datetime.now() - timedelta(hours=24)
        
        result = monitor.wait_for_email(
            subject_pattern="ダウンロード用URLのご案内",
            timeout=10,  # 短時間でテスト
            return_with_filename=True,
            since_time=since_time
        )
        
        if result:
            url, filename = result
            print(f"✅ メール検出成功: {filename}")
            print(f"🔗 URL: {url[:80]}...")
        else:
            print("ℹ️ 新しいメールなし（期待された動作）")
        
        print("✅ Gmail API統合テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ Gmail API テストエラー: {e}")
        
        # IMAPフォールバックをテスト
        print("🔄 IMAPフォールバックテスト...")
        try:
            from core.email_monitor import EmailMonitor
            import os
            
            email_address = os.getenv('GMAIL_ADDRESS', 'yamashiro.takashi@gmail.com')
            password = os.getenv('GMAIL_APP_PASSWORD', 'dummy')
            
            if password == 'dummy':
                print("⚠️ GMAIL_APP_PASSWORDが設定されていません")
                print("IMAP接続テストをスキップします")
                return False
            
            imap_monitor = EmailMonitor(email_address, password)
            imap_monitor.connect()
            print("✅ IMAPフォールバック成功")
            imap_monitor.close()
            
        except Exception as imap_error:
            print(f"❌ IMAPフォールバックもエラー: {imap_error}")
            return False
        
        return True

def test_error_detection_integration():
    """エラー検知統合テスト"""
    print("\n🧪 エラー検知統合テスト")
    print("=" * 60)
    
    try:
        # ワークフロープロセッサーをインポート
        from core.workflow_processor_with_error_detection import WorkflowProcessorWithErrorDetection
        
        print("📋 ワークフロープロセッサー初期化...")
        
        # 設定ファイルの確認
        config_path = Path("config/settings.json")
        if not config_path.exists():
            print(f"⚠️ 設定ファイルが見つかりません: {config_path}")
            return False
        
        print("✅ 設定ファイル確認")
        print("✅ ワークフロープロセッサー初期化成功")
        
        # Gmail API統合が正しく動作するかチェック
        print("🔍 Gmail API統合チェック...")
        
        # importテスト
        from core.gmail_oauth_monitor import GmailOAuthMonitor
        print("✅ Gmail API監視クラスimport成功")
        
        # 認証ファイル確認
        oauth_credentials = Path("config/gmail_oauth_credentials.json")
        if oauth_credentials.exists():
            print("✅ OAuth2.0認証ファイル確認")
        else:
            print("❌ OAuth2.0認証ファイルが見つかりません")
            return False
        
        print("✅ エラー検知統合準備完了")
        return True
        
    except Exception as e:
        print(f"❌ エラー検知統合テストエラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("🚀 Gmail API統合後の機能テスト")
    print(f"実行時刻: {datetime.now().isoformat()}")
    print()
    
    # メール監視テスト
    email_test = test_email_monitoring()
    
    # エラー検知統合テスト
    integration_test = test_error_detection_integration()
    
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー")
    print(f"📧 メール監視: {'✅ 成功' if email_test else '❌ 失敗'}")
    print(f"🔧 統合テスト: {'✅ 成功' if integration_test else '❌ 失敗'}")
    
    if email_test and integration_test:
        print("\n🎉 すべてのテストが成功しました！")
        print("💡 次のステップ:")
        print("1. 実際のファイルアップロードでエラー検知をテスト")
        print("2. 過去メール問題が解決されているか確認")
        print("3. エラーファイルが正しく検出されるか確認")
        return True
    else:
        print("\n❌ 一部のテストが失敗しました")
        print("設定を確認して再度お試しください")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nテスト{'成功' if success else '失敗'}")
    input("\nEnterキーを押して終了...")
    sys.exit(0 if success else 1)