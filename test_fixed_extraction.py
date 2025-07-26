# 修正後のURL抽出テスト

import sys
from pathlib import Path
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_fixed_extraction():
    """修正後のURL抽出をテスト"""
    print("🧪 修正後のURL抽出テスト")
    print("=" * 60)
    
    try:
        from core.gmail_oauth_monitor import GmailOAuthMonitor
        
        # Gmail API初期化
        monitor = GmailOAuthMonitor("config/gmail_oauth_credentials.json")
        monitor.authenticate()
        
        # 最近のメールを検索
        since_time = datetime.now() - timedelta(days=3)
        
        messages = monitor.search_emails(
            subject_pattern="ダウンロード用URLのご案内",
            since_time=since_time,
            max_results=3
        )
        
        print(f"📊 検索結果: {len(messages)}件のメール")
        
        if messages:
            print(f"\n📄 最新メッセージで抽出テスト...")
            message_details = monitor.get_message_details(messages[0]['id'])
            
            if message_details:
                # 修正後の抽出メソッドをテスト
                result = monitor.extract_download_url_and_filename(message_details)
                
                if result:
                    url, filename = result
                    print(f"✅ 修正後抽出成功:")
                    print(f"  📁 ファイル名: {filename}")
                    print(f"  🔗 URL: {url}")
                    
                    # このURLでエラー検知テストも実行
                    print(f"\n🔍 エラー検知テスト実行...")
                    try:
                        from services.nextpublishing_service import NextPublishingService
                        service = NextPublishingService()
                        
                        is_downloadable, message = service.check_pdf_downloadable(url)
                        
                        status_icon = "✅" if is_downloadable else "❌"
                        print(f"  {status_icon} PDF検証結果: {message}")
                        
                        # 04_powershell_sample_advanced.docx の特別確認
                        if "04_powershell_sample_advanced" in filename:
                            print(f"\n🎯 特別確認: {filename}")
                            if is_downloadable:
                                print(f"⚠️ エラーファイルなのに正常判定 - 要調査")
                            else:
                                print(f"✅ 正しくエラーファイルとして検出")
                        
                        return True
                        
                    except Exception as e:
                        print(f"  ❌ エラー検知テストエラー: {e}")
                        return False
                
                else:
                    print(f"❌ 修正後も抽出失敗")
                    
                    # メール本文を再確認
                    payload = message_details.get('payload', {})
                    body_text = monitor._extract_body_text(payload)
                    
                    print(f"\n🔧 メール本文再確認:")
                    print(f"本文長: {len(body_text)}文字")
                    print(f"本文サンプル:\n{body_text[:300]}")
                    
                    # 手動でパターンマッチングを確認
                    import re
                    
                    print(f"\n🔍 手動パターンマッチング:")
                    
                    # URLパターン
                    url_patterns = [
                        r'http://trial\.nextpublishing\.jp/upload_46tate/do_download\?n=[^\s\n\r]+',
                        r'http://trial\.nextpublishing\.jp/upload_46tate/do_download[^\s\n\r]*',
                    ]
                    
                    for i, pattern in enumerate(url_patterns):
                        matches = re.findall(pattern, body_text)
                        print(f"  URLパターン {i+1}: {len(matches)}件")
                        if matches:
                            print(f"    例: {matches[0]}")
                    
                    # ファイル名パターン
                    filename_patterns = [
                        r'超原稿用紙\s*\n\s*([^\n\r]+\.docx)',
                        r'アップロードしていただいた[^\n]*\n\s*([^\n\r]+\.docx)',
                        r'([^\s]+\.docx)',
                    ]
                    
                    for i, pattern in enumerate(filename_patterns):
                        matches = re.findall(pattern, body_text)
                        print(f"  ファイル名パターン {i+1}: {len(matches)}件")
                        if matches:
                            print(f"    例: {matches[0]}")
                    
                    return False
            
            else:
                print(f"❌ メッセージ詳細取得失敗")
                return False
        
        else:
            print(f"❌ 対象メールが見つかりませんでした")
            return False
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 修正後のURL抽出テストツール")
    print()
    
    success = test_fixed_extraction()
    
    if success:
        print("\n🎉 修正版URL抽出テスト成功")
        print("Gmail API統合でのエラー検知が正常に動作します")
    else:
        print("\n❌ 修正版URL抽出テスト失敗")
        print("さらなる調整が必要です")
    
    print(f"\nテスト{'成功' if success else '失敗'}: {datetime.now().strftime('%H:%M:%S')}")
    input("\nEnterキーを押して終了...")
    sys.exit(0 if success else 1)