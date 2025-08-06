#!/usr/bin/env python3
"""詳細なデバッグ情報付きアップロードテスト"""

import requests
import base64
from pathlib import Path
import zipfile
import tempfile
import sys

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

def debug_response(response):
    """レスポンスの詳細をデバッグ"""
    print("\n" + "="*60)
    print("レスポンスデバッグ情報:")
    print("="*60)
    
    # ステータスコード
    print(f"HTTPステータス: {response.status_code}")
    
    # ヘッダー
    print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    print(f"Content-Length: {response.headers.get('Content-Length', 'N/A')}")
    print(f"Encoding: {response.encoding}")
    
    # レスポンスの長さ
    print(f"レスポンスサイズ: {len(response.content)} bytes")
    print(f"テキストサイズ: {len(response.text)} characters")
    
    # 最初の500文字（生テキスト）
    print("\n生のレスポンステキスト（最初の500文字）:")
    print(repr(response.text[:500]))
    
    # BOMチェック
    if response.text.startswith('\ufeff'):
        print("\n⚠️ BOMあり (\\ufeff)")
    elif response.text.startswith('ï»¿'):
        print("\n⚠️ BOMあり (ï»¿)")
    
    # bodyタグ内のテキスト抽出
    import re
    body_match = re.search(r'<body[^>]*>(.*?)</body>', response.text, re.DOTALL | re.IGNORECASE)
    if body_match:
        body_text = body_match.group(1)
        text_only = re.sub(r'<[^>]+>', '', body_text)
        text_only = re.sub(r'\s+', ' ', text_only).strip()
        
        print("\nbodyタグ内のテキスト:")
        print(text_only)
        
        # 文字化けパターンの確認
        patterns_to_check = [
            'ã¢ããã­ã¼ããå®äºãã¾ããã',
            'アップロードが完了しました',
            'アップロード完了',
            'ã¢ããã­ã¼ã',
            '完了',
            '成功'
        ]
        
        print("\n文字化けパターンチェック:")
        for pattern in patterns_to_check:
            if pattern in text_only:
                print(f"  ✅ 検出: {pattern}")
            else:
                print(f"  ❌ 未検出: {pattern}")
        
        # 各文字のコードポイント表示（最初の50文字）
        print("\n文字コードポイント（最初の50文字）:")
        for i, char in enumerate(text_only[:50]):
            if char not in ' \n\t':
                print(f"  [{i}] '{char}' = U+{ord(char):04X}")
    
    # バイトレベルでのチェック
    print("\nバイトレベルチェック:")
    mojibake_bytes = 'ã¢ããã­ã¼ããå®äºãã¾ããã'.encode('utf-8')
    if mojibake_bytes in response.content:
        print("  ✅ バイトレベルで文字化けパターン検出")
    else:
        print("  ❌ バイトレベルで文字化けパターン未検出")

def test_upload():
    """詳細デバッグ付きアップロードテスト"""
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
        print("\nアップロード開始...")
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
        
        # 詳細デバッグ
        debug_response(response)
        
        # レスポンスを保存
        with open("debug_response.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("\nレスポンスを debug_response.html に保存しました。")
        
    finally:
        # テストファイル削除
        if test_zip.exists():
            test_zip.unlink()
            print(f"\nテストファイル削除: {test_zip}")

if __name__ == "__main__":
    test_upload()