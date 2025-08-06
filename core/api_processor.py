from __future__ import annotations
"""ReVIEW変換API処理モジュール"""
import os
import requests
from requests.auth import HTTPBasicAuth
import time
import tempfile
import zipfile
import shutil
import re
import io
from pathlib import Path
from typing import Optional, Tuple, List
from PyQt6.QtCore import QObject, pyqtSignal

from utils.logger import get_logger

# Phase 3-2: DI Container統合によりConfigManager条件分岐import完全解消
from core.configuration_provider import ConfigurationProvider
from core.di_container import inject


class ApiProcessor(QObject):
    """API方式での変換処理を行うクラス"""
    
    # シグナル定義
    log_message = pyqtSignal(str, str)  # message, level
    progress_updated = pyqtSignal(int)  # progress
    status_updated = pyqtSignal(str)  # status
    warning_dialog_needed = pyqtSignal(list, str)  # messages, result_type
    
    @inject
    def __init__(self, config_provider: ConfigurationProvider):
        """
        Phase 3-2: Constructor Injection適用
        
        Args:
            config_provider: DI注入される統一設定プロバイダー
        """
        super().__init__()
        self.logger = get_logger(__name__)
        self.config_provider = config_provider
        
        # 統一設定プロバイダーから設定を取得
        self.API_BASE_URL = (
            self.config_provider.get("api.nextpublishing.api_base_url") or
            self.config_provider.get("api.nextpublishing.base_url") or
            os.getenv("NEXTPUB_API_BASE_URL") or
            "http://sd001.nextpublishing.jp/rapture"
        )
        
        # 認証情報
        self.API_USERNAME = (
            self.config_provider.get("api.nextpublishing.username") or
            os.getenv('NEXTPUB_USERNAME', 'ep_user')
        )
        self.API_PASSWORD = (
            self.config_provider.get("api.nextpublishing.password") or
            os.getenv('NEXTPUB_PASSWORD', 'Nn7eUTX5')
        )
        
        # タイムアウト設定
        self.UPLOAD_TIMEOUT = self.config_provider.get("api.nextpublishing.upload_timeout", 300)
        self.STATUS_CHECK_TIMEOUT = self.config_provider.get("api.nextpublishing.timeout", 30)
        self.DOWNLOAD_TIMEOUT = self.config_provider.get("api.nextpublishing.download_timeout", 300)
        self.MAX_POLLING_ATTEMPTS = self.config_provider.get("processing.max_polling_attempts", 60)
        self.POLLING_INTERVAL = self.config_provider.get("processing.polling_interval", 10)
        
        self.auth = HTTPBasicAuth(self.API_USERNAME, self.API_PASSWORD)
    
    def strip_ansi_escape_sequences(self, text: str) -> str:
        """ANSIエスケープシーケンスを除去"""
        if not text:
            return text
        
        # ANSIエスケープシーケンスのパターン
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def _detect_server_error_response(self, response) -> Tuple[bool, Optional[str]]:
        """
        サーバーサイド設定エラーの検出
        
        Args:
            response: HTTP response object
            
        Returns:
            (エラー検出フラグ, エラーメッセージ) のタプル
        """
        if response.status_code == 200:
            content = response.text.strip()
            
            # PHP警告・エラーメッセージの検出（優先）
            if any(error_pattern in content for error_pattern in ['Warning:', 'Error:', 'Fatal error:', 'include(application/errors/']):
                return True, "サーバーサイドPHP設定エラーが検出されました"
            
            # HTML/PHP エラーレスポンスの検出（PHPエラーが含まれていない場合）
            if content.startswith('<'):
                return True, "サーバーがHTML形式のエラーを返しました（API設定問題）"
            
            # 空のレスポンス
            if len(content) == 0:
                return True, "サーバーから空のレスポンスが返されました"
        
        return False, None
    
    def upload_zip(self, zip_path: Path) -> Optional[str]:
        """
        ZIPファイルをAPIにアップロード（進捗追跡付き）
        
        Args:
            zip_path: アップロードするZIPファイルのパス
            
        Returns:
            成功時はjobid、失敗時はNone
        """
        file_size = zip_path.stat().st_size
        self.log_message.emit(f"ファイルをアップロード中: {zip_path.name}", "INFO")
        self.log_message.emit(f"ファイルサイズ: {file_size:,} bytes ({file_size / 1024 / 1024:.1f} MB)", "INFO")
        
        # URLを適切に結合（二重スラッシュを防ぐ）
        api_url = self.API_BASE_URL.rstrip('/') + '/api/upload'
        self.log_message.emit(f"API URL: {api_url}", "DEBUG")
        
        # プログレスバーを0%に初期化
        self.progress_updated.emit(0)
        self.status_updated.emit(f"アップロード準備中... (0/{file_size:,} bytes)")
        
        try:
            # requests-toolbeltを使用した進捗追跡
            try:
                from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
                use_toolbelt = True
                self.log_message.emit("進捗追跡モードでアップロード", "DEBUG")
            except ImportError:
                use_toolbelt = False
                self.log_message.emit("進捗追跡なしでアップロード", "DEBUG")
            
            if use_toolbelt:
                # 進捗追跡付きアップロード
                self.log_message.emit("ファイルを読み込み中...", "INFO")
                
                # コールバック用の変数
                last_logged_progress = -1
                
                def create_callback(encoder_len):
                    """進捗コールバックを作成"""
                    def callback(monitor):
                        nonlocal last_logged_progress
                        
                        # 進捗計算
                        bytes_read = monitor.bytes_read
                        total = encoder_len
                        progress = int((bytes_read / total) * 100) if total > 0 else 0
                        
                        # UI更新
                        self.progress_updated.emit(progress)
                        mb_read = bytes_read / 1024 / 1024
                        mb_total = total / 1024 / 1024
                        self.status_updated.emit(
                            f"アップロード中... {progress}% ({mb_read:.1f}/{mb_total:.1f} MB)"
                        )
                        
                        # 10%ごとにログ
                        if progress > 0 and progress % 10 == 0 and progress != last_logged_progress:
                            self.log_message.emit(f"アップロード進捗: {progress}%", "INFO")
                            last_logged_progress = progress
                    
                    return callback
                
                # ファイルを開いてエンコーダーを作成
                with open(zip_path, 'rb') as f:
                    encoder = MultipartEncoder(
                        fields={'file': (zip_path.name, f, 'application/zip')}
                    )
                    encoder_len = encoder.len
                    
                    # モニターを作成
                    monitor = MultipartEncoderMonitor(encoder, create_callback(encoder_len))
                    
                    self.log_message.emit("アップロード開始", "INFO")
                    self.log_message.emit(f"アップロードサイズ: {encoder_len:,} bytes", "DEBUG")
                    
                    response = requests.post(
                        api_url,
                        data=monitor,
                        headers={'Content-Type': monitor.content_type},
                        auth=self.auth,
                        timeout=self.UPLOAD_TIMEOUT
                    )
                
                # アップロード完了
                self.progress_updated.emit(100)
                self.status_updated.emit("アップロード完了")
                self.log_message.emit("アップロード完了", "INFO")
                
            else:
                # フォールバック: 段階的な進捗表示
                self.log_message.emit("ファイルを読み込み中...", "INFO")
                
                # 進捗は段階的に表示
                self.progress_updated.emit(10)
                self.status_updated.emit("ファイル読み込み中...")
                
                # 30%: ファイル準備完了
                self.progress_updated.emit(30)
                self.status_updated.emit("アップロード準備中...")
                
                # ファイルを開いてアップロード
                with open(zip_path, 'rb') as f:
                    files = {'file': (zip_path.name, f, 'application/zip')}
                    
                    # 50%: アップロード開始
                    self.progress_updated.emit(50)
                    self.status_updated.emit(f"アップロード中... ({file_size:,} bytes)")
                    
                    self.log_message.emit("アップロード開始", "INFO")
                    
                    response = requests.post(
                        api_url,
                        files=files,
                        auth=self.auth,
                        timeout=self.UPLOAD_TIMEOUT
                    )
                    
                    # 90%: アップロード完了、レスポンス処理中
                    self.progress_updated.emit(90)
                    self.status_updated.emit("レスポンス処理中...")
                
                # アップロード完了
                self.progress_updated.emit(100)
                self.status_updated.emit("アップロード完了")
                self.log_message.emit("アップロード完了", "INFO")
            
            if response.status_code == 200:
                # サーバーエラー検出
                has_error, error_msg = self._detect_server_error_response(response)
                if has_error:
                    self.log_message.emit(f"API SERVER ERROR: {error_msg}", "ERROR")
                    self.log_message.emit("NextPublishing APIサーバーに設定問題があります", "ERROR")
                    self.log_message.emit(f"レスポンス内容: {response.text[:200]}", "DEBUG")
                    self.log_message.emit("メールベースワークフローに切り替えることを推奨", "WARNING")
                    return None
                
                try:
                    data = response.json()
                    if 'jobid' in data:
                        jobid = data['jobid']
                        self.log_message.emit(f"アップロード成功 (Job ID: {jobid})", "INFO")
                        return jobid
                    else:
                        self.log_message.emit("レスポンスにJob IDが含まれていません", "ERROR")
                except ValueError as e:
                    self.log_message.emit(f"JSONパースエラー: {str(e)}", "ERROR")
                    self.log_message.emit(f"レスポンス内容: {response.text[:200]}", "DEBUG")
                    self.log_message.emit("サーバーから無効なJSON応答が返されました", "ERROR")
            else:
                self.log_message.emit(
                    f"アップロード失敗 (HTTP {response.status_code})", 
                    "ERROR"
                )
                self.log_message.emit(f"レスポンス内容: {response.text[:200]}", "DEBUG")
        
        except requests.exceptions.Timeout:
            self.log_message.emit("アップロードがタイムアウトしました", "ERROR")
        except Exception as e:
            self.log_message.emit(f"アップロードエラー: {str(e)}", "ERROR")
            self.log_message.emit(f"エラータイプ: {type(e).__name__}", "ERROR")
            import traceback
            self.log_message.emit(f"スタックトレース:\n{traceback.format_exc()}", "ERROR")
        
        return None
    
    def check_status(self, jobid: str) -> Tuple[Optional[str], Optional[str], Optional[List[str]]]:
        """
        変換ジョブのステータスを確認
        
        Args:
            jobid: ジョブID
            
        Returns:
            (結果, ダウンロードURL, 警告メッセージリスト) のタプル
            結果は 'success', 'partial_success', 'failure', None のいずれか
        """
        self.log_message.emit("変換処理の完了を待機中...", "INFO")
        
        # ステータス確認URLを適切に構築
        status_url = self.API_BASE_URL.rstrip('/') + f'/api/status/{jobid}'
        self.log_message.emit(f"ステータス確認URL: {status_url}", "DEBUG")
        
        for attempt in range(self.MAX_POLLING_ATTEMPTS):
            try:
                response = requests.get(
                    status_url,
                    auth=self.auth,
                    timeout=self.STATUS_CHECK_TIMEOUT
                )
                
                self.log_message.emit(f"ステータス確認 - HTTP Status: {response.status_code}", "DEBUG")
                
                if response.status_code == 200:
                    # サーバーエラー検出
                    has_error, error_msg = self._detect_server_error_response(response)
                    if has_error:
                        self.log_message.emit(f"STATUS CHECK SERVER ERROR: {error_msg}", "ERROR")
                        self.log_message.emit("ステータス確認でサーバー設定問題を検出", "ERROR")
                        self.log_message.emit(f"レスポンス内容: {response.text[:200]}", "DEBUG")
                        return 'failure', None, [f"サーバー設定エラー: {error_msg}"]
                    
                    # レスポンスの内容を確認
                    try:
                        response_text = response.text
                        self.log_message.emit(f"レスポンス内容: {response_text[:500]}", "DEBUG")
                        data = response.json()
                    except Exception as e:
                        self.log_message.emit(f"JSONパースエラー: {str(e)}", "ERROR")
                        self.log_message.emit(f"レスポンス内容: {response.text[:500]}", "ERROR")
                        # 空のレスポンスの場合は処理中として扱う
                        if not response.text:
                            self.log_message.emit("空のレスポンスを受信 - 処理中として継続", "INFO")
                            time.sleep(self.POLLING_INTERVAL)
                            continue
                        raise
                    self.log_message.emit(f"ステータス応答全体: {data}", "DEBUG")
                    
                    status = data.get('status', 'unknown')
                    
                    self.log_message.emit(f"ステータス応答: {status}", "DEBUG")
                    self.status_updated.emit(f"変換状況: {status} ({attempt + 1}/{self.MAX_POLLING_ATTEMPTS})")
                    
                    if status == 'completed':
                        result = data.get('result', 'unknown')
                        output = data.get('output', '')
                        download_url = data.get('download_url')
                        warnings = []
                        
                        self.log_message.emit(f"変換結果: {result}", "DEBUG")
                        self.log_message.emit(f"ダウンロードURL: {download_url}", "DEBUG")
                        self.log_message.emit(f"出力タイプ: {type(output)}", "DEBUG")
                        
                        # ANSIエスケープシーケンスを除去
                        if output:
                            if isinstance(output, str):
                                self.log_message.emit(f"出力文字数（ANSI除去前）: {len(output)}", "DEBUG")
                                output = self.strip_ansi_escape_sequences(output)
                                self.log_message.emit(f"出力文字数（ANSI除去後）: {len(output)}", "DEBUG")
                            elif isinstance(output, list):
                                self.log_message.emit(f"出力リスト長: {len(output)}", "DEBUG")
                                output = '\n'.join(str(item) for item in output)
                                output = self.strip_ansi_escape_sequences(output)
                            
                            # 警告メッセージを行ごとに分割
                            warnings = [line.strip() for line in output.split('\n') if line.strip()]
                            self.log_message.emit(f"警告メッセージ数: {len(warnings)}", "DEBUG")
                        
                        if result == 'success':
                            if not warnings:
                                self.log_message.emit("変換処理が正常に完了しました（警告なし）", "INFO")
                                return 'success', download_url, []
                            else:
                                self.log_message.emit("変換処理が成功しました（警告あり）", "WARNING")
                                self.log_message.emit(f"警告内容: {len(warnings)}件", "DEBUG")
                                for i, warning in enumerate(warnings[:3]):  # 最初の3件だけログに出力
                                    self.log_message.emit(f"  警告{i+1}: {warning[:100]}...", "DEBUG")
                                return 'partial_success', download_url, warnings
                        
                        elif result == 'partial_success':
                            self.log_message.emit("変換処理が一部成功で完了しました", "WARNING")
                            return 'partial_success', download_url, warnings
                        
                        else:  # failure
                            errors = data.get('errors', [])
                            self.log_message.emit("変換処理が失敗しました", "ERROR")
                            self.log_message.emit(f"エラー数: {len(errors)}", "DEBUG")
                            
                            # JSON content-level error detection for server-side issues
                            output_content = data.get('output', '')
                            if output_content:
                                # Check for server-specific error patterns in output content
                                server_error_patterns = [
                                    'Warning:',           # PHP Warning はサーバーエラー  
                                    'Error:',             # PHP Error はサーバーエラー
                                    'Fatal error:',       # PHP Fatal Error はサーバーエラー
                                    'include(application/errors/',
                                    'PHP Warning',
                                    'PHP Error'
                                ]
                                
                                if any(pattern in str(output_content) for pattern in server_error_patterns):
                                    self.log_message.emit("JSON content-level server error detected", "ERROR")
                                    self.log_message.emit(f"Server error pattern found in output: {output_content[:200]}", "DEBUG")
                                    self._show_server_error_guidance("JSON content server error")
                                    return 'failure', None, [f"サーバー設定エラー: {str(output_content)[:100]}"]
                                
                            # review compile段階の詳細ログ（正常な処理ステップとして扱う）
                            if 'review compile' in str(output_content):
                                self.log_message.emit("Review compile段階を検出", "INFO")
                                self.log_message.emit(f"Review compile詳細: {str(output_content)[:500]}", "DEBUG")
                                
                                # review compile 固有のエラーパターンをチェック
                                review_error_patterns = [
                                    'review compile failed',
                                    'compile error', 
                                    'syntax error',
                                    'compilation failed'
                                ]
                                
                                review_has_error = any(pattern in str(output_content).lower() for pattern in review_error_patterns)
                                if review_has_error:
                                    self.log_message.emit("Review compile でエラーを検出", "ERROR")
                                    return 'failure', None, [f"Review compileエラー: {str(output_content)[:200]}"]
                                else:
                                    self.log_message.emit("Review compile は正常に実行中", "INFO")
                            
                            if errors:
                                for error in errors:
                                    self.log_message.emit(f"  - {error}", "ERROR")
                            return 'failure', None, warnings if warnings else errors
                    
                    elif status == 'failed':
                        errors = data.get('errors', [])
                        self.log_message.emit("変換処理が失敗しました", "ERROR")
                        self.log_message.emit(f"エラー詳細: {errors}", "DEBUG")
                        return 'failure', None, errors
                    
                    # まだ処理中の場合は待機
                    time.sleep(self.POLLING_INTERVAL)
                    
                else:
                    self.log_message.emit(
                        f"ステータス取得失敗 (HTTP {response.status_code})", 
                        "ERROR"
                    )
                    self.log_message.emit(f"エラー応答: {response.text[:500]}", "DEBUG")
                    return None, None, []
                    
            except Exception as e:
                self.log_message.emit(f"ステータス確認エラー: {str(e)}", "ERROR")
                self.log_message.emit(f"エラータイプ: {type(e).__name__}", "DEBUG")
                import traceback
                self.log_message.emit(f"スタックトレース: {traceback.format_exc()}", "DEBUG")
                return None, None, []
        
        self.log_message.emit("変換処理がタイムアウトしました", "ERROR")
        return None, None, []
    
    def download_file(self, download_url: str, output_dir: Path) -> Optional[Path]:
        """
        変換済みファイルをダウンロード
        
        Args:
            download_url: ダウンロードURL
            output_dir: 保存先ディレクトリ
            
        Returns:
            成功時はダウンロードしたファイルのパス、失敗時はNone
        """
        self.log_message.emit("変換済みファイルをダウンロード中...", "INFO")
        
        try:
            response = requests.get(
                download_url,
                auth=self.auth,
                stream=True,
                timeout=self.DOWNLOAD_TIMEOUT
            )
            
            if response.status_code == 200:
                # ファイル名を生成
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"converted_{timestamp}.zip"
                output_path = output_dir / filename
                
                # ダウンロード実行
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # 進捗更新
                            if total_size > 0:
                                progress = int(downloaded / total_size * 100)
                                self.progress_updated.emit(progress)
                
                self.log_message.emit(f"ダウンロード完了: {filename}", "INFO")
                
                # ZIPファイルの検証
                try:
                    with zipfile.ZipFile(output_path, 'r') as zf:
                        file_count = len(zf.namelist())
                        self.log_message.emit(f"ZIPファイル内のファイル数: {file_count}", "INFO")
                except zipfile.BadZipFile:
                    self.log_message.emit("ダウンロードしたファイルが有効なZIPファイルではありません", "ERROR")
                    output_path.unlink()
                    return None
                
                return output_path
                
            else:
                self.log_message.emit(
                    f"ダウンロード失敗 (HTTP {response.status_code})", 
                    "ERROR"
                )
                
        except requests.exceptions.Timeout:
            self.log_message.emit("ダウンロードがタイムアウトしました", "ERROR")
        except Exception as e:
            self.log_message.emit(f"ダウンロードエラー: {str(e)}", "ERROR")
        
        return None
    
    def _show_server_error_guidance(self, error_type: str):
        """
        サーバーエラー時のユーザーガイダンス表示
        
        Args:
            error_type: エラーの種類
        """
        self.log_message.emit("=== API サーバーエラー対処法 ===", "WARNING")
        
        if "PHP" in error_type or "設定" in error_type:
            self.log_message.emit("🔴 NextPublishing APIサーバーに設定問題があります", "ERROR")
            self.log_message.emit("", "INFO")
            self.log_message.emit("📋 推奨対処法：", "WARNING")
            self.log_message.emit("1. メールベース変換ワークフローに切り替え", "INFO")
            self.log_message.emit("2. NextPublishing技術サポートに連絡", "INFO")
            self.log_message.emit("3. しばらく時間をおいてAPI再試行", "INFO")
            self.log_message.emit("", "INFO")
            self.log_message.emit("💡 メールワークフローは設定画面から変更可能", "INFO")
            self.log_message.emit("   (ツール → 設定 → 変換方法 → メール方式)", "INFO")
        
        self.log_message.emit("================================", "WARNING")
    
    def process_zip_file(self, zip_path: Path) -> Tuple[bool, Optional[Path], List[str]]:
        """
        ZIPファイルをAPI経由で処理
        
        Args:
            zip_path: 処理するZIPファイルのパス
            
        Returns:
            (成功フラグ, ダウンロードしたファイルのパス, 警告メッセージリスト) のタプル
        """
        self.log_message.emit(f"API処理開始: {zip_path}", "INFO")
        self.log_message.emit(f"ファイルサイズ: {zip_path.stat().st_size:,} bytes", "DEBUG")
        
        # 一時ディレクトリを作成
        temp_dir = Path(tempfile.mkdtemp())
        self.log_message.emit(f"一時ディレクトリ作成: {temp_dir}", "DEBUG")
        
        try:
            # 1. アップロード
            self.log_message.emit("アップロード処理を開始...", "INFO")
            jobid = self.upload_zip(zip_path)
            if not jobid:
                self.log_message.emit("アップロードが失敗しました", "ERROR")
                self.log_message.emit("upload_zipがNoneを返しました", "ERROR")
                
                # サーバーエラーの可能性を考慮してガイダンスを表示
                self._show_server_error_guidance("API アップロードエラー")
                
                return False, None, ["APIアップロードに失敗しました。メールベースワークフローをお試しください。"]
            
            self.log_message.emit(f"アップロード成功 - Job ID: {jobid}", "INFO")
            
            # 2. ステータス確認
            self.log_message.emit("ステータス確認を開始...", "INFO")
            result, download_url, messages = self.check_status(jobid)
            
            self.log_message.emit(f"ステータス確認結果: result={result}", "INFO")
            self.log_message.emit(f"ダウンロードURL: {download_url}", "DEBUG")
            self.log_message.emit(f"メッセージ数: {len(messages) if messages else 0}", "DEBUG")
            
            if result == 'failure' or not download_url:
                # 失敗の場合もエラーダイアログを表示
                self.log_message.emit(f"処理失敗: result={result}, download_url={download_url}", "ERROR")
                
                # サーバーエラーが原因の場合はガイダンスを表示
                if messages and any("サーバー設定エラー" in str(msg) for msg in messages):
                    self._show_server_error_guidance("サーバー設定エラー")
                
                if messages:
                    self.log_message.emit(f"エラーメッセージ: {messages[:3]}", "ERROR")
                    self.log_message.emit(f"エラーダイアログを表示: {len(messages)}件のメッセージ", "ERROR")
                    self.warning_dialog_needed.emit(messages, 'failure')
                return False, None, messages
            
            # 3. ダウンロード
            self.log_message.emit("ダウンロード処理を開始...", "INFO")
            downloaded_file = self.download_file(download_url, temp_dir)
            if not downloaded_file:
                self.log_message.emit("download_fileがNoneを返しました", "ERROR")
                return False, None, ["ファイルのダウンロードに失敗しました"]
            
            self.log_message.emit(f"ダウンロード成功: {downloaded_file}", "INFO")
            
            # 警告がある場合はダイアログを表示
            if result == 'partial_success' and messages:
                self.log_message.emit(f"警告ダイアログを表示: {len(messages)}件のメッセージ", "INFO")
                self.warning_dialog_needed.emit(messages, 'partial_success')
            
            # 成功または一部成功
            return True, downloaded_file, messages
            
        except Exception as e:
            self.log_message.emit(f"API処理エラー: {str(e)}", "ERROR")
            self.log_message.emit(f"エラータイプ: {type(e).__name__}", "ERROR")
            import traceback
            self.log_message.emit(f"スタックトレース:\n{traceback.format_exc()}", "ERROR")
            return False, None, [str(e)]
        
        finally:
            # 一時ディレクトリのクリーンアップは呼び出し側で行う
            self.log_message.emit(f"process_zip_file終了", "DEBUG")