#!/usr/bin/env python3
"""
ReVIEW変換API エラーハンドリングテスト

エラーが発生するファイルを使用して、APIのエラーハンドリングをテストする。
"""

import sys
import os
import requests
from requests.auth import HTTPBasicAuth
import json
import time
from pathlib import Path
from datetime import datetime
import tempfile

# API設定
API_BASE_URL = "http://sd001.nextpublishing.jp/rapture"
API_USERNAME = "ep_user"
API_PASSWORD = "Nn7eUTX5"

# エラーテストファイル
ERROR_FILE_PATH = "/mnt/c/Users/tky99/DEV/technical-fountain-series-support-tool/ReVIEW error.zip"
# 一部成功テストファイル
PARTIAL_ERROR_FILE_PATH = "/mnt/c/Users/tky99/DEV/technical-fountain-series-support-tool/ReVIEW error 2.zip"

# テスト結果を格納
test_results = {
    "timestamp": datetime.now().isoformat(),
    "api_base_url": API_BASE_URL,
    "test_file": ERROR_FILE_PATH,
    "error_tests": []
}


def log_test(test_name, success, message, details=None):
    """テスト結果をログに記録"""
    result = {
        "test_name": test_name,
        "timestamp": datetime.now().isoformat(),
        "success": success,
        "message": message,
        "details": details or {}
    }
    test_results["error_tests"].append(result)
    
    status = "✅" if success else "❌"
    print(f"\n{status} {test_name}")
    print(f"   結果: {message}")
    if details:
        for key, value in details.items():
            if isinstance(value, list):
                print(f"   {key}:")
                for item in value:
                    print(f"      - {item}")
            elif isinstance(value, dict):
                print(f"   {key}: {json.dumps(value, indent=6, ensure_ascii=False)}")
            else:
                print(f"   {key}: {value}")


def test_error_file_upload():
    """エラーファイルのアップロードテスト"""
    print("\n" + "="*60)
    print("エラーファイルアップロードテスト")
    print("="*60)
    
    # ファイルの存在確認
    if not os.path.exists(ERROR_FILE_PATH):
        log_test("ファイル存在確認", False, f"エラーテストファイルが見つかりません: {ERROR_FILE_PATH}")
        return None
    
    file_size = os.path.getsize(ERROR_FILE_PATH) / 1024 / 1024  # MB
    print(f"\nエラーファイルサイズ: {file_size:.2f} MB")
    
    # アップロード実行
    try:
        auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
        
        with open(ERROR_FILE_PATH, 'rb') as f:
            files = {'file': ('ReVIEW_error.zip', f, 'application/zip')}
            
            print(f"\nアップロード開始...")
            start_time = time.time()
            
            response = requests.post(
                f"{API_BASE_URL}/api/upload",
                files=files,
                auth=auth,
                timeout=300
            )
            
            upload_time = time.time() - start_time
            
        if response.status_code == 200:
            try:
                data = response.json()
                if 'jobid' in data:
                    log_test("エラーファイルアップロード", True, 
                            f"アップロード成功 (所要時間: {upload_time:.1f}秒)",
                            {"jobid": data['jobid']})
                    return data['jobid']
                else:
                    log_test("エラーファイルアップロード", False, 
                            "レスポンスにjobidが含まれていません",
                            {"response": data})
            except json.JSONDecodeError:
                log_test("エラーファイルアップロード", False,
                        "JSONレスポンスの解析に失敗",
                        {"response_text": response.text[:500]})
        else:
            log_test("エラーファイルアップロード", False,
                    f"アップロード失敗 (HTTP {response.status_code})",
                    {"status_code": response.status_code})
    
    except Exception as e:
        log_test("エラーファイルアップロード", False, f"エラー発生: {str(e)}")
    
    return None


def test_error_status_check(jobid):
    """エラーステータスの確認"""
    print("\n" + "="*60)
    print("エラーステータス確認")
    print("="*60)
    
    auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
    max_attempts = 30  # 最大5分間（10秒間隔で30回）
    poll_interval = 10
    
    print(f"\n変換処理の結果を確認中...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/status/{jobid}",
                auth=auth,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                
                print(f"\r[{attempt + 1}/{max_attempts}] ステータス: {status}", end='', flush=True)
                
                if status in ['completed', 'failed']:
                    print()  # 改行
                    result = data.get('result', 'unknown')
                    
                    # エラーケースの詳細分析
                    if result == 'failure':
                        log_test("エラーハンドリング", True,
                                "期待通りエラーが検出されました",
                                {
                                    "status": status,
                                    "result": result,
                                    "errors": data.get('errors', []),
                                    "attempts": attempt + 1
                                })
                        return data
                    
                    elif result == 'partial_success':
                        log_test("部分的成功ハンドリング", True,
                                "部分的成功として処理されました",
                                {
                                    "status": status,
                                    "result": result,
                                    "warnings": data.get('warnings', []),
                                    "errors": data.get('errors', []),
                                    "download_url": data.get('download_url')
                                })
                        return data
                    
                    elif result == 'success':
                        log_test("予期しない成功", False,
                                "エラーファイルが成功として処理されました",
                                {
                                    "status": status,
                                    "result": result,
                                    "download_url": data.get('download_url')
                                })
                        return data
                
                # まだ処理中の場合は待機
                time.sleep(poll_interval)
                
            else:
                log_test("ステータス確認エラー", False,
                        f"ステータス取得失敗 (HTTP {response.status_code})")
                return None
                
        except Exception as e:
            log_test("ステータス確認エラー", False, f"エラー発生: {str(e)}")
            return None
    
    print()  # 改行
    log_test("タイムアウト", False,
            f"{max_attempts * poll_interval // 60}分経過しても完了しませんでした")
    return None


def test_invalid_jobid():
    """存在しないjobidのテスト"""
    print("\n" + "="*60)
    print("無効なjobidテスト")
    print("="*60)
    
    auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
    invalid_jobid = "invalid_jobid_12345"
    
    # ステータス確認
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/status/{invalid_jobid}",
            auth=auth,
            timeout=10
        )
        
        if response.status_code == 404:
            log_test("無効jobidハンドリング", True,
                    "期待通り404エラーが返されました")
        else:
            log_test("無効jobidハンドリング", False,
                    f"予期しないステータスコード: {response.status_code}",
                    {"response": response.text[:200]})
    except Exception as e:
        log_test("無効jobidハンドリング", False, f"エラー発生: {str(e)}")
    
    # ダウンロード試行
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/download/{invalid_jobid}",
            auth=auth,
            timeout=10
        )
        
        if response.status_code == 404:
            log_test("無効jobidダウンロード", True,
                    "期待通り404エラーが返されました")
        else:
            log_test("無効jobidダウンロード", False,
                    f"予期しないステータスコード: {response.status_code}")
    except Exception as e:
        log_test("無効jobidダウンロード", False, f"エラー発生: {str(e)}")


def test_partial_error_file():
    """一部成功ファイルのテスト"""
    print("\n" + "="*60)
    print("一部成功ファイルテスト")
    print("="*60)
    
    # ファイルの存在確認
    if not os.path.exists(PARTIAL_ERROR_FILE_PATH):
        log_test("ファイル存在確認", False, f"一部成功テストファイルが見つかりません: {PARTIAL_ERROR_FILE_PATH}")
        return None
    
    file_size = os.path.getsize(PARTIAL_ERROR_FILE_PATH) / 1024 / 1024  # MB
    print(f"\n一部成功ファイルサイズ: {file_size:.2f} MB")
    
    # アップロード実行
    try:
        auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
        
        with open(PARTIAL_ERROR_FILE_PATH, 'rb') as f:
            files = {'file': ('ReVIEW_error_2.zip', f, 'application/zip')}
            
            print(f"\nアップロード開始...")
            start_time = time.time()
            
            response = requests.post(
                f"{API_BASE_URL}/api/upload",
                files=files,
                auth=auth,
                timeout=300
            )
            
            upload_time = time.time() - start_time
            
        if response.status_code == 200:
            try:
                data = response.json()
                if 'jobid' in data:
                    print(f"アップロード成功 - jobid: {data['jobid']}")
                    
                    # ステータス確認
                    auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
                    print(f"\n変換処理の結果を確認中...")
                    
                    for attempt in range(30):  # 最大5分間
                        time.sleep(10)
                        
                        status_response = requests.get(
                            f"{API_BASE_URL}/api/status/{data['jobid']}",
                            auth=auth,
                            timeout=30
                        )
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            status = status_data.get('status', 'unknown')
                            
                            print(f"\r[{attempt + 1}/30] ステータス: {status}", end='', flush=True)
                            
                            if status in ['completed', 'failed']:
                                print()  # 改行
                                result = status_data.get('result', 'unknown')
                                
                                if result == 'partial_success':
                                    log_test("一部成功ハンドリング", True,
                                            "期待通り一部成功として処理されました",
                                            {
                                                "status": status,
                                                "result": result,
                                                "warnings": status_data.get('warnings', []),
                                                "errors": status_data.get('errors', []),
                                                "download_url": status_data.get('download_url')
                                            })
                                else:
                                    log_test("一部成功ハンドリング", False,
                                            f"期待と異なる結果: {result}",
                                            {
                                                "status": status,
                                                "result": result,
                                                "warnings": status_data.get('warnings', []),
                                                "errors": status_data.get('errors', [])
                                            })
                                return
                                
            except json.JSONDecodeError:
                log_test("一部成功ファイルアップロード", False,
                        "JSONレスポンスの解析に失敗")
    
    except Exception as e:
        log_test("一部成功ファイルテスト", False, f"エラー発生: {str(e)}")


def test_timeout_handling():
    """タイムアウトハンドリングのテスト"""
    print("\n" + "="*60)
    print("タイムアウトハンドリングテスト")
    print("="*60)
    
    auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
    
    # 極端に短いタイムアウトでテスト
    try:
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.zip', delete=False) as tmp:
            # 1MBのダミーデータ
            tmp.write(b'0' * 1024 * 1024)
            tmp_path = tmp.name
        
        with open(tmp_path, 'rb') as f:
            files = {'file': ('timeout_test.zip', f, 'application/zip')}
            
            # 0.1秒の極端に短いタイムアウト
            response = requests.post(
                f"{API_BASE_URL}/api/upload",
                files=files,
                auth=auth,
                timeout=0.1
            )
        
        log_test("タイムアウト検出", False, 
                "タイムアウトが発生しませんでした")
                
    except requests.exceptions.Timeout:
        log_test("タイムアウト検出", True,
                "期待通りタイムアウトエラーが発生しました")
    except Exception as e:
        log_test("タイムアウト検出", False, 
                f"予期しないエラー: {str(e)}")
    finally:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def save_error_test_report():
    """エラーテスト結果をレポートファイルに保存"""
    report_dir = Path(__file__).parent.parent / "test_reports"
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"api_error_handling_test_{timestamp}.json"
    
    # 成功/失敗の集計
    total_tests = len(test_results["error_tests"])
    successful_tests = sum(1 for test in test_results["error_tests"] if test["success"])
    
    test_results["summary"] = {
        "total_tests": total_tests,
        "successful_tests": successful_tests,
        "failed_tests": total_tests - successful_tests,
        "success_rate": f"{(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nエラーハンドリングテストレポートを保存しました: {report_file}")
    
    # サマリーを表示
    print("\n" + "="*60)
    print("エラーテストサマリー")
    print("="*60)
    print(f"実行テスト数: {total_tests}")
    print(f"成功: {successful_tests}")
    print(f"失敗: {total_tests - successful_tests}")
    print(f"成功率: {test_results['summary']['success_rate']}")


def main():
    """メイン処理"""
    import tempfile
    
    print("ReVIEW変換API エラーハンドリングテスト開始")
    print(f"API URL: {API_BASE_URL}")
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # テスト1: エラーファイルのアップロードと処理
    jobid = test_error_file_upload()
    if jobid:
        test_error_status_check(jobid)
    
    # テスト2: 一部成功ファイルのテスト
    test_partial_error_file()
    
    # テスト3: 無効なjobidのハンドリング
    test_invalid_jobid()
    
    # テスト4: タイムアウトハンドリング
    test_timeout_handling()
    
    # レポート保存
    save_error_test_report()


if __name__ == "__main__":
    main()