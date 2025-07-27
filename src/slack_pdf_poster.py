#!/usr/bin/env python3
"""
Slack PDF投稿機能の実装
仕様書に基づいた品質重視の実装
"""
import os
import re
import logging
from pathlib import Path
from typing import Optional, Tuple, List
from datetime import datetime

from src.slack_integration import SlackIntegration
from utils.logger import get_logger

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
    
    def __init__(self, slack_token: Optional[str] = None):
        """
        初期化
        
        Args:
            slack_token: Slack Bot Token（省略時は環境変数から取得）
        """
        self.slack_integration = SlackIntegration(slack_token)
        logger.info("SlackPDFPoster initialized")
    
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
        pattern = r'^N(\d+)$'
        match = re.match(pattern, n_code)
        
        if not match:
            raise ValueError(f"不正なN番号形式: {n_code}")
        
        digits = match.group(1)
        
        if len(digits) < 4:
            raise ValueError(f"N番号の数字部分が4桁未満です: {n_code}")
        
        # 下4桁を抽出
        channel_number = digits[-4:]
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
            match = re.search(r'\d{4,5}', channel_number)
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
            
            search_patterns = [
                (f"n{search_number}-", "starts"),      # n1234-xxx (前方一致)
                (f"{search_number}-", "starts"),       # 1234-xxx (前方一致)
                (f"-{search_number}-", "contains"),    # xxx-1234-xxx (部分一致)
                (search_number, "contains")            # 1234を含む任意のパターン
            ]
            
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
            # NP-IRD配下のパス（word_processor.pyと同じロジック）
            base_path = Path("G:/.shortcut-targets-by-id/0B6euJ_grVeOeMnJLU1IyUWgxeWM/NP-IRD")
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
        return "修正後のPDFです。ご確認よろしくおねがいします。"
    
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
                return False, "N番号を入力してください"
            
            # 形式チェック
            self.extract_channel_number(n_code)
            
            return True, ""
            
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"入力検証エラー: {str(e)}"