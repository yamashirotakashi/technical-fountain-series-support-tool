"""PyInstaller ランタイムフック - EXE実行時の初期設定（拡張版）"""

import os
import sys
import json
import shutil
from pathlib import Path

# EXE環境であることを明示的に設定
os.environ['TECHZIP_IS_EXE'] = '1'

# ユーザーディレクトリの確認と作成
user_dir = Path.home() / '.techzip'
user_dir.mkdir(exist_ok=True)

# 必要なサブディレクトリを作成
subdirs = ['config', 'logs', 'temp', 'cache']
for subdir in subdirs:
    (user_dir / subdir).mkdir(exist_ok=True)

# 開発環境からの設定コピー機能
def copy_development_settings():
    """開発環境の設定をユーザーディレクトリにコピー（初回のみ）"""
    
    # settings.jsonのコピーと調整
    user_settings = user_dir / 'config' / 'settings.json'
    if not user_settings.exists() and hasattr(sys, '_MEIPASS'):
        dev_settings = Path(sys._MEIPASS) / 'config' / 'settings.json'
        if dev_settings.exists():
            # settings.jsonを読み込んで調整
            with open(dev_settings, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # Google Sheets認証ファイルのパスを調整
            if 'google_sheet' in settings and 'credentials_path' in settings['google_sheet']:
                creds_path = settings['google_sheet']['credentials_path']
                # 絶対パスまたは古い形式の場合、config/ファイル名形式に修正
                if os.path.isabs(creds_path) or creds_path == "google_service_account.json":
                    # ファイル名を取得（techbook-analytics-aa03914c6639.jsonなど）
                    if creds_path == "google_service_account.json":
                        # 実際のファイルを探す
                        config_dir = user_dir / 'config'
                        for file in config_dir.glob('*.json'):
                            if 'techbook-analytics' in file.name or 'service_account' in file.name:
                                filename = file.name
                                break
                        else:
                            filename = "techbook-analytics-aa03914c6639.json"  # デフォルト
                    else:
                        filename = os.path.basename(creds_path)
                    
                    settings['google_sheet']['credentials_path'] = f"config/{filename}"
            
            # 調整した設定を保存
            with open(user_settings, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            print(f"開発環境の設定をコピーしました: {user_settings}")
    
    # Gmail OAuth認証ファイルのコピー
    user_gmail_oauth = user_dir / 'config' / 'gmail_oauth_credentials.json'
    if not user_gmail_oauth.exists() and hasattr(sys, '_MEIPASS'):
        dev_gmail_oauth = Path(sys._MEIPASS) / 'config' / 'gmail_oauth_credentials.json'
        if dev_gmail_oauth.exists():
            shutil.copy2(dev_gmail_oauth, user_gmail_oauth)
            print(f"Gmail OAuth認証ファイルをコピーしました: {user_gmail_oauth}")

# 開発環境の.envから設定を読み込んでテンプレートに反映
def create_env_template_with_defaults():
    """開発環境の設定を反映したテンプレートを作成"""
    
    # デフォルト値を開発環境から取得
    default_values = {}
    
    # PyInstallerでバンドルされた.envファイルがある場合
    if hasattr(sys, '_MEIPASS'):
        bundled_env = Path(sys._MEIPASS) / '.env.template'
        if bundled_env.exists():
            try:
                with open(bundled_env, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            default_values[key.strip()] = value.strip()
            except Exception as e:
                print(f"開発環境設定の読み込みエラー: {e}")
    
    # 環境変数ファイルのテンプレート作成
    env_template = user_dir / '.env.template'
    env_content = f"""# TechZip環境設定ファイル
# このファイルを .env にコピーして実際の値を設定してください
# デフォルト値は開発環境から引き継がれています

# Gmail設定（IMAP/SMTP用）
GMAIL_ADDRESS={default_values.get('GMAIL_ADDRESS', 'your-email@gmail.com')}
GMAIL_APP_PASSWORD={default_values.get('GMAIL_APP_PASSWORD', 'your-app-password')}

# Slack設定
SLACK_BOT_TOKEN={default_values.get('SLACK_BOT_TOKEN', 'xoxb-your-slack-bot-token')}

# GitHub設定
GITHUB_TOKEN={default_values.get('GITHUB_TOKEN', 'your-github-token')}

# Google Sheets設定
GOOGLE_SHEETS_ID={default_values.get('GOOGLE_SHEETS_ID', 'YOUR_SHEET_ID_HERE')}
GOOGLE_SHEETS_CREDENTIALS_PATH={default_values.get('GOOGLE_SHEETS_CREDENTIALS_PATH', 'config/google_service_account.json')}

# NextPublishing API設定
NEXTPUBLISHING_API_KEY={default_values.get('NEXTPUBLISHING_API_KEY', 'your-api-key')}
NEXTPUBLISHING_API_SECRET={default_values.get('NEXTPUBLISHING_API_SECRET', 'your-api-secret')}

# Word2XHTML5設定
WORD2XHTML5_USERNAME={default_values.get('WORD2XHTML5_USERNAME', 'your-username')}
WORD2XHTML5_PASSWORD={default_values.get('WORD2XHTML5_PASSWORD', 'your-password')}

# デバッグ設定
DEBUG_MODE={default_values.get('DEBUG_MODE', 'false')}
LOG_LEVEL={default_values.get('LOG_LEVEL', 'INFO')}
"""
    
    env_template.write_text(env_content, encoding='utf-8')
    
    # .envファイルが存在しない場合、開発環境の値で初期化
    env_file = user_dir / '.env'
    if not env_file.exists() and default_values:
        env_file.write_text(env_content, encoding='utf-8')
        print(f"開発環境の設定で.envファイルを初期化しました: {env_file}")

# 初回実行時のメッセージファイル作成
first_run_file = user_dir / '.first_run'
if not first_run_file.exists():
    # 開発環境の設定をコピー
    copy_development_settings()
    create_env_template_with_defaults()
    
    first_run_file.write_text(f"""
TechZip 1.5 - 初回実行

設定ファイルとログは以下のディレクトリに保存されます:
{user_dir}

開発環境の設定が自動的にコピーされました。
必要に応じて以下の設定を確認・更新してください:

1. {user_dir}/.env - 認証情報の設定
2. {user_dir}/config/settings.json - アプリケーション設定
3. Gmail OAuth認証ファイル（設定済みの場合）

メニューバー > ツール > 設定 から設定画面を開くこともできます。
""", encoding='utf-8')
    
    # 初回実行フラグ
    os.environ['TECHZIP_FIRST_RUN'] = '1'
else:
    # 既存ユーザーの場合も設定テンプレートを更新
    create_env_template_with_defaults()

# Pythonパスの調整（EXE内のモジュールを確実に見つけられるように）
if hasattr(sys, '_MEIPASS'):
    # PyInstallerの一時展開ディレクトリ
    sys.path.insert(0, sys._MEIPASS)