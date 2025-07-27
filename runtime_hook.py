"""PyInstaller ランタイムフック - EXE実行時の初期設定"""

import os
import sys
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

# 初回実行時のメッセージファイル作成
first_run_file = user_dir / '.first_run'
if not first_run_file.exists():
    first_run_file.write_text("""
TechZip 1.5 - 初回実行

設定ファイルとログは以下のディレクトリに保存されます:
{}

必要な設定:
1. .env ファイルを作成して認証情報を設定
2. Gmail OAuth認証ファイルを配置
3. Google Sheets APIサービスアカウントファイルを配置

詳細はドキュメントを参照してください。
""".format(user_dir), encoding='utf-8')
    
    # 初回実行フラグ
    os.environ['TECHZIP_FIRST_RUN'] = '1'

# 環境変数ファイルのテンプレート作成
env_template = user_dir / '.env.template'
if not env_template.exists():
    env_template.write_text("""# TechZip環境設定ファイル
# このファイルを .env にコピーして実際の値を設定してください

# Gmail設定（IMAP/SMTP用）
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password

# Slack設定
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token

# Google Sheets設定
GOOGLE_SHEETS_ID=YOUR_SHEET_ID_HERE
GOOGLE_SHEETS_CREDENTIALS_PATH=config/google_service_account.json

# その他の設定
DEBUG_MODE=false
LOG_LEVEL=INFO
""", encoding='utf-8')

# Pythonパスの調整（EXE内のモジュールを確実に見つけられるように）
if hasattr(sys, '_MEIPASS'):
    # PyInstallerの一時展開ディレクトリ
    sys.path.insert(0, sys._MEIPASS)