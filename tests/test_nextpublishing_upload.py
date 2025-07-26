"""NextPublishingアップロードのテストスクリプト"""
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.nextpublishing_service import NextPublishingService, UploadSettings
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def test_single_file_upload():
    """単一ファイルアップロードのテスト"""
    print("\n=== 単一ファイルアップロードテスト ===")
    
    # テスト用のWordファイルパス（実際のファイルを指定）
    test_file = Path("test_document.docx")
    
    if not test_file.exists():
        print(f"テストファイルが見つかりません: {test_file}")
        # ダミーファイルを作成（実際のテストでは実際のWordファイルを使用）
        print("ダミーファイルでテストを継続します")
        return
    
    # サービスを初期化
    settings = UploadSettings(
        project_name="テスト - 山城技術の泉",
        email="yamashiro.takashi@gmail.com"
    )
    service = NextPublishingService(settings)
    
    # アップロードを実行
    success, message, control_number = service.upload_single_file(test_file)
    
    print(f"結果: {'成功' if success else '失敗'}")
    print(f"メッセージ: {message}")
    if control_number:
        print(f"管理番号: {control_number}")
    
    service.close()


def test_form_data_preparation():
    """フォームデータの準備テスト"""
    print("\n=== フォームデータ準備テスト ===")
    
    settings = UploadSettings()
    
    form_data = {
        'project_name': settings.project_name,
        'orientation': str(settings.orientation),
        'has_cover': str(settings.has_cover),
        'has_tombo': str(settings.has_tombo),
        'style_vertical': str(settings.style_vertical),
        'style_horizontal': str(settings.style_horizontal),
        'has_index': str(settings.has_index),
        'mail': settings.email,
        'mailconf': settings.email
    }
    
    print("フォームデータ:")
    for key, value in form_data.items():
        print(f"  {key}: {value}")
    
    # 複数ファイル用のフィールド名確認
    print("\n複数ファイルフィールド:")
    for i in range(1, 11):
        print(f"  file{i}: Wordファイル{i}")


def test_pdf_url_check():
    """PDFダウンロードURLチェックのテスト"""
    print("\n=== PDFダウンロードURLチェックテスト ===")
    
    # テスト用URL（実際のURLではない）
    test_urls = [
        "http://trial.nextpublishing.jp/upload_46tate/do_download_pdf?n=DUMMY",
        "http://trial.nextpublishing.jp/upload_46tate/"
    ]
    
    service = NextPublishingService()
    
    for url in test_urls:
        print(f"\nURL: {url}")
        is_downloadable, message = service.check_pdf_downloadable(url)
        print(f"ダウンロード可能: {is_downloadable}")
        print(f"メッセージ: {message}")
    
    service.close()


if __name__ == "__main__":
    print("NextPublishingサービステスト")
    print("=" * 50)
    
    # フォームデータの確認
    test_form_data_preparation()
    
    # 実際のアップロードテストは要注意
    # test_single_file_upload()
    
    # PDFチェックのテスト
    # test_pdf_url_check()
    
    print("\n\n注意: 実際のアップロードテストはコメントアウトしています。")
    print("実行する場合は、適切なWordファイルを準備してください。")