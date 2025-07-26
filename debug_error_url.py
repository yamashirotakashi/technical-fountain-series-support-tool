# エラーURLの挙動を詳細調査

import sys
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def analyze_error_url():
    """エラーURLの詳細分析"""
    
    error_url = "http://trial.nextpublishing.jp/upload_46tate/do_download_pdf?n=JxTuFEr0iW9GiYUABueS3fqC%2F1BOwNeUZPoxHmahvbZ7Un8uFh5wwtnoEgJPDiaI%2F9A9qikFnxiGZe4b%2F%2B9xMQ%3D%3D"
    
    print("=== Error URL Analysis ===")
    print(f"URL: {error_url}")
    print()
    
    try:
        # NextPublishingServiceと同じ認証設定を使用
        from utils.config import get_config
        config = get_config()
        web_config = config.get_web_config()
        username = web_config.get('username', 'ep_user')
        password = web_config.get('password', 'Nn7eUTX5')
        
        session = requests.Session()
        session.auth = HTTPBasicAuth(username, password)
        session.headers.update({
            'User-Agent': 'TechnicalFountainTool/1.0'
        })
        
        print("Making HTTP request...")
        response = session.get(error_url, timeout=30, allow_redirects=True)
        
        print(f"Status Code: {response.status_code}")
        print(f"Initial URL: {error_url}")
        print(f"Final URL: {response.url}")
        print(f"Redirected: {'Yes' if str(response.url) != error_url else 'No'}")
        print()
        
        print("Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        print()
        
        # Content analysis
        content_start = response.content[:50] if response.content else b''
        print(f"Content start (50 bytes): {content_start}")
        print(f"Content length: {len(response.content)} bytes")
        print()
        
        # Check if it's HTML
        if content_start.startswith(b'<html') or content_start.startswith(b'<!DOCTYPE') or content_start.startswith(b'<!doctype'):
            print("Content Type: HTML detected")
            html_content = response.content[:2000].decode('utf-8', errors='ignore')
            print("HTML Content (first 2000 chars):")
            print("-" * 60)
            print(html_content)
            print("-" * 60)
            
            # Check for error keywords
            error_keywords = [
                'ファイルの作成に失敗',
                'エラーが発生',
                'PDF生成エラー',
                'エラー',
                'failed',
                'error'
            ]
            
            found_errors = []
            for keyword in error_keywords:
                if keyword.lower() in html_content.lower():
                    found_errors.append(keyword)
            
            if found_errors:
                print(f"Error keywords found: {found_errors}")
            else:
                print("No error keywords found in HTML")
        
        elif content_start.startswith(b'%PDF'):
            print("Content Type: PDF file")
        
        elif content_start.startswith(b'PK'):
            print("Content Type: ZIP file (or ZIP-like)")
            print("Note: This might be misidentified content")
        
        else:
            print(f"Content Type: Unknown ({content_start})")
        
        print()
        
        # Test current detection logic
        print("Current detection logic test:")
        final_url_str = str(response.url)
        
        if 'do_download_pdf' in final_url_str:
            print("DETECTED: URL contains 'do_download_pdf' - This should be detected as ERROR")
            
            content_text = response.content.decode('utf-8', errors='ignore')
            if 'ファイルの作成に失敗しました' in content_text:
                print("DETECTED: '本ファイルの作成に失敗しました' in content")
                detection_result = "PDF生成エラー（超原稿用紙に不備）"
            else:
                print("DETECTED: General PDF generation error")  
                detection_result = "PDF生成エラー"
            
            print(f"Detection result: {detection_result}")
            return False, detection_result
        else:
            print("NOT DETECTED: URL does not contain 'do_download_pdf'")
            print("This might be why the error is not being caught")
            
        # Check why the current logic might be failing
        content_type = response.headers.get('Content-Type', '')
        print(f"\nContent-Type header: {content_type}")
        
        if 'application/x-zip' in content_type or 'application/zip' in content_type:
            print("PROBLEM: Content-Type indicates ZIP file")
            print("This might be causing incorrect ZIP detection before error URL check")
        
        return True, "Analysis complete"
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return False, f"Analysis error: {e}"

def main():
    print("Error URL Behavior Analysis Tool")
    print()
    
    success, message = analyze_error_url()
    
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print(f"Result: {message}")
    
    if success:
        print("Analysis completed successfully")
    else:
        print("Error detected during analysis")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        print(f"\nAnalysis {'completed' if success else 'failed'}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        success = False
    
    print("\nPress Enter to exit...")
    try:
        input()
    except:
        pass
    
    sys.exit(0 if success else 1)