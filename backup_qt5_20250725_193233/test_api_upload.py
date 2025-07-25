#!/usr/bin/env python3
"""
API アップロードのデバッグ用テストスクリプト
"""
import sys
from pathlib import Path

# プロジェクトのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from core.api_processor import ApiProcessor
import tempfile
import zipfile

def test_upload():
    """アップロードをテスト"""
    # テスト用のZIPファイルを作成
    with tempfile.NamedTemporaryFile(mode='w', suffix='.zip', delete=False) as tmp:
        test_zip_path = Path(tmp.name)
        
    # 小さなテストファイルを含むZIPを作成
    with zipfile.ZipFile(test_zip_path, 'w') as zf:
        # 小さなテストデータ
        test_content = "This is a test file for API upload testing.\n" * 100
        zf.writestr('test_file.txt', test_content)
        
    print(f"テストファイル作成: {test_zip_path}")
    print(f"ファイルサイズ: {test_zip_path.stat().st_size} bytes")
    
    # APIプロセッサを作成
    processor = ApiProcessor()
    
    # ログハンドラを追加
    def log_handler(message, level):
        print(f"[{level}] {message}")
    
    processor.log_message.connect(log_handler)
    
    # アップロードを実行
    print("\nアップロード開始...")
    try:
        jobid = processor.upload_zip(test_zip_path)
        if jobid:
            print(f"アップロード成功: Job ID = {jobid}")
        else:
            print("アップロード失敗")
    except Exception as e:
        print(f"エラー発生: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # テストファイルを削除
        test_zip_path.unlink()

if __name__ == "__main__":
    test_upload()