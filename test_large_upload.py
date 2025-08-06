#!/usr/bin/env python3
"""
大きなファイルでのアップロードテスト
実際のユーザー環境（6MB）を再現
"""
import sys
import tempfile
import zipfile
import os
from pathlib import Path

# プロジェクトのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from core.api_processor import ApiProcessor

def create_test_zip(size_mb=6):
    """指定サイズのテストZIPファイルを作成"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.zip', delete=False) as tmp:
        test_zip_path = Path(tmp.name)
    
    print(f"テストZIPファイル作成中: {size_mb}MB")
    
    # 指定サイズのファイルを含むZIPを作成
    with zipfile.ZipFile(test_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # ReVIEWプロジェクトを模擬
        chunk_size = 1024 * 1024  # 1MB
        total_size = size_mb * chunk_size
        
        # 有効なReVIEW設定ファイル
        config_yml = """# config.yml
booktitle: "Test Book"
aut: ["Test Author"]
language: ja
review_version: 5.0
"""
        
        catalog_yml = """# catalog.yml
PREDEF:

CHAPS:
  - chap01.re
  - chap02.re
  - chap03.re

APPENDIX:

POSTDEF:
"""
        
        # 複数のファイルに分割して実際のプロジェクトを模擬
        files_data = {
            'ReVIEW/config.yml': config_yml.encode('utf-8'),
            'ReVIEW/catalog.yml': catalog_yml.encode('utf-8'),
            'ReVIEW/chap01.re': b'= Chapter 1\n\n' + b'A' * (total_size // 3),
            'ReVIEW/chap02.re': b'= Chapter 2\n\n' + b'B' * (total_size // 3),
            'ReVIEW/chap03.re': b'= Chapter 3\n\n' + b'C' * (total_size // 3),
            'ReVIEW/images/sample.png': b'\x89PNG\r\n\x1a\n' + b'\x00' * 10000,
        }
        
        for filename, data in files_data.items():
            zf.writestr(filename, data)
    
    actual_size = test_zip_path.stat().st_size
    print(f"ZIPファイル作成完了: {test_zip_path}")
    print(f"実際のサイズ: {actual_size:,} bytes ({actual_size / 1024 / 1024:.2f} MB)")
    
    return test_zip_path

def test_upload_with_size(size_mb=6):
    """指定サイズでアップロードテスト"""
    print(f"\n{'='*60}")
    print(f"{size_mb}MB ファイルのアップロードテスト")
    print(f"{'='*60}\n")
    
    # テストファイル作成
    test_zip_path = create_test_zip(size_mb)
    
    try:
        # APIプロセッサを作成
        processor = ApiProcessor()
        
        # ログハンドラ
        logs = []
        def log_handler(message, level):
            log_entry = f"[{level}] {message}"
            print(log_entry)
            logs.append(log_entry)
        
        # 進捗ハンドラ
        last_progress = -1
        def progress_handler(progress):
            nonlocal last_progress
            if progress != last_progress and progress % 10 == 0:
                print(f">>> 進捗: {progress}%")
                last_progress = progress
        
        processor.log_message.connect(log_handler)
        processor.progress_updated.connect(progress_handler)
        
        # アップロード実行
        print("\nアップロード開始...")
        jobid = processor.upload_zip(test_zip_path)
        
        if jobid:
            print(f"\n✅ アップロード成功: Job ID = {jobid}")
            
            # ステータス確認もテスト
            print("\nステータス確認中...")
            result, download_url, messages = processor.check_status(jobid)
            print(f"結果: {result}")
            if download_url:
                print(f"ダウンロードURL: {download_url}")
            if messages:
                print(f"メッセージ: {len(messages)}件")
                
        else:
            print("\n❌ アップロード失敗")
            
        # エラーログを確認
        error_logs = [log for log in logs if "[ERROR]" in log]
        if error_logs:
            print(f"\nエラーログ ({len(error_logs)}件):")
            for error in error_logs:
                print(f"  {error}")
                
    except Exception as e:
        print(f"\n❌ 例外発生: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # テストファイルを削除
        if test_zip_path.exists():
            test_zip_path.unlink()
            print(f"\nテストファイル削除: {test_zip_path}")

def main():
    """メイン処理"""
    # 段階的にテスト
    test_sizes = [1, 3, 6, 10]  # MB
    
    for size in test_sizes:
        test_upload_with_size(size)
        print("\n" + "="*60 + "\n")
        
        # 次のテストまで少し待機
        import time
        if size < test_sizes[-1]:
            print("次のテストまで5秒待機...")
            time.sleep(5)

if __name__ == "__main__":
    # 引数でサイズ指定も可能
    if len(sys.argv) > 1:
        try:
            size = int(sys.argv[1])
            test_upload_with_size(size)
        except ValueError:
            print("使用方法: python test_large_upload.py [サイズ(MB)]")
    else:
        # デフォルトは6MBのみ
        test_upload_with_size(6)