"""エラーチェック統合テスト

エラーチェックの成功・失敗判定が正しく動作するかテスト
"""
import sys
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.error_check_validator import ErrorCheckValidator


def test_error_check_validator():
    """ErrorCheckValidatorのテスト"""
    print("=== ErrorCheckValidator テスト ===\n")
    
    validator = ErrorCheckValidator()
    
    # テストケース
    test_cases = [
        {
            "name": "03_powershell_sample_basic.docx（正常）",
            "url": "http://trial.nextpublishing.jp/upload_46tate/do_download_pdf?n=DWszyxVNUi%2BRBto4Xa8%2FyjA%2BjYdXFlsTir1jImPejtSu%2BIZRwXOD4y5BeT33OTTPZV%2BigZJPiYsnQ603POfqYw%3D%3D",
            "expected_error": False
        },
        {
            "name": "04_powershell_sample_advanced.docx（エラー）",
            "url": "http://trial.nextpublishing.jp/upload_46tate/do_download_pdf?n=QEAhIi0OjyxbOZL1RKha60l4xJF7jv02n42nfHrq6bfYLk%2FN1MhhUp1IKraR3uS2DgTm%2FMQGcEQiAvVpnitNYw%3D%3D",
            "expected_error": True
        },
        {
            "name": "空のURL",
            "url": "",
            "expected_error": True
        },
        {
            "name": "ZIP URL（PDF URLではない）",
            "url": "http://trial.nextpublishing.jp/upload_46tate/do_download?n=zCP6W7ysW8zfiN6iUDRWlRHtJpJsKxM8MQ9qltKs1VQj3kWMAajxB2bPmdm9Ya4PjpxJsT5HNDCxQZzBtjEVRA%3D%3D",
            "expected_error": True
        }
    ]
    
    # 各テストケースを実行
    for test_case in test_cases:
        print(f"テスト: {test_case['name']}")
        print(f"URL: {test_case['url'][:80]}..." if test_case['url'] else "URL: (空)")
        
        is_error, reason = validator.validate_pdf_url(
            test_case['url'], 
            test_case['name']
        )
        
        print(f"結果: {'エラー' if is_error else '正常'}")
        print(f"理由: {reason}")
        
        # 期待値と比較
        if is_error == test_case['expected_error']:
            print("✅ 期待通りの結果")
        else:
            print("❌ 期待と異なる結果")
            print(f"   期待: {'エラー' if test_case['expected_error'] else '正常'}")
            print(f"   実際: {'エラー' if is_error else '正常'}")
        
        print("-" * 60)
        print()


def test_batch_validation():
    """バッチ検証のテスト"""
    print("\n=== バッチ検証テスト ===\n")
    
    validator = ErrorCheckValidator()
    
    # テスト用のfile_url_map
    file_url_map = {
        "03_powershell_sample_basic.docx": "http://trial.nextpublishing.jp/upload_46tate/do_download_pdf?n=DWszyxVNUi%2BRBto4Xa8%2FyjA%2BjYdXFlsTir1jImPejtSu%2BIZRwXOD4y5BeT33OTTPZV%2BigZJPiYsnQ603POfqYw%3D%3D",
        "04_powershell_sample_advanced.docx": "http://trial.nextpublishing.jp/upload_46tate/do_download_pdf?n=QEAhIi0OjyxbOZL1RKha60l4xJF7jv02n42nfHrq6bfYLk%2FN1MhhUp1IKraR3uS2DgTm%2FMQGcEQiAvVpnitNYw%3D%3D",
        "05_appendix.docx": "http://trial.nextpublishing.jp/upload_46tate/do_download_pdf?n=somevalidurl"  # 仮のURL
    }
    
    error_files, normal_files = validator.validate_batch(file_url_map)
    
    print(f"エラーファイル数: {len(error_files)}")
    for error in error_files:
        print(f"  - {error['filename']}: {error['reason']}")
    
    print(f"\n正常ファイル数: {len(normal_files)}")
    for normal in normal_files:
        print(f"  - {normal['filename']}: {normal['reason']}")
    
    print("\n=== テスト完了 ===")


def test_email_processor_integration():
    """EmailProcessorとの統合テスト"""
    print("\n=== EmailProcessor統合テスト ===\n")
    
    from core.email_processors import Word2XHTML5EmailProcessor
    
    processor = Word2XHTML5EmailProcessor()
    
    # サンプルメール本文（実際のメールに近い形式）
    sample_email = """
    いつもお世話になっております。
    
    ダウンロード用URLのご案内
    
    ファイル名：05_appendix.docx
    
    以下のURLからダウンロードしてください：
    
    ZIP形式：
    http://trial.nextpublishing.jp/upload_46tate/do_download?n=zCP6W7ysW8zfiN6iUDRWlRHtJpJsKxM8MQ9qltKs1VQj3kWMAajxB2bPmdm9Ya4PjpxJsT5HNDCxQZzBtjEVRA%3D%3D
    
    GCF形式：
    http://trial.nextpublishing.jp/upload_46tate/do_download_gcf?n=abc123
    
    EPUB形式：
    http://trial.nextpublishing.jp/upload_46tate/do_download_epub?n=def456
    
    PDF形式（1つ目）：
    http://trial.nextpublishing.jp/upload_46tate/do_download_pdf?n=ghi789
    
    PDF形式（2つ目・最後）：
    http://trial.nextpublishing.jp/upload_46tate/do_download_pdf?n=jkl012
    """
    
    # URLを抽出
    urls = processor.extract_urls(sample_email)
    print("抽出されたURL:")
    for url_type, url in urls.items():
        print(f"  {url_type}: {url[:80]}...")
    
    # purpose別のURL取得
    print("\npurpose別のURL:")
    download_url = processor.get_url_for_purpose(urls, 'download')
    print(f"  download用: {download_url[:80] if download_url else 'なし'}...")
    
    error_check_url = processor.get_url_for_purpose(urls, 'error_check')
    print(f"  error_check用: {error_check_url[:80] if error_check_url else 'なし'}...")
    
    # 最後のPDF URLが使用されているか確認
    if 'jkl012' in error_check_url:
        print("\n✅ 最後のPDF URLが正しく使用されています")
    else:
        print("\n❌ 最後のPDF URLが使用されていません")


if __name__ == "__main__":
    # ErrorCheckValidatorのテスト
    test_error_check_validator()
    
    # バッチ検証のテスト
    test_batch_validation()
    
    # EmailProcessor統合テスト
    test_email_processor_integration()