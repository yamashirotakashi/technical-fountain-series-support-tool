# Simple error file detection test without Unicode emojis

import sys
from pathlib import Path
from datetime import datetime, timedelta
import requests
import zipfile
import io

# Project root setup
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def analyze_specific_file():
    """Find and analyze 04_powershell_sample_advanced.docx"""
    print("=== 04_powershell_sample_advanced.docx Error Detection Analysis ===")
    print(f"Execution time: {datetime.now().isoformat()}")
    print()
    
    try:
        from core.gmail_oauth_monitor import GmailOAuthMonitor
        
        print("Searching emails with Gmail API...")
        monitor = GmailOAuthMonitor("config/gmail_oauth_credentials.json")
        monitor.authenticate()
        
        # Search emails from past 2 weeks
        since_time = datetime.now() - timedelta(days=14)
        
        messages = monitor.search_emails(
            subject_pattern="ダウンロード用URLのご案内",
            since_time=since_time,
            max_results=30
        )
        
        print(f"Found {len(messages)} emails")
        
        target_file = None
        target_url = None
        
        # Search for the specific file
        for i, message in enumerate(messages):
            print(f"Checking email {i+1}/{len(messages)}...")
            
            message_details = monitor.get_message_details(message['id'])
            if not message_details:
                continue
            
            result = monitor.extract_download_url_and_filename(message_details)
            if result:
                url, filename = result
                
                if "04_powershell_sample_advanced" in filename:
                    print(f"TARGET FILE FOUND: {filename}")
                    target_file = filename
                    target_url = url
                    break
        
        if target_file and target_url:
            print(f"\nTarget file identified:")
            print(f"Filename: {target_file}")
            print(f"URL: {target_url[:80]}...")
            
            # Analyze the response in detail
            print(f"\nDetailed Response Analysis:")
            return analyze_response_details(target_url, target_file)
            
        else:
            print(f"04_powershell_sample_advanced.docx not found in recent emails")
            return False
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_response_details(url, filename):
    """Analyze HTTP response in detail"""
    try:
        from services.nextpublishing_service import NextPublishingService
        service = NextPublishingService()
        
        print("HTTP Request Analysis:")
        response = service.session.get(url, timeout=30, allow_redirects=True)
        
        print(f"Status Code: {response.status_code}")
        print(f"Final URL: {response.url}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'None')}")
        print(f"Content-Length: {response.headers.get('Content-Length', 'None')}")
        
        # Check content start
        content_start = response.content[:20] if response.content else b''
        print(f"Content start (20 bytes): {content_start}")
        
        # Analyze content type
        if content_start.startswith(b'%PDF'):
            print("Content Type: PDF file")
            current_result = True
            current_message = "PDF file detected"
        elif content_start.startswith(b'PK'):
            print("Content Type: ZIP file")
            
            # Analyze ZIP contents
            print("\nZIP Content Analysis:")
            try:
                zip_data = io.BytesIO(response.content)
                with zipfile.ZipFile(zip_data, 'r') as zip_file:
                    file_list = zip_file.namelist()
                    print(f"Files in ZIP: {len(file_list)}")
                    
                    for file_name in file_list[:10]:  # Show up to 10 files
                        file_info = zip_file.getinfo(file_name)
                        print(f"  {file_name} ({file_info.file_size} bytes)")
                        
                        # Check if it's PDF or error page
                        if file_name.lower().endswith('.pdf'):
                            print("    -> PDF file found")
                        elif file_name.lower().endswith('.html'):
                            print("    -> HTML file found (possible error page)")
                            
                            # Read HTML content to check for errors
                            with zip_file.open(file_name) as html_file:
                                html_content = html_file.read(1000).decode('utf-8', errors='ignore')
                                if 'ファイルの作成に失敗' in html_content or 'エラー' in html_content:
                                    print("    -> ERROR PAGE DETECTED!")
                                    current_result = False
                                    current_message = "ZIP contains error page"
                                else:
                                    print(f"    -> HTML content sample: {html_content[:100]}...")
                    
                    # Final ZIP judgment
                    pdf_files = [f for f in file_list if f.lower().endswith('.pdf')]
                    if pdf_files:
                        print(f"Valid PDF files in ZIP: {len(pdf_files)}")
                        current_result = True
                        current_message = f"ZIP with {len(pdf_files)} PDF files"
                    else:
                        print("No PDF files in ZIP")
                        current_result = False
                        current_message = "ZIP without PDF files"
                        
            except zipfile.BadZipFile:
                print("Invalid ZIP file")
                current_result = False
                current_message = "Invalid ZIP file"
            except Exception as e:
                print(f"ZIP analysis error: {e}")
                current_result = False
                current_message = f"ZIP analysis error: {e}"
        
        elif content_start.startswith(b'<html') or content_start.startswith(b'<!DOCTYPE'):
            print("Content Type: HTML file")
            html_content = response.content[:2000].decode('utf-8', errors='ignore')
            
            if 'ファイルの作成に失敗' in html_content or 'エラー' in html_content:
                print("ERROR PAGE detected in HTML")
                current_result = False
                current_message = "HTML error page"
            else:
                print("Regular HTML page")
                current_result = False
                current_message = "HTML response (PDF generation failed)"
        else:
            print(f"Unknown content type: {content_start}")
            current_result = False
            current_message = "Unknown content type"
        
        # Compare with current detection method
        print(f"\nCurrent Error Detection Method Result:")
        is_downloadable, message = service.check_pdf_downloadable(url)
        status = "OK" if is_downloadable else "ERROR"
        print(f"  {status}: {message}")
        
        print(f"\nFINAL ANALYSIS:")
        print(f"Filename: {filename}")
        print(f"Expected: ERROR (known error file)")
        print(f"Detected: {'OK' if is_downloadable else 'ERROR'}")
        
        if is_downloadable:
            print("PROBLEM: Error file detected as OK - logic needs improvement")
            return False  # Detection failed
        else:
            print("SUCCESS: Error file correctly detected as ERROR")
            return True   # Detection worked
        
    except Exception as e:
        print(f"Analysis error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("04_powershell_sample_advanced.docx Error Detection Diagnostic Tool")
    print()
    
    success = analyze_specific_file()
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC RESULT SUMMARY")
    
    if success:
        print("SUCCESS: Error detection is working correctly")
    else:
        print("PROBLEM: Error detection needs improvement")
    
    print(f"\nDiagnostic completed: {datetime.now().strftime('%H:%M:%S')}")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        
        if success:
            print("\nError detection function is working properly")
        else:
            print("\nError detection function needs improvement")
        
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        success = False
    
    print("\nPress Enter to exit...")
    try:
        input()
    except:
        pass
    
    sys.exit(0 if success else 1)