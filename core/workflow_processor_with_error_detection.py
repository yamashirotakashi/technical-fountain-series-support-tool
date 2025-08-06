"""エラー検知機能を統合したワークフロープロセッサー"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timezone
from PyQt6.QtCore import pyqtSignal

from core.workflow_processor import WorkflowProcessor
from services.nextpublishing_service import NextPublishingService
from services.error_check_validator import ErrorCheckValidator
from core.gmail_oauth_monitor import GmailOAuthMonitor
from utils.logger import get_logger


class WorkflowProcessorWithErrorDetection(WorkflowProcessor):
    """ReVIEW変換後にWord2XHTML5でエラー検知を行うワークフロープロセッサー"""
    
    # 追加シグナル
    error_files_detected = pyqtSignal(list)  # エラーファイルリスト
    error_detection_progress = pyqtSignal(int, int)  # 現在, 全体
    error_file_selection_needed = pyqtSignal(list, object)  # ファイルリスト, コールバック
    
    def __init__(self, email_address: str = None, email_password: str = None, process_mode: str = "traditional"):
        """初期化"""
        super().__init__(email_address, email_password, process_mode)
        self.logger = get_logger(__name__)
        self.nextpublishing_service = None
        self.processed_word_files = []  # ReVIEW変換で生成されたWordファイル
        
    def process_n_codes_with_error_detection(self, n_codes: List[str]):
        """
        Nコードを処理してエラー検知まで実行
        
        Args:
            n_codes: 処理するNコードのリスト
        """
        self.emit_log("=" * 60, "INFO")
        self.emit_log("エラーファイル検知フロー開始", "INFO")
        self.emit_log("フロー: ReVIEW変換 → Word生成 → Word2XHTML5検証", "INFO")
        self.emit_log("=" * 60, "INFO")
        
        # Phase 1: ReVIEW変換（通常のワークフロー）
        self.emit_log("Phase 1: ReVIEW変換を開始します", "INFO")
        total = len(n_codes)
        
        for idx, n_code in enumerate(n_codes):
            self.emit_status(f"ReVIEW変換中: {n_code} ({idx + 1}/{total})")
            self.emit_progress(int((idx / total) * 50))  # 前半50%をReVIEW変換に割り当て
            
            try:
                # 通常の変換処理を実行し、生成されたWordファイルを記録
                word_files = self.process_single_n_code_with_tracking(n_code)
                if word_files:
                    self.processed_word_files.extend(word_files)
                    self.emit_log(f"✓ {n_code} の変換完了: {len(word_files)}個のWordファイル生成", "INFO")
                
            except Exception as e:
                self.emit_log(f"✗ {n_code} の変換に失敗: {str(e)}", "ERROR")
                self.logger.error(f"変換エラー {n_code}: {e}", exc_info=True)
        
        # Phase 2: Word2XHTML5でエラー検知
        if self.processed_word_files:
            self.emit_log("=" * 60, "INFO")
            self.emit_log(f"Phase 2: Word2XHTML5エラー検知を開始します", "INFO")
            self.emit_log(f"検査対象: {len(self.processed_word_files)}個のWordファイル", "INFO")
            
            # ファイル選択ダイアログを表示
            selected_files = self._show_error_detection_file_selection(self.processed_word_files)
            
            if selected_files:
                self.emit_log(f"選択されたファイル: {len(selected_files)}個", "INFO")
                error_files = self.detect_error_files(selected_files)
                
                # 結果を通知
                self.error_files_detected.emit(error_files)
                
                if error_files:
                    self.emit_log(f"⚠️ エラーファイル検出: {len(error_files)}個", "WARNING")
                    for ef in error_files:
                        self.emit_log(f"  ✗ {ef.name}", "ERROR")
                else:
                    self.emit_log("✓ すべてのファイルが正常に処理されます", "INFO")
            else:
                self.emit_log("エラー検知がキャンセルされました", "WARNING")
        else:
            self.emit_log("生成されたWordファイルがありません", "WARNING")
        
        self.emit_progress(100)
        self.emit_status("エラー検知完了")
        self.emit_log("=" * 60, "INFO")
        self.emit_log("エラーファイル検知フロー完了", "INFO")
    
    def process_single_n_code_with_tracking(self, n_code: str) -> List[Path]:
        """
        単一のNコードを処理し、生成されたWordファイルを追跡
        
        Returns:
            生成されたWordファイルのパスリスト
        """
        try:
            # 自動モードで処理（フォルダ選択ダイアログを表示しない）
            self.process_single_n_code_auto(n_code)
        except Exception as e:
            self.emit_log(f"✗ {n_code} の処理エラー: {str(e)}", "ERROR")
            raise
        
        # 生成されたWordファイルを取得
        ncode_folder = self.word_processor.find_ncode_folder(n_code)
        if ncode_folder:
            honbun_folder = self.word_processor.find_honbun_folder(ncode_folder)
            if honbun_folder:
                # 本文フォルダ内のWordファイルを収集
                word_files = list(honbun_folder.glob("*.docx"))
                return word_files
        
        return []
    
    def process_single_n_code_auto(self, n_code: str):
        """
        単一のNコードを自動モードで処理（フォルダ選択ダイアログなし）
        """
        self.logger.info(f"Nコード処理開始（自動モード）: {n_code}")
        
        # 1. Googleシートからリポジトリ名を取得
        self.emit_log(f"Googleシートから {n_code} を検索中...", "INFO")
        repo_info = self.google_client.search_n_code(n_code)
        
        if not repo_info:
            raise ValueError(f"Nコード {n_code} がGoogleシートに見つかりません")
        
        repo_name = repo_info['repository_name']
        self.emit_log(f"リポジトリ名: {repo_name}", "INFO")
        
        # 2. リポジトリフォルダを検索
        self.emit_log(f"リポジトリフォルダを検索中: {repo_name}", "INFO")
        repo_path = self.file_manager.find_repository_folder(repo_name)
        
        if not repo_path:
            raise ValueError(f"リポジトリフォルダが見つかりません: {repo_name}")
        
        # 3. 作業フォルダを自動検出
        self.emit_log("作業フォルダを自動検出中...", "INFO")
        # エラーチェック時は自動検出のみ（ダイアログを表示しない）
        work_folder = self.file_manager.find_work_folder(repo_path)
        
        if not work_folder:
            # articlesフォルダがある場合はそれを使用
            articles_folder = repo_path / "articles"
            if articles_folder.exists() and articles_folder.is_dir():
                self.emit_log(f"articlesフォルダを作業フォルダとして使用: {articles_folder}", "INFO")
                work_folder = articles_folder
            else:
                raise ValueError("作業フォルダが見つかりませんでした")
        
        self.emit_log(f"作業フォルダ: {work_folder}", "INFO")
        
        # 4. ZIPファイルを作成
        self.emit_log("ZIPファイルを作成中...", "INFO")
        zip_path = self.file_manager.create_zip(work_folder)
        
        # 5. 処理方式に応じて分岐
        self.logger.info(f"現在の処理モード: {self.process_mode}")
        if self.process_mode == "api":
            # API方式の処理
            self.emit_log("API方式で変換処理を開始...", "INFO")
            api_proc = self.api_processor
            success, download_path, warnings = api_proc.process_zip_file(zip_path)
            
            if not success:
                error_msg = "API変換処理が失敗しました"
                if warnings:
                    error_msg += f" (エラー/警告: {', '.join(warnings[:3])})"
                raise ValueError(error_msg)
            
            if not download_path:
                raise ValueError("変換ファイルのダウンロードに失敗しました")
        else:
            # 従来方式の処理
            mode_text = "Gmail API方式" if self.process_mode == "gmail_api" else "従来方式"
            self.emit_log(f"{mode_text}で処理を開始...", "INFO")
            upload_success = self.web_client.upload_file(zip_path, self.email_address, self.process_mode)
            
            if not upload_success:
                raise ValueError("ファイルのアップロードに失敗しました")
            
            if self.email_password:
                self.emit_log("変換完了メールを待機中...", "INFO")
                download_url = self.email_monitor.wait_for_email()
                
                if not download_url:
                    raise ValueError("タイムアウト: メールが届きませんでした")
                
                self.emit_log("変換済みファイルをダウンロード中...", "INFO")
                download_path = self.file_manager.temp_dir / f"{n_code}_converted.zip"
                download_success = self.web_client.download_file(download_url, download_path)
                
                if not download_success:
                    raise ValueError("ファイルのダウンロードに失敗しました")
            else:
                self.emit_log("メールパスワードが設定されていないため、手動でダウンロードしてください", "WARNING")
                return
        
        # 6. ZIPファイルを処理（展開 + 1行目削除）
        self.emit_log("ZIPファイルを処理中...", "INFO")
        processed_files = self.word_processor.process_zip_file(download_path)
        
        if not processed_files:
            raise ValueError("ZIPファイルの処理に失敗しました")
        
        self.emit_log(f"{len(processed_files)}個のWordファイルを処理しました", "INFO")
        
        # 7. Nフォルダと本文フォルダの存在確認
        ncode_folder = self.word_processor.find_ncode_folder(n_code)
        if not ncode_folder:
            raise ValueError(f"Nコードフォルダが見つかりません: {n_code}")
        
        honbun_folder = self.word_processor.find_honbun_folder(ncode_folder)
        if not honbun_folder:
            raise ValueError(f"本文フォルダの場所を特定できません: {ncode_folder}")
        
        # 8. ファイルを配置（自動モードなので確認ダイアログなし）
        self.emit_log(f"ファイルを本文フォルダに配置中: {honbun_folder}", "INFO")
        placement_success = self._copy_files_to_honbun_folder(processed_files, honbun_folder)
        
        if not placement_success:
            raise ValueError("ファイルの配置に失敗しました")
        
        self.emit_log("ファイル配置が完了しました", "INFO")
    
    def detect_error_files(self, word_files: List[Path]) -> List[Path]:
        """
        Word2XHTML5を使用してエラーファイルを検出
        
        Args:
            word_files: 検査するWordファイルのリスト
            
        Returns:
            エラーファイルのリスト
        """
        try:
            # NextPublishingサービスを初期化
            if not self.nextpublishing_service:
                self.nextpublishing_service = NextPublishingService()
            
            # メール監視を初期化（Gmail API優先）
            email_monitor = None
            
            # Gmail API設定確認
            gmail_api_enabled = self.config.get_email_config().get('use_gmail_api', False)
            self.emit_log(f"Gmail API設定: {'有効' if gmail_api_enabled else '無効'}", "INFO")
            
            if self.email_password:
                # Gmail API設定チェック
                if gmail_api_enabled:
                    # Gmail APIを試行
                    try:
                        from core.gmail_oauth_monitor import GmailOAuthMonitor
                        from core.gmail_oauth_exe_helper import gmail_oauth_helper
                        
                        self.emit_log("Gmail API初期化を開始します", "INFO")
                        
                        # 開発環境とEXE環境の両方に対応
                        if gmail_oauth_helper.is_exe:
                            # EXE環境: exe_helperを使用
                            self.emit_log("EXE環境でGmail API認証をチェック中...", "DEBUG")
                            credentials_path, token_path = gmail_oauth_helper.get_credentials_path()
                            self.emit_log(f"認証ファイルパス: {credentials_path}", "DEBUG")
                            self.emit_log(f"トークンファイルパス: {token_path}", "DEBUG")
                            
                            if gmail_oauth_helper.check_credentials_exist():
                                self.emit_log("Gmail APIを使用してメール監視を初期化します（EXE環境）", "INFO")
                                # EXE環境では明示的にNoneを渡して内部でパス解決させる
                                email_monitor = GmailOAuthMonitor(credentials_path=None, service_type='word2xhtml5')
                                email_monitor.authenticate()
                                self.emit_log("Gmail APIメール監視を有効化しました", "INFO")
                            else:
                                raise FileNotFoundError(f"OAuth2.0認証ファイルが見つかりません: {credentials_path}")
                        else:
                            # 開発環境: 設定ファイルからパスを取得
                            config_credentials_path = self.config.get_email_config().get('gmail_credentials_path')
                            if config_credentials_path:
                                gmail_credentials_path = Path(config_credentials_path)
                                self.emit_log(f"設定からの認証ファイルパス: {gmail_credentials_path}", "DEBUG")
                            else:
                                gmail_credentials_path = Path("config/gmail_oauth_credentials.json")
                                
                            if not gmail_credentials_path.exists():
                                alt_path = Path("config/gmail_credentials.json")
                                if alt_path.exists():
                                    gmail_credentials_path = alt_path
                                    self.emit_log(f"代替認証ファイルパス使用: {gmail_credentials_path}", "DEBUG")
                            
                            if gmail_credentials_path.exists():
                                self.emit_log("Gmail APIを使用してメール監視を初期化します（開発環境）", "INFO")
                                self.emit_log(f"使用する認証ファイル: {gmail_credentials_path}", "DEBUG")
                                email_monitor = GmailOAuthMonitor(str(gmail_credentials_path), service_type='word2xhtml5')
                                email_monitor.authenticate()
                                self.emit_log("Gmail APIメール監視を有効化しました", "INFO")
                            else:
                                raise FileNotFoundError(f"OAuth2.0認証ファイルが見つかりません: {gmail_credentials_path}")
                    except Exception as e:
                        # Gmail APIが使えない場合はIMAPにフォールバック
                        import traceback
                        self.emit_log(f"Gmail API初期化失敗、IMAPを使用します: {e}", "WARNING")
                        self.emit_log(f"詳細エラー: {traceback.format_exc()}", "DEBUG")
                        gmail_api_enabled = False  # フォールバック時は無効扱い
                
                # Gmail APIが無効またはフォールバック時はIMAPを使用
                if not gmail_api_enabled or not email_monitor:
                    self.emit_log("IMAPメール監視に切り替えます", "INFO")
                    try:
                        from core.email_monitor_enhanced import EmailMonitorEnhanced
                        email_monitor = EmailMonitorEnhanced(
                            email_address=self.email_address,
                            password=self.email_password,
                            service_type='word2xhtml5'  # Word2XHTML5用の処理
                        )
                        email_monitor.connect()
                        self.emit_log("IMAPメール監視を有効化しました", "INFO")
                    except Exception as e2:
                        self.emit_log(f"IMAPメール監視の初期化に失敗: {e2}", "WARNING")
                        email_monitor = None
            
            error_files = []
            total_files = len(word_files)
            
            # バッチサイズを決定（10ファイルずつ）
            batch_size = 10
            
            for i in range(0, total_files, batch_size):
                batch = word_files[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                self.emit_status(f"Word2XHTML5検証中: バッチ {batch_num}")
                self.emit_log(f"バッチ {batch_num} をアップロード中...", "INFO")
                
                # アップロード前にメール監視開始時刻を記録
                upload_start_time = datetime.now(timezone.utc)
                if email_monitor:
                    # 日本時間でも表示
                    from zoneinfo import ZoneInfo
                    jst_time = upload_start_time.astimezone(ZoneInfo('Asia/Tokyo'))
                    self.emit_log(f"アップロード開始時刻(UTC): {upload_start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC", "INFO")
                    self.emit_log(f"アップロード開始時刻(JST): {jst_time.strftime('%Y-%m-%d %H:%M:%S')} JST", "INFO")
                
                # バッチアップロード
                results = self.nextpublishing_service.upload_multiple_files(batch, batch_size)
                
                # アップロード結果を記録
                upload_success_files = []
                for result in results:
                    if result['success']:
                        upload_success_files.append(result['file_path'])
                        self.emit_log(f"  ✓ アップロード成功: {result['file_path'].name}", "INFO")
                    else:
                        self.emit_log(f"  ✗ アップロード失敗: {result['file_path'].name}", "ERROR")
                        error_files.append(result['file_path'])
                
                # メール到着を待機してPDFチェック
                if email_monitor and upload_success_files:
                    self.emit_log(f"変換メールを待機中（最大20分）...", "INFO")
                    
                    # バッチ内のすべてのファイルのメールを収集（アップロード時刻を渡す）
                    file_url_map = self._collect_batch_emails(upload_success_files, email_monitor, upload_start_time)
                    
                    # ErrorCheckValidatorを使用してバッチ検証
                    validator = ErrorCheckValidator()
                    
                    # ファイル名とパスのマッピングを作成
                    filename_to_path = {f.name: f for f in upload_success_files}
                    
                    # バッチ検証を実行
                    error_results, normal_results = validator.validate_batch(file_url_map)
                    
                    # エラーファイルを記録
                    for error_result in error_results:
                        filename = error_result['filename']
                        reason = error_result['reason']
                        if filename in filename_to_path:
                            file_path = filename_to_path[filename]
                            error_files.append(file_path)
                            self.emit_log(f"  ✗ PDFエラー: {filename} - {reason}", "ERROR")
                    
                    # 正常ファイルも記録
                    for normal_result in normal_results:
                        filename = normal_result['filename']
                        self.emit_log(f"  ✓ 正常: {filename}", "INFO")
                    
                    # 進捗更新
                    progress = 50 + int((i + len(upload_success_files)) / total_files * 50)
                    self.emit_progress(progress)
                else:
                    # メール監視なしの場合
                    self.emit_log("メール監視が無効です。手動確認が必要です", "WARNING")
            
            return error_files
            
        except Exception as e:
            self.logger.error(f"エラー検知処理でエラー: {e}", exc_info=True)
            self.emit_log(f"エラー検知エラー: {str(e)}", "ERROR")
            return []
        finally:
            if self.nextpublishing_service:
                self.nextpublishing_service.close()
            if 'email_monitor' in locals() and email_monitor:
                email_monitor.close()
    
    
    def _show_error_detection_file_selection(self, word_files: List[Path]) -> List[Path]:
        """
        エラー検知のためのファイル選択ダイアログを表示
        
        Args:
            word_files: 選択可能なWordファイルのリスト
        
        Returns:
            選択されたファイルのリスト
        """
        import time
        from PyQt6.QtCore import QCoreApplication
        
        self.selected_files_for_error_detection = None
        
        # シグナルを発行してファイル選択ダイアログ表示を要求
        self.error_file_selection_needed.emit(word_files, self.on_error_files_selected)
        
        # 結果を待機（最大60秒）
        timeout = 60
        start_time = time.time()
        while self.selected_files_for_error_detection is None and (time.time() - start_time) < timeout:
            time.sleep(0.1)
            # GUIイベントループを処理
            QCoreApplication.processEvents()
        
        if self.selected_files_for_error_detection is None:
            self.emit_log("ファイル選択がタイムアウトしました", "ERROR")
            return []
        
        return self.selected_files_for_error_detection
    
    def on_error_files_selected(self, selected_files: List[Path]):
        """エラー検知用ファイル選択の結果を受信"""
        self.selected_files_for_error_detection = selected_files
        self.emit_log(f"エラー検知ファイル選択結果: {len(selected_files)}個のファイルを選択", "INFO")
    
    def _collect_batch_emails(self, files: List[Path], email_monitor: EmailMonitorEnhanced, 
                            upload_start_time: datetime = None) -> Dict[str, str]:
        """
        バッチ内のすべてのファイルに対応するメールを収集
        
        Args:
            files: アップロードしたファイルのリスト
            email_monitor: メール監視オブジェクト
            upload_start_time: アップロード開始時刻（この時刻以降のメールのみ取得）
            
        Returns:
            {ファイル名: URL}の辞書
        """
        import time
        from datetime import datetime, timedelta
        
        file_url_map = {}
        start_time = datetime.now()
        timeout = 1200  # 20分
        check_interval = 30
        collected_count = 0
        uploaded_filenames = [f.name for f in files]
        
        self.emit_log(f"バッチ内の{len(files)}個のファイルのメールを収集中...", "INFO")
        self.emit_log(f"対象ファイル: {', '.join(uploaded_filenames)}", "DEBUG")
        # 日本時間に変換して表示
        from zoneinfo import ZoneInfo
        jst_time = upload_start_time.astimezone(ZoneInfo('Asia/Tokyo'))
        self.emit_log(f"アップロード時刻: {upload_start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC", "INFO")
        self.emit_log(f"アップロード時刻(JST): {jst_time.strftime('%Y-%m-%d %H:%M:%S')} JST", "INFO")
        self.emit_log(f"メール検索開始時刻: {upload_start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC (アップロード時刻以降)", "INFO")
        
        # すべてのファイルのメールが見つかるまで待機
        while collected_count < len(files) and (datetime.now() - start_time).seconds < timeout:
            # 新しいメールをチェック（エラーファイル検知用）
            # アップロード時刻以降のメールのみを取得
            result = email_monitor.wait_for_email(
                subject_pattern="ダウンロード用URLのご案内",
                timeout=check_interval,
                check_interval=5,
                return_with_filename=True,
                since_time=upload_start_time,
                purpose='error_check'  # PDF URLを取得
            )
            
            if result:
                if isinstance(result, tuple):
                    url, filename = result
                    # アップロードしたファイルのメールかチェック
                    if filename and filename in uploaded_filenames:
                        if filename not in file_url_map:
                            # purpose='error_check'を指定しているので、PDF URLが返される
                            file_url_map[filename] = url
                            collected_count += 1
                            # メール時刻情報も表示（デバッグ用）
                            self.emit_log(f"  ✓ メール検出: {filename} ({collected_count}/{len(files)})", "INFO")
                            # アップロードとメール検出の時間差を計算
                            time_diff = (datetime.now(timezone.utc) - upload_start_time).total_seconds()
                            self.emit_log(f"     アップロードからの経過時間: {int(time_diff)}秒", "DEBUG")
                        else:
                            self.emit_log(f"  - 既に検出済み: {filename}", "DEBUG")
                    elif filename:
                        # アップロードしていないファイルのメール
                        self.emit_log(f"  - 対象外のファイル: {filename} (今回アップロードしていません)", "WARNING")
                    else:
                        # ファイル名が検出できない場合
                        self.logger.warning("メールからファイル名を検出できませんでした")
                else:
                    # 互換性のため、タプルでない場合も処理
                    self.logger.warning("メールからファイル名情報を取得できませんでした")
            
            # すべて収集できたら終了
            if collected_count >= len(files):
                break
            
            # まだ収集できていない場合は少し待つ
            if collected_count < len(files):
                time.sleep(5)
        
        # 収集結果を報告
        if collected_count < len(files):
            missing_files = [f.name for f in files if f.name not in file_url_map]
            self.emit_log(f"警告: {len(missing_files)}個のファイルのメールが見つかりませんでした", "WARNING")
            for mf in missing_files:
                self.emit_log(f"  - {mf}", "WARNING")
        
        return file_url_map