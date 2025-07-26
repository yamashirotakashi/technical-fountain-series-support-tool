# Gmail API メール内容とURL抽出のデバッグ

import sys
from pathlib import Path
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_email_content():
    """メール内容とURL抽出をデバッグ"""
    print("🔍 Gmail API メール内容デバッグ")
    print("=" * 60)
    
    try:
        from core.gmail_oauth_monitor import GmailOAuthMonitor
        
        # Gmail API初期化
        monitor = GmailOAuthMonitor("config/gmail_oauth_credentials.json")
        monitor.authenticate()
        
        # 過去3日間のメールを検索
        since_time = datetime.now() - timedelta(days=3)
        
        messages = monitor.search_emails(
            subject_pattern="ダウンロード用URLのご案内",
            since_time=since_time,
            max_results=3
        )
        
        print(f"📊 検索結果: {len(messages)}件のメール")
        
        if not messages:
            print("ℹ️ 対象メールが見つかりません。より広い範囲で検索します...")
            
            # 過去2週間で再検索
            since_time = datetime.now() - timedelta(days=14)
            messages = monitor.search_emails(
                subject_pattern="ダウンロード用URLのご案内",
                since_time=since_time,
                max_results=5
            )
            print(f"📊 拡張検索結果: {len(messages)}件のメール")
        
        if not messages:
            print("❌ メールが見つかりません。件名パターンを確認します...")
            
            # 件名パターンを変更して検索
            patterns = [
                "ダウンロード用URL",
                "nextpublishing",
                "trial.nextpublishing"
            ]
            
            for pattern in patterns:
                print(f"🔍 パターン '{pattern}' で検索中...")
                test_messages = monitor.search_emails(
                    subject_pattern=pattern,
                    since_time=datetime.now() - timedelta(days=7),
                    max_results=3
                )
                print(f"   結果: {len(test_messages)}件")
                if test_messages:
                    messages = test_messages
                    break
        
        # 最新の1件を詳細分析
        if messages:
            print(f"\n📄 最新メッセージを詳細分析...")
            message_details = monitor.get_message_details(messages[0]['id'])
            
            if message_details:
                # ヘッダー情報を表示
                headers = message_details.get('payload', {}).get('headers', [])
                print("\n📧 メールヘッダー:")
                for header in headers:
                    if header['name'] in ['Subject', 'From', 'Date']:
                        print(f"  {header['name']}: {header['value']}")
                
                # ペイロード構造を分析
                payload = message_details.get('payload', {})
                print(f"\n📦 ペイロード情報:")
                print(f"  mimeType: {payload.get('mimeType', 'なし')}")
                print(f"  parts: {'あり' if 'parts' in payload else 'なし'}")
                
                # 本文抽出を試行
                print(f"\n📄 本文抽出試行...")
                body_text = monitor._extract_body_text(payload)
                
                if body_text:
                    print(f"✅ 本文抽出成功 ({len(body_text)}文字)")
                    print(f"📄 本文サンプル（先頭500文字）:")
                    print("-" * 40)
                    print(body_text[:500])
                    print("-" * 40)
                    
                    # URL抽出パターンをテスト
                    import re
                    url_patterns = [
                        r'http://trial\.nextpublishing\.jp/upload_46tate/do_download\?n=[^\s\n\r]+',
                        r'<(http://trial\.nextpublishing\.jp/upload_46tate/do_download\?[^>]+)>',
                        r'http://trial\.nextpublishing\.jp[^\s\n\r]+',
                        r'https?://[^\s\n\r]+',
                    ]
                    
                    print(f"\n🔍 URL抽出パターンテスト:")
                    for i, pattern in enumerate(url_patterns):
                        matches = re.findall(pattern, body_text)
                        print(f"  パターン {i+1}: {len(matches)}件")
                        if matches:
                            print(f"    例: {matches[0][:80]}...")
                    
                    # ファイル名抽出パターンをテスト
                    filename_patterns = [
                        r'ファイル名：([^\n\r]+\.docx)',
                        r'ファイル名：([^\n\r]+)',
                        r'ファイル：([^\n\r]+\.docx)',
                        r'([^\s]+\.docx)'
                    ]
                    
                    print(f"\n📁 ファイル名抽出パターンテスト:")
                    for i, pattern in enumerate(filename_patterns):
                        matches = re.findall(pattern, body_text)
                        print(f"  パターン {i+1}: {len(matches)}件")
                        if matches:
                            print(f"    例: {matches[0]}")
                    
                    # 実際の抽出メソッドをテスト
                    print(f"\n🧪 実際の抽出メソッドテスト:")
                    result = monitor.extract_download_url_and_filename(message_details)
                    if result:
                        url, filename = result
                        print(f"✅ 抽出成功:")
                        print(f"  📁 ファイル名: {filename}")
                        print(f"  🔗 URL: {url}")
                    else:
                        print(f"❌ 抽出失敗")
                        
                        # 失敗原因を調査
                        print(f"\n🔧 失敗原因調査:")
                        if 'nextpublishing' in body_text:
                            print(f"  ✅ nextpublishing文字列は存在")
                        else:
                            print(f"  ❌ nextpublishing文字列が見つからない")
                        
                        if '.docx' in body_text:
                            print(f"  ✅ .docx文字列は存在")
                        else:
                            print(f"  ❌ .docx文字列が見つからない")
                
                else:
                    print(f"❌ 本文抽出失敗")
                    
                    # ペイロード詳細を確認
                    print(f"\n🔧 ペイロード詳細確認:")
                    if 'parts' in payload:
                        print(f"  マルチパート構造:")
                        for i, part in enumerate(payload['parts']):
                            print(f"    Part {i}: {part.get('mimeType', 'unknown')}")
                    else:
                        print(f"  シンプル構造: {payload.get('mimeType', 'unknown')}")
                        body_data = payload.get('body', {}).get('data')
                        if body_data:
                            print(f"  Body data: {len(body_data)}文字")
                        else:
                            print(f"  Body data: なし")
            
            else:
                print(f"❌ メッセージ詳細取得失敗")
        
        else:
            print(f"❌ 対象メールが見つかりませんでした")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ デバッグエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Gmail API メール内容デバッグツール")
    print()
    
    success = debug_email_content()
    
    if success:
        print("\n✅ デバッグ完了")
    else:
        print("\n❌ デバッグ失敗")
    
    print(f"\nデバッグ{'成功' if success else '失敗'}: {datetime.now().strftime('%H:%M:%S')}")
    input("\nEnterキーを押して終了...")
    sys.exit(0 if success else 1)