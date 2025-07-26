#!/usr/bin/env python3
"""Word2XHTML5エラー検出統合テスト"""
import os
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
import email
from email.message import EmailMessage

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.email_monitor import EmailMonitor
from services.nextpublishing_service import NextPublishingService

def create_mock_email(subject, body, from_addr="support-np@impress.co.jp"):
    """モックメールメッセージを作成"""
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = "test@example.com"
    msg.set_content(body)
    return msg

def test_email_processing():
    """メール処理の統合テスト"""
    print("=" * 80)
    print("メール処理統合テスト")
    print("=" * 80)
    
    # テストケース
    test_emails = [
        {
            "filename": "04_powershell_sample_advanced.docx",
            "body": """
山城 敬 様

Word2XHTML5 PDFジェネレータをご利用いただきまして、ありがとうございます。

アップロードされた超原稿用紙から生成されたファイルを
以下のURLからダウンロードできます。

http://trial.nextpublishing.jp/upload_46tate/do_download?n=hLXTDhYvktP%2B5O4rsHMn8l63%2BMt5xmRwg0ZnDb5lZisoqOxrjuJqU7ZzzVSiddVCO04BsD%2FTC7J8c%2F%2FGR3Y2GQ%3D%3D

04_powershell_sample_advanced.docx

※ダウンロード期限は本メール配信後72時間(3日間)です。
            """,
            "expected_error": True
        },
        {
            "filename": "05_appendix.docx",
            "body": """
山城 敬 様

Word2XHTML5 PDFジェネレータをご利用いただきまして、ありがとうございます。

アップロードされた超原稿用紙から生成されたファイルを
以下のURLからダウンロードできます。

http://trial.nextpublishing.jp/upload_46tate/do_download?n=cOc%2BWtyOaiCygUI0QyVpjOAIr%2F4PR7ifWZbNZzUhpKqukbY3LhsyO3oqOIoMwB47KUGNYXnnw2lMcDoYZMBosQ%3D%3D

05_appendix.docx

※ダウンロード期限は本メール配信後72時間(3日間)です。
            """,
            "expected_error": False
        }
    ]
    
    # EmailMonitorのメソッドをモック化してテスト
    monitor = EmailMonitor("test@example.com", "password")
    
    for test in test_emails:
        print(f"\nテストケース: {test['filename']}")
        print(f"期待される結果: {'エラー' if test['expected_error'] else '正常'}")
        
        # メールメッセージを作成
        msg = create_mock_email("ダウンロード用URLのご案内", test['body'])
        
        # ファイル名とURLを抽出
        result = monitor._extract_download_url_with_filename(msg)
        
        if result:
            url, filename = result
            print(f"抽出結果:")
            print(f"  - ファイル名: {filename}")
            print(f"  - URL: {url[:80]}...")
            
            if filename == test['filename']:
                print(f"  ✓ ファイル名の抽出成功")
            else:
                print(f"  ✗ ファイル名の抽出失敗")
        else:
            print(f"  ✗ 抽出失敗")

def test_workflow_simulation():
    """ワークフロー全体のシミュレーションテスト"""
    print("\n" + "=" * 80)
    print("ワークフローシミュレーションテスト")
    print("=" * 80)
    
    # アップロードしたファイルリスト
    uploaded_files = [
        Path("04_powershell_sample_advanced.docx"),
        Path("05_appendix.docx")
    ]
    
    # メール収集シミュレーション
    file_url_map = {
        "04_powershell_sample_advanced.docx": "http://trial.nextpublishing.jp/upload_46tate/do_download?n=hLXTDhYvktP%2B5O4rsHMn8l63%2BMt5xmRwg0ZnDb5lZisoqOxrjuJqU7ZzzVSiddVCO04BsD%2FTC7J8c%2F%2FGR3Y2GQ%3D%3D",
        "05_appendix.docx": "http://trial.nextpublishing.jp/upload_46tate/do_download?n=cOc%2BWtyOaiCygUI0QyVpjOAIr%2F4PR7ifWZbNZzUhpKqukbY3LhsyO3oqOIoMwB47KUGNYXnnw2lMcDoYZMBosQ%3D%3D"
    }
    
    print("\n1. メール収集結果:")
    for filename, url in file_url_map.items():
        print(f"  - {filename}: {url[:60]}...")
    
    print("\n2. PDFチェック結果:")
    
    # NextPublishingServiceをモック化
    service = Mock(spec=NextPublishingService)
    
    # check_pdf_downloadableの動作をシミュレート
    def mock_check_pdf(url):
        # 04_powershell_sample_advanced.docxはエラー
        if "hLXTDhYvktP" in url:
            return False, "PDF生成エラー（超原稿用紙に不備）"
        else:
            return True, "PDFダウンロード可能"
    
    service.check_pdf_downloadable.side_effect = mock_check_pdf
    
    error_files = []
    
    for file_path in uploaded_files:
        url = file_url_map.get(file_path.name)
        if url:
            is_downloadable, message = service.check_pdf_downloadable(url)
            
            print(f"\n  {file_path.name}:")
            print(f"    - URL: {url[:60]}...")
            print(f"    - 結果: {message}")
            
            if not is_downloadable:
                error_files.append(file_path)
                print(f"    ✗ エラーファイルとして記録")
            else:
                print(f"    ✓ 正常ファイルとして記録")
    
    print(f"\n3. 最終結果:")
    print(f"  - エラーファイル数: {len(error_files)}")
    for ef in error_files:
        print(f"    - {ef.name}")
    
    # 期待される結果と比較
    expected_error_files = ["04_powershell_sample_advanced.docx"]
    actual_error_files = [ef.name for ef in error_files]
    
    if actual_error_files == expected_error_files:
        print(f"\n✓ テスト成功: 期待通りのエラーファイルが検出されました")
    else:
        print(f"\n✗ テスト失敗:")
        print(f"  期待: {expected_error_files}")
        print(f"  実際: {actual_error_files}")

if __name__ == "__main__":
    test_email_processing()
    test_workflow_simulation()