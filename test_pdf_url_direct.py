"""PDF URL判定テストスクリプト（直接実行版）"""
import requests
from requests.auth import HTTPBasicAuth
from typing import Tuple

def test_pdf_url(url: str, use_auth: bool = True) -> Tuple[bool, str]:
    """
    PDF URLにアクセスして、正常にPDFがダウンロードできるかテスト
    
    Args:
        url: テストするPDF URL
        use_auth: Basic認証を使用するかどうか
        
    Returns:
        (成功フラグ, 詳細メッセージ)
    """
    print(f"\nテストURL: {url[:100]}...")
    print(f"認証使用: {use_auth}")
    
    try:
        # ブラウザのようなヘッダーを設定
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        }
        
        # Basic認証の設定
        auth = HTTPBasicAuth('ep_user', 'Nn7eUTX5') if use_auth else None
        
        # HEADリクエストで確認
        print("1. HEADリクエストで確認...")
        head_response = requests.head(url, headers=headers, auth=auth, allow_redirects=True, timeout=10)
        print(f"   - ステータスコード: {head_response.status_code}")
        print(f"   - Content-Type: {head_response.headers.get('Content-Type', 'なし')}")
        print(f"   - Content-Length: {head_response.headers.get('Content-Length', 'なし')}")
        
        # GETリクエストで最初の部分を取得
        print("\n2. GETリクエストで内容確認...")
        response = requests.get(url, headers=headers, auth=auth, allow_redirects=True, timeout=30, stream=True)
        print(f"   - ステータスコード: {response.status_code}")
        print(f"   - Content-Type: {response.headers.get('Content-Type', 'なし')}")
        
        # 最初の1KBを読み取り
        content_start = b''
        for chunk in response.iter_content(chunk_size=1024):
            content_start = chunk
            break
        
        # ファイル形式を判定
        if content_start.startswith(b'%PDF'):
            print("   ✓ PDFファイルのマジックナンバーを検出")
            return True, "正常: PDFファイルがダウンロード可能"
        elif content_start.startswith(b'PK'):
            print("   ! ZIPファイルのマジックナンバーを検出")
            return False, "エラー: ZIPファイルが返された（PDF変換失敗の可能性）"
        elif b'<html' in content_start.lower() or b'<!doctype' in content_start.lower():
            print("   ! HTMLを検出")
            # HTMLの内容を確認
            content_text = content_start.decode('utf-8', errors='ignore')
            print(f"   HTML内容（最初の200文字）: {content_text[:200]}")
            
            if 'ファイルの作成に失敗' in content_text or 'エラー' in content_text:
                return False, "エラー: PDF生成エラーページが返された"
            else:
                return False, "エラー: HTMLページが返された（詳細不明）"
        else:
            print(f"   ? 不明な形式: {content_start[:50]}")
            return False, "エラー: 不明な形式のレスポンス"
            
    except requests.exceptions.RequestException as e:
        print(f"   × リクエストエラー: {e}")
        return False, f"エラー: リクエスト失敗 - {str(e)}"
    except Exception as e:
        print(f"   × 予期しないエラー: {e}")
        return False, f"エラー: 予期しないエラー - {str(e)}"


def main():
    """メイン処理"""
    print("=== PDF URL判定テスト ===\n")
    
    # テストケース
    test_cases = [
        {
            "name": "03_powershell_sample_basic.docx（正常）",
            "url": "http://trial.nextpublishing.jp/upload_46tate/do_download_pdf?n=DWszyxVNUi%2BRBto4Xa8%2FyjA%2BjYdXFlsTir1jImPejtSu%2BIZRwXOD4y5BeT33OTTPZV%2BigZJPiYsnQ603POfqYw%3D%3D"
        },
        {
            "name": "04_powershell_sample_advanced.docx（エラー）",
            "url": "http://trial.nextpublishing.jp/upload_46tate/do_download_pdf?n=QEAhIi0OjyxbOZL1RKha60l4xJF7jv02n42nfHrq6bfYLk%2FN1MhhUp1IKraR3uS2DgTm%2FMQGcEQiAvVpnitNYw%3D%3D"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"テスト: {test_case['name']}")
        print(f"{'='*60}")
        
        # まず認証なしでテスト
        print("\n--- 認証なしでテスト ---")
        success_no_auth, message_no_auth = test_pdf_url(test_case['url'], use_auth=False)
        
        # 次に認証ありでテスト
        print("\n--- 認証ありでテスト ---")
        success, message = test_pdf_url(test_case['url'], use_auth=True)
        
        print(f"\n=== 結果 ===")
        print(f"成功: {success}")
        print(f"詳細: {message}")
        
        # 期待される結果との比較
        if "正常" in test_case['name'] and success:
            print("✅ 期待通り: 正常ファイルが正常と判定された")
        elif "エラー" in test_case['name'] and not success:
            print("✅ 期待通り: エラーファイルがエラーと判定された")
        else:
            print("❌ 期待と異なる結果")


if __name__ == "__main__":
    main()