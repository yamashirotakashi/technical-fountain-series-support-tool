#!/usr/bin/env python3
"""
ReVIEW変換API疎通テストスクリプト

新しいREST APIサーバー（sd001.nextpublishing.jp）の基本的な接続性をテストする。
認証情報の確認も含む。
"""

import sys
import os
import requests
from requests.auth import HTTPBasicAuth
import json
from pathlib import Path
from datetime import datetime

# API設定
import os
API_BASE_URL = os.getenv("NEXTPUB_API_BASE_URL", "http://sd001.nextpublishing.jp/rapture")
API_USERNAME = os.getenv("NEXTPUB_USERNAME", "ep_user")
API_PASSWORD = os.getenv("NEXTPUB_PASSWORD", "Nn7eUTX5")

# テスト結果を格納
test_results = {
    "timestamp": datetime.now().isoformat(),
    "api_base_url": API_BASE_URL,
    "tests": []
}


def log_test(test_name, success, message, details=None):
    """テスト結果をログに記録"""
    result = {
        "test_name": test_name,
        "success": success,
        "message": message,
        "details": details or {}
    }
    test_results["tests"].append(result)
    
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"\n{status} - {test_name}")
    print(f"  Message: {message}")
    if details:
        print(f"  Details: {json.dumps(details, indent=2, ensure_ascii=False)}")


def test_basic_auth():
    """Basic認証のテスト"""
    print("\n=== Basic認証テスト ===")
    
    # 認証なしでアクセス
    try:
        response = requests.get(f"{API_BASE_URL}/api/status/test", timeout=10)
        if response.status_code == 401:
            log_test("認証なしアクセス", True, "期待通り401 Unauthorizedを返しました")
        else:
            log_test("認証なしアクセス", False, 
                    f"予期しないステータスコード: {response.status_code}",
                    {"status_code": response.status_code, "response": response.text[:200]})
    except Exception as e:
        log_test("認証なしアクセス", False, f"エラー発生: {str(e)}")
    
    # 認証ありでアクセス
    try:
        auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
        response = requests.get(f"{API_BASE_URL}/api/status/test", auth=auth, timeout=10)
        
        # 404は認証は通ったが、リソースが見つからない（正常）
        if response.status_code in [200, 404]:
            log_test("認証ありアクセス", True, 
                    f"認証成功（ステータス: {response.status_code}）",
                    {"status_code": response.status_code})
        elif response.status_code == 401:
            log_test("認証ありアクセス", False, "認証失敗（401 Unauthorized）")
        else:
            log_test("認証ありアクセス", False,
                    f"予期しないステータスコード: {response.status_code}",
                    {"status_code": response.status_code, "response": response.text[:200]})
    except Exception as e:
        log_test("認証ありアクセス", False, f"エラー発生: {str(e)}")


def test_api_endpoints():
    """APIエンドポイントの存在確認"""
    print("\n=== APIエンドポイント確認 ===")
    
    auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
    
    # アップロードエンドポイント（POSTなのでOPTIONSで確認）
    try:
        response = requests.options(f"{API_BASE_URL}/api/upload", auth=auth, timeout=10)
        if response.status_code in [200, 204, 405]:  # 405 Method Not Allowedも許容
            log_test("アップロードエンドポイント", True, 
                    f"エンドポイント存在確認（ステータス: {response.status_code}）")
        else:
            log_test("アップロードエンドポイント", False,
                    f"予期しないステータスコード: {response.status_code}")
    except Exception as e:
        log_test("アップロードエンドポイント", False, f"エラー発生: {str(e)}")
    
    # ステータスエンドポイント（存在しないjobidでテスト）
    try:
        response = requests.get(f"{API_BASE_URL}/api/status/test_jobid", auth=auth, timeout=10)
        if response.status_code == 404:
            log_test("ステータスエンドポイント", True, 
                    "エンドポイント存在確認（404: jobid not found）")
        elif response.status_code == 200:
            log_test("ステータスエンドポイント", True,
                    "エンドポイント存在確認（200: 成功）",
                    {"response": response.json() if response.content else None})
        else:
            log_test("ステータスエンドポイント", False,
                    f"予期しないステータスコード: {response.status_code}",
                    {"response": response.text[:200]})
    except Exception as e:
        log_test("ステータスエンドポイント", False, f"エラー発生: {str(e)}")
    
    # ダウンロードエンドポイント（存在しないjobidでテスト）
    try:
        response = requests.head(f"{API_BASE_URL}/api/download/test_jobid", auth=auth, timeout=10)
        if response.status_code in [404, 200]:
            log_test("ダウンロードエンドポイント", True,
                    f"エンドポイント存在確認（ステータス: {response.status_code}）")
        else:
            log_test("ダウンロードエンドポイント", False,
                    f"予期しないステータスコード: {response.status_code}")
    except Exception as e:
        log_test("ダウンロードエンドポイント", False, f"エラー発生: {str(e)}")


def test_minimal_upload():
    """最小限のアップロードテスト（小さなテストZIPファイル）"""
    print("\n=== 最小アップロードテスト ===")
    
    # テスト用の小さなZIPファイルを作成
    import zipfile
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.zip', delete=False) as tmp:
        test_zip_path = tmp.name
    
    try:
        # 簡単なテストZIPを作成
        with zipfile.ZipFile(test_zip_path, 'w') as zf:
            zf.writestr("test.txt", "This is a test file for API connectivity check.")
        
        # アップロードテスト
        auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
        with open(test_zip_path, 'rb') as f:
            files = {'file': ('test_api.zip', f, 'application/zip')}
            response = requests.post(
                f"{API_BASE_URL}/api/upload",
                files=files,
                auth=auth,
                timeout=30
            )
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'jobid' in data:
                    log_test("アップロード機能", True,
                            f"アップロード成功 - jobid: {data['jobid']}",
                            {"jobid": data['jobid'], "response": data})
                    return data['jobid']  # 後続のテストで使用
                else:
                    log_test("アップロード機能", False,
                            "レスポンスにjobidが含まれていません",
                            {"response": data})
            except json.JSONDecodeError:
                log_test("アップロード機能", False,
                        "JSONレスポンスの解析に失敗",
                        {"response_text": response.text[:200]})
        else:
            log_test("アップロード機能", False,
                    f"アップロード失敗（ステータス: {response.status_code}）",
                    {"status_code": response.status_code, "response": response.text[:200]})
    
    except Exception as e:
        log_test("アップロード機能", False, f"エラー発生: {str(e)}")
        return None
    
    finally:
        # テンポラリファイルを削除
        if os.path.exists(test_zip_path):
            os.unlink(test_zip_path)


def save_test_report():
    """テスト結果をレポートファイルに保存"""
    report_dir = Path(__file__).parent.parent / "test_reports"
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"api_connectivity_test_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nテストレポートを保存しました: {report_file}")
    
    # サマリーを表示
    total_tests = len(test_results["tests"])
    passed_tests = sum(1 for t in test_results["tests"] if t["success"])
    failed_tests = total_tests - passed_tests
    
    print("\n=== テストサマリー ===")
    print(f"合計: {total_tests}件")
    print(f"成功: {passed_tests}件")
    print(f"失敗: {failed_tests}件")
    print(f"成功率: {(passed_tests/total_tests*100):.1f}%")


def main():
    """メイン処理"""
    print("ReVIEW変換API疎通テスト開始")
    print(f"API URL: {API_BASE_URL}")
    print(f"認証ユーザー: {API_USERNAME}")
    print("-" * 50)
    
    # 各テストを実行
    test_basic_auth()
    test_api_endpoints()
    jobid = test_minimal_upload()
    
    # アップロードが成功した場合、ステータス確認もテスト
    if jobid:
        print(f"\n=== ステータス確認テスト (jobid: {jobid}) ===")
        auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
        try:
            response = requests.get(f"{API_BASE_URL}/api/status/{jobid}", auth=auth, timeout=10)
            if response.status_code == 200:
                data = response.json()
                log_test("ステータス確認機能", True,
                        f"ステータス取得成功 - status: {data.get('status', 'unknown')}",
                        {"response": data})
            else:
                log_test("ステータス確認機能", False,
                        f"ステータス確認失敗（ステータス: {response.status_code}）")
        except Exception as e:
            log_test("ステータス確認機能", False, f"エラー発生: {str(e)}")
    
    # レポート保存
    save_test_report()


if __name__ == "__main__":
    main()