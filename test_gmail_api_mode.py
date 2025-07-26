#!/usr/bin/env python3
"""Gmail API方式のテスト"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_gmail_api_mode():
    """Gmail API方式の動作確認"""
    print("=== Gmail API方式テスト ===\n")
    
    try:
        # 1. 処理方式ダイアログの確認
        print("1. 処理方式ダイアログのテスト...")
        from gui.dialogs.process_mode_dialog import ProcessModeDialog
        from PyQt6.QtWidgets import QApplication
        import sys
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        dialog = ProcessModeDialog()
        print(f"   MODE_TRADITIONAL: {dialog.MODE_TRADITIONAL}")
        print(f"   MODE_API: {dialog.MODE_API}")
        print(f"   MODE_GMAIL_API: {dialog.MODE_GMAIL_API}")
        print("   ✓ 処理方式定義OK")
        
        # 2. WorkflowProcessorでのGmail API処理
        print("\n2. WorkflowProcessorのGmail API処理テスト...")
        from core.workflow_processor import WorkflowProcessor
        
        # Gmail API方式でプロセッサを作成
        processor = WorkflowProcessor(
            email_password="GMAIL_API",
            process_mode="gmail_api"
        )
        
        # email_monitorプロパティアクセス
        monitor = processor.email_monitor
        
        if monitor:
            monitor_type = type(monitor).__name__
            print(f"   使用中のモニター: {monitor_type}")
            
            if monitor_type == "GmailOAuthMonitor":
                print("   ✓ Gmail APIモニターが正常に選択されました")
                
                # 認証状態確認
                if hasattr(monitor, 'service') and monitor.service:
                    print("   ✓ Gmail API認証成功")
                else:
                    print("   [警告] Gmail API認証が未完了の可能性")
            else:
                print(f"   [エラー] 期待と異なるモニター: {monitor_type}")
        else:
            print("   [エラー] モニターの初期化に失敗")
        
        # 3. 既存の認証ファイル確認
        print("\n3. 既存の認証ファイル確認...")
        import os
        
        credentials_path = "config/gmail_oauth_credentials.json"
        token_path = "config/gmail_token.pickle"
        
        if os.path.exists(credentials_path):
            print(f"   ✓ 認証情報ファイル存在: {credentials_path}")
        else:
            print(f"   [警告] 認証情報ファイルが見つかりません: {credentials_path}")
        
        if os.path.exists(token_path):
            print(f"   ✓ トークンファイル存在: {token_path}")
            print("   → 既存の認証を再利用可能")
        else:
            print(f"   [情報] トークンファイルなし: {token_path}")
            print("   → 初回実行時にブラウザ認証が必要")
        
        # クリーンアップ
        if processor:
            processor.cleanup()
        
        print("\n✓ Gmail API方式テスト完了")
        
    except Exception as e:
        print(f"\n[エラー] テスト中にエラーが発生: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gmail_api_mode()