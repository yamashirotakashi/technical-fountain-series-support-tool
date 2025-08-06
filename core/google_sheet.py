from __future__ import annotations
"""Google Sheets連携モジュール"""
import os
import time
import random
from typing import Optional, Dict, Any
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils.logger import get_logger
from utils.config import get_config


class GoogleSheetClient:
    """Google Sheetsとの連携を管理するクラス"""
    
    def __init__(self):
        """GoogleSheetClientを初期化"""
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.service = None
        
        # Sheet IDを取得（デバッグログ付き）
        self.sheet_id = self.config.get('google_sheet.sheet_id')
        self.logger.info(f"設定から取得したSheet ID: {self.sheet_id}")
        
        # Sheet IDが無効な場合のチェック
        if not self.sheet_id or self.sheet_id == "YOUR_SHEET_ID_HERE" or self.sheet_id == "your-sheet-id":
            self.logger.error(f"無効なSheet ID: {self.sheet_id}")
            raise ValueError("Google Sheet IDが設定されていません。設定画面から正しいSheet IDを設定してください。")
        
        self._authenticate()
    
    def _authenticate(self):
        """Google Sheets APIの認証を行う"""
        try:
            # 認証情報ファイルのパスを取得
            creds_path = self.config.get_credentials_path()
            if not creds_path or not creds_path.exists():
                raise FileNotFoundError(f"認証ファイルが見つかりません: {creds_path}")
            
            self.logger.info(f"認証ファイルを使用: {creds_path}")
            
            # サービスアカウントの認証情報を作成
            credentials = service_account.Credentials.from_service_account_file(
                str(creds_path),
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            
            # Google Sheets APIのサービスを構築
            self.service = build('sheets', 'v4', credentials=credentials)
            self.logger.info("Google Sheets APIの認証に成功しました")
            
        except Exception as e:
            self.logger.error(f"Google Sheets APIの認証に失敗: {e}")
            raise
    
    def search_n_code(self, n_code: str) -> Optional[Dict[str, Any]]:
        """
        NコードをA列から検索し、該当行の情報を取得
        
        Args:
            n_code: 検索するNコード
        
        Returns:
            見つかった場合は行の情報を含む辞書、見つからない場合はNone
            {
                'row': 行番号（1ベース）,
                'n_code': Nコード,
                'repository_name': リポジトリ名（C列）,
                'author_slack_id': 著者SlackID（J列）
            }
        """
        return self._execute_with_retry(self._search_n_code_impl, n_code)
    
    def _search_n_code_impl(self, n_code: str) -> Optional[Dict[str, Any]]:
        """
        Nコード検索の実装（リトライ対象）
        """
        self.logger.info(f"Nコード検索開始: {n_code}")
        
        # A列、C列、J列のデータを取得（1000行まで）
        range_name = 'A1:J1000'
        self.logger.debug(f"API呼び出し - Sheet ID: {self.sheet_id}, Range: {range_name}")
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
        except HttpError as e:
            self.logger.error(f"Google Sheets API エラー: {e}")
            self.logger.error(f"使用したSheet ID: {self.sheet_id}")
            raise
        
        values = result.get('values', [])
        
        if not values:
            self.logger.warning("スプレッドシートにデータがありません")
            return None
        
        # Nコードを検索
        for row_idx, row in enumerate(values, start=1):
            if row and len(row) > 0:
                # A列の値を確認
                cell_value = str(row[0]).strip().upper()
                if cell_value == n_code.upper():
                    # C列の値を取得（存在する場合）
                    repository_name = row[2] if len(row) > 2 else None
                    
                    if not repository_name:
                        self.logger.warning(f"行 {row_idx} のC列にリポジトリ名がありません")
                        return None
                    
                    # J列の値を取得（存在する場合）
                    author_slack_id = row[9] if len(row) > 9 else None
                    
                    result_dict = {
                        'row': row_idx,
                        'n_code': n_code,
                        'repository_name': repository_name.strip(),
                        'author_slack_id': author_slack_id.strip() if author_slack_id else None
                    }
                    
                    self.logger.info(f"Nコード {n_code} を行 {row_idx} で発見: {repository_name}")
                    if author_slack_id:
                        self.logger.info(f"著者SlackID: {author_slack_id}")
                    return result_dict
        
        self.logger.warning(f"Nコード {n_code} が見つかりませんでした")
        return None
    
    def _execute_with_retry(self, func, *args, max_retries: int = 3, **kwargs):
        """
        指数バックオフでリトライ実行
        
        Args:
            func: 実行する関数
            max_retries: 最大リトライ回数
            *args, **kwargs: 関数に渡す引数
        
        Returns:
            関数の実行結果
        """
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
                
            except HttpError as e:
                # リトライ可能なエラーかチェック
                if self._is_retryable_error(e) and attempt < max_retries:
                    # 指数バックオフで待機時間を計算（ジッターを追加）
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    self.logger.warning(
                        f"Google Sheets APIエラー (試行 {attempt + 1}/{max_retries + 1}): {e.resp.status} - "
                        f"{wait_time:.2f}秒後にリトライします"
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    # リトライ不可能なエラーまたは最大リトライ回数に達した場合
                    self.logger.error(f"Google Sheets APIエラー (最終): {e}")
                    raise
                    
            except Exception as e:
                # HttpError以外のエラーはリトライしない
                self.logger.error(f"予期しないエラー: {e}")
                raise
    
    def _is_retryable_error(self, error: HttpError) -> bool:
        """
        リトライ可能なエラーかどうかを判定
        
        Args:
            error: HttpErrorオブジェクト
        
        Returns:
            リトライ可能な場合True
        """
        # リトライ可能なHTTPステータスコード
        retryable_codes = {
            429,  # Too Many Requests
            500,  # Internal Server Error
            502,  # Bad Gateway
            503,  # Service Unavailable
            504,  # Gateway Timeout
        }
        
        status_code = error.resp.status if error.resp else None
        return status_code in retryable_codes
    
    def get_repository_name(self, n_code: str) -> Optional[str]:
        """
        Nコードからリポジトリ名を取得
        
        Args:
            n_code: Nコード
        
        Returns:
            リポジトリ名（見つからない場合はNone）
        """
        result = self.search_n_code(n_code)
        return result['repository_name'] if result else None
    
    def test_connection(self) -> bool:
        """
        Google Sheetsへの接続をテスト
        
        Returns:
            接続が成功した場合True
        """
        try:
            # リトライ機能付きで接続テストを実行
            sheet_metadata = self._execute_with_retry(
                lambda: self.service.spreadsheets().get(spreadsheetId=self.sheet_id).execute()
            )
            
            sheet_title = sheet_metadata.get('properties', {}).get('title', 'Unknown')
            self.logger.info(f"スプレッドシートに接続成功: {sheet_title}")
            return True
            
        except Exception as e:
            self.logger.error(f"接続テストに失敗: {e}")
            return False