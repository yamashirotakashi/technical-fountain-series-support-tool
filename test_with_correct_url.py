#!/usr/bin/env python3
"""正しいURLでメインアプリをテスト"""

import sys
from pathlib import Path
import tempfile
import zipfile

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from services.nextpublishing_service import NextPublishingService

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

def main():
    """正しいURLでテスト実行"""
    print("="*60)
    print("正しいURL設定でのテスト")
    print("="*60)
    
    # テストファイル作成
    test_zip = create_test_zip()
    print(f"テストファイル作成: {test_zip}")
    
    try:
        # 環境変数で正しいURLを強制設定
        import os
        os.environ['NEXTPUBLISHING_BASE_URL'] = 'http://trial.nextpublishing.jp/rapture/'
        
        # NextPublishingサービス初期化
        service = NextPublishingService()
        
        # 正しいURLが設定されたか確認
        print(f"使用URL: {service.base_url}")
        
        # アップロード実行
        print("\nアップロード実行中...")
        success, message, management_number = service.upload_single_file(test_zip)
        
        # 結果表示
        print("\n" + "="*60)
        print("実行結果:")
        print(f"  成功: {success}")
        print(f"  メッセージ: {message}")
        print(f"  管理番号: {management_number}")
        print("="*60)
        
        if success:
            print("\n✅ アップロード成功！")
        else:
            print("\n❌ アップロード失敗")
        
    finally:
        # テストファイル削除
        if test_zip.exists():
            test_zip.unlink()
            print(f"\nテストファイル削除: {test_zip}")

if __name__ == "__main__":
    main()