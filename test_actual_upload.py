#!/usr/bin/env python3
"""実際のアップロード検証（検証アプリと同じ条件）"""

import requests
import base64
from pathlib import Path
import zipfile
import tempfile

# 認証情報（検証アプリと同じ）
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
    """検証アプリと同じ条件でアップロードテスト"""
    print("テスト用ZIPファイルを作成中...")
    test_zip = create_test_zip()
    print(f"テストファイル作成完了: {test_zip}")
    
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
        print("アップロード開始...")
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
        
        print(f"HTTPステータス: {response.status_code}")
        print(f"レスポンスの最初の500文字:")
        print(response.text[:500])
        
        # 成功判定
        if 'ã¢ããã­ã¼ããå®äºãã¾ããã' in response.text:
            print("\n✅ アップロード成功！")
            print("文字化けパターンを検出しました。")
            return True
        else:
            print("\n❌ アップロード失敗")
            print("成功パターンが見つかりません。")
            return False
        
    finally:
        # テストファイル削除
        if test_zip.exists():
            test_zip.unlink()
            print(f"テストファイル削除: {test_zip}")

if __name__ == "__main__":
    test_upload()