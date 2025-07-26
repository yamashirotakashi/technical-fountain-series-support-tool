# 04_powershell_sample_advanced.docxのエラー検知詳細調査

import sys
from pathlib import Path
from datetime import datetime, timedelta
import requests
import zipfile
import io

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def analyze_error_file_response(url, filename):
    """エラーファイルのレスポンスを詳細分析"""
    print(f"🔍 詳細分析: {filename}")
    print(f"📋 URL: {url}")
    print("=" * 70)
    
    try:
        from services.nextpublishing_service import NextPublishingService
        service = NextPublishingService()
        
        # 手動でHTTPリクエストして詳細を確認
        print("📡 HTTPリクエスト詳細分析...")
        
        response = service.session.get(url, timeout=30, allow_redirects=True)
        
        print(f"🔹 ステータスコード: {response.status_code}")
        print(f"🔹 最終URL: {response.url}")
        print(f"🔹 Content-Type: {response.headers.get('Content-Type', 'なし')}")
        print(f"🔹 Content-Length: {response.headers.get('Content-Length', 'なし')}")
        
        # レスポンス内容の先頭を確認
        content_start = response.content[:20] if response.content else b''
        print(f"🔹 内容（先頭20バイト）: {content_start}")
        print(f"🔹 マジックナンバー判定:")
        
        if content_start.startswith(b'%PDF'):
            print("   ✅ PDFファイル")
        elif content_start.startswith(b'PK'):
            print("   🗜️ ZIPファイル")
        elif content_start.startswith(b'<html') or content_start.startswith(b'<!DOCTYPE'):
            print("   📄 HTMLファイル")
        else:
            print(f"   ❓ 不明な形式: {content_start}")
        
        # ZIPファイルの場合、内容を詳細分析
        if content_start.startswith(b'PK'):
            print("\n🗜️ ZIPファイル内容分析:")
            try:
                zip_data = io.BytesIO(response.content)
                with zipfile.ZipFile(zip_data, 'r') as zip_file:
                    file_list = zip_file.namelist()
                    print(f"   📁 含まれるファイル数: {len(file_list)}")
                    
                    for file_name in file_list[:10]:  # 最大10ファイル表示
                        file_info = zip_file.getinfo(file_name)
                        print(f"     📄 {file_name} ({file_info.file_size} bytes)")
                        
                        # ファイルがPDFかエラーページかを確認
                        if file_name.lower().endswith('.pdf'):
                            print("       ✅ PDFファイル発見")
                        elif file_name.lower().endswith('.html'):
                            print("       ⚠️ HTMLファイル発見（エラーページの可能性）")
                            
                            # HTMLファイルの内容を少し読む
                            with zip_file.open(file_name) as html_file:
                                html_content = html_file.read(500).decode('utf-8', errors='ignore')
                                if 'エラー' in html_content or 'ファイルの作成に失敗' in html_content:
                                    print("       ❌ エラーページ確定")
                                    return False, "ZIP内にエラーページを検出"
                                else:
                                    print(f"       📄 HTML内容サンプル: {html_content[:100]}...")
                    
                    # ZIPに正常なPDFが含まれているか判定
                    pdf_files = [f for f in file_list if f.lower().endswith('.pdf')]
                    if pdf_files:
                        print(f"   ✅ 正常なPDFファイル: {len(pdf_files)}個")
                        return True, f"ZIP内に{len(pdf_files)}個のPDFファイル"
                    else:
                        print("   ❌ PDFファイルなし")
                        return False, "ZIP内にPDFファイルが見つからない"
                        
            except zipfile.BadZipFile:
                print("   ❌ 不正なZIPファイル")
                return False, "不正なZIPファイル"
            except Exception as e:
                print(f"   ❌ ZIP分析エラー: {e}")
                return False, f"ZIP分析エラー: {e}"
        
        # HTMLレスポンスの場合
        elif content_start.startswith(b'<html') or content_start.startswith(b'<!DOCTYPE'):
            print("\n📄 HTML内容分析:")
            html_content = response.content[:2000].decode('utf-8', errors='ignore')
            print(f"   📋 HTML内容（先頭2000文字）:")
            print("   " + "-" * 50)
            print("   " + html_content[:500].replace('\n', '\n   '))
            print("   " + "-" * 50)
            
            if 'ファイルの作成に失敗' in html_content or 'エラー' in html_content:
                print("   ❌ エラーページ検出")
                return False, "HTMLエラーページ"
            else:
                print("   ❓ 通常のHTMLページ")
                return False, "HTMLレスポンス（PDF生成失敗）"
        
        # 現在のcheck_pdf_downloadableメソッドの結果と比較
        print("\n🧪 現在のエラー検知メソッド結果:")
        is_downloadable, message = service.check_pdf_downloadable(url)
        status_icon = "✅" if is_downloadable else "❌"
        print(f"   {status_icon} 判定: {message}")
        
        return is_downloadable, message
        
    except Exception as e:
        print(f"❌ 分析エラー: {e}")
        import traceback
        traceback.print_exc()
        return False, f"分析エラー: {e}"

def find_and_analyze_error_file():
    """04_powershell_sample_advanced.docxを検索して分析"""
    print("🎯 04_powershell_sample_advanced.docx 専用分析ツール")
    print(f"実行時刻: {datetime.now().isoformat()}")
    print("=" * 70)
    
    try:
        # Gmail APIで過去のメールを検索
        from core.gmail_oauth_monitor import GmailOAuthMonitor
        
        print("📧 Gmail APIでメール検索中...")
        monitor = GmailOAuthMonitor("config/gmail_oauth_credentials.json")
        monitor.authenticate()
        
        # 過去2週間のメールを検索
        since_time = datetime.now() - timedelta(days=14)
        
        messages = monitor.search_emails(
            subject_pattern="ダウンロード用URLのご案内",
            since_time=since_time,
            max_results=50
        )
        
        print(f"📊 検索結果: {len(messages)}件のメール")
        
        target_file = None
        target_url = None
        
        # 各メールを確認して04_powershell_sample_advanced.docxを探す
        for i, message in enumerate(messages):
            print(f"📄 メール {i+1}/{len(messages)} 確認中...")
            
            message_details = monitor.get_message_details(message['id'])
            if not message_details:
                continue
            
            result = monitor.extract_download_url_and_filename(message_details)
            if result:
                url, filename = result
                
                if "04_powershell_sample_advanced" in filename:
                    print(f"🎯 ターゲットファイル発見: {filename}")
                    target_file = filename
                    target_url = url
                    break
        
        if target_file and target_url:
            print(f"\n✅ ターゲットファイル特定完了")
            print(f"📁 ファイル名: {target_file}")
            print(f"🔗 URL: {target_url}")
            
            # 詳細分析を実行
            print(f"\n🔬 詳細分析開始...")
            is_downloadable, analysis_message = analyze_error_file_response(target_url, target_file)
            
            print(f"\n📊 最終判定:")
            if is_downloadable:
                print(f"⚠️ エラー: このファイルはエラーファイルなのに正常判定されています")
                print(f"🔧 検知ロジックの修正が必要です")
                print(f"💡 判定理由: {analysis_message}")
            else:
                print(f"✅ 正常: エラーファイルとして正しく検出されました")
                print(f"📋 検出理由: {analysis_message}")
            
            return True, is_downloadable, analysis_message
            
        else:
            print(f"❌ 04_powershell_sample_advanced.docx が見つかりませんでした")
            print(f"ℹ️ 過去2週間以内にアップロードされていない可能性があります")
            return False, None, "ターゲットファイルなし"
        
    except Exception as e:
        print(f"❌ 検索・分析エラー: {e}")
        import traceback
        traceback.print_exc()
        return False, None, f"エラー: {e}"

def main():
    """メイン実行"""
    print("🚀 04_powershell_sample_advanced.docx エラー検知診断ツール")
    print()
    
    found, is_downloadable, message = find_and_analyze_error_file()
    
    print("\n" + "=" * 70)
    print("📋 診断結果サマリー")
    
    if found:
        print(f"🎯 ターゲットファイル: 発見")
        if is_downloadable:
            print(f"❌ 問題発生: エラーファイルが正常と判定")
            print(f"🔧 対策必要: check_pdf_downloadable()メソッドの改善")
            print(f"💡 原因: {message}")
        else:
            print(f"✅ 正常動作: エラーファイルを正しく検出")
            print(f"📋 検出理由: {message}")
    else:
        print(f"ℹ️ ターゲットファイル: 見つからず")
        print(f"📋 理由: {message}")
    
    print(f"\n診断完了: {datetime.now().strftime('%H:%M:%S')}")
    
    return found and not is_downloadable  # 正常な検知ができている場合True

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 エラー検知機能は正常に動作しています")
    else:
        print("\n🔧 エラー検知機能の改善が必要です")
    
    input("\nEnterキーを押して終了...")
    sys.exit(0 if success else 1)