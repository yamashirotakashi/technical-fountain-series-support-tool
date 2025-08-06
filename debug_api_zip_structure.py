#!/usr/bin/env python3
"""
N02360 API ZIP構造修正デバッグスクリプト
NextPublishing APIが期待するディレクトリ構造でZIPファイルを作成してテスト
"""
import os
import sys
import tempfile
import zipfile
import shutil
import requests
from pathlib import Path
from requests.auth import HTTPBasicAuth

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_proper_review_zip(source_review_dir: Path, output_zip: Path) -> bool:
    """
    NextPublishing APIが期待する構造でZIPファイルを作成
    
    Args:
        source_review_dir: 元のReVIEWディレクトリ
        output_zip: 出力ZIPファイルのパス
        
    Returns:
        True: 成功, False: 失敗
    """
    try:
        print(f"📁 ReVIEW ZIP作成開始...")
        print(f"  ソース: {source_review_dir}")
        print(f"  出力: {output_zip}")
        
        # ZIPファイル作成
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # ReVIEWディレクトリ内の全ファイルをZIPのルートに追加
            for root, dirs, files in os.walk(source_review_dir):
                for file in files:
                    file_path = Path(root) / file
                    # 相対パスを計算（ReVIEWディレクトリからの相対パス）
                    relative_path = file_path.relative_to(source_review_dir)
                    
                    print(f"  追加: {relative_path}")
                    zipf.write(file_path, str(relative_path))
        
        print(f"✅ ZIP作成完了: {output_zip}")
        print(f"📊 ファイルサイズ: {output_zip.stat().st_size:,} bytes")
        
        # ZIP内容の確認
        with zipfile.ZipFile(output_zip, 'r') as zipf:
            file_list = zipf.namelist()
            print(f"📋 ZIP内容確認: {len(file_list)} ファイル")
            
            # 重要ファイルの存在確認
            required_files = ['catalog.yml', 'config.yml']
            for req_file in required_files:
                if req_file in file_list:
                    print(f"  ✅ {req_file} - 存在")
                else:
                    print(f"  ❌ {req_file} - 不存在")
                    return False
            
            # .reファイルの数を確認
            re_files = [f for f in file_list if f.endswith('.re')]
            print(f"  📄 ReVIEWファイル: {len(re_files)} 個")
            
            # imagesディレクトリの確認
            image_files = [f for f in file_list if f.startswith('images/')]
            print(f"  🖼️ 画像ファイル: {len(image_files)} 個")
        
        return True
        
    except Exception as e:
        print(f"❌ ZIP作成エラー: {e}")
        return False

def test_api_upload(zip_path: Path) -> tuple[bool, str]:
    """
    APIアップロードテスト
    
    Args:
        zip_path: ZIPファイルのパス
        
    Returns:
        (成功/失敗, 結果メッセージ)
    """
    try:
        print(f"🚀 APIアップロードテスト開始...")
        
        # API設定
        api_base_url = "http://sd001.nextpublishing.jp/rapture"
        api_username = "ep_user"
        api_password = "Nn7eUTX5"
        auth = HTTPBasicAuth(api_username, api_password)
        
        # アップロードURL
        upload_url = f"{api_base_url.rstrip('/')}/api/upload"
        print(f"📡 アップロードURL: {upload_url}")
        
        # ファイルアップロード
        with open(zip_path, 'rb') as f:
            files = {'file': (zip_path.name, f, 'application/zip')}
            
            print(f"⬆️ アップロード実行中...")
            response = requests.post(
                upload_url,
                files=files,
                auth=auth,
                timeout=300
            )
        
        print(f"📈 HTTP Status: {response.status_code}")
        print(f"📄 Response Content Type: {response.headers.get('content-type', 'N/A')}")
        print(f"📏 Response Length: {len(response.text)}")
        print(f"📝 Response Preview: '{response.text[:300]}'")
        
        if response.status_code == 200:
            # 空のレスポンスをチェック
            if not response.text.strip():
                print(f"⚠️ 空のレスポンスを受信")
                return False, "サーバーから空のレスポンスが返されました"
            
            try:
                data = response.json()
                jobid = data.get('jobid')
                print(f"✅ アップロード成功")
                print(f"📋 Job ID: {jobid}")
                print(f"🔍 レスポンス全体: {data}")
                
                if jobid:
                    # ステータス確認
                    return check_job_status(api_base_url, jobid, auth)
                else:
                    return False, "Job IDが取得できませんでした"
            except ValueError as e:
                error_msg = f"JSON解析エラー: {e}"
                print(f"❌ {error_msg}")
                return False, error_msg
        else:
            error_msg = f"アップロード失敗 (HTTP {response.status_code}): {response.text[:200]}"
            print(f"❌ {error_msg}")
            return False, error_msg
            
    except Exception as e:
        error_msg = f"APIアップロードエラー: {e}"
        print(f"❌ {error_msg}")
        return False, error_msg

def check_job_status(api_base_url: str, jobid: str, auth, max_attempts: int = 30) -> tuple[bool, str]:
    """
    ジョブステータス確認
    
    Args:
        api_base_url: API ベースURL
        jobid: ジョブID
        auth: 認証情報
        max_attempts: 最大確認回数
        
    Returns:
        (成功/失敗, 結果メッセージ)
    """
    import time
    
    print(f"⏳ ジョブステータス確認開始...")
    status_url = f"{api_base_url.rstrip('/')}/api/status/{jobid}"
    print(f"📡 ステータスURL: {status_url}")
    
    for attempt in range(max_attempts):
        try:
            print(f"🔍 ステータス確認 ({attempt + 1}/{max_attempts})")
            response = requests.get(status_url, auth=auth, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                print(f"📊 ステータス: {status}")
                
                if status == 'completed':
                    result = data.get('result', 'unknown')
                    output = data.get('output', '')
                    download_url = data.get('download_url')
                    
                    print(f"🎯 変換結果: {result}")
                    print(f"📄 出力: {output[:200]}...")
                    print(f"⬇️ ダウンロードURL: {download_url}")
                    
                    if result == 'success':
                        return True, f"変換成功: {download_url}"
                    elif result == 'partial_success':
                        return True, f"一部成功: {download_url}\n警告: {output}"
                    else:  # failure
                        return False, f"変換失敗: {output}"
                
                elif status == 'failed':
                    errors = data.get('errors', [])
                    error_msg = f"処理失敗: {errors}"
                    print(f"❌ {error_msg}")
                    return False, error_msg
                
                # まだ処理中
                time.sleep(10)  # 10秒待機
                
            else:
                error_msg = f"ステータス取得失敗 (HTTP {response.status_code}): {response.text[:200]}"
                print(f"❌ {error_msg}")
                return False, error_msg
                
        except Exception as e:
            error_msg = f"ステータス確認エラー: {e}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    # タイムアウト
    timeout_msg = f"ステータス確認タイムアウト ({max_attempts} 回試行)"
    print(f"⏰ {timeout_msg}")
    return False, timeout_msg

def main():
    """メイン処理"""
    print("=" * 60)
    print("🔧 N02360 API ZIP構造修正デバッグテスト")
    print("=" * 60)
    
    # ReVIEWディレクトリの場所
    source_review_dir = project_root / "cache/repo_cache/n2360-2361-chatgpt/ReVIEW"
    
    if not source_review_dir.exists():
        print(f"❌ ReVIEWディレクトリが見つかりません: {source_review_dir}")
        return False
    
    print(f"📁 ReVIEWディレクトリ確認: {source_review_dir}")
    
    # 一時ファイル作成
    temp_dir = Path(tempfile.mkdtemp())
    output_zip = temp_dir / "n02360_fixed_structure.zip"
    
    try:
        # 1. 適切な構造でZIPファイル作成
        print(f"\n📦 Phase 1: ZIP構造修正")
        if not create_proper_review_zip(source_review_dir, output_zip):
            print(f"❌ ZIP作成失敗")
            return False
        
        # 2. APIアップロードテスト
        print(f"\n🚀 Phase 2: APIアップロードテスト")
        success, message = test_api_upload(output_zip)
        
        print(f"\n" + "=" * 60)
        if success:
            print(f"✅ テスト成功!")
            print(f"📋 結果: {message}")
        else:
            print(f"❌ テスト失敗!")
            print(f"📋 エラー: {message}")
        print("=" * 60)
        
        return success
        
    finally:
        # 一時ファイルクリーンアップ
        try:
            shutil.rmtree(temp_dir)
            print(f"🧹 一時ファイルクリーンアップ完了")
        except:
            pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)