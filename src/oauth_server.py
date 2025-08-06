#!/usr/bin/env python3
"""
Slack OAuth認証サーバー（User Token取得用）

このスクリプトを実行して、ブラウザでlocalhost:8888にアクセスし、
管理者権限でSlack認証を行うことでUser Tokenを取得できます。
"""
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import webbrowser
import requests

# ConfigManagerをインポート
try:
    from src.slack_pdf_poster import ConfigManager
except ImportError:
    ConfigManager = None

def get_oauth_config():
    """OAuth設定を取得"""
    config_manager = ConfigManager() if ConfigManager else None
    if config_manager:
        return {
            'client_id': config_manager.get("api.slack.client_id", "266696553856.9282469142480"),
            'client_secret': config_manager.get("api.slack.client_secret", "2f6e8c88de63e41694597f17d4d8b5fa"),
            'redirect_uri': config_manager.get("oauth.redirect_uri", "http://localhost:8888/callback")
        }
    else:
        # フォールバック値
        return {
            'client_id': "266696553856.9282469142480",
            'client_secret': "2f6e8c88de63e41694597f17d4d8b5fa", 
            'redirect_uri': "http://localhost:8888/callback"
        }

# OAuth設定を取得
oauth_config = get_oauth_config()
CLIENT_ID = oauth_config['client_id']
CLIENT_SECRET = oauth_config['client_secret']
REDIRECT_URI = oauth_config['redirect_uri']

# 必要なUser Scopes
USER_SCOPES = [
    "channels:read",
    "groups:read",
    "groups:write",
    "users:read"
]

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == "/":
            # 認証開始
            auth_url = f"https://slack.com/oauth/v2/authorize?" \
                      f"client_id={CLIENT_ID}&" \
                      f"user_scope={','.join(USER_SCOPES)}&" \
                      f"redirect_uri={REDIRECT_URI}"
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = f"""
            <html>
            <head><title>TechZip Slack認証</title></head>
            <body>
                <h1>TechZip Bot 管理者認証</h1>
                <p>Botの一括チャネル招待を行うため、管理者権限での認証が必要です。</p>
                <p><a href="{auth_url}" style="
                    background-color: #4CAF50;
                    color: white;
                    padding: 14px 20px;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                ">Slackで認証</a></p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        elif parsed_path.path == "/callback":
            # 認証コールバック
            query = parse_qs(parsed_path.query)
            code = query.get('code', [None])[0]
            
            if code:
                # アクセストークンを取得
                # Slack OAuth URL設定から取得
                slack_oauth_url = os.getenv('SLACK_OAUTH_URL', 'https://slack.com/api/oauth.v2.access')
                response = requests.post(slack_oauth_url, data={
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'code': code,
                    'redirect_uri': REDIRECT_URI
                })
                
                data = response.json()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                if data.get('ok'):
                    user_token = data.get('authed_user', {}).get('access_token')
                    
                    # トークンを保存
                    with open('.slack_user_token', 'w') as f:
                        json.dump({
                            'user_token': user_token,
                            'user_id': data.get('authed_user', {}).get('id'),
                            'team_id': data.get('team', {}).get('id')
                        }, f, indent=2)
                    
                    html = f"""
                    <html>
                    <body>
                        <h1>認証成功！</h1>
                        <p>User Token: <code>{user_token[:20]}...{user_token[-10:]}</code></p>
                        <p>このトークンを使って一括招待スクリプトを実行できます。</p>
                        <p>ウィンドウを閉じて、ターミナルに戻ってください。</p>
                    </body>
                    </html>
                    """
                else:
                    html = f"""
                    <html>
                    <body>
                        <h1>認証失敗</h1>
                        <p>エラー: {data.get('error', 'Unknown error')}</p>
                    </body>
                    </html>
                    """
                
                self.wfile.write(html.encode())
                
                # サーバーを停止
                if data.get('ok'):
                    self.server.shutdown()
            
    def log_message(self, format, *args):
        pass  # ログを抑制

def main():
    print("🚀 Slack OAuth認証サーバーを起動します...")
    print(f"ブラウザで http://localhost:8888 にアクセスしてください")
    print("\n⚠️  注意: Client Secretを設定してください！")
    print("1. https://api.slack.com/apps/A097K6HTULW/general")
    print("2. App CredentialsセクションのClient Secretをコピー")
    print("3. このスクリプトのCLIENT_SECRET変数に設定\n")
    
    # 自動的にブラウザを開く
    webbrowser.open('http://localhost:8888')
    
    # サーバー起動
    httpd = HTTPServer(('localhost', 8888), OAuthHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    main()