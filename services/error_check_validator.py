"""エラーチェックの成功・失敗判定を行うモジュール

エラーファイル検知のための判定ロジックを集約
"""
from typing import Tuple, Optional
import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path

from utils.logger import get_logger
from utils.config import get_config
from src.slack_pdf_poster import ConfigManager


class ErrorCheckValidator:
    """エラーチェックの判定を行うクラス"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.config_manager = config_manager or ConfigManager()
        
        # Basic認証情報をConfigManagerから取得
        nextpub_config = self.config_manager.get_api_config('nextpublishing')
        self.username = nextpub_config.get('username', 'ep_user')
        self.password = nextpub_config.get('password', 'Nn7eUTX5')
        self.auth = HTTPBasicAuth(self.username, self.password)
        
    def validate_pdf_url(self, pdf_url: str, filename: str = "") -> Tuple[bool, str]:
        """
        PDF URLをチェックして、エラーファイルかどうか判定
        
        Args:
            pdf_url: チェックするPDF URL
            filename: ファイル名（ログ用）
            
        Returns:
            (is_error, reason)
            - is_error: True=エラーファイル, False=正常ファイル
            - reason: 判定理由
        """
        try:
            self.logger.info(f"PDF URLチェック開始: {filename}")
            self.logger.debug(f"URL: {pdf_url}")
            
            # 1. URLが空の場合
            if not pdf_url:
                return True, "URLが空です"
            
            # 2. PDF URL形式チェック
            if 'do_download_pdf' not in pdf_url:
                self.logger.warning(f"PDF URLではありません: {pdf_url}")
                return True, "PDF URL形式ではありません"
            
            # 3. Basic認証付きでアクセス
            headers = {
                'User-Agent': 'TechnicalFountainTool/1.0',
                'Accept': 'application/pdf,text/html,*/*'
            }
            
            # タイムアウト値をConfigManagerから取得
            timeout = self.config_manager.get("api.nextpublishing.timeout", 30)
            response = requests.get(
                pdf_url, 
                auth=self.auth,
                headers=headers,
                timeout=timeout,
                allow_redirects=True
            )
            
            # 4. ステータスコードチェック
            if response.status_code == 401:
                return True, "認証エラー（401）"
            elif response.status_code == 404:
                return True, "ファイルが見つかりません（404）"
            elif response.status_code != 200:
                return True, f"HTTPエラー（{response.status_code}）"
            
            # 5. Content-Typeチェック
            content_type = response.headers.get('Content-Type', '').lower()
            
            # 6. ファイル内容チェック（デフォルト1000バイト、設定可能）
            content_check_size = self.config_manager.get("processing.content_check_size", 1000)
            content_start = response.content[:content_check_size] if response.content else b''
            
            # 6.1 PDFマジックナンバーチェック（正常）
            if content_start.startswith(b'%PDF'):
                self.logger.info(f"✓ 正常なPDFファイル: {filename}")
                return False, "正常なPDFファイル"
            
            # 6.2 明示的にPDF Content-Typeの場合（正常）
            if 'application/pdf' in content_type and len(response.content) > 100:
                self.logger.info(f"✓ 正常なPDFファイル（Content-Type判定）: {filename}")
                return False, "正常なPDFファイル（Content-Type判定）"
            
            # 6.3 HTMLエラーページチェック（エラー）
            if b'<html' in content_start.lower() or b'<!doctype' in content_start.lower():
                # HTMLの内容を確認
                try:
                    html_content = content_start.decode('utf-8', errors='ignore')
                    
                    # エラーページのキーワード
                    error_keywords = [
                        'ファイルの作成に失敗',
                        'エラーが発生',
                        'PDF生成エラー',
                        'conversion failed',
                        'error occurred'
                    ]
                    
                    for keyword in error_keywords:
                        if keyword in html_content:
                            self.logger.error(f"✗ エラーページ検出: {filename} - {keyword}")
                            return True, f"エラーページ（{keyword}）"
                    
                    # エラーキーワードがなくてもHTMLならエラー
                    self.logger.error(f"✗ HTMLページが返されました: {filename}")
                    return True, "HTMLページが返されました（PDF生成失敗）"
                    
                except Exception as e:
                    self.logger.error(f"HTMLデコードエラー: {e}")
                    return True, "不正なHTMLレスポンス"
            
            # 6.4 空のレスポンス（エラー）
            if len(response.content) == 0:
                self.logger.error(f"✗ 空のレスポンス: {filename}")
                return True, "空のレスポンス"
            
            # 6.5 その他の形式（エラー）
            self.logger.error(f"✗ 不明な形式: {filename}")
            self.logger.debug(f"Content-Type: {content_type}")
            self.logger.debug(f"Content先頭: {content_start[:50]}")
            return True, f"不明な形式（Content-Type: {content_type}）"
            
        except requests.exceptions.Timeout:
            self.logger.error(f"✗ タイムアウト: {filename}")
            return True, "タイムアウト"
        except requests.exceptions.ConnectionError:
            self.logger.error(f"✗ 接続エラー: {filename}")
            return True, "接続エラー"
        except Exception as e:
            self.logger.error(f"✗ 予期しないエラー: {filename} - {e}")
            return True, f"予期しないエラー: {str(e)}"
    
    def validate_batch(self, file_url_map: dict) -> Tuple[list, list]:
        """
        複数ファイルのバッチ検証
        
        Args:
            file_url_map: {ファイル名: PDF URL}の辞書
            
        Returns:
            (error_files, normal_files)
            - error_files: エラーファイルのリスト
            - normal_files: 正常ファイルのリスト
        """
        error_files = []
        normal_files = []
        
        for filename, pdf_url in file_url_map.items():
            is_error, reason = self.validate_pdf_url(pdf_url, filename)
            
            if is_error:
                error_files.append({
                    'filename': filename,
                    'url': pdf_url,
                    'reason': reason
                })
            else:
                normal_files.append({
                    'filename': filename,
                    'url': pdf_url,
                    'reason': reason
                })
        
        return error_files, normal_files

class ErrorDetectionAPI:
    """
    エラーファイル検知API - 外部呼び出し用統一インターフェース
    
    機能:
    - N-codeの処理状況チェック
    - 複数N-codeの継続監視（メール監視の代替）
    - PDF URL一括検証
    - リアルタイムステータス監視
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """初期化"""
        self.config_manager = config_manager or ConfigManager()
        self.validator = ErrorCheckValidator(self.config_manager)
        self.logger = get_logger(__name__)
        self.config = get_config()
        
    def check_n_code_status(self, 
                           n_code: str,
                           mode: str = "automated",
                           **mode_params) -> Dict[str, Any]:
        """
        N-codeの処理状況チェック - メイン API エントリポイント
        
        Args:
            n_code: チェック対象のN-code
            mode: 処理モード ("interactive", "automated", "parameterized")
            **mode_params: モード固有パラメータ
                - deep_analysis: 詳細分析実行（bool）
                - include_metadata: メタデータ詳細出力（bool）
                - auto_retry: 自動リトライ（bool）
                - timeout: タイムアウト時間（秒）
                
        Returns:
            {
                "success": bool,
                "n_code": str,
                "status": str,  # "processing", "completed", "error", "not_found"
                "pdf_url": Optional[str],
                "is_error": bool,
                "error_reason": Optional[str],
                "last_checked": str,  # ISO format timestamp
                "mode": str,
                "interaction_log": List[str],
                "metadata": Dict[str, Any]
            }
        """
        from datetime import datetime
        
        # 統一モードハンドラー（SlackPostAPIと同じクラスを使用）
        from src.slack_pdf_poster import ProcessMode, ModeHandler
        mode_handler = ModeHandler(self.logger)
        
        result = {
            "success": False,
            "n_code": n_code,
            "status": "not_found",
            "pdf_url": None,
            "is_error": False,
            "error_reason": None,
            "last_checked": datetime.now().isoformat(),
            "mode": mode,
            "interaction_log": [],
            "metadata": {}
        }
        
        try:
            self.logger.info(f"N-code状況チェック開始: {n_code} (mode: {mode})")
            
            # 1. モード検証
            if not mode_handler.validate_mode(mode):
                result["error_reason"] = f"無効なモード: {mode}"
                return result
            
            # 2. パラメータ駆動モード処理
            if mode == "parameterized":
                default_params = {
                    "deep_analysis": False,
                    "include_metadata": True,
                    "auto_retry": True,
                    "timeout": 30
                }
                final_params = mode_handler.handle_parameterized_mode(default_params, mode_params)
                deep_analysis = final_params.get("deep_analysis", False)
                include_metadata = final_params.get("include_metadata", True)
                auto_retry = final_params.get("auto_retry", True)
                timeout = final_params.get("timeout", 30)
            else:
                deep_analysis = mode_params.get("deep_analysis", mode == "interactive")
                include_metadata = mode_params.get("include_metadata", True)
                auto_retry = mode_params.get("auto_retry", True)
                timeout = mode_params.get("timeout", 30)
            
            # 3. 対話モード処理
            if mode == "interactive":
                operation_params = {
                    "N-code": n_code,
                    "詳細分析": "有効" if deep_analysis else "無効",
                    "メタデータ出力": "有効" if include_metadata else "無効",
                    "タイムアウト": f"{timeout}秒"
                }
                
                should_continue = mode_handler.handle_interactive_mode("エラー状況チェック", operation_params)
                result["interaction_log"].append(f"対話確認: {'承認' if should_continue else '中止'}")
                
                if not should_continue:
                    result["error_reason"] = "ユーザーにより処理が中止されました"
                    return result
            
            # 4. N-codeフォルダ存在確認
            n_folder = self._find_ncode_folder(n_code)
            if not n_folder:
                result["status"] = "not_found"
                result["error_reason"] = f"N-codeフォルダが見つかりません: {n_code}"
                result["interaction_log"].append("フォルダ検索: 見つからず")
                return result
            
            result["interaction_log"].append(f"フォルダ検出: {n_folder}")
            if include_metadata:
                result["metadata"]["folder_path"] = str(n_folder)
            
            # 5. Word ファイルの確認
            word_files = list(n_folder.glob("*.docx"))
            if not word_files:
                result["status"] = "not_found"
                result["error_reason"] = "Word ファイルが見つかりません"
                result["interaction_log"].append("Wordファイル検索: 見つからず")
                return result
            
            result["interaction_log"].append(f"Wordファイル検出: {len(word_files)}件")
            if include_metadata:
                result["metadata"]["word_files"] = [str(f) for f in word_files]
                if deep_analysis:
                    # 詳細分析: ファイルサイズ、更新日時など
                    word_analysis = []
                    for wf in word_files:
                        stat = wf.stat()
                        word_analysis.append({
                            "name": wf.name,
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                    result["metadata"]["word_files_detail"] = word_analysis
            
            # 6. 処理済みPDFの確認（リトライ機能付き）
            max_retries = 3 if auto_retry else 1
            pdf_found = False
            
            for attempt in range(max_retries):
                out_folder = n_folder / "out"
                pdf_files = list(out_folder.glob("*.pdf")) if out_folder.exists() else []
                
                if pdf_files:
                    pdf_found = True
                    break
                elif attempt < max_retries - 1:
                    result["interaction_log"].append(f"PDF検索リトライ {attempt + 1}/{max_retries}")
                    import time
                    # リトライ遅延をConfigManagerから取得
                    retry_delay = self.config_manager.get("processing.delay_between_batches", 2.0)
                    time.sleep(retry_delay)
            
            if pdf_found:
                # PDF が存在する場合
                latest_pdf = max(pdf_files, key=lambda p: p.stat().st_mtime)
                result["interaction_log"].append(f"PDF検出: {latest_pdf.name}")
                
                if include_metadata:
                    result["metadata"]["pdf_path"] = str(latest_pdf)
                    if deep_analysis:
                        stat = latest_pdf.stat()
                        result["metadata"]["pdf_detail"] = {
                            "name": latest_pdf.name,
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                        }
                
                # PDF URL を構築
                pdf_url = self._construct_pdf_url(n_code, latest_pdf.name)
                
                if pdf_url:
                    result["pdf_url"] = pdf_url
                    result["interaction_log"].append(f"PDF URL構築: 成功")
                    
                    # PDF の有効性を検証（タイムアウト付き）
                    try:
                        import signal
                        
                        def timeout_handler(signum, frame):
                            raise TimeoutError("PDF検証タイムアウト")
                        
                        signal.signal(signal.SIGALRM, timeout_handler)
                        signal.alarm(timeout)
                        
                        is_error, reason = self.validator.validate_pdf_url(pdf_url, latest_pdf.name)
                        
                        signal.alarm(0)  # タイムアウト解除
                        
                        if is_error:
                            result["status"] = "error"
                            result["is_error"] = True
                            result["error_reason"] = reason
                            result["interaction_log"].append(f"PDF検証: エラー - {reason}")
                        else:
                            result["status"] = "completed"
                            result["success"] = True
                            result["interaction_log"].append("PDF検証: 正常")
                            
                    except TimeoutError:
                        result["status"] = "error"
                        result["is_error"] = True
                        result["error_reason"] = f"PDF検証タイムアウト（{timeout}秒）"
                        result["interaction_log"].append(f"PDF検証: タイムアウト")
                        
                else:
                    result["status"] = "error"
                    result["is_error"] = True
                    result["error_reason"] = "PDF URL を構築できませんでした"
                    result["interaction_log"].append("PDF URL構築: 失敗")
            else:
                # PDF が存在しない場合は処理中とみなす
                result["status"] = "processing"
                result["success"] = True  # 処理中も正常状態
                result["interaction_log"].append("PDF状態: 処理中")
            
        except Exception as e:
            error_msg = f"状況チェック中にエラー: {str(e)}"
            result["error_reason"] = error_msg
            result["interaction_log"].append(f"システムエラー: {error_msg}")
            self.logger.error(error_msg, exc_info=True)
        
        return result
    
    def monitor_n_codes(self, 
                       n_codes: List[str],
                       check_interval: int = 300) -> Dict[str, Any]:
        """
        複数N-codeの継続監視（API版メール監視の代替）
        
        Args:
            n_codes: 監視対象N-codeリスト
            check_interval: チェック間隔（秒）
            
        Returns:
            {
                "monitoring_id": str,
                "n_codes": List[str],
                "results": List[Dict],
                "summary": {
                    "total": int,
                    "completed": int,
                    "errors": int,
                    "processing": int,
                    "not_found": int
                }
            }
        """
        import uuid
        from datetime import datetime
        
        monitoring_id = str(uuid.uuid4())[:8]
        
        self.logger.info(f"N-code監視開始: {len(n_codes)}件 (ID: {monitoring_id})")
        
        results = []
        summary = {
            "total": len(n_codes),
            "completed": 0,
            "errors": 0,
            "processing": 0,
            "not_found": 0
        }
        
        for n_code in n_codes:
            status_result = self.check_n_code_status(n_code)
            results.append(status_result)
            
            # サマリー更新
            status = status_result["status"]
            if status in summary:
                summary[status] += 1
            
            # ログ出力
            if status_result["success"]:
                self.logger.info(f"✓ {n_code}: {status}")
            else:
                self.logger.warning(f"✗ {n_code}: {status} - {status_result.get('error_reason', '')}")
        
        monitor_result = {
            "monitoring_id": monitoring_id,
            "n_codes": n_codes,
            "results": results,
            "summary": summary,
            "check_interval": check_interval,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"監視完了 (ID: {monitoring_id}): "
                        f"完了={summary['completed']}, エラー={summary['errors']}, "
                        f"処理中={summary['processing']}, 未発見={summary['not_found']}")
        
        return monitor_result
    
    def validate_pdf_urls(self, url_map: Dict[str, str]) -> Dict[str, Any]:
        """
        PDF URL一括検証（既存機能のAPI化）
        
        Args:
            url_map: {filename: pdf_url} のマッピング
            
        Returns:
            {
                "success": bool,
                "total_files": int,
                "error_files": List[Dict],
                "normal_files": List[Dict],
                "summary": {
                    "error_count": int,
                    "normal_count": int,
                    "error_rate": float
                }
            }
        """
        try:
            self.logger.info(f"PDF URL一括検証開始: {len(url_map)}件")
            
            error_files, normal_files = self.validator.validate_batch(url_map)
            
            error_count = len(error_files)
            normal_count = len(normal_files)
            total_count = error_count + normal_count
            error_rate = (error_count / total_count * 100) if total_count > 0 else 0
            
            result = {
                "success": True,
                "total_files": total_count,
                "error_files": error_files,
                "normal_files": normal_files,
                "summary": {
                    "error_count": error_count,
                    "normal_count": normal_count,
                    "error_rate": round(error_rate, 2)
                }
            }
            
            self.logger.info(f"検証完了: エラー={error_count}, 正常={normal_count}, "
                           f"エラー率={error_rate:.2f}%")
            
            return result
            
        except Exception as e:
            error_msg = f"PDF URL検証中にエラー: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            return {
                "success": False,
                "error": error_msg,
                "total_files": len(url_map),
                "error_files": [],
                "normal_files": [],
                "summary": {
                    "error_count": 0,
                    "normal_count": 0,
                    "error_rate": 0
                }
            }
    
    def _find_ncode_folder(self, n_code: str) -> Optional[Path]:
        """
        N-codeフォルダを検索
        
        Args:
            n_code: 検索するN-code
            
        Returns:
            見つかったN-codeフォルダのパス、見つからない場合はNone
        """
        try:
            # 基本パス（ConfigManagerから取得）
            base_path_str = self.config_manager.get("paths.base_repository_path")
            base_path = Path(base_path_str)
            n_folder = base_path / n_code
            
            if n_folder.exists() and n_folder.is_dir():
                return n_folder
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"N-codeフォルダ検索エラー: {e}")
            return None
    
    def _construct_pdf_url(self, n_code: str, pdf_filename: str) -> Optional[str]:
        """
        PDF URLを構築
        
        Args:
            n_code: N-code
            pdf_filename: PDFファイル名
            
        Returns:
            構築されたPDF URL、構築できない場合はNone
        """
        try:
            # 実際の変換サービスのURL構築ロジックに基づく
            # 注: 実際の実装では変換サービスの仕様に合わせる
            base_url = self.config_manager.get("api.nextpublishing.base_url", "http://trial.nextpublishing.jp/upload_46tate/")
            download_endpoint = self.config_manager.get("api.nextpublishing.download_endpoint", "do_download_pdf")
            full_url = f"{base_url.rstrip('/')}/{download_endpoint}"
            
            # URLパラメータを構築（実際のサービスに依存）
            # 例: http://trial.nextpublishing.jp/upload_46tate/do_download_pdf?file=example.pdf
            pdf_url = f"{full_url}?file={pdf_filename}"
            
            return pdf_url
            
        except Exception as e:
            self.logger.error(f"PDF URL構築エラー: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """
        API状態確認
        
        Returns:
            API状態情報
        """
        try:
            # 基本パス接続テスト（ConfigManagerから取得）
            base_path_str = self.config_manager.get("paths.base_repository_path")
            base_path = Path(base_path_str)
            base_accessible = base_path.exists()
            
            return {
                "api_status": "healthy" if base_accessible else "degraded",
                "base_path_accessible": base_accessible,
                "base_path": str(base_path),
                "validator_status": "ready",
                "api_info": "TechZip Error Detection API"
            }
        except Exception as e:
            return {
                "api_status": "error",
                "base_path_accessible": False,
                "error": str(e),
                "api_info": "TechZip Error Detection API"
            }
