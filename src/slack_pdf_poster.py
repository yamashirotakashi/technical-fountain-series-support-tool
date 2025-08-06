#!/usr/bin/env python3
"""
Slack PDF投稿機能の実装
仕様書に基づいた品質重視の実装
"""
from __future__ import annotations

import os
import re
import logging
import yaml
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from datetime import datetime

from src.slack_integration import SlackIntegration
from utils.logger import get_logger
from core.config_manager import ConfigManager, get_config_manager
from core.hardcoding_detector import HardcodingDetector

logger = get_logger(__name__)


class SlackPDFPoster:
    """
    Slack PDF投稿機能のメインクラス
    
    責務:
    - N番号からチャネル番号の抽出
    - Slackチャネルの検索
    - PDFファイルの検出
    - Slack投稿の実行
    """
    
    def __init__(self, slack_token: Optional[str] = None, config_manager: Optional[ConfigManager] = None):
        """
        初期化
        
        Args:
            slack_token: Slack Bot Token（省略時は環境変数から取得）
            config_manager: 設定管理インスタンス（省略時は新規作成）
        """
        self.config_manager = config_manager or ConfigManager()
        self.slack_integration = SlackIntegration(slack_token)
        logger.info("SlackPDFPoster initialized with ConfigManager")
    
    def extract_channel_number(self, n_code: str) -> str:
        """
        N番号から下4桁を抽出
        
        Args:
            n_code: N番号（例: N01234, n01234）
            
        Returns:
            4桁の数字文字列（例: "1234"）
            
        Raises:
            ValueError: N番号が不正な形式の場合
        """
        if not n_code:
            raise ValueError("N番号が空です")
        
        # 大文字小文字を正規化
        n_code = n_code.upper()
        
        # N番号の形式をチェック（Nまたはnで始まり、その後に数字）
        pattern = self.config_manager.get("validation.n_code_pattern", r'^N(\d+)$')
        match = re.match(pattern, n_code)
        
        if not match:
            raise ValueError(f"不正なN番号形式: {n_code}")
        
        digits = match.group(1)
        
        min_digits = self.config_manager.get("validation.min_n_code_digits", 4)
        if len(digits) < min_digits:
            raise ValueError(f"N番号の数字部分が{min_digits}桁未満です: {n_code}")
        
        # 下n桁を抽出
        extract_digits = self.config_manager.get("validation.extract_n_code_digits", 4)
        channel_number = digits[-extract_digits:]
        logger.debug(f"Extracted channel number: {channel_number} from {n_code}")
        
        return channel_number
    
    def find_slack_channel(self, channel_number: str) -> Optional[str]:
        """
        NコードまたはNコードの4桁番号からSlackチャネルを検索
        
        Args:
            channel_number: NコードまたはNコードの4桁番号 (例: "N01798" または "1798")
            
        Returns:
            チャネル名（見つからない場合はNone）
        """
        try:
            # Nコードから4桁番号を抽出
            import re
            digit_pattern = self.config_manager.get("validation.channel_digit_pattern", r'\d{4,5}')
            match = re.search(digit_pattern, channel_number)
            if match:
                # 4桁または5桁の数字を抽出（N01798なら01798、最後の4桁1798を使用）
                extracted_number = match.group()
                if len(extracted_number) == 5:
                    # 01798の場合、末尾4桁を使用
                    extracted_number = extracted_number[-4:]
                search_number = extracted_number
                logger.info(f"Extracted number '{search_number}' from input '{channel_number}'")
            else:
                # 数字が見つからない場合はそのまま使用
                search_number = channel_number
                logger.warning(f"No digits found in '{channel_number}', using as-is")
            
            # Botが参加しているチャネル一覧を取得
            channels = self.slack_integration.get_bot_channels()
            
            # 複数のパターンでチャネルを検索（優先度順）
            # 1. n{4桁}-* (従来パターン)
            # 2. {4桁}-* (数字のみパターン)
            # 3. *-{4桁}-* (中間に数字があるパターン)
            # 4. *{4桁}* (数字を含む任意のパターン)
            
            # 検索パターンを設定から取得
            default_patterns = [
                ("n{number}-", "starts"),      # n1234-xxx (前方一致)
                ("{number}-", "starts"),       # 1234-xxx (前方一致)
                ("-{number}-", "contains"),    # xxx-1234-xxx (部分一致)
                ("{number}", "contains")       # 1234を含む任意のパターン
            ]
            search_patterns = []
            pattern_configs = self.config_manager.get("slack.channel_search_patterns", default_patterns)
            
            for pattern_template, match_type in pattern_configs:
                pattern = pattern_template.format(number=search_number)
                search_patterns.append((pattern, match_type))
            
            # 各パターンで検索（優先度順）
            for pattern, match_type in search_patterns:
                for channel in channels:
                    channel_name = channel.get('name', '')
                    
                    if match_type == "starts" and channel_name.startswith(pattern):
                        logger.info(f"Found channel: {channel_name} for input: {channel_number} (extracted: {search_number}, starts with: {pattern})")
                        return channel_name
                    elif match_type == "contains" and pattern in channel_name:
                        logger.info(f"Found channel: {channel_name} for input: {channel_number} (extracted: {search_number}, contains: {pattern})")
                        return channel_name
            
            # 見つからない場合
            logger.warning(f"No channel found for input: {channel_number} (extracted: {search_number})")
            return None
            
        except Exception as e:
            logger.error(f"Error finding channel: {e}")
            return None
    
    def find_ncode_folder(self, ncode: str) -> Optional[Path]:
        """
        指定されたNコードのフォルダをNP-IRD配下から検索
        
        Args:
            ncode: 検索するNコード（例: N01798）
            
        Returns:
            見つかったNフォルダのパス、見つからない場合はNone
        """
        try:
            # NP-IRD配下のパス（ConfigManagerから取得）
            base_path_str = self.config_manager.get("paths.base_repository_path")
            if not base_path_str:
                logger.error("Base repository path not configured")
                return None
                
            base_path = Path(base_path_str)
            ncode_folder = base_path / ncode
            
            if ncode_folder.exists() and ncode_folder.is_dir():
                logger.info(f"Nフォルダ発見: {ncode_folder}")
                return ncode_folder
            else:
                logger.warning(f"Nフォルダが見つかりません: {ncode_folder}")
                return None
                
        except Exception as e:
            logger.error(f"Error finding N-code folder: {e}")
            return None
    
    def find_pdf_file(self, ncode: str) -> Optional[str]:
        """
        NコードからPDFファイルを検出
        
        Args:
            ncode: Nコード（例: N01798）
            
        Returns:
            PDFファイルのパス（見つからない場合はNone）
        """
        try:
            # Nフォルダを検索
            n_folder = self.find_ncode_folder(ncode)
            if not n_folder:
                return None
            
            # outフォルダを探す
            out_folder = n_folder / "out"
            if not out_folder.exists():
                logger.warning(f"'out' folder not found in: {n_folder}")
                return None
            
            # PDFファイルを検索
            pdf_files = list(out_folder.glob("*.pdf"))
            
            if not pdf_files:
                logger.warning(f"No PDF files found in: {out_folder}")
                return None
            
            # 複数ある場合は最新のものを選択
            if len(pdf_files) > 1:
                # 更新時刻でソート（降順）
                pdf_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                logger.info(f"Multiple PDFs found, selecting latest: {pdf_files[0]}")
            
            pdf_path = str(pdf_files[0])
            logger.info(f"Found PDF: {pdf_path}")
            
            return pdf_path
            
        except Exception as e:
            logger.error(f"Error finding PDF file: {e}")
            return None
    
    def get_default_message(self) -> str:
        """
        デフォルトの投稿メッセージを取得
        
        Returns:
            デフォルトメッセージ
        """
        return self.config_manager.get("slack.default_message", "修正後のPDFです。ご確認よろしくおねがいします。")
    
    def post_to_slack(self, pdf_path: str, channel: str, message: str) -> Tuple[bool, str]:
        """
        SlackにPDFを投稿
        
        Args:
            pdf_path: PDFファイルのパス
            channel: 投稿先チャネル名
            message: 投稿メッセージ
            
        Returns:
            (成功/失敗, エラーメッセージまたは成功時のURL)
        """
        try:
            # ファイル名を取得（パスから）
            pdf_filename = os.path.basename(pdf_path)
            
            # 投稿実行
            result = self.slack_integration.post_pdf_to_channel(
                pdf_path=pdf_path,
                repo_name=channel,  # チャネル名をrepo_nameとして使用
                message_template=message,
                book_title=pdf_filename
            )
            
            if result['success']:
                logger.info(f"Successfully posted to {channel}")
                return True, result.get('permalink', 'Success')
            else:
                error_msg = result.get('error', 'Unknown error')
                instruction = result.get('instruction', '')
                
                if instruction:
                    error_msg = f"{error_msg}\n\n{instruction}"
                
                logger.error(f"Failed to post: {error_msg}")
                return False, error_msg
                
        except Exception as e:
            error_msg = f"投稿中にエラーが発生しました: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def validate_inputs(self, n_code: str) -> Tuple[bool, str]:
        """
        入力値の検証
        
        Args:
            n_code: N番号
            
        Returns:
            (検証成功/失敗, エラーメッセージ)
        """
        try:
            # N番号の検証
            if not n_code or not n_code.strip():
                return False, self.config_manager.get("validation.empty_n_code_message", "N番号を入力してください")
            
            # 形式チェック
            self.extract_channel_number(n_code)
            
            return True, ""
            
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, self.config_manager.get("validation.error_prefix", "入力検証エラー") + f": {str(e)}"




# HardcodingDetectorクラスは core/hardcoding_detector.py に移動済み

# ConfigManagerクラスは core/config_manager.py に移動済み
# このクラスは削除済み - インポート文で利用してください

# get_config_manager関数は core/config_manager.py からインポート済み

class ProcessMode:
    """処理モード定数クラス"""
    INTERACTIVE = "interactive"      # 対話モード - GUI確認ダイアログ表示
    AUTOMATED = "automated"         # 自動モード - 完全自動実行
    PARAMETERIZED = "parameterized" # パラメータ駆動モード - 事前設定による実行

class ModeHandler:
    """
    モード処理の統一ハンドラー
    全APIで共通のモード処理ロジックを提供
    """
    
    def __init__(self, logger):
        self.logger = logger
        
    def handle_interactive_mode(self, operation_name: str, params: Dict[str, Any]) -> bool:
        """
        対話モード処理
        
        Args:
            operation_name: 操作名（例: "PDF Slack投稿"）
            params: 操作パラメータ
            
        Returns:
            True: 実行継続, False: 実行中止
        """
        try:
            # 対話モードの場合、確認ダイアログを表示
            self.logger.info(f"=== {operation_name} 確認 ===")
            self.logger.info("以下の内容で実行します:")
            
            for key, value in params.items():
                self.logger.info(f"  {key}: {value}")
            
            # 実際のGUI実装では、ここでQMessageBoxなどの確認ダイアログを表示
            # 現在はログベースの確認（本来はユーザー入力を待つ）
            self.logger.info("対話モード: 実行を継続します")
            return True
            
        except Exception as e:
            self.logger.error(f"対話モード処理エラー: {e}")
            return False
    
    def handle_parameterized_mode(self, default_params: Dict[str, Any], 
                                 override_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        パラメータ駆動モード処理
        
        Args:
            default_params: デフォルトパラメータ
            override_params: 上書きパラメータ
            
        Returns:
            最終パラメータセット
        """
        final_params = default_params.copy()
        
        if override_params:
            final_params.update(override_params)
            self.logger.info(f"パラメータ上書き適用: {list(override_params.keys())}")
        
        self.logger.info("パラメータ駆動モード: 設定済みパラメータで実行")
        return final_params
    
    def validate_mode(self, mode: str) -> bool:
        """
        モード値の検証
        
        Args:
            mode: 検証するモード
            
        Returns:
            True: 有効, False: 無効
        """
        valid_modes = [ProcessMode.INTERACTIVE, ProcessMode.AUTOMATED, ProcessMode.PARAMETERIZED]
        return mode in valid_modes

class SlackPostAPI:
    """
    PDF Slack投稿API - 外部呼び出し用統一インターフェース
    
    機能:
    - N-codeによるPDF自動投稿
    - 複数N-codeの一括処理
    - 対話モード/自動モードの切り替え
    - カスタムメッセージ対応
    """
    
    def __init__(self, slack_token: Optional[str] = None):
        """
        初期化
        
        Args:
            slack_token: Slack Bot Token（省略時は環境変数から取得）
        """
        self.poster = SlackPDFPoster(slack_token)
        self.config_manager = self.poster.config_manager  # ConfigManagerへの参照を追加
        self.logger = get_logger(__name__)
        
    def post_pdf_by_ncode(self, 
                         n_code: str,
                         mode: str = ProcessMode.AUTOMATED,
                         message: Optional[str] = None,
                         channel_override: Optional[str] = None,
                         **mode_params) -> Dict[str, Any]:
        """
        N-codeによるPDF Slack投稿 - メイン API エントリポイント
        
        Args:
            n_code: N-code（例: "N01798"）
            mode: 処理モード (ProcessMode.INTERACTIVE, AUTOMATED, PARAMETERIZED)
            message: カスタムメッセージ（省略時はデフォルト）
            channel_override: チャネル名の強制指定
            **mode_params: モード固有パラメータ
                - interactive_timeout: 対話タイムアウト（秒）
                - confirm_before_post: 投稿前確認（bool）
                - retry_on_failure: 失敗時リトライ（bool）
                - custom_notification: カスタム通知設定（dict）
            
        Returns:
            {
                "success": bool,
                "n_code": str,
                "channel": str,
                "pdf_path": str,
                "slack_url": str,  # 投稿成功時のURL
                "message": str,
                "mode": str,       # 実行されたモード
                "errors": List[str],
                "warnings": List[str],
                "processing_time": float,
                "interaction_log": List[str]  # 対話モード時のログ
            }
        """
        import time
        start_time = time.time()
        
        # 統一モードハンドラー初期化
        mode_handler = ModeHandler(self.logger)
        
        result = {
            "success": False,
            "n_code": n_code,
            "channel": "",
            "pdf_path": "",
            "slack_url": "",
            "message": message or self.poster.get_default_message(),
            "mode": mode,
            "errors": [],
            "warnings": [],
            "processing_time": 0.0,
            "interaction_log": []
        }
        
        try:
            self.logger.info(f"PDF Slack投稿API開始: {n_code} (mode: {mode})")
            
            # 1. モード検証
            if not mode_handler.validate_mode(mode):
                result["errors"].append(f"無効なモード: {mode}")
                return result
            
            # 2. 入力検証
            is_valid, error_msg = self.poster.validate_inputs(n_code)
            if not is_valid:
                result["errors"].append(error_msg)
                return result
            
            # 3. パラメータ駆動モード処理
            if mode == ProcessMode.PARAMETERIZED:
                default_params = {
                    "confirm_before_post": False,
                    "retry_on_failure": True,
                    "custom_notification": None
                }
                final_params = mode_handler.handle_parameterized_mode(default_params, mode_params)
                confirm_before_post = final_params.get("confirm_before_post", False)
                retry_on_failure = final_params.get("retry_on_failure", True)
            else:
                confirm_before_post = mode_params.get("confirm_before_post", mode == ProcessMode.INTERACTIVE)
                retry_on_failure = mode_params.get("retry_on_failure", True)
            
            # 4. チャネル検索
            if channel_override:
                channel = channel_override
                self.logger.info(f"チャネル強制指定: {channel}")
                result["interaction_log"].append(f"チャネル指定: {channel}")
            else:
                # N-codeから4桁番号を抽出してチャネル検索
                try:
                    channel_number = self.poster.extract_channel_number(n_code)
                    channel = self.poster.find_slack_channel(channel_number)
                    result["interaction_log"].append(f"チャネル自動検索: {channel_number} -> {channel}")
                except Exception as e:
                    result["errors"].append(f"チャネル検索エラー: {str(e)}")
                    return result
                
                if not channel:
                    result["errors"].append(f"該当するSlackチャネルが見つかりません: {n_code}")
                    return result
            
            result["channel"] = channel
            
            # 5. PDF検索
            pdf_path = self.poster.find_pdf_file(n_code)
            if not pdf_path:
                result["errors"].append(f"PDFファイルが見つかりません: {n_code}")
                return result
            
            result["pdf_path"] = pdf_path
            result["interaction_log"].append(f"PDF検出: {pdf_path}")
            
            # 6. 対話モード処理
            if mode == ProcessMode.INTERACTIVE or confirm_before_post:
                operation_params = {
                    "N-code": n_code,
                    "チャネル": channel,
                    "PDFファイル": pdf_path,
                    "メッセージ": result["message"]
                }
                
                should_continue = mode_handler.handle_interactive_mode("PDF Slack投稿", operation_params)
                result["interaction_log"].append(f"対話確認: {'承認' if should_continue else '中止'}")
                
                if not should_continue:
                    result["warnings"].append("ユーザーにより処理が中止されました")
                    return result
            
            # 7. Slack投稿実行（リトライ機能付き）
            max_retries = 3 if retry_on_failure else 1
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    success, slack_result = self.poster.post_to_slack(
                        pdf_path=pdf_path,
                        channel=channel,
                        message=result["message"]
                    )
                    
                    if success:
                        result["success"] = True
                        result["slack_url"] = slack_result
                        result["interaction_log"].append(f"投稿成功 (試行 {attempt + 1}/{max_retries})")
                        self.logger.info(f"投稿成功: {channel}")
                        break
                    else:
                        last_error = slack_result
                        result["interaction_log"].append(f"投稿失敗 (試行 {attempt + 1}/{max_retries}): {slack_result}")
                        if attempt < max_retries - 1:
                            retry_delay = self.config_manager.get("api.slack.rate_limit_delay", 2.0)
                            time.sleep(retry_delay)  # リトライ前の待機
                
                except Exception as e:
                    last_error = str(e)
                    result["interaction_log"].append(f"投稿エラー (試行 {attempt + 1}/{max_retries}): {str(e)}")
                    if attempt < max_retries - 1:
                        retry_delay = self.config_manager.get("api.slack.rate_limit_delay", 2.0)
                        time.sleep(retry_delay)
            
            if not result["success"]:
                result["errors"].append(f"投稿失敗 ({max_retries}回試行): {last_error}")
            
            # 8. カスタム通知処理（パラメータ駆動モード）
            if mode == ProcessMode.PARAMETERIZED and mode_params.get("custom_notification"):
                notification_config = mode_params["custom_notification"]
                self._handle_custom_notification(result, notification_config)
                
        except Exception as e:
            error_msg = f"予期しないエラー: {str(e)}"
            result["errors"].append(error_msg)
            result["interaction_log"].append(f"システムエラー: {error_msg}")
            self.logger.error(error_msg, exc_info=True)
        
        finally:
            result["processing_time"] = time.time() - start_time
            
        return result
    
    def post_multiple(self, 
                     n_codes: List[str],
                     mode: str = "automated",
                     message_template: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        複数N-codeの一括投稿
        
        Args:
            n_codes: N-codeリスト
            mode: 処理モード
            message_template: メッセージテンプレート
            
        Returns:
            各N-codeの処理結果リスト
        """
        results = []
        
        self.logger.info(f"一括投稿開始: {len(n_codes)}件")
        
        for i, n_code in enumerate(n_codes, 1):
            self.logger.info(f"処理中 ({i}/{len(n_codes)}): {n_code}")
            
            result = self.post_pdf_by_ncode(
                n_code=n_code,
                mode=mode,
                message=message_template
            )
            
            results.append(result)
            
            # 成功/失敗ログ
            if result["success"]:
                self.logger.info(f"✓ {n_code}: 投稿成功 -> {result['channel']}")
            else:
                self.logger.error(f"✗ {n_code}: 投稿失敗 -> {', '.join(result['errors'])}")
        
        # サマリー
        success_count = sum(1 for r in results if r["success"])
        self.logger.info(f"一括投稿完了: {success_count}/{len(n_codes)} 成功")
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """
        API状態確認
        
        Returns:
            API状態情報
        """
        try:
            # Slack接続テスト
            channels = self.poster.slack_integration.get_bot_channels()
            
            return {
                "api_status": "healthy",
                "slack_connected": True,
                "available_channels": len(channels),
                "bot_info": "TechZip PDF Poster API"
            }
        except Exception as e:
            return {
                "api_status": "error",
                "slack_connected": False,
                "error": str(e),
                "bot_info": "TechZip PDF Poster API"
            }

    def _handle_custom_notification(self, result: Dict[str, Any], notification_config: Dict[str, Any]):
        """
        カスタム通知処理（パラメータ駆動モード用）
        
        Args:
            result: 処理結果
            notification_config: 通知設定
        """
        try:
            if notification_config.get("log_to_file"):
                # ファイルログ出力
                log_file = notification_config.get("log_file", "slack_post_log.txt")
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"{result['n_code']}: {'成功' if result['success'] else '失敗'}\n")
            
            if notification_config.get("email_notification"):
                # メール通知（実装例）
                self.logger.info(f"メール通知: {result['n_code']} 投稿完了")
            
            if notification_config.get("webhook_url"):
                # Webhook通知（実装例）
                webhook_url = notification_config["webhook_url"]
                self.logger.info(f"Webhook通知: {webhook_url}")
                
        except Exception as e:
            self.logger.error(f"カスタム通知エラー: {e}")
    
    def post_multiple_enhanced(self, 
                             n_codes: List[str],
                             mode: str = ProcessMode.AUTOMATED,
                             message_template: Optional[str] = None,
                             batch_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        拡張複数N-code一括投稿 - 全モード対応
        
        Args:
            n_codes: N-codeリスト
            mode: 処理モード
            message_template: メッセージテンプレート
            batch_config: バッチ処理設定
                - batch_size: バッチサイズ（デフォルト: 5）
                - delay_between_batches: バッチ間待機時間（秒）
                - stop_on_error: エラー時停止（bool）
                - progress_callback: 進捗コールバック関数
                
        Returns:
            {
                "success": bool,
                "mode": str,
                "total_count": int,
                "success_count": int,
                "error_count": int,
                "results": List[Dict],
                "summary": Dict[str, Any],
                "processing_time": float
            }
        """
        import time
        start_time = time.time()
        
        mode_handler = ModeHandler(self.logger)
        
        # デフォルトバッチ設定
        default_batch_config = {
            "batch_size": 5,
            "delay_between_batches": 1.0,
            "stop_on_error": False,
            "progress_callback": None
        }
        
        if batch_config:
            default_batch_config.update(batch_config)
        
        batch_config = default_batch_config
        
        result = {
            "success": False,
            "mode": mode,
            "total_count": len(n_codes),
            "success_count": 0,
            "error_count": 0,
            "results": [],
            "summary": {"batches": [], "errors": [], "warnings": []},
            "processing_time": 0.0
        }
        
        try:
            self.logger.info(f"拡張一括投稿開始: {len(n_codes)}件 (mode: {mode})")
            
            # 対話モード - 一括処理確認
            if mode == ProcessMode.INTERACTIVE:
                operation_params = {
                    "処理件数": len(n_codes),
                    "N-codeリスト": ", ".join(n_codes[:5]) + ("..." if len(n_codes) > 5 else ""),
                    "バッチサイズ": batch_config["batch_size"],
                    "モード": mode
                }
                
                should_continue = mode_handler.handle_interactive_mode("一括PDF投稿", operation_params)
                if not should_continue:
                    result["summary"]["warnings"].append("ユーザーにより一括処理が中止されました")
                    return result
            
            # バッチ処理実行
            batch_size = batch_config["batch_size"]
            total_batches = (len(n_codes) + batch_size - 1) // batch_size
            
            for batch_idx in range(0, len(n_codes), batch_size):
                batch_n_codes = n_codes[batch_idx:batch_idx + batch_size]
                current_batch = batch_idx // batch_size + 1
                
                self.logger.info(f"バッチ {current_batch}/{total_batches} 処理中: {len(batch_n_codes)}件")
                
                batch_results = []
                batch_success_count = 0
                
                for i, n_code in enumerate(batch_n_codes):
                    try:
                        # 個別投稿実行
                        post_result = self.post_pdf_by_ncode(
                            n_code=n_code,
                            mode=ProcessMode.AUTOMATED,  # バッチ内は自動実行
                            message=message_template
                        )
                        
                        batch_results.append(post_result)
                        result["results"].append(post_result)
                        
                        if post_result["success"]:
                            batch_success_count += 1
                            result["success_count"] += 1
                            self.logger.info(f"✓ [{current_batch}-{i+1}] {n_code}: 投稿成功")
                        else:
                            result["error_count"] += 1
                            error_msg = ", ".join(post_result["errors"])
                            self.logger.error(f"✗ [{current_batch}-{i+1}] {n_code}: {error_msg}")
                            
                            # エラー時停止チェック
                            if batch_config["stop_on_error"]:
                                result["summary"]["errors"].append(f"エラーにより処理停止: {n_code}")
                                break
                        
                        # 進捗コールバック
                        if batch_config["progress_callback"]:
                            batch_config["progress_callback"](
                                current=batch_idx + i + 1,
                                total=len(n_codes),
                                batch=current_batch,
                                n_code=n_code,
                                success=post_result["success"]
                            )
                    
                    except Exception as e:
                        error_msg = f"バッチ処理エラー [{current_batch}-{i+1}] {n_code}: {str(e)}"
                        result["summary"]["errors"].append(error_msg)
                        self.logger.error(error_msg)
                        result["error_count"] += 1
                        
                        if batch_config["stop_on_error"]:
                            break
                
                # バッチサマリー
                batch_summary = {
                    "batch_number": current_batch,
                    "total_in_batch": len(batch_n_codes),
                    "success_in_batch": batch_success_count,
                    "error_in_batch": len(batch_n_codes) - batch_success_count
                }
                result["summary"]["batches"].append(batch_summary)
                
                # バッチ間待機
                if current_batch < total_batches and batch_config["delay_between_batches"] > 0:
                    time.sleep(batch_config["delay_between_batches"])
            
            # 全体結果評価
            result["success"] = result["success_count"] > 0
            success_rate = (result["success_count"] / result["total_count"] * 100) if result["total_count"] > 0 else 0
            
            self.logger.info(f"拡張一括投稿完了: {result['success_count']}/{result['total_count']} 成功 ({success_rate:.1f}%)")
            
        except Exception as e:
            error_msg = f"拡張一括投稿エラー: {str(e)}"
            result["summary"]["errors"].append(error_msg)
            self.logger.error(error_msg, exc_info=True)
        
        finally:
            result["processing_time"] = time.time() - start_time
        
        return result
