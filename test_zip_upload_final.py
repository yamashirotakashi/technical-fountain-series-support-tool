#!/usr/bin/env python3
"""
ZIPファイルアップロード最終テスト - 成功判定込み
"""
import requests
from pathlib import Path
import logging
from requests.auth import HTTPBasicAuth
import base64

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_final_upload():
    """最終的なアップロードテスト"""
    
    # 設定値を正しく読み込む
    from utils.config import get_config
    config = get_config()
    web_config = config.get_web_config()
    
    username = web_config.get('username', 'ep_user')
    password = web_config.get('password', '')
    
    if not password:
        # 環境変数から取得
        import os
        password = os.environ.get('NEXTPUBLISHING_PASSWORD', '')
    
    base_url = "http://trial.nextpublishing.jp/rapture/"
    test_file = Path("test_upload.zip")
    
    logger.info(f"認証情報: username={username}, password={'*' * len(password) if password else 'NONE'}")
    
    if not test_file.exists():
        logger.error(f"テストファイルが見つかりません: {test_file}")
        return False
    
    logger.info(f"テストファイル: {test_file.name} ({test_file.stat().st_size} bytes)")
    
    # セッション作成
    session = requests.Session()
    
    # Basic認証ヘッダーを手動で設定
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    # ヘッダー設定
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }
    
    try:
        # 1. まずGETリクエストでフォームページにアクセス
        logger.info("Step 1: フォームページにGETリクエスト...")
        response = session.get(base_url, headers=headers)
        logger.info(f"GET応答: HTTP {response.status_code}")
        
        if response.status_code == 401:
            logger.error("認証失敗 (401)")
            return False
        
        if response.status_code == 200:
            logger.info("認証成功！フォームページを取得")
            
            # 2. POSTリクエストでファイルアップロード
            logger.info("Step 2: ファイルをPOSTリクエストで送信...")
            
            # multipart/form-dataでファイル送信
            with open(test_file, 'rb') as f:
                files = {
                    'userfile': (test_file.name, f, 'application/zip')
                }
                
                data = {
                    'mail': 'yamashiro.takashi@gmail.com',
                    'mailconf': 'yamashiro.takashi@gmail.com'
                }
                
                # POSTヘッダー（Authorizationは維持）
                post_headers = {
                    'Authorization': f'Basic {encoded_credentials}',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
                    'Referer': base_url,
                    'Origin': 'http://trial.nextpublishing.jp'
                }
                
                response = session.post(
                    base_url,
                    files=files,
                    data=data,
                    headers=post_headers,
                    allow_redirects=False  # リダイレクトを手動で処理
                )
                
                logger.info(f"POST応答: HTTP {response.status_code}")
                logger.info(f"Location: {response.headers.get('Location', 'なし')}")
                
                # 3. リダイレクトまたは同じURLでの成功確認
                if response.status_code in [301, 302, 303, 307]:
                    # リダイレクトの場合
                    redirect_url = response.headers.get('Location')
                    if redirect_url:
                        logger.info(f"リダイレクト先: {redirect_url}")
                        response = session.get(redirect_url, headers=headers)
                        logger.info(f"リダイレクト先応答: HTTP {response.status_code}")
                
                # 成功パターンのチェック（正確な文字化けパターン）
                success_pattern = "ã¢ããã­ã¼ããå®äºãã¾ããã"
                
                if success_pattern in response.text:
                    logger.info("✅ アップロード成功！")
                    logger.info("   成功メッセージ: アップロードが完了しました")
                    
                    # レスポンスを保存
                    with open("success_result_final.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    logger.info("   成功レスポンスをsuccess_result_final.htmlに保存")
                    
                    return True
                else:
                    logger.warning("成功パターンが見つかりません")
                    
                    # レスポンスを保存
                    with open("upload_result_final.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    logger.info("レスポンスをupload_result_final.htmlに保存")
                    
                    # レスポンスの最初の500文字を表示
                    logger.debug(f"レスポンス内容（最初の500文字）:\n{response.text[:500]}")
                    
                    return False
        
        logger.error(f"予期しないステータスコード: {response.status_code}")
        return False
        
    except Exception as e:
        logger.error(f"エラー発生: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("=== ZIPファイルアップロード最終テスト ===")
    print("==" * 30)
    
    success = test_final_upload()
    
    print("==" * 30)
    if success:
        print("✅ アップロード成功！")
        print("")
        print("【検証結果】")
        print("1. ZIPファイルのアップロード: 成功")
        print("2. Basic認証処理: 成功")
        print("3. 成功メッセージ検出: 成功")
        print("4. 同じURLでの成功判定: 成功")
        print("")
        print("【メインアプリへのフィードバック】")
        print("- HTTP RequestsアプローチでもZIPファイルなら成功可能")
        print("- Basic認証はBase64エンコードヘッダーで対応可能")
        print("- 成功判定は文字化けパターンも考慮する必要あり")
        print("- userfileフィールドにZIPファイルを送信")
        print("- mail/mailconfフィールドも必須")
    else:
        print("❌ アップロード失敗")
        print("詳細はupload_result_final.htmlまたはログを確認してください")