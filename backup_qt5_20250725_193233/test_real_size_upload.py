#!/usr/bin/env python3
"""
実際のサイズ（6MB）でのアップロードテスト
"""
import sys
import tempfile
import zipfile
import os
from pathlib import Path

# プロジェクトのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from core.api_processor import ApiProcessor

def create_realistic_zip(target_size_mb=6):
    """実際のサイズのReVIEWプロジェクトZIPを作成"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.zip', delete=False) as tmp:
        test_zip_path = Path(tmp.name)
    
    print(f"リアルなZIPファイル作成中: 目標 {target_size_mb}MB")
    
    # 有効なReVIEW設定ファイル
    config_yml = """# config.yml
booktitle: "技術の泉シリーズ テストブック"
aut: ["テスト著者"]
language: ja
review_version: 5.0
texdocumentclass: ["jsbook", "uplatex,papersize,b5paper,openany"]
"""
        
    catalog_yml = """# catalog.yml
PREDEF:

CHAPS:
  - chap01.re
  - chap02.re
  - chap03.re
  - chap04.re
  - chap05.re

APPENDIX:

POSTDEF:
"""
    
    # ZIPファイルを作成（圧縮なしでサイズを確保）
    with zipfile.ZipFile(test_zip_path, 'w', zipfile.ZIP_STORED) as zf:
        # 設定ファイル
        zf.writestr('ReVIEW/config.yml', config_yml.encode('utf-8'))
        zf.writestr('ReVIEW/catalog.yml', catalog_yml.encode('utf-8'))
        
        # 実際のReVIEWファイルのような内容を生成
        target_bytes = target_size_mb * 1024 * 1024
        current_size = 0
        
        # 章ごとにファイルを作成
        for i in range(1, 6):
            chapter_content = f"= 第{i}章 テスト章\n\n"
            
            # 日本語テキストを含む現実的な内容
            sample_text = """
これはテスト用の文章です。技術書の内容を模擬しています。
プログラミングの基本的な概念について説明します。

//list[sample{i}][サンプルコード{i}]{{
def hello_world():
    print("Hello, World!")
    return True
//}}

@<list>{{sample{i}}}はPythonの基本的な関数の例です。

"""
            
            # ファイルサイズを調整
            while len(chapter_content.encode('utf-8')) < target_bytes // 5:
                chapter_content += sample_text.format(i=i)
                chapter_content += "\n" * 10  # 改行で調整
            
            filename = f'ReVIEW/chap{i:02d}.re'
            zf.writestr(filename, chapter_content.encode('utf-8'))
            current_size += len(chapter_content.encode('utf-8'))
        
        # 画像ファイル（ダミー）
        dummy_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR' + b'\x00' * 100000
        zf.writestr('ReVIEW/images/dummy.png', dummy_image)
        
    actual_size = test_zip_path.stat().st_size
    print(f"ZIPファイル作成完了: {test_zip_path}")
    print(f"実際のサイズ: {actual_size:,} bytes ({actual_size / 1024 / 1024:.2f} MB)")
    
    # ファイル一覧を表示
    with zipfile.ZipFile(test_zip_path, 'r') as zf:
        print("\nZIP内のファイル:")
        for info in zf.infolist():
            print(f"  {info.filename}: {info.file_size:,} bytes")
    
    return test_zip_path

def test_upload():
    """アップロードテスト実行"""
    print("="*60)
    print("実サイズファイルのアップロードテスト")
    print("="*60)
    
    # 6MBのテストファイル作成
    test_zip_path = create_realistic_zip(6)
    
    try:
        # APIプロセッサを作成
        processor = ApiProcessor()
        
        # ログとエラーを記録
        logs = []
        errors = []
        
        def log_handler(message, level):
            log_entry = f"[{level}] {message}"
            print(log_entry)
            logs.append((level, message))
            if level == "ERROR":
                errors.append(message)
        
        def progress_handler(progress):
            if progress % 10 == 0:
                print(f">>> 進捗: {progress}%")
        
        def status_handler(status):
            print(f">>> ステータス: {status}")
        
        processor.log_message.connect(log_handler)
        processor.progress_updated.connect(progress_handler)
        processor.status_updated.connect(status_handler)
        
        # アップロード実行
        print("\nアップロード開始...")
        print("-" * 40)
        
        jobid = processor.upload_zip(test_zip_path)
        
        print("-" * 40)
        
        if jobid:
            print(f"\n✅ アップロード成功!")
            print(f"Job ID: {jobid}")
            
            # 変換処理も試す
            print("\n変換処理を実行...")
            success, download_path, warnings = processor.process_zip_file(test_zip_path)
            
            if success:
                print(f"\n✅ 変換成功!")
                if download_path:
                    print(f"ダウンロードファイル: {download_path}")
                if warnings:
                    print(f"警告: {len(warnings)}件")
            else:
                print(f"\n❌ 変換失敗")
                
        else:
            print(f"\n❌ アップロード失敗")
            
        # エラーサマリー
        if errors:
            print(f"\n{'='*40}")
            print(f"エラー詳細 ({len(errors)}件):")
            for i, error in enumerate(errors, 1):
                print(f"{i}. {error}")
                
    except Exception as e:
        print(f"\n❌ 例外発生: {type(e).__name__}")
        print(f"詳細: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # クリーンアップ
        if test_zip_path.exists():
            test_zip_path.unlink()
            print(f"\nテストファイル削除完了")

if __name__ == "__main__":
    test_upload()