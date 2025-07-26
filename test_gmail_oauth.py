#!/usr/bin/env python3
"""
Gmail API OAuth2.0認証テストスクリプト
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_oauth_setup():
    """OAuth2.0認証セットアップのテスト"""
    print("🔐 Gmail API OAuth2.0認証テスト")
    print("=" * 60)
    
    # 認証ファイルの確認
    credentials_path = "config/gmail_oauth_credentials.json"
    if not Path(credentials_path).exists():
        print("❌ OAuth2.0認証ファイルが見つかりません")
        print()
        print("🔧 セットアップ手順:")
        print("1. Google Cloud Console にアクセス:")
        print("   https://console.cloud.google.com/apis/credentials?project=techbook-analytics")
        print()
        print("2. 「+ CREATE CREDENTIALS」> OAuth client ID")
        print()
        print("3. Application type: Desktop application")
        print("   Name: TechZip Gmail Monitor")
        print()
        print("4. ダウンロードしたJSONファイルを以下に保存:")
        print(f"   {Path(credentials_path).absolute()}")
        print()
        return False
    
    print(f"✅ OAuth2.0認証ファイル確認: {credentials_path}")
    
    # ライブラリの確認
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        print("✅ Google OAuth2.0ライブラリ確認")
    except ImportError as e:
        print(f"❌ ライブラリ不足: {e}")
        print("pip install google-auth-oauthlib が必要です")
        return False
    
    return True

def test_gmail_oauth():
    """Gmail API OAuth2.0認証のテスト"""
    if not test_oauth_setup():
        return False
    
    try:
        from core.gmail_oauth_monitor import GmailOAuthMonitor
        
        print()
        print("📧 Gmail OAuth Monitor初期化中...")
        monitor = GmailOAuthMonitor("config/gmail_oauth_credentials.json")
        
        print("🔐 OAuth2.0認証開始...")
        print("ℹ️ ブラウザが開きます。Googleアカウントでログインしてください")
        
        monitor.authenticate()
        print("✅ OAuth2.0認証成功！")
        
        # 最近のメール検索テスト
        print("🔍 最近のメール検索テスト...")
        from datetime import datetime, timedelta
        since_time = datetime.now() - timedelta(hours=24)
        
        messages = monitor.search_emails(
            subject_pattern="ダウンロード用URLのご案内",
            since_time=since_time,
            max_results=5
        )
        
        print(f"📧 検索結果: {len(messages)}件のメール")
        
        # メッセージ詳細取得テスト
        if messages:
            print("📄 最新メッセージ詳細取得テスト...")
            message_details = monitor.get_message_details(messages[0]['id'])
            
            if message_details:
                print("✅ メッセージ詳細取得成功")
                
                # URL/ファイル名抽出テスト
                result = monitor.extract_download_url_and_filename(message_details)
                if result:
                    url, filename = result
                    print(f"✅ URL/ファイル名抽出成功: {filename}")
                    print(f"🔗 URL: {url[:60]}...")
                else:
                    print("⚠️ URL/ファイル名抽出失敗（対象メールなし）")
            else:
                print("❌ メッセージ詳細取得失敗")
        else:
            print("ℹ️ 対象メールなし（期待された動作）")
        
        print("=" * 60)
        print("🎉 Gmail API OAuth2.0認証テスト完了")
        print()
        print("🎯 次のステップ:")
        print("1. 実際のワークフローでGmail APIを使用")
        print("2. IMAPからGmail OAuth APIに切り替え")
        print("3. より精密な時刻フィルタリングを活用")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import エラー: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Gmail OAuth テストエラー: {e}")
        print("\n🔧 トラブルシューティング:")
        print("1. OAuth2.0認証ファイルが正しく配置されているか確認")
        print("2. Gmail API が有効化されているか確認")
        print("3. 正しいGoogleアカウントでログインしているか確認")
        return False

def quick_start_guide():
    """クイックスタートガイド"""
    print("🚀 Gmail API OAuth2.0 クイックスタートガイド")
    print()
    print("📋 必要な手順:")
    print("1. [⏳] Google Cloud Console でOAuth2.0クライアントIDを作成")
    print("2. [⏳] 認証ファイルを config/gmail_oauth_credentials.json に配置")
    print("3. [⏳] テストスクリプトを実行")
    print()
    print("🔗 参考リンク:")
    print("Google Cloud Console:")
    print("https://console.cloud.google.com/apis/credentials?project=techbook-analytics")
    print()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--guide":
        quick_start_guide()
    else:
        success = test_gmail_oauth()
        sys.exit(0 if success else 1)