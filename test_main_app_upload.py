#!/usr/bin/env python3
"""メインアプリケーションのアップロードテスト - 文字化けパターン対応確認"""

import os
import sys
from pathlib import Path
import zipfile
import tempfile

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.nextpublishing_service import NextPublishingService, UploadSettings
from utils.logger import get_logger

def create_test_zip():
    """テスト用ZIPファイルを作成"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as txt_file:
        txt_file.write("Test content for NextPublishing upload test\n")
        txt_file.write("このファイルはテスト用です。\n")
        txt_path = Path(txt_file.name)
    
    # ZIPファイル作成
    zip_path = Path(tempfile.gettempdir()) / "test_upload.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(txt_path, arcname="test.txt")
    
    # 一時テキストファイル削除
    txt_path.unlink()
    
    return zip_path

def test_main_app_upload():
    """メインアプリケーションでアップロードテスト"""
    logger = get_logger(__name__)
    
    # テストZIPファイル作成
    logger.info("テスト用ZIPファイルを作成中...")
    test_zip = create_test_zip()
    logger.info(f"テストファイル作成完了: {test_zip}")
    
    try:
        # UploadSettings設定
        settings = UploadSettings()
        settings.email = "yamashiro.takashi@gmail.com"
        settings.email_confirmation = "yamashiro.takashi@gmail.com"
        
        # NextPublishingServiceでアップロード実行
        logger.info("メインアプリケーションでアップロード開始...")
        service = NextPublishingService(settings, process_mode="traditional")
        
        # アップロード実行
        success, message, control_number = service.upload_single_file(test_zip)
        
        # 結果出力
        logger.info("=" * 60)
        logger.info(f"テスト結果:")
        logger.info(f"  成功: {success}")
        logger.info(f"  メッセージ: {message}")
        logger.info(f"  管理番号: {control_number}")
        logger.info("=" * 60)
        
        if success:
            logger.info("✅ メインアプリケーションでのアップロード成功！")
            logger.info("文字化けパターンの対応が正常に動作しています。")
        else:
            logger.error("❌ メインアプリケーションでのアップロード失敗")
            logger.error("詳細ログを確認してください。")
        
        return success
        
    finally:
        # テストファイル削除
        if test_zip.exists():
            test_zip.unlink()
            logger.info(f"テストファイル削除: {test_zip}")

if __name__ == "__main__":
    success = test_main_app_upload()
    sys.exit(0 if success else 1)