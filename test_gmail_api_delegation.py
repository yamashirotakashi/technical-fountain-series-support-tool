#!/usr/bin/env python3
"""
Gmail API Domain-wide Delegation テストスクリプト
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_gmail_api_delegation():
    """Gmail API Domain-wide Delegationのテスト"""
    print("🧪 Gmail API Domain-wide Delegation テスト")
    print("=" * 60)
    
    try:
        from core.gmail_api_monitor import GmailAPIMonitor
        
        # Gmail API Monitorを初期化
        print("📧 Gmail API Monitor初期化中...")
        monitor = GmailAPIMonitor()
        
        # 認証テスト
        print("🔐 Gmail API認証テスト...")
        monitor.authenticate()
        print("✅ 認証成功！")
        
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
        print("🎉 Gmail API Domain-wide Delegation テスト完了")
        return True
        
    except ImportError as e:
        print(f"❌ Import エラー: {e}")
        print("必要なライブラリがインストールされていません")
        return False
        
    except Exception as e:
        print(f"❌ Gmail API テストエラー: {e}")
        print("\n🔧 トラブルシューティング:")
        print("1. Google Cloud Console で Gmail API が有効化されているか確認")
        print("2. サービスアカウントで Domain-wide delegation が有効か確認")
        print("3. Google Admin Console で API クライアントアクセスが設定されているか確認")
        print("4. 正しいスコープ（gmail.readonly）が設定されているか確認")
        
        return False

def check_prerequisites():
    """前提条件チェック"""
    print("🔍 前提条件チェック...")
    
    # 認証ファイル確認
    credentials_path = "/mnt/c/Users/tky99/dev/techbookanalytics/config/techbook-analytics-aa03914c6639.json"
    if Path(credentials_path).exists():
        print("✅ サービスアカウント認証ファイル確認")
    else:
        print(f"❌ 認証ファイルが見つかりません: {credentials_path}")
        return False
    
    # ライブラリ確認
    try:
        import google.oauth2.service_account
        import googleapiclient.discovery
        print("✅ Google API ライブラリ確認")
    except ImportError as e:
        print(f"❌ ライブラリ不足: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Gmail API Domain-wide Delegation 設定テスト")
    print()
    
    if not check_prerequisites():
        print("❌ 前提条件が満たされていません")
        sys.exit(1)
    
    success = test_gmail_api_delegation()
    
    if success:
        print("\n🎯 次のステップ:")
        print("1. 実際のワークフローでGmail APIを使用")
        print("2. IMAPからGmail APIに切り替え")
        print("3. より精密な時刻フィルタリングを活用")
    else:
        print("\n🔧 Domain-wide Delegation設定を完了してください")
    
    sys.exit(0 if success else 1)