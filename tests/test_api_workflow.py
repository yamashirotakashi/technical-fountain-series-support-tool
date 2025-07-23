#!/usr/bin/env python3
"""
ReVIEW変換API 基本フロー動作確認テスト

実際のReVIEWファイルを使用して、アップロード→ステータス確認→ダウンロードの
完全なワークフローをテストする。
"""

import sys
import os
import requests
from requests.auth import HTTPBasicAuth
import json
import time
from pathlib import Path
from datetime import datetime
import zipfile
import tempfile
import re

# API設定
API_BASE_URL = "http://sd001.nextpublishing.jp/rapture"
API_USERNAME = "ep_user"
API_PASSWORD = "Nn7eUTX5"

# テストファイル
# 成功確認用（警告なし）
SUCCESS_FILE_PATH = "C:\\Users\\tky99\\DEV\\articles.zip"
# 一部成功確認用（警告あり+ダウンロードURLあり）
PARTIAL_SUCCESS_FILE_PATH = "C:\\Users\\tky99\\DEV\\technical-fountain-series-support-tool\\ReVIEW error 2.zip"
# 失敗確認用（警告メッセージのみ）
FAILURE_FILE_PATH = "C:\\Users\\tky99\\DEV\\technical-fountain-series-support-tool\\run_direct.zip"

# テスト結果を格納
test_results = {
    "timestamp": datetime.now().isoformat(),
    "api_base_url": API_BASE_URL,
    "workflow_steps": []
}


def log_step(step_name, success, message, details=None):
    """ワークフローステップをログに記録"""
    step_result = {
        "step_name": step_name,
        "timestamp": datetime.now().isoformat(),
        "success": success,
        "message": message,
        "details": details or {}
    }
    test_results["workflow_steps"].append(step_result)
    
    status = "✅" if success else "❌"
    print(f"\n{status} {step_name}")
    print(f"   時刻: {datetime.now().strftime('%H:%M:%S')}")
    print(f"   結果: {message}")
    if details:
        for key, value in details.items():
            if key == "output" and value and isinstance(value, str) and len(value) > 100:
                # 長い出力メッセージは改行して表示
                print(f"   {key}:")
                # 各行にインデントを付けて表示
                for line in value.split('\n'):
                    if line.strip():
                        print(f"      {line}")
            elif key == "errors" and isinstance(value, list) and value:
                # エラーリストを見やすく表示
                print(f"   {key}:")
                for i, error in enumerate(value, 1):
                    print(f"      [{i}] {error}")
            elif isinstance(value, dict) or isinstance(value, list):
                print(f"   {key}: {json.dumps(value, indent=6, ensure_ascii=False)}")
            else:
                print(f"   {key}: {value}")


def test_file_upload():
    """ステップ1: ファイルアップロード"""
    print("\n" + "="*60)
    print("ステップ1: ファイルアップロード")
    print("="*60)
    
    # ファイルの存在確認
    if not os.path.exists(TEST_FILE_PATH):
        log_step("ファイル存在確認", False, f"テストファイルが見つかりません: {TEST_FILE_PATH}")
        return None
    
    file_size = os.path.getsize(TEST_FILE_PATH) / 1024 / 1024  # MB
    log_step("ファイル確認", True, f"ファイルサイズ: {file_size:.2f} MB")
    
    # アップロード実行
    try:
        auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
        
        with open(TEST_FILE_PATH, 'rb') as f:
            files = {'file': ('ReVIEW.zip', f, 'application/zip')}
            
            print(f"\nアップロード開始...")
            start_time = time.time()
            
            response = requests.post(
                f"{API_BASE_URL}/api/upload",
                files=files,
                auth=auth,
                timeout=300  # 5分タイムアウト
            )
            
            upload_time = time.time() - start_time
            
        if response.status_code == 200:
            try:
                data = response.json()
                if 'jobid' in data:
                    log_step("アップロード", True, 
                            f"アップロード成功 (所要時間: {upload_time:.1f}秒)",
                            {
                                "jobid": data['jobid'],
                                "upload_time_sec": upload_time,
                                "file_size_mb": file_size
                            })
                    return data['jobid']
                else:
                    log_step("アップロード", False, 
                            "レスポンスにjobidが含まれていません",
                            {"response": data})
            except json.JSONDecodeError:
                log_step("アップロード", False,
                        "JSONレスポンスの解析に失敗",
                        {"response_text": response.text[:500]})
        else:
            log_step("アップロード", False,
                    f"アップロード失敗 (HTTP {response.status_code})",
                    {
                        "status_code": response.status_code,
                        "response": response.text[:500]
                    })
    
    except requests.exceptions.Timeout:
        log_step("アップロード", False, "タイムアウト (5分経過)")
    except Exception as e:
        log_step("アップロード", False, f"エラー発生: {str(e)}")
    
    return None


def strip_ansi_escape_sequences(text):
    """ANSIエスケープシーケンスを除去"""
    # ANSIエスケープシーケンスのパターン
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def test_status_check(jobid):
    """ステップ2: ステータス確認（ポーリング）"""
    print("\n" + "="*60)
    print("ステップ2: ステータス確認")
    print("="*60)
    
    auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
    max_attempts = 60  # 最大10分間（10秒間隔で60回）
    poll_interval = 10  # 10秒間隔
    
    print(f"\n変換処理の完了を待機中... (最大{max_attempts * poll_interval // 60}分)")
    
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
                
                if status == 'completed':
                    print()  # 改行
                    result = data.get('result', 'unknown')
                    output = data.get('output', '')  # 警告メッセージ
                    
                    # ANSIエスケープシーケンスを除去
                    if output and isinstance(output, str):
                        output = strip_ansi_escape_sequences(output)
                    elif isinstance(output, list):
                        # outputがリストの場合は結合
                        output = '\n'.join(str(item) for item in output)
                    
                    if result == 'success':
                        # outputキーが空または存在しない = 警告なし
                        if output:
                            # 警告ありの成功（一部成功として扱う）
                            log_step("ステータス確認", True,
                                    "変換処理が成功しました（警告あり）",
                                    {
                                        "status": status,
                                        "result": result,
                                        "output": output,
                                        "download_url": data.get('download_url'),
                                        "attempts": attempt + 1,
                                        "total_wait_time_sec": (attempt + 1) * poll_interval
                                    })
                        else:
                            # 完全な成功（警告なし）
                            log_step("ステータス確認", True,
                                    "変換処理が正常に完了しました（警告なし）",
                                    {
                                        "status": status,
                                        "result": result,
                                        "output": "警告メッセージなし",
                                        "download_url": data.get('download_url'),
                                        "attempts": attempt + 1,
                                        "total_wait_time_sec": (attempt + 1) * poll_interval
                                    })
                        return data
                    
                    elif result == 'partial_success':
                        # outputキーに警告メッセージあり + ダウンロードURLあり
                        log_step("ステータス確認", True,
                                "変換処理が一部成功で完了しました（警告あり）",
                                {
                                    "status": status,
                                    "result": result,
                                    "output": output,  # ReVIEWの警告メッセージ
                                    "warnings": data.get('warnings', []),
                                    "errors": data.get('errors', []),
                                    "download_url": data.get('download_url'),
                                    "attempts": attempt + 1,
                                    "total_wait_time_sec": (attempt + 1) * poll_interval
                                })
                        return data
                    
                    else:  # failure
                        # errorsキーに失敗理由が出力される
                        errors = data.get('errors', [])
                        log_step("ステータス確認", False,
                                "変換処理が失敗しました",
                                {
                                    "status": status,
                                    "result": result,
                                    "output": output if output else "（出力なし）",
                                    "errors": errors if errors else ["エラー情報なし"],
                                    "attempts": attempt + 1,
                                    "total_wait_time_sec": (attempt + 1) * poll_interval
                                })
                        return None
                
                elif status == 'failed':
                    print()  # 改行
                    errors = data.get('errors', [])
                    log_step("ステータス確認", False,
                            "変換処理が失敗しました",
                            {
                                "status": status,
                                "errors": errors if errors else ["エラー情報なし"]
                            })
                    return None
                
                # まだ処理中の場合は待機
                time.sleep(poll_interval)
                
            else:
                log_step("ステータス確認", False,
                        f"ステータス取得失敗 (HTTP {response.status_code})",
                        {"attempt": attempt + 1})
                return None
                
        except Exception as e:
            log_step("ステータス確認", False,
                    f"エラー発生: {str(e)}",
                    {"attempt": attempt + 1})
            return None
    
    print()  # 改行
    log_step("ステータス確認", False,
            f"タイムアウト: {max_attempts * poll_interval // 60}分経過しても完了しませんでした")
    return None


def test_file_download(download_url, jobid):
    """ステップ3: ファイルダウンロード"""
    print("\n" + "="*60)
    print("ステップ3: ファイルダウンロード")
    print("="*60)
    
    auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
    
    # ダウンロード先を準備
    download_dir = Path(__file__).parent.parent / "test_downloads"
    download_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    download_path = download_dir / f"converted_{jobid}_{timestamp}.zip"
    
    try:
        print(f"\nダウンロード開始...")
        start_time = time.time()
        
        response = requests.get(
            download_url,
            auth=auth,
            stream=True,
            timeout=300
        )
        
        if response.status_code == 200:
            # ファイルサイズを取得
            total_size = int(response.headers.get('content-length', 0))
            
            # ダウンロード実行
            downloaded = 0
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # 進捗表示
                        if total_size > 0:
                            progress = downloaded / total_size * 100
                            print(f"\r進捗: {progress:.1f}% ({downloaded:,} / {total_size:,} bytes)", 
                                  end='', flush=True)
            
            download_time = time.time() - start_time
            file_size_mb = downloaded / 1024 / 1024
            
            print()  # 改行
            
            # ZIPファイルの内容を確認
            file_list = []
            try:
                with zipfile.ZipFile(download_path, 'r') as zf:
                    file_list = zf.namelist()
                    docx_files = [f for f in file_list if f.endswith('.docx')]
                    
                    log_step("ダウンロード", True,
                            f"ダウンロード成功 (所要時間: {download_time:.1f}秒)",
                            {
                                "download_path": str(download_path),
                                "file_size_mb": f"{file_size_mb:.2f}",
                                "download_time_sec": download_time,
                                "total_files": len(file_list),
                                "docx_files": len(docx_files),
                                "file_list": file_list[:10]  # 最初の10ファイルのみ
                            })
                    return download_path
                    
            except zipfile.BadZipFile:
                log_step("ダウンロード", False,
                        "ダウンロードしたファイルが有効なZIPファイルではありません")
                return None
        
        else:
            log_step("ダウンロード", False,
                    f"ダウンロード失敗 (HTTP {response.status_code})")
            return None
            
    except requests.exceptions.Timeout:
        log_step("ダウンロード", False, "タイムアウト (5分経過)")
    except Exception as e:
        log_step("ダウンロード", False, f"エラー発生: {str(e)}")
    
    return None


def save_workflow_report():
    """ワークフロー結果をレポートファイルに保存"""
    report_dir = Path(__file__).parent.parent / "test_reports"
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"api_workflow_test_{timestamp}.json"
    
    # 成功/失敗の集計
    total_steps = len(test_results["workflow_steps"])
    successful_steps = sum(1 for step in test_results["workflow_steps"] if step["success"])
    
    test_results["summary"] = {
        "total_steps": total_steps,
        "successful_steps": successful_steps,
        "failed_steps": total_steps - successful_steps,
        "success_rate": f"{(successful_steps/total_steps*100):.1f}%" if total_steps > 0 else "0%"
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nワークフローテストレポートを保存しました: {report_file}")
    
    # サマリーを表示
    print("\n" + "="*60)
    print("テストサマリー")
    print("="*60)
    print(f"実行ステップ数: {total_steps}")
    print(f"成功: {successful_steps}")
    print(f"失敗: {total_steps - successful_steps}")
    print(f"成功率: {test_results['summary']['success_rate']}")


def main():
    """メイン処理"""
    # コマンドライン引数でテストケースを選択
    test_case = "success"  # デフォルト
    if len(sys.argv) > 1:
        test_case = sys.argv[1].lower()
    
    # テストファイルを選択
    if test_case == "success":
        test_file = SUCCESS_FILE_PATH
        test_name = "成功ケース（警告なし）"
    elif test_case == "partial":
        test_file = PARTIAL_SUCCESS_FILE_PATH
        test_name = "一部成功ケース（警告あり）"
    elif test_case == "failure":
        test_file = FAILURE_FILE_PATH
        test_name = "失敗ケース"
    else:
        print("使用方法: python test_api_workflow.py [success|partial|failure]")
        return
    
    # Windowsパスを変換
    if sys.platform != "win32":
        test_file = test_file.replace("C:\\", "/mnt/c/").replace("\\", "/")
    
    print("ReVIEW変換API 基本フローテスト開始")
    print(f"API URL: {API_BASE_URL}")
    print(f"テストケース: {test_name}")
    print(f"テストファイル: {test_file}")
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # テスト結果にテストケース情報を追加
    test_results["test_case"] = test_case
    test_results["test_name"] = test_name
    test_results["test_file"] = test_file
    
    # ステップ1: アップロード（テストファイルを差し替え）
    global TEST_FILE_PATH
    TEST_FILE_PATH = test_file
    
    jobid = test_file_upload()
    if not jobid:
        print("\nアップロードに失敗したため、テストを中止します。")
        save_workflow_report()
        return
    
    # ステップ2: ステータス確認
    status_data = test_status_check(jobid)
    if not status_data:
        print("\nステータス確認に失敗したため、テストを中止します。")
        save_workflow_report()
        return
    
    # ステップ3: ダウンロード
    download_url = status_data.get('download_url')
    if download_url:
        download_path = test_file_download(download_url, jobid)
        if download_path:
            print(f"\n✅ 完全なワークフローが成功しました！")
            print(f"   変換済みファイル: {download_path}")
    else:
        log_step("ダウンロードURL取得", False, "ダウンロードURLが提供されませんでした")
    
    # レポート保存
    save_workflow_report()


if __name__ == "__main__":
    main()