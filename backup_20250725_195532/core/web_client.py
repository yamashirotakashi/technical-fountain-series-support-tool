"""Web騾｣謳ｺ繝｢繧ｸ繝･繝ｼ繝ｫ"""
import os
from pathlib import Path
from typing import Optional, Tuple
import requests
from requests.auth import HTTPBasicAuth

from utils.logger import get_logger
from utils.config import get_config


class WebClient:
    """Web繧ｵ繝ｼ繝薙せ縺ｨ縺ｮ騾｣謳ｺ繧堤ｮ｡逅・☆繧九け繝ｩ繧ｹ"""
    
    def __init__(self):
        """WebClient繧貞・譛溷喧"""
        self.logger = get_logger(__name__)
        self.config = get_config()
        
        # Web險ｭ螳壹ｒ蜿門ｾ・        web_config = self.config.get_web_config()
        self.base_url = web_config.get('upload_url')
        self.username = web_config.get('username')
        self.password = web_config.get('password')
        
        # HTTP繧ｻ繝・す繝ｧ繝ｳ繧剃ｽ懈・
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(self.username, self.password)
        
        # 繝・ヵ繧ｩ繝ｫ繝医・繝・ム繝ｼ繧定ｨｭ螳・        self.session.headers.update({
            'User-Agent': 'TechnicalFountainTool/1.0'
        })
    
    def upload_file(self, file_path: Path, email: str) -> bool:
        """
        繝輔ぃ繧､繝ｫ繧偵い繝・・繝ｭ繝ｼ繝・        
        Args:
            file_path: 繧｢繝・・繝ｭ繝ｼ繝峨☆繧九ヵ繧｡繧､繝ｫ縺ｮ繝代せ
            email: 騾夂衍蜈医Γ繝ｼ繝ｫ繧｢繝峨Ξ繧ｹ
        
        Returns:
            繧｢繝・・繝ｭ繝ｼ繝峨′謌仙粥縺励◆蝣ｴ蜷・rue
        """
        try:
            self.logger.info(f"繝輔ぃ繧､繝ｫ繧｢繝・・繝ｭ繝ｼ繝蛾幕蟋・ {file_path}")
            
            if not file_path.exists():
                self.logger.error(f"繝輔ぃ繧､繝ｫ縺悟ｭ伜惠縺励∪縺帙ｓ: {file_path}")
                return False
            
            # 繝輔か繝ｼ繝繝・・繧ｿ繧呈ｺ門ｙ
            data = {
                'mail': email,
                'mailconf': email
            }
            
            # 繝輔ぃ繧､繝ｫ繧呈ｺ門ｙ
            with open(file_path, 'rb') as f:
                files = {
                    'userfile': (file_path.name, f, 'application/zip')
                }
                
                # POST繝ｪ繧ｯ繧ｨ繧ｹ繝医ｒ騾∽ｿ｡
                self.logger.info(f"繧｢繝・・繝ｭ繝ｼ繝牙・: {self.base_url}")
                response = self.session.post(
                    self.base_url,
                    data=data,
                    files=files,
                    timeout=300  # 5蛻・・繧ｿ繧､繝繧｢繧ｦ繝・                )
            
            # 繝ｬ繧ｹ繝昴Φ繧ｹ繧堤｢ｺ隱・            if response.status_code == 200:
                self.logger.info("繝輔ぃ繧､繝ｫ繧｢繝・・繝ｭ繝ｼ繝峨↓謌仙粥縺励∪縺励◆")
                self.logger.debug(f"繝ｬ繧ｹ繝昴Φ繧ｹ: {response.text[:500]}...")
                return True
            else:
                self.logger.error(f"繧｢繝・・繝ｭ繝ｼ繝峨↓螟ｱ謨・ HTTP {response.status_code}")
                self.logger.error(f"繝ｬ繧ｹ繝昴Φ繧ｹ: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            self.logger.error("繧｢繝・・繝ｭ繝ｼ繝峨′繧ｿ繧､繝繧｢繧ｦ繝医＠縺ｾ縺励◆")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"繝ｪ繧ｯ繧ｨ繧ｹ繝医お繝ｩ繝ｼ: {e}")
            return False
        except Exception as e:
            self.logger.error(f"繧｢繝・・繝ｭ繝ｼ繝我ｸｭ縺ｫ繧ｨ繝ｩ繝ｼ縺檎匱逕・ {e}")
            return False
    
    def download_file(self, url: str, save_path: Path) -> bool:
        """
        繝輔ぃ繧､繝ｫ繧偵ム繧ｦ繝ｳ繝ｭ繝ｼ繝・        
        Args:
            url: 繝繧ｦ繝ｳ繝ｭ繝ｼ繝蔚RL
            save_path: 菫晏ｭ伜・繝代せ
        
        Returns:
            繝繧ｦ繝ｳ繝ｭ繝ｼ繝峨′謌仙粥縺励◆蝣ｴ蜷・rue
        """
        try:
            self.logger.info(f"繝輔ぃ繧､繝ｫ繝繧ｦ繝ｳ繝ｭ繝ｼ繝蛾幕蟋・ {url}")
            
            # 繝・ぅ繝ｬ繧ｯ繝医Μ縺悟ｭ伜惠縺励↑縺・ｴ蜷医・菴懈・
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # GET繝ｪ繧ｯ繧ｨ繧ｹ繝医〒繝繧ｦ繝ｳ繝ｭ繝ｼ繝会ｼ医せ繝医Μ繝ｼ繝溘Φ繧ｰ・・            response = self.session.get(
                url,
                stream=True,
                timeout=300
            )
            
            # 繝ｬ繧ｹ繝昴Φ繧ｹ繧堤｢ｺ隱・            if response.status_code == 200:
                # 繝輔ぃ繧､繝ｫ縺ｫ譖ｸ縺崎ｾｼ縺ｿ
                total_size = int(response.headers.get('content-length', 0))
                self.logger.info(f"繝繧ｦ繝ｳ繝ｭ繝ｼ繝峨し繧､繧ｺ: {total_size:,} bytes")
                
                downloaded = 0
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # 騾ｲ謐励ｒ繝ｭ繧ｰ・・0%縺斐→・・                            if total_size > 0:
                                progress = int((downloaded / total_size) * 100)
                                if progress % 10 == 0 and progress != getattr(self, '_last_progress', -1):
                                    self.logger.info(f"繝繧ｦ繝ｳ繝ｭ繝ｼ繝蛾ｲ謐・ {progress}%")
                                    self._last_progress = progress
                
                self.logger.info(f"繝繧ｦ繝ｳ繝ｭ繝ｼ繝牙ｮ御ｺ・ {save_path}")
                return True
            else:
                self.logger.error(f"繝繧ｦ繝ｳ繝ｭ繝ｼ繝峨↓螟ｱ謨・ HTTP {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            self.logger.error("繝繧ｦ繝ｳ繝ｭ繝ｼ繝峨′繧ｿ繧､繝繧｢繧ｦ繝医＠縺ｾ縺励◆")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"繝ｪ繧ｯ繧ｨ繧ｹ繝医お繝ｩ繝ｼ: {e}")
            return False
        except Exception as e:
            self.logger.error(f"繝繧ｦ繝ｳ繝ｭ繝ｼ繝我ｸｭ縺ｫ繧ｨ繝ｩ繝ｼ縺檎匱逕・ {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        謗･邯壹ｒ繝・せ繝・        
        Returns:
            謗･邯壹′謌仙粥縺励◆蝣ｴ蜷・rue
        """
        try:
            self.logger.info("Web謗･邯壹ユ繧ｹ繝磯幕蟋・)
            
            # HEAD繝ｪ繧ｯ繧ｨ繧ｹ繝医〒繝・せ繝・            response = self.session.head(
                self.base_url,
                timeout=10
            )
            
            # 隱崎ｨｼ縺悟ｿ・ｦ√↑繧ｵ繧､繝医・蝣ｴ蜷医・01莉･螟悶・謌仙粥縺ｨ縺ｿ縺ｪ縺・            if response.status_code != 401:
                self.logger.info(f"謗･邯壹ユ繧ｹ繝域・蜉・ HTTP {response.status_code}")
                return True
            else:
                self.logger.error("隱崎ｨｼ縺ｫ螟ｱ謨励＠縺ｾ縺励◆")
                return False
                
        except Exception as e:
            self.logger.error(f"謗･邯壹ユ繧ｹ繝医↓螟ｱ謨・ {e}")
            return False
    
    def close(self):
        """繧ｻ繝・す繝ｧ繝ｳ繧帝哩縺倥ｋ"""
        self.session.close()
        self.logger.info("HTTP繧ｻ繝・す繝ｧ繝ｳ繧帝哩縺倥∪縺励◆")