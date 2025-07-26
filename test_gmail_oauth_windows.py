#!/usr/bin/env python3
"""
Gmail API OAuth2.0認証テストスクリプト (Windows版)
"""

import os
import sys
from pathlib import Path

# Windows環境での実行を確認
if os.name == 'nt':
    # Windows環境
    project_root = Path(__file__).parent
else:
    # WSL環境
    project_root = Path(__file__).parent

sys.path.insert(0, str(project_root))

def test_oauth_setup():
    """OAuth2.0認証セットアップのテスト"""
    print("🔐 Gmail API OAuth2.0認証テスト (Windows版)")
    print("=" * 60)
    
    # 認証ファイルの確認
    credentials_path = project_root / "config" / "gmail_oauth_credentials.json"
    if not credentials_path.exists():
        print("❌ OAuth2.0認証ファイルが見つかりません")
        print(f"   期待されるパス: {credentials_path}")
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
        # Windows環境用のパス調整
        sys.path.insert(0, str(project_root))
        
        print()
        print("📧 Gmail OAuth Monitor初期化中...")
        
        # 直接インポートして初期化
        import pickle
        import base64
        import json
        import re
        from datetime import datetime, timedelta
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        
        # Gmail APIスコープ
        scopes = ['https://www.googleapis.com/auth/gmail.readonly']
        credentials_path = project_root / "config" / "gmail_oauth_credentials.json"
        token_path = project_root / "config" / "gmail_token.pickle"
        
        creds = None
        
        # 既存のトークンファイルを確認
        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # 認証情報が無効または存在しない場合
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    print("✅ OAuth2.0認証をリフレッシュしました")
                except Exception as e:
                    print(f"⚠️ 認証リフレッシュ失敗: {e}")
                    creds = None
            
            if not creds:
                # 新規OAuth2.0フロー
                print("🔐 OAuth2.0認証開始...")
                print("ℹ️ ブラウザが開きます。Googleアカウントでログインしてください")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path), scopes)
                creds = flow.run_local_server(port=0)
                print("✅ 新しいOAuth2.0認証を完了しました")
            
            # トークンを保存
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # Gmail APIサービスを構築
        service = build('gmail', 'v1', credentials=creds)
        print("✅ Gmail API認証成功")
        
        # 最近のメール検索テスト
        print("🔍 最近のメール検索テスト...")
        since_time = datetime.now() - timedelta(hours=24)
        
        # 検索クエリを構築
        query_parts = ['subject:"ダウンロード用URLのご案内"']
        epoch_timestamp = int(since_time.timestamp())
        query_parts.append(f'after:{epoch_timestamp}')
        query = ' '.join(query_parts)
        
        print(f"Gmail検索クエリ: {query}")
        
        # メールを検索
        result = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=5
        ).execute()
        
        messages = result.get('messages', [])
        print(f"📧 検索結果: {len(messages)}件のメール")
        
        # メッセージ詳細取得テスト
        if messages:
            print("📄 最新メッセージ詳細取得テスト...")
            message = service.users().messages().get(
                userId='me',
                id=messages[0]['id'],
                format='full'
            ).execute()
            
            if message:
                print("✅ メッセージ詳細取得成功")
                
                # ヘッダーから件名を取得
                headers = message.get('payload', {}).get('headers', [])
                subject = None
                for header in headers:
                    if header['name'] == 'Subject':
                        subject = header['value']
                        break
                
                print(f"📧 件名: {subject}")
                
                # 簡単な本文確認
                payload = message.get('payload', {})
                if 'parts' in payload:
                    print("✅ マルチパートメッセージ確認")
                else:
                    print("✅ シンプルメッセージ確認")
                
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
        print(f"エラー詳細: {type(e).__name__}: {str(e)}")
        print("\n🔧 トラブルシューティング:")
        print("1. OAuth2.0認証ファイルが正しく配置されているか確認")
        print("2. Gmail API が有効化されているか確認")
        print("3. 正しいGoogleアカウントでログインしているか確認")
        return False

if __name__ == "__main__":
    print("🚀 Gmail API OAuth2.0テスト (Windows版)")
    print(f"Python実行パス: {sys.executable}")
    print(f"作業ディレクトリ: {Path.cwd()}")
    print()
    
    success = test_gmail_oauth()
    
    if success:
        print("\n✅ テスト成功！Gmail APIが使用可能です")
    else:
        print("\n❌ テスト失敗。設定を確認してください")
    
    input("\nEnterキーを押して終了...")
    sys.exit(0 if success else 1)