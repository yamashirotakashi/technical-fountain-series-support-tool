# Gmail APIから取得した実際のdo_download URLのテスト

import sys
from pathlib import Path
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_actual_download_url():
    """実際のdo_download URLをテスト"""
    print("=== Actual Download URL Test ===")
    print(f"Execution time: {datetime.now().isoformat()}")
    print()
    
    try:
        from core.gmail_oauth_monitor import GmailOAuthMonitor
        
        print("Searching for 04_powershell_sample_advanced.docx...")
        monitor = GmailOAuthMonitor("config/gmail_oauth_credentials.json")
        monitor.authenticate()
        
        # 過去2週間のメールを検索
        since_time = datetime.now() - timedelta(days=14)
        
        messages = monitor.search_emails(
            subject_pattern="ダウンロード用URLのご案内",
            since_time=since_time,
            max_results=30
        )
        
        print(f"Found {len(messages)} emails")
        
        # 対象ファイルを検索
        target_url = None
        target_filename = None
        
        for i, message in enumerate(messages):
            print(f"Checking email {i+1}/{len(messages)}...")
            
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
                    break
        
        if not target_url:
            print("04_powershell_sample_advanced.docx not found")
            return False
        
        print(f"\nTesting URL: {target_url}")
        print(f"Filename: {target_filename}")
        print()
        
        # 現在のcheck_pdf_downloadableメソッドをテスト
        from services.nextpublishing_service import NextPublishingService
        service = NextPublishingService()
        
        print("=== Current Detection Method Test ===")
        is_downloadable, message = service.check_pdf_downloadable(target_url)
        
        print(f"Result: {'DOWNLOADABLE' if is_downloadable else 'ERROR'}")
        print(f"Message: {message}")
        print()
        
        # 手動でHTTPリクエストして詳細確認
        print("=== Manual HTTP Request Analysis ===")
        
        response = service.session.get(target_url, timeout=30, allow_redirects=True)
        
        print(f"Status Code: {response.status_code}")
        print(f"Initial URL: {target_url}")
        print(f"Final URL: {response.url}")
        print(f"Redirected: {'Yes' if str(response.url) != target_url else 'No'}")
        print()
        
        print("Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        print()
        
        content_start = response.content[:100] if response.content else b''
        print(f"Content start (100 bytes): {content_start}")
        print(f"Content length: {len(response.content)} bytes")
        print()
        
        # 詳細な内容分析
        final_url = str(response.url)
        content_type = response.headers.get('Content-Type', '')
        
        print("=== Content Analysis ===")
        
        # URL分析
        if 'do_download_pdf' in final_url:
            print("URL ANALYSIS: Contains 'do_download_pdf' - ERROR PAGE")
        else:
            print("URL ANALYSIS: Does not contain 'do_download_pdf' - NORMAL DOWNLOAD")
        
        # Content-Type分析
        print(f"CONTENT-TYPE: {content_type}")
        
        # Magic Number分析
        if content_start.startswith(b'%PDF'):
            print("MAGIC NUMBER: PDF file")
        elif content_start.startswith(b'PK'):
            print("MAGIC NUMBER: ZIP file")
        elif content_start.startswith(b'<html') or content_start.startswith(b'<!DOCTYPE'):
            print("MAGIC NUMBER: HTML file")
        else:
            print(f"MAGIC NUMBER: Unknown ({content_start[:20]})")
        
        # HTMLの場合の詳細分析
        if content_start.startswith(b'<html') or content_start.startswith(b'<!DOCTYPE'):
            html_content = response.content.decode('utf-8', errors='ignore')
            print("\nHTML Content Analysis:")
            print(f"Content length: {len(html_content)} characters")
            
            error_keywords = [
                'ファイルの作成に失敗',
                'エラーが発生',
                'PDF生成エラー',
                'エラー'
            ]
            
            found_errors = []
            for keyword in error_keywords:
                if keyword in html_content:
                    found_errors.append(keyword)
            
            if found_errors:
                print(f"ERROR KEYWORDS FOUND: {found_errors}")
            else:
                print("NO ERROR KEYWORDS FOUND")
            
            print("\nHTML Content Sample (first 500 chars):")
            print("-" * 50)
            print(html_content[:500])
            print("-" * 50)
        
        # 現在のロジックの問題を分析
        print("\n=== Logic Analysis ===")
        
        if 'do_download_pdf' in final_url:
            print("EXPECTED: Should be detected as ERROR (URL contains do_download_pdf)")
        
        if 'application/x-zip' in content_type or 'application/zip' in content_type:
            print("PROBLEM: Content-Type indicates ZIP - this might cause misdetection")
        
        if content_start.startswith(b'PK'):
            print("PROBLEM: Content starts with PK - might be misidentified as ZIP")
        
        # 期待される結果 vs 実際の結果
        print(f"\nEXPECTED: ERROR (known error file)")
        print(f"ACTUAL: {'DOWNLOADABLE' if is_downloadable else 'ERROR'}")
        
        if is_downloadable:
            print("ISSUE: Error file detected as downloadable - NEEDS FIX")
            return False
        else:
            print("SUCCESS: Error file correctly detected as error")
            return True
        
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Actual Download URL Test Tool")
    print()
    
    success = test_actual_download_url()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    
    if success:
        print("SUCCESS: Error detection is working correctly")
    else:
        print("ISSUE: Error detection needs improvement")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        print(f"\nTest {'passed' if success else 'failed'}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        success = False
    
    print("\nPress Enter to exit...")
    try:
        input()
    except:
        pass
    
    sys.exit(0 if success else 1)