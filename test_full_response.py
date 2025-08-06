#!/usr/bin/env python3
"""レスポンス全体を確認"""

import requests
import base64
from pathlib import Path
import zipfile
import tempfile

# 認証情報
USERNAME = "ep_user"
PASSWORD = "Nn7eUTX5"
EMAIL = "yamashiro.takashi@gmail.com"
BASE_URL = "http://trial.nextpublishing.jp/rapture/"

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

def test_upload():
    """レスポンス全体を確認"""
    test_zip = create_test_zip()
    
    try:
        # セッション作成
        session = requests.Session()
        
        # Basic認証設定
        credentials = f"{USERNAME}:{PASSWORD}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # アップロード実行
        with open(test_zip, 'rb') as f:
            files = {
                'userfile': (test_zip.name, f, 'application/zip')
            }
            data = {
                'mail': EMAIL,
                'mailconf': EMAIL
            }
            
            response = session.post(
                BASE_URL,
                files=files,
                data=data,
                headers=headers
            )
        
        # レスポンス全体を保存
        with open("response_full.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print("レスポンスを response_full.html に保存しました。")
        
        # bodyタグ内のテキストを抽出
        import re
        body_match = re.search(r'<body[^>]*>(.*?)</body>', response.text, re.DOTALL | re.IGNORECASE)
        if body_match:
            body_text = body_match.group(1)
            # HTMLタグを除去
            text_only = re.sub(r'<[^>]+>', '', body_text)
            text_only = re.sub(r'\s+', ' ', text_only).strip()
            print(f"\nbodyタグ内のテキスト:")
            print(text_only)
            
            # 文字化けパターンの検索
            if 'ã¢ããã­ã¼ããå®äºãã¾ããã' in text_only:
                print("\n✅ 文字化けパターン検出！")
            else:
                print("\n❌ 文字化けパターンが見つかりません")
                print(f"\n文字コードの確認:")
                for char in 'ã¢ããã­ã¼ããå®äºãã¾ããã':
                    print(f"{char} = {ord(char):04x}")
        
    finally:
        if test_zip.exists():
            test_zip.unlink()

if __name__ == "__main__":
    test_upload()