# 04_powershell_sample_advanced.docxのURL検証

import sys
from pathlib import Path
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def verify_error_file_url():
    """04_powershell_sample_advanced.docxのURL詳細検証"""
    print("=== ERROR FILE URL VERIFICATION ===")
    print("Checking 04_powershell_sample_advanced.docx URL handling")
    print(f"Execution time: {datetime.now().isoformat()}")
    print()
    
    try:
        from core.gmail_oauth_monitor import GmailOAuthMonitor
        from services.nextpublishing_service import NextPublishingService
        
        # Gmail API初期化
        print("1. Searching for 04_powershell_sample_advanced.docx...")
        monitor = GmailOAuthMonitor("config/gmail_oauth_credentials.json")
        monitor.authenticate()
        
        # 過去24時間から検索
        since_time = datetime.now() - timedelta(hours=24)
        
        messages = monitor.search_emails(
            subject_pattern="ダウンロード用URLのご案内",
            since_time=since_time,
            max_results=50
        )
        
        print(f"Found {len(messages)} emails")
        
        # 04_powershell_sample_advanced.docxを探す
        target_found = False
        target_url = None
        target_filename = None
        
        for i, message in enumerate(messages):
            message_details = monitor.get_message_details(message['id'])
            if not message_details:
                continue
            
            result = monitor.extract_download_url_and_filename(message_details)
            if result:
                url, filename = result
                
                if "04_powershell_sample_advanced" in filename:
                    print(f"TARGET FOUND: {filename}")
                    target_url = url
                    target_filename = filename
                    target_found = True
                    break
        
        if not target_found:
            print("ERROR: 04_powershell_sample_advanced.docx not found")
            return False
        
        print(f"Target filename: {target_filename}")
        print(f"Target URL: {target_url}")
        print()
        
        # 既知のエラーURLと比較
        known_error_url = "http://trial.nextpublishing.jp/upload_46tate/do_download_pdf?n=JxTuFEr0iW9GiYUABueS3fqC%2F1BOwNeUZPoxHmahvbZ7Un8uFh5wwtnoEgJPDiaI%2F9A9qikFnxiGZe4b%2F%2B9xMQ%3D%3D"
        
        print("2. URL Comparison:")
        print(f"Found URL:      {target_url}")
        print(f"Known Error URL: {known_error_url}")
        print()
        
        # URLの違いをチェック
        if 'do_download_pdf' in target_url:
            print("ANALYSIS: Found URL contains 'do_download_pdf' - This IS an error URL")
        elif 'do_download' in target_url:
            print("ANALYSIS: Found URL contains 'do_download' - This is a download URL")
        else:
            print("ANALYSIS: URL pattern unknown")
        
        print()
        
        # 両方のURLをテスト
        service = NextPublishingService()
        
        print("3. Testing Found URL:")
        print(f"URL: {target_url}")
        
        # 手動HTTPリクエスト
        response = service.session.get(target_url, timeout=30, allow_redirects=True)
        
        print(f"Status: {response.status_code}")
        print(f"Final URL: {response.url}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'None')}")
        
        content_start = response.content[:50] if response.content else b''
        print(f"Content start: {content_start}")
        
        # リダイレクト確認
        if str(response.url) != target_url:
            print(f"REDIRECT DETECTED:")
            print(f"  From: {target_url}")
            print(f"  To:   {response.url}")
            
            if 'do_download_pdf' in str(response.url):
                print("  -> Redirected to ERROR PAGE (do_download_pdf)")
            else:
                print("  -> Redirected to unknown page")
        else:
            print("NO REDIRECT - Direct response")
        
        # 内容分析
        if content_start.startswith(b'<html') or content_start.startswith(b'<!DOCTYPE'):
            print("CONTENT: HTML page")
            html_content = response.content.decode('utf-8', errors='ignore')
            if 'ファイルの作成に失敗' in html_content:
                print("  -> ERROR PAGE detected")
            else:
                print("  -> Regular HTML page")
                
        elif content_start.startswith(b'%PDF'):
            print("CONTENT: PDF file")
            
        elif content_start.startswith(b'PK'):
            print("CONTENT: ZIP file")
            print("  -> This should NOT happen for error files!")
            
        else:
            print(f"CONTENT: Unknown type ({content_start})")
        
        print()
        
        # 現在の検出メソッドをテスト
        print("4. Current Detection Method:")
        is_downloadable, message = service.check_pdf_downloadable(target_url)
        
        print(f"Result: {'DOWNLOADABLE' if is_downloadable else 'ERROR'}")
        print(f"Message: {message}")
        
        # 期待される結果
        print("\n5. Expected vs Actual:")
        print("Expected: ERROR (with redirect to do_download_pdf)")
        print(f"Actual: {'DOWNLOADABLE' if is_downloadable else 'ERROR'}")
        
        if is_downloadable:
            print("PROBLEM: Error file detected as downloadable")
        else:
            if 'ZIP' in message:
                print("PROBLEM: Error detection reason mentions ZIP - should mention redirect")
            else:
                print("SUCCESS: Correctly detected as error")
        
        # 既知のエラーURLもテスト
        print("\n6. Testing Known Error URL:")
        print(f"URL: {known_error_url}")
        
        is_downloadable2, message2 = service.check_pdf_downloadable(known_error_url)
        print(f"Result: {'DOWNLOADABLE' if is_downloadable2 else 'ERROR'}")
        print(f"Message: {message2}")
        
        # 結論
        print("\n7. CONCLUSION:")
        if target_url == known_error_url:
            print("URLs match - Same error file being tested")
        else:
            print("URLs differ - Different instances or extraction error")
            print("This might explain the ZIP detection issue")
        
        return True
        
    except Exception as e:
        print(f"Verification error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Error File URL Verification Tool")
    print("Investigating ZIP detection issue")
    print()
    
    success = verify_error_file_url()
    
    print("\n" + "=" * 60)
    if success:
        print("Verification completed")
    else:
        print("Verification failed")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
    except Exception as e:
        print(f"Unexpected error: {e}")
        success = False
    
    print("\nPress Enter to exit...")
    try:
        input()
    except:
        pass
    
    sys.exit(0 if success else 1)