"""繝｡繝ｼ繝ｫ逶｣隕悶Δ繧ｸ繝･繝ｼ繝ｫ"""
import imaplib
import email
import re
import time
from typing import Optional
from datetime import datetime, timedelta

from utils.logger import get_logger
from utils.config import get_config


class EmailMonitor:
    """繝｡繝ｼ繝ｫ繧堤屮隕悶＠縺ｦ繝繧ｦ繝ｳ繝ｭ繝ｼ繝蔚RL繧貞叙蠕励☆繧九け繝ｩ繧ｹ"""
    
    def __init__(self, email_address: str, password: str):
        """
        EmailMonitor繧貞・譛溷喧
        
        Args:
            email_address: 繝｡繝ｼ繝ｫ繧｢繝峨Ξ繧ｹ
            password: 繝代せ繝ｯ繝ｼ繝会ｼ医い繝励Μ繝代せ繝ｯ繝ｼ繝会ｼ・        """
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.email_address = email_address
        self.password = password
        
        # IMAP險ｭ螳壹ｒ蜿門ｾ・        email_config = self.config.get_email_config()
        self.imap_server = email_config.get('imap_server', 'imap.gmail.com')
        self.imap_port = email_config.get('imap_port', 993)
        
        self.connection = None
    
    def connect(self):
        """IMAP繧ｵ繝ｼ繝舌・縺ｫ謗･邯・""
        try:
            self.logger.info(f"IMAP繧ｵ繝ｼ繝舌・縺ｫ謗･邯壻ｸｭ: {self.imap_server}:{self.imap_port}")
            
            # SSL謗･邯・            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            
            # 繝ｭ繧ｰ繧､繝ｳ
            self.connection.login(self.email_address, self.password)
            
            # INBOX繧帝∈謚・            self.connection.select('INBOX')
            
            self.logger.info("IMAP繧ｵ繝ｼ繝舌・縺ｸ縺ｮ謗･邯壹↓謌仙粥縺励∪縺励◆")
            
        except imaplib.IMAP4.error as e:
            self.logger.error(f"IMAP謗･邯壹お繝ｩ繝ｼ: {e}")
            raise
        except Exception as e:
            self.logger.error(f"謗･邯壻ｸｭ縺ｫ繧ｨ繝ｩ繝ｼ縺檎匱逕・ {e}")
            raise
    
    def wait_for_email(self, subject_pattern: str = "Re:VIEW to 雜・次遞ｿ逕ｨ邏・, 
                      timeout: int = 600, check_interval: int = 10) -> Optional[str]:
        """
        迚ｹ螳壹・莉ｶ蜷阪・繝｡繝ｼ繝ｫ繧貞ｾ・ｩ溘＠縺ｦ繝繧ｦ繝ｳ繝ｭ繝ｼ繝蔚RL繧貞叙蠕・        
        Args:
            subject_pattern: 蠕・ｩ溘☆繧倶ｻｶ蜷阪・繝代ち繝ｼ繝ｳ
            timeout: 繧ｿ繧､繝繧｢繧ｦ繝域凾髢難ｼ育ｧ抵ｼ・            check_interval: 繝√ぉ繝・け髢馴囈・育ｧ抵ｼ・        
        Returns:
            繝繧ｦ繝ｳ繝ｭ繝ｼ繝蔚RL・郁ｦ九▽縺九ｉ縺ｪ縺・ｴ蜷医・None・・        """
        if not self.connection:
            self.connect()
        
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=timeout)
        
        self.logger.info(f"繝｡繝ｼ繝ｫ蠕・ｩ滄幕蟋・ 莉ｶ蜷・'{subject_pattern}' (繧ｿ繧､繝繧｢繧ｦ繝・ {timeout}遘・")
        
        while datetime.now() < end_time:
            try:
                # 譁ｰ縺励＞繝｡繝ｼ繝ｫ繧呈､懃ｴ｢
                since_date = start_time.strftime("%d-%b-%Y")
                
                # 譌･譛ｬ隱槭ｒ蜷ｫ繧讀懃ｴ｢縺ｮ蝣ｴ蜷医・迚ｹ蛻･縺ｪ蜃ｦ逅・                if any(ord(c) > 127 for c in subject_pattern):
                    # UTF-8繧偵し繝昴・繝医☆繧九ｈ縺・↓險ｭ螳・                    try:
                        # UTF-8讀懃ｴ｢繧呈怏蜉ｹ蛹厄ｼ・mail縺ｧ繧ｵ繝昴・繝茨ｼ・                        self.connection.literal = subject_pattern.encode('utf-8')
                        search_criteria = f'SINCE "{since_date}" SUBJECT {{{len(self.connection.literal)}}}'
                        typ, data = self.connection.search('UTF-8', search_criteria)
                    except:
                        # UTF-8縺後し繝昴・繝医＆繧後↑縺・ｴ蜷医・譌･莉倥・縺ｿ縺ｧ讀懃ｴ｢
                        self.logger.warning("UTF-8讀懃ｴ｢縺後し繝昴・繝医＆繧後※縺・∪縺帙ｓ縲よ律莉倥・縺ｿ縺ｧ讀懃ｴ｢縺励∪縺吶・)
                        search_criteria = f'SINCE "{since_date}"'
                        typ, data = self.connection.search(None, search_criteria)
                else:
                    # ASCII譁・ｭ励・縺ｿ縺ｮ蝣ｴ蜷医・騾壼ｸｸ縺ｮ讀懃ｴ｢
                    search_criteria = f'SINCE "{since_date}" SUBJECT "{subject_pattern}"'
                    typ, data = self.connection.search(None, search_criteria)
                
                if typ == 'OK':
                    email_ids = data[0].split()
                    
                    if email_ids:
                        # 譁ｰ縺励＞繝｡繝ｼ繝ｫ縺九ｉ鬆・↓遒ｺ隱搾ｼ磯・・ｼ・                        for email_id in reversed(email_ids):
                            self.logger.info(f"繝｡繝ｼ繝ｫID {email_id} 繧堤｢ｺ隱堺ｸｭ...")
                            
                            # 繝｡繝ｼ繝ｫ繧貞叙蠕・                            typ, msg_data = self.connection.fetch(email_id, '(RFC822)')
                            
                            if typ == 'OK':
                                # 繝｡繝ｼ繝ｫ繧定ｧ｣譫・                                raw_email = msg_data[0][1]
                                msg = email.message_from_bytes(raw_email)
                                
                                # 莉ｶ蜷阪ｒ遒ｺ隱・                                subject = msg.get('Subject', '')
                                if subject:
                                    try:
                                        # 莉ｶ蜷阪ｒ繝・さ繝ｼ繝・                                        decoded_subject = str(email.header.make_header(email.header.decode_header(subject)))
                                        self.logger.info(f"莉ｶ蜷・ {decoded_subject}")
                                        
                                        # 莉ｶ蜷阪ヱ繧ｿ繝ｼ繝ｳ縺ｨ荳閾ｴ縺吶ｋ縺狗｢ｺ隱・                                        if subject_pattern in decoded_subject:
                                            self.logger.info(f"隧ｲ蠖薙☆繧九Γ繝ｼ繝ｫ繧堤匱隕・ ID {email_id}, 莉ｶ蜷・ {decoded_subject}")
                                            
                                            # URL繧呈歓蜃ｺ
                                            download_url = self._extract_download_url(msg)
                                            if download_url:
                                                self.logger.info(f"繝繧ｦ繝ｳ繝ｭ繝ｼ繝蔚RL繧貞叙蠕・ {download_url}")
                                                return download_url
                                    except Exception as decode_error:
                                        self.logger.warning(f"莉ｶ蜷阪ョ繧ｳ繝ｼ繝峨お繝ｩ繝ｼ (ID {email_id}): {decode_error}")
                                        # 繝・さ繝ｼ繝峨お繝ｩ繝ｼ縺ｮ蝣ｴ蜷医・繧ｹ繧ｭ繝・・縺励※谺｡縺ｸ
                                        continue
                
                # 谺｡縺ｮ繝√ぉ繝・け縺ｾ縺ｧ蠕・ｩ・                remaining = (end_time - datetime.now()).total_seconds()
                if remaining > check_interval:
                    self.logger.info(f"谺｡縺ｮ繝√ぉ繝・け縺ｾ縺ｧ{check_interval}遘貞ｾ・ｩ・..")
                    time.sleep(check_interval)
                else:
                    time.sleep(max(1, remaining))
                    
            except Exception as e:
                self.logger.error(f"繝｡繝ｼ繝ｫ遒ｺ隱堺ｸｭ縺ｫ繧ｨ繝ｩ繝ｼ: {e}")
                # 繧ｨ繝ｩ繝ｼ譎ゅ・蟆代＠蠕・▲縺ｦ繝ｪ繝医Λ繧､
                time.sleep(check_interval)
        
        self.logger.warning(f"繧ｿ繧､繝繧｢繧ｦ繝・ {timeout}遘剃ｻ･蜀・↓繝｡繝ｼ繝ｫ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ縺ｧ縺励◆")
        return None
    
    def _extract_download_url(self, msg: email.message.Message) -> Optional[str]:
        """
        繝｡繝ｼ繝ｫ縺九ｉ繝繧ｦ繝ｳ繝ｭ繝ｼ繝蔚RL繧呈歓蜃ｺ
        
        Args:
            msg: 繝｡繝ｼ繝ｫ繝｡繝・そ繝ｼ繧ｸ
        
        Returns:
            繝繧ｦ繝ｳ繝ｭ繝ｼ繝蔚RL・郁ｦ九▽縺九ｉ縺ｪ縺・ｴ蜷医・None・・        """
        try:
            # 繝｡繝ｼ繝ｫ譛ｬ譁・ｒ蜿門ｾ・            body = ""
            
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            # 隍・焚縺ｮ繧ｨ繝ｳ繧ｳ繝ｼ繝・ぅ繝ｳ繧ｰ繧定ｩｦ陦・                            body = self._safe_decode_payload(payload)
                            if body:
                                break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = self._safe_decode_payload(payload)
            
            if not body:
                self.logger.warning("繝｡繝ｼ繝ｫ譛ｬ譁・ｒ蜿門ｾ励〒縺阪∪縺帙ｓ縺ｧ縺励◆")
                return None
            
            # URL繝代ち繝ｼ繝ｳ繧呈､懃ｴ｢
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+\.zip'
            urls = re.findall(url_pattern, body)
            
            if urls:
                # 譛蛻昴・ZIP繝輔ぃ繧､繝ｫURL繧定ｿ斐☆
                return urls[0]
            
            # 繧医ｊ荳闊ｬ逧・↑URL繝代ち繝ｼ繝ｳ繧りｩｦ縺・            general_url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
            all_urls = re.findall(general_url_pattern, body)
            
            # 繝繧ｦ繝ｳ繝ｭ繝ｼ繝蛾未騾｣縺ｮ繧ｭ繝ｼ繝ｯ繝ｼ繝峨ｒ蜷ｫ繧URL繧呈爾縺・            for url in all_urls:
                if any(keyword in url.lower() for keyword in ['download', 'dl', 'file']):
                    return url
            
            self.logger.warning("繝｡繝ｼ繝ｫ譛ｬ譁・°繧蔚RL縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ縺ｧ縺励◆")
            return None
            
        except Exception as e:
            self.logger.error(f"URL謚ｽ蜃ｺ荳ｭ縺ｫ繧ｨ繝ｩ繝ｼ: {e}")
            return None
    
    def _safe_decode_payload(self, payload: bytes) -> str:
        """
        繝壹う繝ｭ繝ｼ繝峨ｒ螳牙・縺ｫ繝・さ繝ｼ繝・        
        Args:
            payload: 繝舌う繝医ョ繝ｼ繧ｿ
        
        Returns:
            繝・さ繝ｼ繝峨＆繧後◆譁・ｭ怜・
        """
        # 隧ｦ陦後☆繧九お繝ｳ繧ｳ繝ｼ繝・ぅ繝ｳ繧ｰ繝ｪ繧ｹ繝・        encodings = ['utf-8', 'iso-2022-jp', 'shift_jis', 'euc-jp', 'ascii']
        
        for encoding in encodings:
            try:
                return payload.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                continue
        
        # 縺吶∋縺ｦ螟ｱ謨励＠縺溷ｴ蜷医・繧ｨ繝ｩ繝ｼ繧堤┌隕悶＠縺ｦ繝・さ繝ｼ繝・        try:
            return payload.decode('utf-8', errors='ignore')
        except Exception:
            self.logger.warning("繝壹う繝ｭ繝ｼ繝峨・繝・さ繝ｼ繝峨↓螟ｱ謨励＠縺ｾ縺励◆")
            return ""
    
    def close(self):
        """謗･邯壹ｒ髢峨§繧・""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                self.logger.info("IMAP謗･邯壹ｒ髢峨§縺ｾ縺励◆")
            except:
                pass