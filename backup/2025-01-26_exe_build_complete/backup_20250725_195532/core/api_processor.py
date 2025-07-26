"""ReVIEW螟画鋤API蜃ｦ逅・Δ繧ｸ繝･繝ｼ繝ｫ"""
import requests
from requests.auth import HTTPBasicAuth
import time
import tempfile
import zipfile
import shutil
import re
import io
from pathlib import Path
from typing import Optional, Tuple, List
from PyQt6.QtCore import QObject, pyqtSignal

from utils.logger import get_logger


class ApiProcessor(QObject):
    """API譁ｹ蠑上〒縺ｮ螟画鋤蜃ｦ逅・ｒ陦後≧繧ｯ繝ｩ繧ｹ"""
    
    # 繧ｷ繧ｰ繝翫Ν螳夂ｾｩ
    log_message = pyqtSignal(str, str)  # message, level
    progress_updated = pyqtSignal(int)  # progress
    status_updated = pyqtSignal(str)  # status
    warning_dialog_needed = pyqtSignal(list, str)  # messages, result_type
    
    # API險ｭ螳・    API_BASE_URL = "http://sd001.nextpublishing.jp/rapture"
    API_USERNAME = "ep_user"
    API_PASSWORD = "Nn7eUTX5"
    
    # 繧ｿ繧､繝繧｢繧ｦ繝郁ｨｭ螳・    UPLOAD_TIMEOUT = 300  # 5蛻・    STATUS_CHECK_TIMEOUT = 30
    DOWNLOAD_TIMEOUT = 300  # 5蛻・    MAX_POLLING_ATTEMPTS = 60  # 譛螟ｧ10蛻・俣・・0遘帝俣髫費ｼ・    POLLING_INTERVAL = 10  # 10遘・    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.auth = HTTPBasicAuth(self.API_USERNAME, self.API_PASSWORD)
    
    def strip_ansi_escape_sequences(self, text: str) -> str:
        """ANSI繧ｨ繧ｹ繧ｱ繝ｼ繝励す繝ｼ繧ｱ繝ｳ繧ｹ繧帝勁蜴ｻ"""
        if not text:
            return text
        
        # ANSI繧ｨ繧ｹ繧ｱ繝ｼ繝励す繝ｼ繧ｱ繝ｳ繧ｹ縺ｮ繝代ち繝ｼ繝ｳ
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def upload_zip(self, zip_path: Path) -> Optional[str]:
        """
        ZIP繝輔ぃ繧､繝ｫ繧但PI縺ｫ繧｢繝・・繝ｭ繝ｼ繝会ｼ磯ｲ謐苓ｿｽ霍｡莉倥″・・        
        Args:
            zip_path: 繧｢繝・・繝ｭ繝ｼ繝峨☆繧技IP繝輔ぃ繧､繝ｫ縺ｮ繝代せ
            
        Returns:
            謌仙粥譎ゅ・jobid縲∝､ｱ謨玲凾縺ｯNone
        """
        file_size = zip_path.stat().st_size
        self.log_message.emit(f"繝輔ぃ繧､繝ｫ繧偵い繝・・繝ｭ繝ｼ繝我ｸｭ: {zip_path.name}", "INFO")
        self.log_message.emit(f"繝輔ぃ繧､繝ｫ繧ｵ繧､繧ｺ: {file_size:,} bytes ({file_size / 1024 / 1024:.1f} MB)", "INFO")
        self.log_message.emit(f"API URL: {self.API_BASE_URL}/api/upload", "DEBUG")
        
        # 繝励Ο繧ｰ繝ｬ繧ｹ繝舌・繧・%縺ｫ蛻晄悄蛹・        self.progress_updated.emit(0)
        self.status_updated.emit(f"繧｢繝・・繝ｭ繝ｼ繝画ｺ門ｙ荳ｭ... (0/{file_size:,} bytes)")
        
        try:
            # requests-toolbelt繧剃ｽｿ逕ｨ縺励◆騾ｲ謐苓ｿｽ霍｡
            try:
                from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
                use_toolbelt = True
                self.log_message.emit("騾ｲ謐苓ｿｽ霍｡繝｢繝ｼ繝峨〒繧｢繝・・繝ｭ繝ｼ繝・, "DEBUG")
            except ImportError:
                use_toolbelt = False
                self.log_message.emit("騾ｲ謐苓ｿｽ霍｡縺ｪ縺励〒繧｢繝・・繝ｭ繝ｼ繝・, "DEBUG")
            
            if use_toolbelt:
                # 騾ｲ謐苓ｿｽ霍｡莉倥″繧｢繝・・繝ｭ繝ｼ繝・                self.log_message.emit("繝輔ぃ繧､繝ｫ繧定ｪｭ縺ｿ霎ｼ縺ｿ荳ｭ...", "INFO")
                
                # 繧ｳ繝ｼ繝ｫ繝舌ャ繧ｯ逕ｨ縺ｮ螟画焚
                last_logged_progress = -1
                
                def create_callback(encoder_len):
                    """騾ｲ謐励さ繝ｼ繝ｫ繝舌ャ繧ｯ繧剃ｽ懈・"""
                    def callback(monitor):
                        nonlocal last_logged_progress
                        
                        # 騾ｲ謐苓ｨ育ｮ・                        bytes_read = monitor.bytes_read
                        total = encoder_len
                        progress = int((bytes_read / total) * 100) if total > 0 else 0
                        
                        # UI譖ｴ譁ｰ
                        self.progress_updated.emit(progress)
                        mb_read = bytes_read / 1024 / 1024
                        mb_total = total / 1024 / 1024
                        self.status_updated.emit(
                            f"繧｢繝・・繝ｭ繝ｼ繝我ｸｭ... {progress}% ({mb_read:.1f}/{mb_total:.1f} MB)"
                        )
                        
                        # 10%縺斐→縺ｫ繝ｭ繧ｰ
                        if progress > 0 and progress % 10 == 0 and progress != last_logged_progress:
                            self.log_message.emit(f"繧｢繝・・繝ｭ繝ｼ繝蛾ｲ謐・ {progress}%", "INFO")
                            last_logged_progress = progress
                    
                    return callback
                
                # 繝輔ぃ繧､繝ｫ繧帝幕縺・※繧ｨ繝ｳ繧ｳ繝ｼ繝繝ｼ繧剃ｽ懈・
                with open(zip_path, 'rb') as f:
                    encoder = MultipartEncoder(
                        fields={'file': (zip_path.name, f, 'application/zip')}
                    )
                    encoder_len = encoder.len
                    
                    # 繝｢繝九ち繝ｼ繧剃ｽ懈・
                    monitor = MultipartEncoderMonitor(encoder, create_callback(encoder_len))
                    
                    self.log_message.emit("繧｢繝・・繝ｭ繝ｼ繝蛾幕蟋・, "INFO")
                    self.log_message.emit(f"繧｢繝・・繝ｭ繝ｼ繝峨し繧､繧ｺ: {encoder_len:,} bytes", "DEBUG")
                    
                    response = requests.post(
                        f"{self.API_BASE_URL}/api/upload",
                        data=monitor,
                        headers={'Content-Type': monitor.content_type},
                        auth=self.auth,
                        timeout=self.UPLOAD_TIMEOUT
                    )
                
                # 繧｢繝・・繝ｭ繝ｼ繝牙ｮ御ｺ・                self.progress_updated.emit(100)
                self.status_updated.emit("繧｢繝・・繝ｭ繝ｼ繝牙ｮ御ｺ・)
                self.log_message.emit("繧｢繝・・繝ｭ繝ｼ繝牙ｮ御ｺ・, "INFO")
                
            else:
                # 繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ: 谿ｵ髫守噪縺ｪ騾ｲ謐苓｡ｨ遉ｺ
                self.log_message.emit("繝輔ぃ繧､繝ｫ繧定ｪｭ縺ｿ霎ｼ縺ｿ荳ｭ...", "INFO")
                
                # 騾ｲ謐励・谿ｵ髫守噪縺ｫ陦ｨ遉ｺ
                self.progress_updated.emit(10)
                self.status_updated.emit("繝輔ぃ繧､繝ｫ隱ｭ縺ｿ霎ｼ縺ｿ荳ｭ...")
                
                # 30%: 繝輔ぃ繧､繝ｫ貅門ｙ螳御ｺ・                self.progress_updated.emit(30)
                self.status_updated.emit("繧｢繝・・繝ｭ繝ｼ繝画ｺ門ｙ荳ｭ...")
                
                # 繝輔ぃ繧､繝ｫ繧帝幕縺・※繧｢繝・・繝ｭ繝ｼ繝・                with open(zip_path, 'rb') as f:
                    files = {'file': (zip_path.name, f, 'application/zip')}
                    
                    # 50%: 繧｢繝・・繝ｭ繝ｼ繝蛾幕蟋・                    self.progress_updated.emit(50)
                    self.status_updated.emit(f"繧｢繝・・繝ｭ繝ｼ繝我ｸｭ... ({file_size:,} bytes)")
                    
                    self.log_message.emit("繧｢繝・・繝ｭ繝ｼ繝蛾幕蟋・, "INFO")
                    
                    response = requests.post(
                        f"{self.API_BASE_URL}/api/upload",
                        files=files,
                        auth=self.auth,
                        timeout=self.UPLOAD_TIMEOUT
                    )
                    
                    # 90%: 繧｢繝・・繝ｭ繝ｼ繝牙ｮ御ｺ・√Ξ繧ｹ繝昴Φ繧ｹ蜃ｦ逅・ｸｭ
                    self.progress_updated.emit(90)
                    self.status_updated.emit("繝ｬ繧ｹ繝昴Φ繧ｹ蜃ｦ逅・ｸｭ...")
                
                # 繧｢繝・・繝ｭ繝ｼ繝牙ｮ御ｺ・                self.progress_updated.emit(100)
                self.status_updated.emit("繧｢繝・・繝ｭ繝ｼ繝牙ｮ御ｺ・)
                self.log_message.emit("繧｢繝・・繝ｭ繝ｼ繝牙ｮ御ｺ・, "INFO")
            
            if response.status_code == 200:
                data = response.json()
                if 'jobid' in data:
                    jobid = data['jobid']
                    self.log_message.emit(f"繧｢繝・・繝ｭ繝ｼ繝画・蜉・(Job ID: {jobid})", "INFO")
                    return jobid
                else:
                    self.log_message.emit("繝ｬ繧ｹ繝昴Φ繧ｹ縺ｫJob ID縺悟性縺ｾ繧後※縺・∪縺帙ｓ", "ERROR")
            else:
                self.log_message.emit(
                    f"繧｢繝・・繝ｭ繝ｼ繝牙､ｱ謨・(HTTP {response.status_code})", 
                    "ERROR"
                )
                self.log_message.emit(f"繝ｬ繧ｹ繝昴Φ繧ｹ蜀・ｮｹ: {response.text[:200]}", "DEBUG")
        
        except requests.exceptions.Timeout:
            self.log_message.emit("繧｢繝・・繝ｭ繝ｼ繝峨′繧ｿ繧､繝繧｢繧ｦ繝医＠縺ｾ縺励◆", "ERROR")
        except Exception as e:
            self.log_message.emit(f"繧｢繝・・繝ｭ繝ｼ繝峨お繝ｩ繝ｼ: {str(e)}", "ERROR")
            self.log_message.emit(f"繧ｨ繝ｩ繝ｼ繧ｿ繧､繝・ {type(e).__name__}", "ERROR")
            import traceback
            self.log_message.emit(f"繧ｹ繧ｿ繝・け繝医Ξ繝ｼ繧ｹ:\n{traceback.format_exc()}", "ERROR")
        
        return None
    
    def check_status(self, jobid: str) -> Tuple[Optional[str], Optional[str], Optional[List[str]]]:
        """
        螟画鋤繧ｸ繝ｧ繝悶・繧ｹ繝・・繧ｿ繧ｹ繧堤｢ｺ隱・        
        Args:
            jobid: 繧ｸ繝ｧ繝蜂D
            
        Returns:
            (邨先棡, 繝繧ｦ繝ｳ繝ｭ繝ｼ繝蔚RL, 隴ｦ蜻翫Γ繝・そ繝ｼ繧ｸ繝ｪ繧ｹ繝・ 縺ｮ繧ｿ繝励Ν
            邨先棡縺ｯ 'success', 'partial_success', 'failure', None 縺ｮ縺・★繧後°
        """
        self.log_message.emit("螟画鋤蜃ｦ逅・・螳御ｺ・ｒ蠕・ｩ滉ｸｭ...", "INFO")
        self.log_message.emit(f"繧ｹ繝・・繧ｿ繧ｹ遒ｺ隱攻RL: {self.API_BASE_URL}/api/status/{jobid}", "DEBUG")
        
        for attempt in range(self.MAX_POLLING_ATTEMPTS):
            try:
                response = requests.get(
                    f"{self.API_BASE_URL}/api/status/{jobid}",
                    auth=self.auth,
                    timeout=self.STATUS_CHECK_TIMEOUT
                )
                
                self.log_message.emit(f"繧ｹ繝・・繧ｿ繧ｹ遒ｺ隱・- HTTP Status: {response.status_code}", "DEBUG")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_message.emit(f"繧ｹ繝・・繧ｿ繧ｹ蠢懃ｭ泌・菴・ {data}", "DEBUG")
                    
                    status = data.get('status', 'unknown')
                    
                    self.log_message.emit(f"繧ｹ繝・・繧ｿ繧ｹ蠢懃ｭ・ {status}", "DEBUG")
                    self.status_updated.emit(f"螟画鋤迥ｶ豕・ {status} ({attempt + 1}/{self.MAX_POLLING_ATTEMPTS})")
                    
                    if status == 'completed':
                        result = data.get('result', 'unknown')
                        output = data.get('output', '')
                        download_url = data.get('download_url')
                        warnings = []
                        
                        self.log_message.emit(f"螟画鋤邨先棡: {result}", "DEBUG")
                        self.log_message.emit(f"繝繧ｦ繝ｳ繝ｭ繝ｼ繝蔚RL: {download_url}", "DEBUG")
                        self.log_message.emit(f"蜃ｺ蜉帙ち繧､繝・ {type(output)}", "DEBUG")
                        
                        # ANSI繧ｨ繧ｹ繧ｱ繝ｼ繝励す繝ｼ繧ｱ繝ｳ繧ｹ繧帝勁蜴ｻ
                        if output:
                            if isinstance(output, str):
                                self.log_message.emit(f"蜃ｺ蜉帶枚蟄玲焚・・NSI髯､蜴ｻ蜑搾ｼ・ {len(output)}", "DEBUG")
                                output = self.strip_ansi_escape_sequences(output)
                                self.log_message.emit(f"蜃ｺ蜉帶枚蟄玲焚・・NSI髯､蜴ｻ蠕鯉ｼ・ {len(output)}", "DEBUG")
                            elif isinstance(output, list):
                                self.log_message.emit(f"蜃ｺ蜉帙Μ繧ｹ繝磯聞: {len(output)}", "DEBUG")
                                output = '\n'.join(str(item) for item in output)
                                output = self.strip_ansi_escape_sequences(output)
                            
                            # 隴ｦ蜻翫Γ繝・そ繝ｼ繧ｸ繧定｡後＃縺ｨ縺ｫ蛻・牡
                            warnings = [line.strip() for line in output.split('\n') if line.strip()]
                            self.log_message.emit(f"隴ｦ蜻翫Γ繝・そ繝ｼ繧ｸ謨ｰ: {len(warnings)}", "DEBUG")
                        
                        if result == 'success':
                            if not warnings:
                                self.log_message.emit("螟画鋤蜃ｦ逅・′豁｣蟶ｸ縺ｫ螳御ｺ・＠縺ｾ縺励◆・郁ｭｦ蜻翫↑縺暦ｼ・, "INFO")
                                return 'success', download_url, []
                            else:
                                self.log_message.emit("螟画鋤蜃ｦ逅・′謌仙粥縺励∪縺励◆・郁ｭｦ蜻翫≠繧奇ｼ・, "WARNING")
                                self.log_message.emit(f"隴ｦ蜻雁・螳ｹ: {len(warnings)}莉ｶ", "DEBUG")
                                for i, warning in enumerate(warnings[:3]):  # 譛蛻昴・3莉ｶ縺縺代Ο繧ｰ縺ｫ蜃ｺ蜉・                                    self.log_message.emit(f"  隴ｦ蜻顎i+1}: {warning[:100]}...", "DEBUG")
                                return 'partial_success', download_url, warnings
                        
                        elif result == 'partial_success':
                            self.log_message.emit("螟画鋤蜃ｦ逅・′荳驛ｨ謌仙粥縺ｧ螳御ｺ・＠縺ｾ縺励◆", "WARNING")
                            return 'partial_success', download_url, warnings
                        
                        else:  # failure
                            errors = data.get('errors', [])
                            self.log_message.emit("螟画鋤蜃ｦ逅・′螟ｱ謨励＠縺ｾ縺励◆", "ERROR")
                            self.log_message.emit(f"繧ｨ繝ｩ繝ｼ謨ｰ: {len(errors)}", "DEBUG")
                            if errors:
                                for error in errors:
                                    self.log_message.emit(f"  - {error}", "ERROR")
                            return 'failure', None, warnings if warnings else errors
                    
                    elif status == 'failed':
                        errors = data.get('errors', [])
                        self.log_message.emit("螟画鋤蜃ｦ逅・′螟ｱ謨励＠縺ｾ縺励◆", "ERROR")
                        self.log_message.emit(f"繧ｨ繝ｩ繝ｼ隧ｳ邏ｰ: {errors}", "DEBUG")
                        return 'failure', None, errors
                    
                    # 縺ｾ縺蜃ｦ逅・ｸｭ縺ｮ蝣ｴ蜷医・蠕・ｩ・                    time.sleep(self.POLLING_INTERVAL)
                    
                else:
                    self.log_message.emit(
                        f"繧ｹ繝・・繧ｿ繧ｹ蜿門ｾ怜､ｱ謨・(HTTP {response.status_code})", 
                        "ERROR"
                    )
                    self.log_message.emit(f"繧ｨ繝ｩ繝ｼ蠢懃ｭ・ {response.text[:500]}", "DEBUG")
                    return None, None, []
                    
            except Exception as e:
                self.log_message.emit(f"繧ｹ繝・・繧ｿ繧ｹ遒ｺ隱阪お繝ｩ繝ｼ: {str(e)}", "ERROR")
                self.log_message.emit(f"繧ｨ繝ｩ繝ｼ繧ｿ繧､繝・ {type(e).__name__}", "DEBUG")
                import traceback
                self.log_message.emit(f"繧ｹ繧ｿ繝・け繝医Ξ繝ｼ繧ｹ: {traceback.format_exc()}", "DEBUG")
                return None, None, []
        
        self.log_message.emit("螟画鋤蜃ｦ逅・′繧ｿ繧､繝繧｢繧ｦ繝医＠縺ｾ縺励◆", "ERROR")
        return None, None, []
    
    def download_file(self, download_url: str, output_dir: Path) -> Optional[Path]:
        """
        螟画鋤貂医∩繝輔ぃ繧､繝ｫ繧偵ム繧ｦ繝ｳ繝ｭ繝ｼ繝・        
        Args:
            download_url: 繝繧ｦ繝ｳ繝ｭ繝ｼ繝蔚RL
            output_dir: 菫晏ｭ伜・繝・ぅ繝ｬ繧ｯ繝医Μ
            
        Returns:
            謌仙粥譎ゅ・繝繧ｦ繝ｳ繝ｭ繝ｼ繝峨＠縺溘ヵ繧｡繧､繝ｫ縺ｮ繝代せ縲∝､ｱ謨玲凾縺ｯNone
        """
        self.log_message.emit("螟画鋤貂医∩繝輔ぃ繧､繝ｫ繧偵ム繧ｦ繝ｳ繝ｭ繝ｼ繝我ｸｭ...", "INFO")
        
        try:
            response = requests.get(
                download_url,
                auth=self.auth,
                stream=True,
                timeout=self.DOWNLOAD_TIMEOUT
            )
            
            if response.status_code == 200:
                # 繝輔ぃ繧､繝ｫ蜷阪ｒ逕滓・
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"converted_{timestamp}.zip"
                output_path = output_dir / filename
                
                # 繝繧ｦ繝ｳ繝ｭ繝ｼ繝牙ｮ溯｡・                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # 騾ｲ謐玲峩譁ｰ
                            if total_size > 0:
                                progress = int(downloaded / total_size * 100)
                                self.progress_updated.emit(progress)
                
                self.log_message.emit(f"繝繧ｦ繝ｳ繝ｭ繝ｼ繝牙ｮ御ｺ・ {filename}", "INFO")
                
                # ZIP繝輔ぃ繧､繝ｫ縺ｮ讀懆ｨｼ
                try:
                    with zipfile.ZipFile(output_path, 'r') as zf:
                        file_count = len(zf.namelist())
                        self.log_message.emit(f"ZIP繝輔ぃ繧､繝ｫ蜀・・繝輔ぃ繧､繝ｫ謨ｰ: {file_count}", "INFO")
                except zipfile.BadZipFile:
                    self.log_message.emit("繝繧ｦ繝ｳ繝ｭ繝ｼ繝峨＠縺溘ヵ繧｡繧､繝ｫ縺梧怏蜉ｹ縺ｪZIP繝輔ぃ繧､繝ｫ縺ｧ縺ｯ縺ゅｊ縺ｾ縺帙ｓ", "ERROR")
                    output_path.unlink()
                    return None
                
                return output_path
                
            else:
                self.log_message.emit(
                    f"繝繧ｦ繝ｳ繝ｭ繝ｼ繝牙､ｱ謨・(HTTP {response.status_code})", 
                    "ERROR"
                )
                
        except requests.exceptions.Timeout:
            self.log_message.emit("繝繧ｦ繝ｳ繝ｭ繝ｼ繝峨′繧ｿ繧､繝繧｢繧ｦ繝医＠縺ｾ縺励◆", "ERROR")
        except Exception as e:
            self.log_message.emit(f"繝繧ｦ繝ｳ繝ｭ繝ｼ繝峨お繝ｩ繝ｼ: {str(e)}", "ERROR")
        
        return None
    
    def process_zip_file(self, zip_path: Path) -> Tuple[bool, Optional[Path], List[str]]:
        """
        ZIP繝輔ぃ繧､繝ｫ繧但PI邨檎罰縺ｧ蜃ｦ逅・        
        Args:
            zip_path: 蜃ｦ逅・☆繧技IP繝輔ぃ繧､繝ｫ縺ｮ繝代せ
            
        Returns:
            (謌仙粥繝輔Λ繧ｰ, 繝繧ｦ繝ｳ繝ｭ繝ｼ繝峨＠縺溘ヵ繧｡繧､繝ｫ縺ｮ繝代せ, 隴ｦ蜻翫Γ繝・そ繝ｼ繧ｸ繝ｪ繧ｹ繝・ 縺ｮ繧ｿ繝励Ν
        """
        self.log_message.emit(f"API蜃ｦ逅・幕蟋・ {zip_path}", "INFO")
        self.log_message.emit(f"繝輔ぃ繧､繝ｫ繧ｵ繧､繧ｺ: {zip_path.stat().st_size:,} bytes", "DEBUG")
        
        # 荳譎ゅョ繧｣繝ｬ繧ｯ繝医Μ繧剃ｽ懈・
        temp_dir = Path(tempfile.mkdtemp())
        self.log_message.emit(f"荳譎ゅョ繧｣繝ｬ繧ｯ繝医Μ菴懈・: {temp_dir}", "DEBUG")
        
        try:
            # 1. 繧｢繝・・繝ｭ繝ｼ繝・            self.log_message.emit("繧｢繝・・繝ｭ繝ｼ繝牙・逅・ｒ髢句ｧ・..", "INFO")
            jobid = self.upload_zip(zip_path)
            if not jobid:
                self.log_message.emit("繧｢繝・・繝ｭ繝ｼ繝峨′螟ｱ謨励＠縺ｾ縺励◆", "ERROR")
                self.log_message.emit("upload_zip縺君one繧定ｿ斐＠縺ｾ縺励◆", "ERROR")
                return False, None, ["繝輔ぃ繧､繝ｫ縺ｮ繧｢繝・・繝ｭ繝ｼ繝峨↓螟ｱ謨励＠縺ｾ縺励◆"]
            
            self.log_message.emit(f"繧｢繝・・繝ｭ繝ｼ繝画・蜉・- Job ID: {jobid}", "INFO")
            
            # 2. 繧ｹ繝・・繧ｿ繧ｹ遒ｺ隱・            self.log_message.emit("繧ｹ繝・・繧ｿ繧ｹ遒ｺ隱阪ｒ髢句ｧ・..", "INFO")
            result, download_url, messages = self.check_status(jobid)
            
            self.log_message.emit(f"繧ｹ繝・・繧ｿ繧ｹ遒ｺ隱咲ｵ先棡: result={result}", "INFO")
            self.log_message.emit(f"繝繧ｦ繝ｳ繝ｭ繝ｼ繝蔚RL: {download_url}", "DEBUG")
            self.log_message.emit(f"繝｡繝・そ繝ｼ繧ｸ謨ｰ: {len(messages) if messages else 0}", "DEBUG")
            
            if result == 'failure' or not download_url:
                # 螟ｱ謨励・蝣ｴ蜷医ｂ繧ｨ繝ｩ繝ｼ繝繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ
                self.log_message.emit(f"蜃ｦ逅・､ｱ謨・ result={result}, download_url={download_url}", "ERROR")
                if messages:
                    self.log_message.emit(f"繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ: {messages[:3]}", "ERROR")
                    self.log_message.emit(f"繧ｨ繝ｩ繝ｼ繝繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ: {len(messages)}莉ｶ縺ｮ繝｡繝・そ繝ｼ繧ｸ", "ERROR")
                    self.warning_dialog_needed.emit(messages, 'failure')
                return False, None, messages
            
            # 3. 繝繧ｦ繝ｳ繝ｭ繝ｼ繝・            self.log_message.emit("繝繧ｦ繝ｳ繝ｭ繝ｼ繝牙・逅・ｒ髢句ｧ・..", "INFO")
            downloaded_file = self.download_file(download_url, temp_dir)
            if not downloaded_file:
                self.log_message.emit("download_file縺君one繧定ｿ斐＠縺ｾ縺励◆", "ERROR")
                return False, None, ["繝輔ぃ繧､繝ｫ縺ｮ繝繧ｦ繝ｳ繝ｭ繝ｼ繝峨↓螟ｱ謨励＠縺ｾ縺励◆"]
            
            self.log_message.emit(f"繝繧ｦ繝ｳ繝ｭ繝ｼ繝画・蜉・ {downloaded_file}", "INFO")
            
            # 隴ｦ蜻翫′縺ゅｋ蝣ｴ蜷医・繝繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ
            if result == 'partial_success' and messages:
                self.log_message.emit(f"隴ｦ蜻翫ム繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ: {len(messages)}莉ｶ縺ｮ繝｡繝・そ繝ｼ繧ｸ", "INFO")
                self.warning_dialog_needed.emit(messages, 'partial_success')
            
            # 謌仙粥縺ｾ縺溘・荳驛ｨ謌仙粥
            return True, downloaded_file, messages
            
        except Exception as e:
            self.log_message.emit(f"API蜃ｦ逅・お繝ｩ繝ｼ: {str(e)}", "ERROR")
            self.log_message.emit(f"繧ｨ繝ｩ繝ｼ繧ｿ繧､繝・ {type(e).__name__}", "ERROR")
            import traceback
            self.log_message.emit(f"繧ｹ繧ｿ繝・け繝医Ξ繝ｼ繧ｹ:\n{traceback.format_exc()}", "ERROR")
            return False, None, [str(e)]
        
        finally:
            # 荳譎ゅョ繧｣繝ｬ繧ｯ繝医Μ縺ｮ繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・縺ｯ蜻ｼ縺ｳ蜃ｺ縺怜・縺ｧ陦後≧
            self.log_message.emit(f"process_zip_file邨ゆｺ・, "DEBUG")