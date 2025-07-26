# Gmail API OAuth2.0認証テストスクリプト (Windows対応版)

import os
import sys
import pickle
import json
from pathlib import Path
from datetime import datetime, timedelta

def test_oauth_setup():
    """OAuth2.0認証セットアップのテスト"""
    print("🔐 Gmail API OAuth2.0認証テスト")
    print("=" * 60)
    
    # 認証ファイルの確認
    credentials_path = Path("config/gmail_oauth_credentials.json")
    if not credentials_path.exists():
        print("❌ OAuth2.0認証ファイルが見つかりません")
        print(f"   期待されるパス: {credentials_path.absolute()}")
        return False
    
    print(f"✅ OAuth2.0認証ファイル確認: {credentials_path}")
    
    # ライブラリの確認
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        print("✅ Google OAuth2.0ライブラリ確認")
    except ImportError as e:
        print(f"❌ ライブラリ不足: {e}")
        print("pip install google-auth-oauthlib google-api-python-client が必要です")
        return False
    
    return True

def test_gmail_oauth():
    """Gmail API OAuth2.0認証のテスト"""
    if not test_oauth_setup():
        return False
    
    try:
        print()
        print("📧 Gmail OAuth認証開始...")
        
        # 必要なライブラリをインポート
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        
        # Gmail APIスコープ
        scopes = ['https://www.googleapis.com/auth/gmail.readonly']
        credentials_path = "config/gmail_oauth_credentials.json"
        token_path = "config/gmail_token.pickle"
        
        creds = None
        
        # 既存のトークンファイルを確認
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
                print("📁 既存の認証トークンを発見")
        
        # 認証情報が無効または存在しない場合
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    print("🔄 認証トークンをリフレッシュ中...")
                    creds.refresh(Request())
                    print("✅ 認証トークンをリフレッシュしました")
                except Exception as e:
                    print(f"⚠️ 認証リフレッシュ失敗: {e}")
                    creds = None
            
            if not creds:
                # 新規OAuth2.0フロー
                print("🌐 ブラウザでOAuth2.0認証を開始...")
                print("ℹ️ ブラウザが開きます。Googleアカウントでログインしてください")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, scopes)
                creds = flow.run_local_server(port=0)
                print("✅ OAuth2.0認証を完了しました")
            
            # トークンを保存
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
                print("💾 認証トークンを保存しました")
        
        # Gmail APIサービスを構築
        service = build('gmail', 'v1', credentials=creds)
        print("✅ Gmail API接続成功")
        
        # プロフィール情報を取得してテスト
        print("👤 Gmailプロフィール情報を取得中...")
        profile = service.users().getProfile(userId='me').execute()
        print(f"📧 メールアドレス: {profile.get('emailAddress')}")
        print(f"📊 総メッセージ数: {profile.get('messagesTotal')}")
        
        # 最近のメール検索テスト
        print("🔍 最近のメール検索テスト...")
        since_time = datetime.now() - timedelta(hours=24)
        
        # 検索クエリを構築
        query_parts = ['subject:"ダウンロード用URLのご案内"']
        epoch_timestamp = int(since_time.timestamp())
        query_parts.append(f'after:{epoch_timestamp}')
        query = ' '.join(query_parts)
        
        print(f"🔍 検索クエリ: {query}")
        
        # メールを検索
        result = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=5
        ).execute()
        
        messages = result.get('messages', [])
        print(f"📧 検索結果: {len(messages)}件のメール")
        
        # 一般的なメール検索もテスト
        print("🔍 一般的なメール検索テスト...")
        general_result = service.users().messages().list(
            userId='me',
            maxResults=3
        ).execute()
        
        general_messages = general_result.get('messages', [])
        print(f"📧 最新メール: {len(general_messages)}件")
        
        if general_messages:
            # 最新メッセージの詳細を取得
            latest_message = service.users().messages().get(
                userId='me',
                id=general_messages[0]['id'],
                format='metadata',
                metadataHeaders=['Subject', 'From', 'Date']
            ).execute()
            
            # ヘッダー情報を表示
            headers = latest_message.get('payload', {}).get('headers', [])
            for header in headers:
                if header['name'] in ['Subject', 'From', 'Date']:
                    print(f"📄 {header['name']}: {header['value']}")
        
        print("=" * 60)
        print("🎉 Gmail API OAuth2.0認証テスト完了")
        print()
        print("🎯 テスト結果:")
        print("✅ OAuth2.0認証成功")
        print("✅ Gmail API接続成功")
        print("✅ メール検索機能動作確認")
        print()
        print("🚀 次のステップ:")
        print("1. 実際のワークフローでGmail APIを使用")
        print("2. IMAPからGmail OAuth APIに切り替え")
        print("3. より精密な時刻フィルタリングを活用")
        
        return True
        
    except ImportError as e:
        print(f"❌ ライブラリImportエラー: {e}")
        print("必要なライブラリをインストールしてください:")
        print("pip install google-auth-oauthlib google-api-python-client")
        return False
        
    except Exception as e:
        print(f"❌ Gmail OAuth テストエラー: {e}")
        print(f"エラータイプ: {type(e).__name__}")
        print(f"エラー詳細: {str(e)}")
        print()
        print("🔧 トラブルシューティング:")
        print("1. OAuth2.0認証ファイルが正しく配置されているか確認")
        print("2. Gmail API が有効化されているか確認")
        print("3. 正しいGoogleアカウントでログインしているか確認")
        print("4. ネットワーク接続を確認")
        return False

if __name__ == "__main__":
    print("🚀 Gmail API OAuth2.0テスト")
    print(f"Python実行環境: {sys.executable}")
    print(f"作業ディレクトリ: {os.getcwd()}")
    print(f"Pythonバージョン: {sys.version}")
    print()
    
    success = test_gmail_oauth()
    
    if success:
        print("\n✅ すべてのテストが成功しました！")
        print("Gmail APIが正常に動作しています。")
    else:
        print("\n❌ テストに失敗しました。")
        print("設定を確認して再度お試しください。")
    
    print("\nEnterキーを押して終了...")
    input()
    sys.exit(0 if success else 1)