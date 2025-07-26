#!/usr/bin/env python3
"""03_powershell_sample_basic.docxの修正確認テスト"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_03_file_fix():
    """03ファイルが正常と判定されるか確認"""
    print("=== 03ファイル修正確認テスト ===")
    print(f"実行時刻: {datetime.now().isoformat()}")
    print()
    
    try:
        # モジュールを最新状態で読み込み
        from core.gmail_oauth_monitor import GmailOAuthMonitor
        from services.nextpublishing_service import NextPublishingService
        
        # Gmail API初期化
        print("1. Gmail API認証...")
        gmail_monitor = GmailOAuthMonitor("config/gmail_oauth_credentials.json")
        gmail_monitor.authenticate()
        print("   ✓ 認証成功")
        
        # 過去1時間のメールを検索
        print("\n2. メール検索...")
        since_time = datetime.now() - timedelta(hours=1)
        
        messages = gmail_monitor.search_emails(
            subject_pattern="ダウンロード用URLのご案内",
            since_time=since_time,
            max_results=10
        )
        
        print(f"   検索結果: {len(messages)}件のメール")
        
        # 各ファイルの検証結果を確認
        print("\n3. 各ファイルの検証結果:")
        print("   " + "-" * 60)
        
        service = NextPublishingService()
        results = []
        
        for message in messages:
            message_details = gmail_monitor.get_message_details(message['id'])
            if message_details:
                result = gmail_monitor.extract_download_url_and_filename(message_details)
                if result:
                    url, filename = result
                    
                    # PDF検証実行
                    is_downloadable, message = service.check_pdf_downloadable(url)
                    
                    status = "✓ 正常" if is_downloadable else "✗ エラー"
                    results.append((filename, is_downloadable, message))
                    
                    print(f"   {status} {filename}")
                    print(f"        判定: {message}")
                    print()
        
        # 結果サマリー
        print("4. 結果サマリー:")
        normal_files = [r for r in results if r[1]]
        error_files = [r for r in results if not r[1]]
        
        print(f"   正常ファイル: {len(normal_files)}件")
        for filename, _, message in normal_files:
            print(f"     - {filename}: {message}")
        
        print(f"   エラーファイル: {len(error_files)}件")
        for filename, _, message in error_files:
            print(f"     - {filename}: {message}")
        
        # 03ファイルの確認
        print("\n5. 03ファイルの状態:")
        for filename, is_ok, message in results:
            if "03_powershell_sample_basic.docx" in filename:
                if is_ok:
                    print("   ✓ 修正成功！ 03ファイルは正常と判定されました")
                else:
                    print("   ✗ 修正失敗: 03ファイルがまだエラーと判定されています")
                    print(f"   理由: {message}")
                break
        
        service.close()
        gmail_monitor.close()
        
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_03_file_fix()
        if success:
            print("\nテスト完了")
        else:
            print("\nテスト失敗")
    except KeyboardInterrupt:
        print("\nテスト中断")
    except Exception as e:
        print(f"\n予期しないエラー: {e}")