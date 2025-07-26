#!/usr/bin/env python3
"""Word2XHTML5のメール検出テスト（シンプル版）"""
import os
import sys
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.email_monitor import EmailMonitor

# .envファイルから環境変数を読み込み
env_path = project_root / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

def test_simple_email_detection():
    """シンプルなメール検出テスト"""
    email_address = os.getenv('GMAIL_ADDRESS')
    email_password = os.getenv('GMAIL_APP_PASSWORD')
    
    if not email_address or not email_password:
        print("エラー: 環境変数GMAIL_ADDRESSとGMAIL_APP_PASSWORDを設定してください")
        return
    
    print(f"メールアドレス: {email_address}")
    
    # 元のEmailMonitorを使用
    monitor = EmailMonitor(email_address, email_password)
    monitor.connect()
    
    # Word2XHTML5のメールを検索（件名で検索）
    print("\n件名で検索を開始...")
    url = monitor.wait_for_email(
        subject_pattern="ダウンロード用URLのご案内",
        timeout=60,  # 1分でタイムアウト
        check_interval=5
    )
    
    if url:
        print(f"\n成功！ダウンロードURL: {url}")
    else:
        print("\nメールが見つかりませんでした")
    
    monitor.close()

if __name__ == "__main__":
    test_simple_email_detection()