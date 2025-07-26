#!/usr/bin/env python3
"""
04_powershell_sample_advanced.docx エラー検知テスト
ダウンロードURLからPDFエラーを検出するロジックの簡易テスト
"""

import requests
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_pdf_downloadable(url: str) -> tuple[bool, str]:
    """
    PDFダウンロード可否をチェック（NextPublishingServiceから抜粋）
    
    Args:
        url: ダウンロードURL
        
    Returns:
        (ダウンロード可能, メッセージ)
    """
    print(f"🔍 PDFチェック開始: {url}")
    
    try:
        # HEADリクエストでContent-Typeを確認
        head_response = requests.head(url, timeout=10)
        print(f"📊 HEADレスポンス: {head_response.status_code}")
        print(f"📊 Content-Type: {head_response.headers.get('Content-Type', 'Unknown')}")
        
        # 実際のコンテンツを取得
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            # レスポンスサイズを確認
            content_size = len(response.content)
            print(f"📊 コンテンツサイズ: {content_size} bytes")
            
            # 小さすぎるレスポンスはエラーページの可能性
            if content_size < 1000:
                print(f"⚠️  コンテンツが小さすぎます: {content_size} bytes")
                # 内容を確認
                content_text = response.content.decode('utf-8', errors='ignore')
                print(f"📄 コンテンツ内容（先頭500文字）:\n{content_text[:500]}")
                
                if 'エラー' in content_text or 'ファイルの作成に失敗' in content_text:
                    return False, "PDF生成エラー"
                else:
                    return False, "PDF生成エラー"
            
            # PDFファイルかどうかを確認
            content_type = response.headers.get('Content-Type', '')
            content_start = response.content[:20] if response.content else b''
            
            print(f"📊 Content-Type: {content_type}")
            print(f"📊 Content開始: {content_start}")
            
            # PDFファイルのマジックナンバーをチェック
            if content_start.startswith(b'%PDF'):
                print("✅ PDFマジックナンバー確認")
                return True, "PDFダウンロード可能"
            elif 'application/pdf' in content_type:
                print("✅ Content-TypeがPDF")
                return True, "PDFダウンロード可能"
            elif 'application/x-zip' in content_type or 'application/zip' in content_type:
                if content_start.startswith(b'PK'):  # ZIPファイルのマジックナンバー
                    print("✅ ZIPファイル（正常なPDFを含む可能性）")
                    return True, "PDFダウンロード可能（ZIP形式）"
                else:
                    print("❌ 不正なZIPファイル")
                    return False, "不正なZIPファイル"
            else:
                # HTMLレスポンスの場合
                if b'<html' in content_start.lower() or b'<!doctype' in content_start.lower():
                    print("❌ HTMLレスポンス検出")
                    # HTMLの内容を確認
                    content_text = response.content[:1000].decode('utf-8', errors='ignore').lower()
                    print(f"📄 HTML内容（先頭1000文字）:\n{content_text}")
                    
                    if 'ファイルの作成に失敗' in content_text or 'エラー' in content_text:
                        return False, "PDF生成エラー"
                    else:
                        return False, "HTMLレスポンス（PDF生成失敗）"
                else:
                    print(f"❌ 不明なコンテンツ")
                    return False, f"不明なコンテンツ（Content-Type: {content_type}）"
        else:
            print(f"❌ HTTPエラー: {response.status_code}")
            return False, f"HTTPステータス {response.status_code}"
            
    except requests.RequestException as e:
        print(f"❌ ネットワークエラー: {e}")
        return False, f"ネットワークエラー: {str(e)}"

def main():
    """メイン関数"""
    print("🧪 04_powershell_sample_advanced.docx エラー検知テスト")
    print("=" * 60)
    
    # ログから取得したURL（実際のエラーファイル）- 最新
    test_url = "http://trial.nextpublishing.jp/upload_46tate/do_download?n=%2BdBX6s%2BfNwenOwInf8Uixo7KFAq4daIpOMd3QZdOeHwvy3pOtspIKLD9Lpxy21b0sbNG%2FT5up9pmxBGd%2FZUptg%3D%3D"
    
    print(f"📂 ファイル名: 04_powershell_sample_advanced.docx")
    print(f"🔗 ダウンロードURL: {test_url[:80]}...")
    print()
    
    # エラー検知テスト
    is_downloadable, message = check_pdf_downloadable(test_url)
    
    print()
    print("=" * 60)
    print("🎯 テスト結果")
    print(f"✅ ダウンロード可能: {is_downloadable}")
    print(f"📝 メッセージ: {message}")
    
    if not is_downloadable:
        print("🎉 エラー検知成功！")
    else:
        print("❌ エラー検知失敗（エラーファイルなのに正常判定）")
    
    print("=" * 60)

if __name__ == "__main__":
    main()