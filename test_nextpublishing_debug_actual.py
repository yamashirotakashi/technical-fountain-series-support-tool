#!/usr/bin/env python3
"""
NextPublishing実際のアップロードデバッグテスト
実際のWordファイルを使用してNextPublishingServiceの詳細なデバッグログを取得
"""
import sys
import os
from pathlib import Path
import logging

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

def setup_detailed_logging():
    """詳細なロギング設定"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('nextpublishing_debug.log', encoding='utf-8')
        ]
    )

def test_actual_nextpublishing_upload():
    """実際のNextPublishingアップロードテスト"""
    setup_detailed_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # インポート
        from services.nextpublishing_service import NextPublishingService, UploadSettings
        from src.slack_pdf_poster import ConfigManager
        
        logger.info("=== NextPublishing実際アップロードテスト開始 ===")
        
        # 設定管理システムの初期化
        config_manager = ConfigManager()
        logger.info("ConfigManager初期化完了")
        
        # アップロード設定
        settings = UploadSettings()
        settings.email = "yamashiro.takashi@gmail.com"
        logger.info(f"アップロード設定: email={settings.email}")
        
        # サービス初期化
        service = NextPublishingService(settings, config_manager)
        logger.info("NextPublishingService初期化完了")
        
        # 設定値確認
        base_url = config_manager.get("api.nextpublishing.base_url")
        username = config_manager.get("api.nextpublishing.username")
        password = config_manager.get("api.nextpublishing.password")
        
        logger.info(f"設定値確認:")
        logger.info(f"  - Base URL: {base_url}")
        logger.info(f"  - Username: {username}")
        logger.info(f"  - Password: {'*' * len(password) if password else 'None'}")
        
        # テスト用の小さなWordファイルを作成
        test_file = Path("test_upload.docx")
        
        # 既存のWordファイルがあるかチェック
        sample_files = [
            Path("venv/Lib/site-packages/docx/templates/default.docx"),
            Path("backup/2025-01-26_exe_build_complete/sample/test.docx"),
            Path("backup/sample.docx"),
            Path("sample.docx"),
            Path("test.docx")
        ]
        
        existing_file = None
        for sample_file in sample_files:
            if sample_file.exists():
                existing_file = sample_file
                logger.info(f"既存のサンプルファイルを発見: {sample_file}")
                break
        
        if existing_file:
            test_file = existing_file
        else:
            # 最小限のWordファイルを作成（実際のテスト用）
            logger.warning("既存のWordファイルが見つかりません。最小限のテストファイルを作成します")
            # 注意: 実際のWordファイル形式のバイナリデータが必要
            logger.error("実際のWordファイルが必要です。テストをスキップします。")
            return False
            
        logger.info(f"使用するテストファイル: {test_file}")
        logger.info(f"ファイルサイズ: {test_file.stat().st_size} bytes")
        
        # 実際のアップロード実行
        logger.info("=== 実際のアップロード開始 ===")
        success, message, control_number = service.upload_single_file(test_file)
        
        logger.info("=== アップロード結果 ===")
        logger.info(f"成功フラグ: {success}")
        logger.info(f"メッセージ: {message}")
        logger.info(f"管理番号: {control_number}")
        
        if success:
            logger.info("✅ NextPublishingアップロード成功！")
            if control_number:
                logger.info(f"📋 管理番号: {control_number}")
            return True
        else:
            logger.error(f"❌ NextPublishingアップロード失敗: {message}")
            return False
            
    except Exception as e:
        logger.error(f"テストエラー: {e}")
        import traceback
        logger.error(f"スタックトレース: {traceback.format_exc()}")
        return False
        
    finally:
        # クリーンアップ
        if service:
            service.close()

def main():
    """メインテスト実行"""
    print("NextPublishing実際アップロードデバッグテスト")
    print("=" * 60)
    
    success = test_actual_nextpublishing_upload()
    
    print("=" * 60)
    if success:
        print("SUCCESS: NextPublishingアップロードテスト成功")
        print("debug.logファイルで詳細なレスポンス内容を確認してください")
    else:
        print("FAILED: NextPublishingアップロードテスト失敗")
        print("nextpublishing_debug.logファイルでエラー詳細を確認してください")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())