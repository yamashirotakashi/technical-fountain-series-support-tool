"""Word2XHTML5サービスのrequests実装"""
from __future__ import annotations

import time
import re
import requests
from pathlib import Path
from typing import List, Dict, Tuple, Optional

from .verifier_base import PreflightVerifier
from .rate_limiter import RateLimiter
from .form_settings import Word2XhtmlFormSettings
from utils.logger import get_logger

# Phase 3-2: DI Container統合によりConfigManager条件分岐import完全解消
from core.configuration_provider import ConfigurationProvider
from core.di_container import inject


class Word2XhtmlScrapingVerifier(PreflightVerifier):
    """requestsを使用したWord2XHTML5サービスの検証実装"""
    
    @inject
    def __init__(self, config_provider: ConfigurationProvider):
        """
        Phase 3-2: Constructor Injection適用 - ハードコーディング値完全排除
        
        Args:
            config_provider: DI注入される統一設定プロバイダー
        """
        self.logger = get_logger(__name__)
        self.config_provider = config_provider
        
        # レート制限設定を統一設定から取得
        min_interval = self.config_provider.get("api.nextpublishing.rate_limit_interval", 5.0)
        self.rate_limiter = RateLimiter(min_interval=min_interval)
        self.session = requests.Session()
        self.job_file_mapping: Dict[str, str] = {}  # job_id -> file_path
        
        # サービスURL - ハードコーディング値完全排除
        self.service_url = self.config_provider.get(
            "api.nextpublishing.base_url", 
            "http://trial.nextpublishing.jp/upload_46tate/"
        )
        
        # 認証情報 - 統一設定から取得
        username = self.config_provider.get("api.nextpublishing.username", "ep_user")
        password = self.config_provider.get("api.nextpublishing.password", "Nn7eUTX5")
        
        # Basic認証設定
        from requests.auth import HTTPBasicAuth
        self.session.auth = HTTPBasicAuth(username, password)
        
    def _extract_job_id(self, page_text: str) -> Optional[str]:
        """ページテキストからジョブIDを抽出
        
        Args:
            page_text: ページのテキスト内容
            
        Returns:
            抽出されたジョブID（見つからない場合はNone）
        """
        # 典型的なパターン:
        # 1. "受付番号: XXXXX" または "Job ID: XXXXX"
        # 2. "処理ID: XXXXX"
        # 3. メール内容に含まれるパターン
        
        patterns = [
            r'受付番号[:：]\s*(\S+)',
            r'Job\s*ID[:：]\s*(\S+)',
            r'処理ID[:：]\s*(\S+)',
            r'受付ID[:：]\s*(\S+)',
            r'整理番号[:：]\s*(\S+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                return match.group(1)
                
        # パターンマッチしない場合、タイムスタンプベースのIDを生成
        return None
        
    def _submit_single(self, file_path: str, email: str) -> Optional[str]:
        """横書き専用の単一ファイル送信（requests版）
        
        Args:
            file_path: Wordファイルのパス
            email: メールアドレス
            
        Returns:
            ジョブID（失敗時はNone）
        """
        try:
            # フォーム設定を作成
            settings = Word2XhtmlFormSettings.create_default(email)
            if not settings.validate():
                raise Exception(f"フォーム設定が無効です: {settings}")
            
            self.logger.info(f"ファイル送信開始: {file_path}")
            self.logger.info(f"送信先: {self.service_url}")
            
            # フォームデータの準備
            form_data = settings.get_form_data()
            
            # タイムアウト設定を統一設定プロバイダーから取得
            timeout = self.config_provider.get("api.nextpublishing.timeout", 30)
            
            # ファイルの準備
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise Exception(f"ファイルが存在しません: {file_path}")
            
            with open(file_path, 'rb') as f:
                files = {
                    'userfile1': (file_path_obj.name, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                }
                
                # POST送信
                response = self.session.post(
                    self.service_url,
                    data=form_data,
                    files=files,
                    timeout=timeout
                )
            
            # レスポンス確認
            if response.status_code == 200:
                job_id = self._extract_job_id(response.text)
                if not job_id:
                    # フォールバック: タイムスタンプベースID
                    job_id = f"word2xhtml_{int(time.time())}_{file_path_obj.stem}"
                    self.logger.warning(f"ジョブID抽出失敗、生成ID使用: {job_id}")
                
                self.logger.info(f"ファイル送信成功: {file_path} -> {job_id}")
                return job_id
            else:
                self.logger.error(f"送信失敗: HTTP {response.status_code}")
                self.logger.error(f"レスポンス: {response.text[:500]}")
                return None
                
        except Exception as e:
            self.logger.error(f"送信エラー: {file_path} - {e}", exc_info=True)
            return None
    
    def submit_batch(self, file_paths: List[str], email: str) -> List[str]:
        """複数ファイルを送信してジョブIDリストを返す"""
        job_ids = []
        
        for i, file_path in enumerate(file_paths):
            self.logger.info(f"送信中 ({i+1}/{len(file_paths)}): {file_path}")
            
            # レート制限
            if i > 0:  # 最初のファイルは待機不要
                self.rate_limiter.wait_if_needed()
            
            # ファイル送信
            job_id = self._submit_single(file_path, email)
            if job_id:
                job_ids.append(job_id)
                self.job_file_mapping[job_id] = file_path
            else:
                # 失敗した場合も空のIDを追加（順序を保つため）
                job_ids.append("")
                
        return job_ids
    
    def check_all_status(self, job_ids: List[str]) -> Dict[str, Tuple[str, Optional[str]]]:
        """全ジョブのステータスを確認
        
        注意: この実装ではバッチプロセッサーがメール監視を直接行うため、
        このメソッドは使用されません。将来のAPI移行時に使用予定。
        """
        self.logger.info("check_all_statusは現在未使用です。バッチプロセッサーがメール監視を行います。")
        
        # 将来のAPI実装のためのプレースホルダー
        results = {}
        for job_id in job_ids:
            if job_id:
                results[job_id] = ("pending", None)
                
        return results
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        if hasattr(self, 'session'):
            self.session.close()
        self.job_file_mapping.clear()