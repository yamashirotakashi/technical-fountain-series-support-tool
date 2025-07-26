#!/usr/bin/env python3
"""Gmail API統合テスト"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_gmail_api_mode():
    """Gmail APIモードのテスト"""
    print("=== Gmail API統合テスト ===\n")
    
    try:
        # 設定確認
        from utils.config import get_config
        config = get_config()
        
        use_gmail_api = config.get('email', {}).get('use_gmail_api', False)
        print(f"1. Gmail API使用設定: {use_gmail_api}")
        
        if not use_gmail_api:
            print("\n[情報] Gmail APIは無効です。")
            print("有効にするには config/settings.json で 'use_gmail_api': true に設定してください。")
            return
        
        # WorkflowProcessorでの動作確認
        print("\n2. WorkflowProcessorでの初期化テスト...")
        from core.workflow_processor import WorkflowProcessor
        
        # Gmail APIモードでは email_password は不要
        processor = WorkflowProcessor(email_password="GMAIL_API")
        
        # email_monitorプロパティアクセス時に初期化される
        monitor = processor.email_monitor
        
        if monitor is None:
            print("   [エラー] メールモニターの初期化に失敗しました")
            return
        
        # 正しい実装が使われているか確認
        monitor_type = type(monitor).__name__
        print(f"   使用中のモニター: {monitor_type}")
        
        if monitor_type == "GmailOAuthMonitor":
            print("   ✓ Gmail APIモニターが正常に初期化されました")
        else:
            print(f"   [警告] 期待と異なるモニタータイプ: {monitor_type}")
        
        # 認証状態確認
        if hasattr(monitor, 'service') and monitor.service:
            print("   ✓ Gmail API認証成功")
        else:
            print("   [警告] Gmail API認証が完了していない可能性があります")
        
        print("\n3. メール検索テスト...")
        # 最近のメールを検索
        from datetime import datetime, timedelta
        since_time = datetime.now() - timedelta(hours=1)
        
        messages = monitor.search_emails(
            subject_pattern="ダウンロード用URLのご案内",
            since_time=since_time,
            max_results=5
        )
        
        print(f"   検索結果: {len(messages)}件のメール")
        
        # クリーンアップ
        processor.cleanup()
        print("\n✓ Gmail API統合テスト完了")
        
    except Exception as e:
        print(f"\n[エラー] テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

def check_imap_mode():
    """IMAPモードの確認"""
    print("\n=== IMAPモード確認 ===\n")
    
    from utils.config import get_config
    config = get_config()
    
    # use_gmail_api を false に設定
    config['email']['use_gmail_api'] = False
    
    print("1. IMAPモードでの初期化テスト...")
    from core.workflow_processor import WorkflowProcessor
    
    # IMAPモードでは email_password が必要
    import os
    email_password = os.getenv('GMAIL_APP_PASSWORD', 'dummy_password')
    
    processor = WorkflowProcessor(email_password=email_password)
    monitor = processor.email_monitor
    
    if monitor:
        monitor_type = type(monitor).__name__
        print(f"   使用中のモニター: {monitor_type}")
        
        if monitor_type == "EmailMonitor":
            print("   ✓ IMAPモニターが正常に初期化されました")
        else:
            print(f"   [警告] 期待と異なるモニタータイプ: {monitor_type}")
    else:
        print("   [情報] パスワードが設定されていないため、モニターは初期化されませんでした")
    
    # クリーンアップ
    if processor:
        processor.cleanup()

if __name__ == "__main__":
    test_gmail_api_mode()
    print("\n" + "="*50)
    check_imap_mode()