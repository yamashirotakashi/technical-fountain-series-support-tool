#!/usr/bin/env python3
"""401エラーハンドリングの詳細テスト"""

import sys
from pathlib import Path
import logging

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# ロギング設定
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_401_handling():
    """401エラーハンドリングの詳細確認"""
    print("=== 401エラーハンドリング詳細テスト ===")
    
    try:
        from services.nextpublishing_service import NextPublishingService
        
        # テスト用URL（03ファイル）
        test_url = "http://trial.nextpublishing.jp/upload_46tate/do_download_pdf?n=UoJtKTuBr9M0keNGidNOpCDBnb1QteICcgX9SyEgrDAyl1SJIGoR7KLDqhk03CA3ukU299utI%2B2F3fMTTXVA8Q%3D%3D"
        
        print(f"\nテストURL: {test_url}")
        print("\nPDF検証実行...")
        
        service = NextPublishingService()
        
        # ログレベルを一時的にDEBUGに設定
        service.logger.setLevel(logging.DEBUG)
        
        is_downloadable, message = service.check_pdf_downloadable(test_url)
        
        print(f"\n検証結果:")
        print(f"  ダウンロード可能: {is_downloadable}")
        print(f"  メッセージ: {message}")
        
        service.close()
        
    except Exception as e:
        print(f"\nエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_401_handling()