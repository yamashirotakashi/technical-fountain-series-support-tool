"""
Google Sheets連携モジュール
発行計画シートと購入リストシートとの連携
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

class GoogleSheetsClient:
    """Google Sheets API クライアント"""
    
    def __init__(self, credentials_path: str):
        """
        Args:
            credentials_path: サービスアカウントJSONファイルのパス
        """
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.sheets = self.service.spreadsheets()
    
    async def get_project_info(self, sheet_id: str, n_code: str) -> Optional[Dict[str, Any]]:
        """
        発行計画シートからプロジェクト情報を取得
        
        Args:
            sheet_id: スプレッドシートID
            n_code: Nコード (例: N09999)
            
        Returns:
            プロジェクト情報の辞書、見つからない場合はNone
        """
        try:
            # シート名とレンジを指定
            range_name = '2020.10-!A:S'  # A列からS列まで
            
            result = self.sheets.values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            # ヘッダー行をスキップして検索
            for i, row in enumerate(values[1:], start=2):  # 2行目から開始
                if len(row) > 0 and row[0] == n_code:
                    # 列の対応
                    # A(0): Nコード, C(2): リポジトリ名, E(4): 書籍URL(転記先), H(7): 書籍名
                    # J(9): Slack ID, L(11): GitHub, S(18): メール
                    
                    return {
                        'n_code': row[0] if len(row) > 0 else None,
                        'repository_name': row[2] if len(row) > 2 else None,
                        'book_url': row[4] if len(row) > 4 else None,  # 既存の値
                        'book_title': row[7] if len(row) > 7 else None,  # H列: 書籍名
                        'slack_user_id': row[9] if len(row) > 9 else None,  # J列
                        'github_account': row[11] if len(row) > 11 else None,  # L列
                        'author_email': row[18] if len(row) > 18 else None,  # S列
                        'row_number': i  # 行番号（1ベース）
                    }
            
            logger.warning(f"N-code {n_code} not found in planning sheet")
            return None
            
        except HttpError as e:
            logger.error(f"Google Sheets API error: {e}")
            raise
    
    async def get_book_url_from_purchase_list(self, sheet_id: str, n_code: str) -> Optional[str]:
        """
        購入リストシートから書籍URLを取得
        
        Args:
            sheet_id: 購入リストシートのID
            n_code: Nコード
            
        Returns:
            書籍URL、見つからない場合はNone
        """
        try:
            # 全データを取得（シート名は指定しない）
            range_name = 'A:M'  # A列からM列（Nコード）まで
            
            result = self.sheets.values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            # ヘッダー行をスキップして検索
            for row in values[1:]:
                # M列（インデックス12）にNコードがある
                if len(row) > 12 and row[12] == n_code:
                    # D列（インデックス3）のURLを返す
                    return row[3] if len(row) > 3 else None
            
            logger.warning(f"N-code {n_code} not found in purchase list")
            return None
            
        except HttpError as e:
            logger.error(f"Google Sheets API error: {e}")
            raise
    
    async def update_book_url(self, sheet_id: str, n_code: str, book_url: str) -> bool:
        """
        発行計画シートのE列に書籍URLを転記
        
        Args:
            sheet_id: 発行計画シートのID
            n_code: Nコード
            book_url: 転記する書籍URL
            
        Returns:
            成功時True
        """
        try:
            # まず行番号を取得
            project_info = await self.get_project_info(sheet_id, n_code)
            if not project_info:
                logger.error(f"Cannot find project {n_code} to update")
                return False
            
            # E列を更新
            update_range = f'2020.10-!E{project_info["row_number"]}'
            body = {'values': [[book_url]]}
            
            result = self.sheets.values().update(
                spreadsheetId=sheet_id,
                range=update_range,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Updated book URL for {n_code} at row {project_info['row_number']}")
            return True
            
        except HttpError as e:
            logger.error(f"Failed to update book URL: {e}")
            return False
    
    async def update_slack_user_id(self, sheet_id: str, row_number: int, user_id: str) -> bool:
        """
        J列にSlackユーザーIDを更新
        
        Args:
            sheet_id: 発行計画シートのID
            row_number: 行番号（1ベース）
            user_id: SlackユーザーID
            
        Returns:
            成功時True
        """
        try:
            update_range = f'2020.10-!J{row_number}'
            body = {'values': [[user_id]]}
            
            result = self.sheets.values().update(
                spreadsheetId=sheet_id,
                range=update_range,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Updated Slack user ID at row {row_number}")
            return True
            
        except HttpError as e:
            logger.error(f"Failed to update Slack user ID: {e}")
            return False
    
    async def append_manual_task(self, sheet_id: str, task_data: List[Any]) -> bool:
        """
        手動タスク管理シートにタスクを追加
        
        Args:
            sheet_id: 発行計画シートのID
            task_data: タスクデータのリスト
            
        Returns:
            成功時True
        """
        try:
            range_name = '手動タスク管理!A:J'
            body = {'values': [task_data]}
            
            result = self.sheets.values().append(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Added manual task: {task_data[0]}")
            return True
            
        except HttpError as e:
            logger.error(f"Failed to add manual task: {e}")
            return False
    
    def extract_github_username(self, value: str) -> Optional[str]:
        """
        L列の値からGitHubユーザー名を抽出
        
        Args:
            value: L列の値（URLまたはユーザー名）
            
        Returns:
            GitHubユーザー名、無効な場合はNone
        """
        if not value:
            return None
        
        value = value.strip()
        
        # URLの場合（https://github.com/username）
        if value.startswith('http'):
            parts = value.rstrip('/').split('/')
            if len(parts) >= 4 and 'github.com' in value:
                return parts[-1]
            return None
        
        # アカウント名のみの場合
        # 有効なGitHubユーザー名かチェック（英数字、ハイフン、アンダースコア）
        if value and all(c.isalnum() or c in '-_' for c in value):
            return value
        
        return None
    
    async def add_manual_task_record(self, sheet_id: str, n_code: str, status: str, additional_info: dict = None) -> bool:
        """
        手動タスク管理シートにプロジェクト初期化の記録を追加
        
        Args:
            sheet_id: スプレッドシートID（発行計画シートと同じ）
            n_code: Nコード
            status: ステータス（例: "初期化完了", "手動タスクあり"）
            additional_info: 追加情報（リポジトリURL、チャンネル名など）
            
        Returns:
            記録成功時True、失敗時False
        """
        try:
            # 手動タスク管理シートに追加する行データ
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            slack_channel = additional_info.get('slack_channel', '未作成') if additional_info else '未作成'
            github_repo = additional_info.get('github_repo', '未作成') if additional_info else '未作成'
            manual_tasks_count = additional_info.get('manual_tasks_count', 0) if additional_info else 0
            
            # A列から順に項目を配置（より詳細で理解しやすい情報）
            task_data = [
                timestamp,          # A列: 実行日時
                n_code,            # B列: Nコード
                status,            # C列: ステータス
                slack_channel,     # D列: Slackチャンネル
                github_repo,       # E列: GitHubリポジトリ
                str(manual_tasks_count),  # F列: 手動タスク数
                "Slack招待失敗" if manual_tasks_count > 0 else "すべて自動完了",  # G列: 要対応内容
                f"チャンネル作成: {'成功' if slack_channel != '未作成' else '失敗'}, " +
                f"GitHub作成: {'成功' if github_repo != '未作成' else '失敗'}"  # H列: 実行結果詳細
            ]
            
            # まず1行目に項目名があるかチェック
            header_range = '手動タスク管理!A1:H1'
            try:
                header_result = self.sheets.values().get(
                    spreadsheetId=sheet_id,
                    range=header_range
                ).execute()
                
                header_values = header_result.get('values', [])
                
                # 1行目が空の場合は項目名を設定
                if not header_values or not header_values[0]:
                    header_data = [
                        "実行日時",
                        "Nコード", 
                        "ステータス",
                        "Slackチャンネル", 
                        "GitHubリポジトリ",
                        "手動タスク数",
                        "要対応内容",
                        "実行結果詳細"
                    ]
                    
                    # 項目名を設定
                    self.sheets.values().update(
                        spreadsheetId=sheet_id,
                        range=header_range,
                        valueInputOption='RAW',
                        body={'values': [header_data]}
                    ).execute()
                    
                    logger.info("Added header row to 手動タスク管理 sheet")
                    
            except HttpError as e:
                logger.warning(f"Could not check/set header row: {e}")
            
            # データ行を追加
            append_range = '手動タスク管理!A:H'
            self.sheets.values().append(
                spreadsheetId=sheet_id,
                range=append_range,
                valueInputOption='RAW',
                body={'values': [task_data]}
            ).execute()
            
            logger.info(f"Added manual task record for {n_code}: {status}")
            return True
            
        except HttpError as e:
            logger.error(f"Failed to add manual task record: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error adding manual task record: {e}")
            return False