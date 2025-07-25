"""Google Sheets騾｣謳ｺ繝｢繧ｸ繝･繝ｼ繝ｫ"""
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
    """Google Sheets縺ｨ縺ｮ騾｣謳ｺ繧堤ｮ｡逅・☆繧九け繝ｩ繧ｹ"""
    
    def __init__(self):
        """GoogleSheetClient繧貞・譛溷喧"""
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.service = None
        self.sheet_id = self.config.get('google_sheet.sheet_id')
        self._authenticate()
    
    def _authenticate(self):
        """Google Sheets API縺ｮ隱崎ｨｼ繧定｡後≧"""
        try:
            # 隱崎ｨｼ諠・ｱ繝輔ぃ繧､繝ｫ縺ｮ繝代せ繧貞叙蠕・            creds_path = self.config.get_credentials_path()
            if not creds_path or not creds_path.exists():
                raise FileNotFoundError(f"隱崎ｨｼ繝輔ぃ繧､繝ｫ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ: {creds_path}")
            
            self.logger.info(f"隱崎ｨｼ繝輔ぃ繧､繝ｫ繧剃ｽｿ逕ｨ: {creds_path}")
            
            # 繧ｵ繝ｼ繝薙せ繧｢繧ｫ繧ｦ繝ｳ繝医・隱崎ｨｼ諠・ｱ繧剃ｽ懈・
            credentials = service_account.Credentials.from_service_account_file(
                str(creds_path),
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            
            # Google Sheets API縺ｮ繧ｵ繝ｼ繝薙せ繧呈ｧ狗ｯ・            self.service = build('sheets', 'v4', credentials=credentials)
            self.logger.info("Google Sheets API縺ｮ隱崎ｨｼ縺ｫ謌仙粥縺励∪縺励◆")
            
        except Exception as e:
            self.logger.error(f"Google Sheets API縺ｮ隱崎ｨｼ縺ｫ螟ｱ謨・ {e}")
            raise
    
    def search_n_code(self, n_code: str) -> Optional[Dict[str, Any]]:
        """
        N繧ｳ繝ｼ繝峨ｒA蛻励°繧画､懃ｴ｢縺励∬ｩｲ蠖楢｡後・諠・ｱ繧貞叙蠕・        
        Args:
            n_code: 讀懃ｴ｢縺吶ｋN繧ｳ繝ｼ繝・        
        Returns:
            隕九▽縺九▲縺溷ｴ蜷医・陦後・諠・ｱ繧貞性繧霎樊嶌縲∬ｦ九▽縺九ｉ縺ｪ縺・ｴ蜷医・None
            {
                'row': 陦檎分蜿ｷ・・繝吶・繧ｹ・・
                'n_code': N繧ｳ繝ｼ繝・
                'repository_name': 繝ｪ繝昴ず繝医Μ蜷搾ｼ・蛻暦ｼ・            }
        """
        return self._execute_with_retry(self._search_n_code_impl, n_code)
    
    def _search_n_code_impl(self, n_code: str) -> Optional[Dict[str, Any]]:
        """
        N繧ｳ繝ｼ繝画､懃ｴ｢縺ｮ螳溯｣・ｼ医Μ繝医Λ繧､蟇ｾ雎｡・・        """
        self.logger.info(f"N繧ｳ繝ｼ繝画､懃ｴ｢髢句ｧ・ {n_code}")
        
        # A蛻励→C蛻励・繝・・繧ｿ繧貞叙蠕暦ｼ・000陦後∪縺ｧ・・        range_name = 'A1:C1000'
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.sheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            self.logger.warning("繧ｹ繝励Ξ繝・ラ繧ｷ繝ｼ繝医↓繝・・繧ｿ縺後≠繧翫∪縺帙ｓ")
            return None
        
        # N繧ｳ繝ｼ繝峨ｒ讀懃ｴ｢
        for row_idx, row in enumerate(values, start=1):
            if row and len(row) > 0:
                # A蛻励・蛟､繧堤｢ｺ隱・                cell_value = str(row[0]).strip().upper()
                if cell_value == n_code.upper():
                    # C蛻励・蛟､繧貞叙蠕暦ｼ亥ｭ伜惠縺吶ｋ蝣ｴ蜷茨ｼ・                    repository_name = row[2] if len(row) > 2 else None
                    
                    if not repository_name:
                        self.logger.warning(f"陦・{row_idx} 縺ｮC蛻励↓繝ｪ繝昴ず繝医Μ蜷阪′縺ゅｊ縺ｾ縺帙ｓ")
                        return None
                    
                    result_dict = {
                        'row': row_idx,
                        'n_code': n_code,
                        'repository_name': repository_name.strip()
                    }
                    
                    self.logger.info(f"N繧ｳ繝ｼ繝・{n_code} 繧定｡・{row_idx} 縺ｧ逋ｺ隕・ {repository_name}")
                    return result_dict
        
        self.logger.warning(f"N繧ｳ繝ｼ繝・{n_code} 縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ縺ｧ縺励◆")
        return None
    
    def _execute_with_retry(self, func, *args, max_retries: int = 3, **kwargs):
        """
        謖・焚繝舌ャ繧ｯ繧ｪ繝輔〒繝ｪ繝医Λ繧､螳溯｡・        
        Args:
            func: 螳溯｡後☆繧矩未謨ｰ
            max_retries: 譛螟ｧ繝ｪ繝医Λ繧､蝗樊焚
            *args, **kwargs: 髢｢謨ｰ縺ｫ貂｡縺吝ｼ墓焚
        
        Returns:
            髢｢謨ｰ縺ｮ螳溯｡檎ｵ先棡
        """
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
                
            except HttpError as e:
                # 繝ｪ繝医Λ繧､蜿ｯ閭ｽ縺ｪ繧ｨ繝ｩ繝ｼ縺九メ繧ｧ繝・け
                if self._is_retryable_error(e) and attempt < max_retries:
                    # 謖・焚繝舌ャ繧ｯ繧ｪ繝輔〒蠕・ｩ滓凾髢薙ｒ險育ｮ暦ｼ医ず繝・ち繝ｼ繧定ｿｽ蜉・・                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    self.logger.warning(
                        f"Google Sheets API繧ｨ繝ｩ繝ｼ (隧ｦ陦・{attempt + 1}/{max_retries + 1}): {e.resp.status} - "
                        f"{wait_time:.2f}遘貞ｾ後↓繝ｪ繝医Λ繧､縺励∪縺・
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    # 繝ｪ繝医Λ繧､荳榊庄閭ｽ縺ｪ繧ｨ繝ｩ繝ｼ縺ｾ縺溘・譛螟ｧ繝ｪ繝医Λ繧､蝗樊焚縺ｫ驕斐＠縺溷ｴ蜷・                    self.logger.error(f"Google Sheets API繧ｨ繝ｩ繝ｼ (譛邨・: {e}")
                    raise
                    
            except Exception as e:
                # HttpError莉･螟悶・繧ｨ繝ｩ繝ｼ縺ｯ繝ｪ繝医Λ繧､縺励↑縺・                self.logger.error(f"莠域悄縺励↑縺・お繝ｩ繝ｼ: {e}")
                raise
    
    def _is_retryable_error(self, error: HttpError) -> bool:
        """
        繝ｪ繝医Λ繧､蜿ｯ閭ｽ縺ｪ繧ｨ繝ｩ繝ｼ縺九←縺・°繧貞愛螳・        
        Args:
            error: HttpError繧ｪ繝悶ず繧ｧ繧ｯ繝・        
        Returns:
            繝ｪ繝医Λ繧､蜿ｯ閭ｽ縺ｪ蝣ｴ蜷・rue
        """
        # 繝ｪ繝医Λ繧､蜿ｯ閭ｽ縺ｪHTTP繧ｹ繝・・繧ｿ繧ｹ繧ｳ繝ｼ繝・        retryable_codes = {
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
        N繧ｳ繝ｼ繝峨°繧峨Μ繝昴ず繝医Μ蜷阪ｒ蜿門ｾ・        
        Args:
            n_code: N繧ｳ繝ｼ繝・        
        Returns:
            繝ｪ繝昴ず繝医Μ蜷搾ｼ郁ｦ九▽縺九ｉ縺ｪ縺・ｴ蜷医・None・・        """
        result = self.search_n_code(n_code)
        return result['repository_name'] if result else None
    
    def test_connection(self) -> bool:
        """
        Google Sheets縺ｸ縺ｮ謗･邯壹ｒ繝・せ繝・        
        Returns:
            謗･邯壹′謌仙粥縺励◆蝣ｴ蜷・rue
        """
        try:
            # 繝ｪ繝医Λ繧､讖溯・莉倥″縺ｧ謗･邯壹ユ繧ｹ繝医ｒ螳溯｡・            sheet_metadata = self._execute_with_retry(
                lambda: self.service.spreadsheets().get(spreadsheetId=self.sheet_id).execute()
            )
            
            sheet_title = sheet_metadata.get('properties', {}).get('title', 'Unknown')
            self.logger.info(f"繧ｹ繝励Ξ繝・ラ繧ｷ繝ｼ繝医↓謗･邯壽・蜉・ {sheet_title}")
            return True
            
        except Exception as e:
            self.logger.error(f"謗･邯壹ユ繧ｹ繝医↓螟ｱ謨・ {e}")
            return False