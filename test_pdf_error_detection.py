#!/usr/bin/env python3
"""Word2XHTML5 PDFエラー検出テスト"""
import os
import sys
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.nextpublishing_service import NextPublishingService
from utils.logger import get_logger

# .envファイルから環境変数を読み込み
env_path = project_root / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

def test_pdf_error_detection():
    """PDFエラー検出のテスト"""
    logger = get_logger(__name__)
    
    # テスト用URL（実際のログから取得）
    test_cases = [
        {
            "name": "04_powershell_sample_advanced.docx",
            "url": "http://trial.nextpublishing.jp/upload_46tate/do_download?n=hLXTDhYvktP%2B5O4rsHMn8l63%2BMt5xmRwg0ZnDb5lZisoqOxrjuJqU7ZzzVSiddVCO04BsD%2FTC7J8c%2F%2FGR3Y2GQ%3D%3D",
            "expected_error": True,
            "description": "エラーファイル（do_download_pdfにリダイレクトされるはず）"
        },
        {
            "name": "05_appendix.docx",
            "url": "http://trial.nextpublishing.jp/upload_46tate/do_download?n=cOc%2BWtyOaiCygUI0QyVpjOAIr%2F4PR7ifWZbNZzUhpKqukbY3LhsyO3oqOIoMwB47KUGNYXnnw2lMcDoYZMBosQ%3D%3D",
            "expected_error": False,
            "description": "正常ファイル（PDFがダウンロードできるはず）"
        }
    ]
    
    # NextPublishingサービスを初期化
    service = NextPublishingService()
    
    print("=" * 80)
    print("Word2XHTML5 PDFエラー検出テスト")
    print("=" * 80)
    
    # 各テストケースを実行
    for i, test in enumerate(test_cases, 1):
        print(f"\nテストケース {i}: {test['name']}")
        print(f"説明: {test['description']}")
        print(f"URL: {test['url'][:100]}...")
        print(f"期待される結果: {'エラー' if test['expected_error'] else '正常'}")
        
        try:
            # PDFダウンロード可否をチェック
            is_downloadable, message = service.check_pdf_downloadable(test['url'])
            
            print(f"\n実行結果:")
            print(f"  - ダウンロード可能: {is_downloadable}")
            print(f"  - メッセージ: {message}")
            
            # 期待値と比較
            if test['expected_error']:
                # エラーが期待される場合
                if not is_downloadable:
                    print(f"  ✓ テスト成功: 期待通りエラーと判定されました")
                else:
                    print(f"  ✗ テスト失敗: エラーと判定されるべきですが、正常と判定されました")
            else:
                # 正常が期待される場合
                if is_downloadable:
                    print(f"  ✓ テスト成功: 期待通り正常と判定されました")
                else:
                    print(f"  ✗ テスト失敗: 正常と判定されるべきですが、エラーと判定されました")
                    
        except Exception as e:
            print(f"  ✗ テストエラー: {e}")
            logger.error(f"テストエラー: {e}", exc_info=True)
    
    # クリーンアップ
    service.close()
    
    print("\n" + "=" * 80)
    print("テスト完了")
    print("=" * 80)

def test_url_patterns():
    """URLパターンのテスト（実際のアクセスなし）"""
    print("\n" + "=" * 80)
    print("URLパターンテスト")
    print("=" * 80)
    
    test_patterns = [
        ("http://trial.nextpublishing.jp/upload_46tate/do_download?n=xxx", "正常パターン"),
        ("http://trial.nextpublishing.jp/upload_46tate/do_download_pdf?n=xxx", "エラーパターン"),
        ("https://trial.nextpublishing.jp/upload_46tate/do_download?n=xxx", "HTTPS正常パターン"),
        ("http://trial.nextpublishing.jp/upload_46tate/download?n=xxx", "不明なパターン"),
    ]
    
    for url, description in test_patterns:
        print(f"\nURL: {url}")
        print(f"説明: {description}")
        
        if 'do_download_pdf' in url:
            print("  → エラーURLパターンと判定")
        elif 'do_download?' in url:
            print("  → 正常URLパターンと判定")
        else:
            print("  → 不明なURLパターン")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Word2XHTML5 PDFエラー検出テスト")
    parser.add_argument('--pattern-only', action='store_true', 
                        help='URLパターンのテストのみ実行（実際のアクセスなし）')
    parser.add_argument('--real-test', action='store_true',
                        help='実際のURLにアクセスしてテスト')
    
    args = parser.parse_args()
    
    if args.pattern_only:
        test_url_patterns()
    elif args.real_test:
        # 注意: 実際のサーバーにアクセスするため、認証情報が必要
        print("警告: 実際のサーバーにアクセスします。認証情報が必要です。")
        response = input("続行しますか？ (y/N): ")
        if response.lower() == 'y':
            test_pdf_error_detection()
        else:
            print("テストを中止しました。")
    else:
        # デフォルトはパターンテストのみ
        test_url_patterns()
        print("\n実際のURLでテストする場合は --real-test オプションを使用してください。")