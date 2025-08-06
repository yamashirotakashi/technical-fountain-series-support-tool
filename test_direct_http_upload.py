#!/usr/bin/env python3
"""
HTTPリクエストによる直接アップロードテスト
実際のWebフォームの仕様に基づいた実装
"""
import requests
from pathlib import Path
import logging
from requests.auth import HTTPBasicAuth

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_http_upload():
    """HTTPリクエストでの直接アップロード"""
    
    # 設定
    username = "ep_user"
    password = "Nextpublishing20241218@2024"
    base_url = "http://trial.nextpublishing.jp/rapture/"
    test_file = Path("venv/Lib/site-packages/docx/templates/default.docx")
    
    if not test_file.exists():
        logger.error(f"テストファイルが見つかりません: {test_file}")
        return False
    
    logger.info(f"テストファイル: {test_file.name} ({test_file.stat().st_size} bytes)")
    
    # セッション作成
    session = requests.Session()
    session.auth = HTTPBasicAuth(username, password)
    
    # ヘッダー設定（ブラウザを模倣）
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'http://trial.nextpublishing.jp',
        'Referer': base_url
    }
    session.headers.update(headers)
    
    try:
        # まずフォームページにアクセスしてセッションを確立
        logger.info("フォームページにアクセス中...")
        response = session.get(base_url)
        logger.info(f"フォームページ取得: HTTP {response.status_code}")
        
        # HTMLフォームの構造に基づいてファイルアップロード
        # enctype="multipart/form-data" でuserfileフィールドにファイルを送信
        with open(test_file, 'rb') as f:
            files = {
                'userfile': (test_file.name, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # その他のフォームデータ
            data = {
                'mail': 'yamashiro.takashi@gmail.com',
                'mailconf': 'yamashiro.takashi@gmail.com'  # 確認用メールアドレス
            }
            
            logger.info("ファイルアップロード中...")
            logger.info(f"送信先: {base_url}")
            logger.info(f"ファイル: {test_file.name}")
            logger.info(f"メール: {data['mail']}")
            
            # POSTリクエスト送信
            response = session.post(
                base_url,
                files=files,
                data=data,
                allow_redirects=True  # リダイレクトを自動的に追従
            )
            
            logger.info(f"レスポンス: HTTP {response.status_code}")
            logger.info(f"最終URL: {response.url}")
            logger.info(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            # レスポンス内容を解析
            response_text = response.text.lower()
            
            # 成功パターンのチェック
            success_patterns = [
                'アップロード完了',
                '受付完了',
                'success',
                '管理番号',
                '受付番号',
                '成功',
                'ファイルを受け付けました',
                '処理を開始'
            ]
            
            for pattern in success_patterns:
                if pattern.lower() in response_text:
                    logger.info(f"✅ 成功パターン検出: {pattern}")
                    
                    # レスポンスをファイルに保存
                    with open("success_response.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    logger.info("成功レスポンスをsuccess_response.htmlに保存")
                    
                    # 管理番号を探す
                    import re
                    control_patterns = [
                        r'受付番号[:\s]*([A-Z0-9\-]+)',
                        r'管理番号[:\s]*([A-Z0-9\-]+)',
                        r'ID[:\s]*([A-Z0-9\-]+)'
                    ]
                    
                    for pattern in control_patterns:
                        match = re.search(pattern, response.text, re.IGNORECASE)
                        if match:
                            control_number = match.group(1)
                            logger.info(f"📋 管理番号: {control_number}")
                            break
                    
                    return True
            
            # エラーパターンのチェック
            error_patterns = [
                'error',
                'エラー',
                '失敗',
                'invalid',
                '不正',
                'ファイルサイズ',
                '形式が不正'
            ]
            
            for pattern in error_patterns:
                if pattern.lower() in response_text and 'error' not in base_url:
                    logger.error(f"❌ エラーパターン検出: {pattern}")
                    break
            
            # レスポンスを保存（デバッグ用）
            with open("response_debug.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            logger.info("レスポンスをresponse_debug.htmlに保存")
            
            # レスポンスの最初の500文字を表示
            logger.info(f"レスポンス内容（最初の500文字）:\n{response.text[:500]}")
            
            return False
            
    except Exception as e:
        logger.error(f"エラー発生: {e}")
        return False

if __name__ == "__main__":
    print("=== HTTP直接アップロードテスト ===")
    print("=" * 60)
    success = test_http_upload()
    print("=" * 60)
    print(f"結果: {'✅ アップロード成功' if success else '❌ アップロード失敗'}")
    
    if not success:
        print("\n💡 次のステップ:")
        print("1. response_debug.htmlを確認してレスポンス内容を分析")
        print("2. 成功ページが同じURLで表示される仕様に対応が必要")
        print("3. Selenium WebDriverでのブラウザ自動化が推奨される")