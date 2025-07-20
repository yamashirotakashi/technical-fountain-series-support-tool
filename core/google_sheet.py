"""Google Sheets連携モジュール"""
import os
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
        self.sheet_id = self.config.get('google_sheet.sheet_id')
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
                'repository_name': リポジトリ名（C列）
            }
        """
        try:
            self.logger.info(f"Nコード検索開始: {n_code}")
            
            # A列とC列のデータを取得（1000行まで）
            range_name = 'A1:C1000'
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
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
                        
                        result_dict = {
                            'row': row_idx,
                            'n_code': n_code,
                            'repository_name': repository_name.strip()
                        }
                        
                        self.logger.info(f"Nコード {n_code} を行 {row_idx} で発見: {repository_name}")
                        return result_dict
            
            self.logger.warning(f"Nコード {n_code} が見つかりませんでした")
            return None
            
        except HttpError as e:
            self.logger.error(f"Google Sheets APIエラー: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Nコード検索中にエラーが発生: {e}")
            raise
    
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
            # スプレッドシートのメタデータを取得してテスト
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.sheet_id
            ).execute()
            
            sheet_title = sheet_metadata.get('properties', {}).get('title', 'Unknown')
            self.logger.info(f"スプレッドシートに接続成功: {sheet_title}")
            return True
            
        except Exception as e:
            self.logger.error(f"接続テストに失敗: {e}")
            return False