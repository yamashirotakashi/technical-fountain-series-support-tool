"""繝ｯ繝ｼ繧ｯ繝輔Ο繝ｼ蜃ｦ逅・ｮ｡逅・Δ繧ｸ繝･繝ｼ繝ｫ"""
import os
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from core.google_sheet import GoogleSheetClient
from core.file_manager import FileManager
from core.word_processor import WordProcessor
from utils.logger import get_logger
from utils.config import get_config


class WorkflowProcessor(QObject):
    """蜃ｦ逅・ヵ繝ｭ繝ｼ蜈ｨ菴薙ｒ邂｡逅・☆繧九け繝ｩ繧ｹ"""
    
    # 繧ｷ繧ｰ繝翫Ν螳夂ｾｩ
    log_message = pyqtSignal(str, str)  # message, level
    progress_updated = pyqtSignal(int)  # progress value
    status_updated = pyqtSignal(str)  # status message
    confirmation_needed = pyqtSignal(str, str, object)  # title, message, callback
    folder_selection_needed = pyqtSignal(object, str, object)  # repo_path, repo_name, default_folder
    file_placement_confirmation_needed = pyqtSignal(str, list, object)  # honbun_folder_path, file_list, callback
    warning_dialog_needed = pyqtSignal(list, str)  # messages, result_type
    
    def __init__(self, email_address: str = None, email_password: str = None, process_mode: str = "traditional"):
        """
        WorkflowProcessor繧貞・譛溷喧
        
        Args:
            email_address: 繝｡繝ｼ繝ｫ繧｢繝峨Ξ繧ｹ・育怐逡･譎ゅ・險ｭ螳壹°繧牙叙蠕暦ｼ・            email_password: 繝｡繝ｼ繝ｫ繝代せ繝ｯ繝ｼ繝・            process_mode: 蜃ｦ逅・婿蠑・("traditional" 縺ｾ縺溘・ "api")
        """
        super().__init__()
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.process_mode = process_mode
        
        # 蛻晄悄蛹冶ｩｳ邏ｰ繝ｭ繧ｰ
        self.logger.info(f"[INIT] WorkflowProcessor蛻晄悄蛹夜幕蟋・)
        self.logger.info(f"[INIT] process_mode: {process_mode}")
        self.logger.info(f"[INIT] email_address: {email_address}")
        self.logger.info(f"[INIT] has email_password: {email_password is not None}")
        
        # 蜷・さ繝ｳ繝昴・繝阪Φ繝医ｒ蛻晄悄蛹・        self.google_client = GoogleSheetClient()
        self.file_manager = FileManager()
        self.word_processor = WordProcessor()
        
        # WebClient縺ｨEmailMonitor縺ｯ驕・ｻｶ蛻晄悄蛹・        self._web_client = None
        self._email_monitor = None
        self._api_processor = None
        
        # 螻樊ｧ繝√ぉ繝・け
        self.logger.debug(f"[INIT] _api_processor蛻晄悄蛹・ {self._api_processor}")
        self.logger.debug(f"[INIT] hasattr(_api_processor): {hasattr(self, '_api_processor')}")
        self.logger.debug(f"[INIT] hasattr(api_processor): {hasattr(self, 'api_processor')}")
        
        # 蜈ｨ螻樊ｧ縺ｮ遒ｺ隱・        self.logger.debug(f"[INIT] 蜈ｨ螻樊ｧ: {dir(self)}")
        
        # 繝｡繝ｼ繝ｫ險ｭ螳夲ｼ育腸蠅・､画焚繧貞━蜈茨ｼ・        email_config = self.config.get_email_config()
        self.email_address = email_address or os.getenv('GMAIL_ADDRESS') or email_config.get('default_address')
        self.email_password = email_password or os.getenv('GMAIL_APP_PASSWORD')
        
        # 繝繧､繧｢繝ｭ繧ｰ邨先棡縺ｮ菫晏ｭ倡畑
        self.dialog_result = None
        self.file_placement_result = None
    
    @property
    def web_client(self):
        """WebClient縺ｮ驕・ｻｶ蛻晄悄蛹・""
        if self._web_client is None:
            from core.web_client import WebClient
            self._web_client = WebClient()
        return self._web_client
    
    @property
    def email_monitor(self):
        """EmailMonitor縺ｮ驕・ｻｶ蛻晄悄蛹・""
        if self._email_monitor is None and self.email_password:
            from core.email_monitor import EmailMonitor
            self._email_monitor = EmailMonitor(self.email_address, self.email_password)
            self._email_monitor.connect()
        return self._email_monitor
    
    @property
    def api_processor(self):
        """ApiProcessor縺ｮ驕・ｻｶ蛻晄悄蛹・""
        self.logger.debug(f"[PROPERTY] api_processor繝励Ο繝代ユ繧｣縺悟他縺ｰ繧後∪縺励◆")
        self.logger.debug(f"[PROPERTY] _api_processor迴ｾ蝨ｨ縺ｮ蛟､: {self._api_processor}")
        
        if self._api_processor is None:
            self.logger.debug(f"[PROPERTY] ApiProcessor繧偵う繝ｳ繝昴・繝井ｸｭ...")
            from core.api_processor import ApiProcessor
            
            self.logger.debug(f"[PROPERTY] ApiProcessor繧偵う繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ蛹紋ｸｭ...")
            self._api_processor = ApiProcessor()
            
            self.logger.debug(f"[PROPERTY] 繧ｷ繧ｰ繝翫Ν繧呈磁邯壻ｸｭ...")
            # 繧ｷ繧ｰ繝翫Ν繧呈磁邯・            self._api_processor.log_message.connect(self.log_message.emit)
            self._api_processor.progress_updated.connect(self.progress_updated.emit)
            self._api_processor.warning_dialog_needed.connect(self.warning_dialog_needed.emit)
            
            self.logger.debug(f"[PROPERTY] ApiProcessor蛻晄悄蛹門ｮ御ｺ・ {self._api_processor}")
            
        return self._api_processor
    
    def process_n_codes(self, n_codes: List[str]):
        """
        隍・焚縺ｮN繧ｳ繝ｼ繝峨ｒ蜃ｦ逅・        
        Args:
            n_codes: 蜃ｦ逅・☆繧起繧ｳ繝ｼ繝峨・繝ｪ繧ｹ繝・        """
        total = len(n_codes)
        self.emit_log(f"蜃ｦ逅・幕蟋・ {total}蛟九・N繧ｳ繝ｼ繝・, "INFO")
        
        for idx, n_code in enumerate(n_codes):
            self.emit_status(f"蜃ｦ逅・ｸｭ: {n_code} ({idx + 1}/{total})")
            self.emit_progress(int((idx / total) * 100))
            
            try:
                self.process_single_n_code(n_code)
                self.emit_log(f"笨・{n_code} 縺ｮ蜃ｦ逅・′螳御ｺ・＠縺ｾ縺励◆", "INFO")
            except Exception as e:
                self.emit_log(f"笨・{n_code} 縺ｮ蜃ｦ逅・↓螟ｱ謨・ {str(e)}", "ERROR")
                self.logger.error(f"蜃ｦ逅・お繝ｩ繝ｼ {n_code}: {e}", exc_info=True)
        
        self.emit_progress(100)
        self.emit_status("縺吶∋縺ｦ縺ｮ蜃ｦ逅・′螳御ｺ・＠縺ｾ縺励◆")
        self.emit_log("蜃ｦ逅・ｮ御ｺ・, "INFO")
    
    def process_single_n_code(self, n_code: str):
        """
        蜊倅ｸ縺ｮN繧ｳ繝ｼ繝峨ｒ蜃ｦ逅・        
        Args:
            n_code: 蜃ｦ逅・☆繧起繧ｳ繝ｼ繝・        """
        self.logger.info(f"N繧ｳ繝ｼ繝牙・逅・幕蟋・ {n_code}")
        
        # 1. Google繧ｷ繝ｼ繝医°繧峨Μ繝昴ず繝医Μ蜷阪ｒ蜿門ｾ・        self.emit_log(f"Google繧ｷ繝ｼ繝医°繧・{n_code} 繧呈､懃ｴ｢荳ｭ...", "INFO")
        repo_info = self.google_client.search_n_code(n_code)
        
        if not repo_info:
            raise ValueError(f"N繧ｳ繝ｼ繝・{n_code} 縺隈oogle繧ｷ繝ｼ繝医↓隕九▽縺九ｊ縺ｾ縺帙ｓ")
        
        repo_name = repo_info['repository_name']
        self.emit_log(f"繝ｪ繝昴ず繝医Μ蜷・ {repo_name}", "INFO")
        
        # 2. 繝ｪ繝昴ず繝医Μ繝輔か繝ｫ繝繧呈､懃ｴ｢
        self.emit_log(f"繝ｪ繝昴ず繝医Μ繝輔か繝ｫ繝繧呈､懃ｴ｢荳ｭ: {repo_name}", "INFO")
        repo_path = self.file_manager.find_repository_folder(repo_name)
        
        if not repo_path:
            raise ValueError(f"繝ｪ繝昴ず繝医Μ繝輔か繝ｫ繝縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ: {repo_name}")
        
        # 3. 菴懈･ｭ繝輔か繝ｫ繝繧堤音螳・        self.emit_log("菴懈･ｭ繝輔か繝ｫ繝繧呈､懃ｴ｢荳ｭ...", "INFO")
        
        # 菫晏ｭ倥＆繧後◆險ｭ螳壹∪縺溘・閾ｪ蜍墓､懷・縺輔ｌ縺滉ｽ懈･ｭ繝輔か繝ｫ繝繧貞叙蠕・        default_work_folder = self.file_manager.find_work_folder_interactive(repo_path, repo_name)
        
        # 繝輔か繝ｫ繝驕ｸ謚槭ム繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ・医す繧ｰ繝翫Ν繧堤匱陦鯉ｼ・        self.selected_work_folder = None
        self.folder_selection_completed = False
        self.folder_selection_needed.emit(repo_path, repo_name, default_work_folder)
        
        # 繝繧､繧｢繝ｭ繧ｰ縺ｮ邨先棡繧貞ｾ・▽・域怙螟ｧ30遘抵ｼ・        timeout = 30
        start_time = time.time()
        while not self.folder_selection_completed and (time.time() - start_time) < timeout:
            time.sleep(0.1)
            # GUI繧､繝吶Φ繝医Ν繝ｼ繝励ｒ蜃ｦ逅・☆繧九◆繧√↓蠢・ｦ・            from PyQt6.QtCore import QCoreApplication
            QCoreApplication.processEvents()
        
        work_folder = self.selected_work_folder
        
        if not work_folder:
            raise ValueError("菴懈･ｭ繝輔か繝ｫ繝縺碁∈謚槭＆繧後∪縺帙ｓ縺ｧ縺励◆")
        
        # 4. ZIP繝輔ぃ繧､繝ｫ繧剃ｽ懈・
        self.emit_log("ZIP繝輔ぃ繧､繝ｫ繧剃ｽ懈・荳ｭ...", "INFO")
        zip_path = self.file_manager.create_zip(work_folder)
        
        # 5. 蜃ｦ逅・婿蠑上↓蠢懊§縺ｦ蛻・ｲ・        self.logger.info(f"[PROCESS] 蜃ｦ逅・婿蠑上・蛻・ｲ・ process_mode={self.process_mode}")
        if self.process_mode == "api":
            # API譁ｹ蠑上・蜃ｦ逅・            self.emit_log("API譁ｹ蠑上〒螟画鋤蜃ｦ逅・ｒ髢句ｧ・..", "INFO")
            
            # 繧ｨ繝ｩ繝ｼ繝医Ξ繝ｼ繧ｹ逕ｨ縺ｮ隧ｳ邏ｰ繝ｭ繧ｰ
            self.logger.debug(f"[API] api_processor蜿門ｾ怜燕縺ｮ螻樊ｧ繝√ぉ繝・け")
            self.logger.debug(f"[API] hasattr(self, '_api_processor'): {hasattr(self, '_api_processor')}")
            self.logger.debug(f"[API] hasattr(self, 'api_processor'): {hasattr(self, 'api_processor')}")
            self.logger.debug(f"[API] self._api_processor: {self._api_processor}")
            
            try:
                # API縺ｧ蜃ｦ逅・ｼ医・繝ｭ繝代ユ繧｣繧剃ｽｿ逕ｨ縺励※驕・ｻｶ蛻晄悄蛹厄ｼ・                self.logger.debug(f"[API] api_processor繝励Ο繝代ユ繧｣縺ｫ繧｢繧ｯ繧ｻ繧ｹ荳ｭ...")
                api_proc = self.api_processor
                self.logger.debug(f"[API] api_processor蜿門ｾ玲・蜉・ {api_proc}")
                
                self.logger.debug(f"[API] process_zip_file繧貞他縺ｳ蜃ｺ縺嶺ｸｭ...")
                self.logger.debug(f"[API] ZIP繝輔ぃ繧､繝ｫ繝代せ: {zip_path}")
                self.logger.debug(f"[API] ZIP繝輔ぃ繧､繝ｫ繧ｵ繧､繧ｺ: {zip_path.stat().st_size:,} bytes")
                
                success, download_path, warnings = api_proc.process_zip_file(zip_path)
                
                self.logger.debug(f"[API] process_zip_file螳御ｺ・ success={success}, download_path={download_path}, warnings={len(warnings) if warnings else 0}")
                
                if warnings:
                    self.logger.debug(f"[API] 隴ｦ蜻翫Γ繝・そ繝ｼ繧ｸ:")
                    for i, warning in enumerate(warnings[:5]):  # 譛蛻昴・5莉ｶ
                        self.logger.debug(f"  {i+1}. {warning}")
                
            except AttributeError as e:
                self.logger.error(f"[API] AttributeError隧ｳ邏ｰ: {e}")
                self.logger.error(f"[API] 蛻ｩ逕ｨ蜿ｯ閭ｽ縺ｪ螻樊ｧ: {[attr for attr in dir(self) if not attr.startswith('_')]}")
                self.logger.error(f"[API] 繝励Λ繧､繝吶・繝亥ｱ樊ｧ: {[attr for attr in dir(self) if attr.startswith('_') and not attr.startswith('__')]}")
                raise
            except Exception as e:
                self.logger.error(f"[API] 莠域悄縺励↑縺・お繝ｩ繝ｼ: {type(e).__name__}: {e}")
                self.logger.error(f"[API] 繧ｨ繝ｩ繝ｼ隧ｳ邏ｰ: {str(e)}")
                import traceback
                self.logger.error(f"[API] 繧ｹ繧ｿ繝・け繝医Ξ繝ｼ繧ｹ:\n{traceback.format_exc()}")
                raise
            
            if not success:
                # 螟ｱ謨励・蝣ｴ蜷医∬ｩｳ邏ｰ縺ｪ繧ｨ繝ｩ繝ｼ諠・ｱ繧貞性繧√ｋ
                error_msg = "API螟画鋤蜃ｦ逅・′螟ｱ謨励＠縺ｾ縺励◆"
                if warnings:
                    error_msg += f" (繧ｨ繝ｩ繝ｼ/隴ｦ蜻・ {', '.join(warnings[:3])})"
                self.logger.error(f"[API] 蜃ｦ逅・､ｱ謨励・隧ｳ邏ｰ: {error_msg}")
                raise ValueError(error_msg)
            
            if not download_path:
                # 繝繧ｦ繝ｳ繝ｭ繝ｼ繝峨ヵ繧｡繧､繝ｫ縺後↑縺・ｴ蜷茨ｼ医お繝ｩ繝ｼ縺ｮ縺ｿ・・                raise ValueError("螟画鋤繝輔ぃ繧､繝ｫ縺ｮ繝繧ｦ繝ｳ繝ｭ繝ｼ繝峨↓螟ｱ謨励＠縺ｾ縺励◆")
            
            # 謌仙粥縺ｾ縺溘・荳驛ｨ謌仙粥縺ｮ蝣ｴ蜷医∝・逅・ｒ邯夊｡・            # download_path縺ｯ螟画鋤貂医∩繝輔ぃ繧､繝ｫ縺ｮ繝代せ
            
        else:
            # 蠕捺擂譁ｹ蠑上・蜃ｦ逅・            self.emit_log("蠕捺擂譁ｹ蠑上〒蜃ｦ逅・ｒ髢句ｧ・..", "INFO")
            
            # 繝輔ぃ繧､繝ｫ繧偵い繝・・繝ｭ繝ｼ繝・            self.emit_log("繝輔ぃ繧､繝ｫ繧偵い繝・・繝ｭ繝ｼ繝我ｸｭ...", "INFO")
            upload_success = self.web_client.upload_file(zip_path, self.email_address)
            
            if not upload_success:
                raise ValueError("繝輔ぃ繧､繝ｫ縺ｮ繧｢繝・・繝ｭ繝ｼ繝峨↓螟ｱ謨励＠縺ｾ縺励◆")
            
            # 6. 繝｡繝ｼ繝ｫ繧堤屮隕・            if self.email_password:
                self.emit_log("螟画鋤螳御ｺ・Γ繝ｼ繝ｫ繧貞ｾ・ｩ滉ｸｭ...", "INFO")
                
                # email_monitor繝励Ο繝代ユ繧｣繧剃ｽｿ逕ｨ・磯≦蟒ｶ蛻晄悄蛹厄ｼ・                download_url = self.email_monitor.wait_for_email()
                
                if not download_url:
                    raise ValueError("繧ｿ繧､繝繧｢繧ｦ繝・ 繝｡繝ｼ繝ｫ縺悟ｱ翫″縺ｾ縺帙ｓ縺ｧ縺励◆")
                
                # 7. 繝輔ぃ繧､繝ｫ繧偵ム繧ｦ繝ｳ繝ｭ繝ｼ繝・                self.emit_log("螟画鋤貂医∩繝輔ぃ繧､繝ｫ繧偵ム繧ｦ繝ｳ繝ｭ繝ｼ繝我ｸｭ...", "INFO")
                download_path = self.file_manager.temp_dir / f"{n_code}_converted.zip"
                download_success = self.web_client.download_file(download_url, download_path)
                
                if not download_success:
                    raise ValueError("繝輔ぃ繧､繝ｫ縺ｮ繝繧ｦ繝ｳ繝ｭ繝ｼ繝峨↓螟ｱ謨励＠縺ｾ縺励◆")
            else:
                self.emit_log("繝｡繝ｼ繝ｫ繝代せ繝ｯ繝ｼ繝峨′險ｭ螳壹＆繧後※縺・↑縺・◆繧√∵焔蜍輔〒繝繧ｦ繝ｳ繝ｭ繝ｼ繝峨＠縺ｦ縺上□縺輔＞", "WARNING")
                return
        
        # 8. ZIP繝輔ぃ繧､繝ｫ繧貞・逅・ｼ亥ｱ暮幕 + 1陦檎岼蜑企勁・・        self.emit_log("ZIP繝輔ぃ繧､繝ｫ繧貞・逅・ｸｭ...", "INFO")
        processed_files = self.word_processor.process_zip_file(download_path)
        
        if not processed_files:
            raise ValueError("ZIP繝輔ぃ繧､繝ｫ縺ｮ蜃ｦ逅・↓螟ｱ謨励＠縺ｾ縺励◆")
        
        self.emit_log(f"{len(processed_files)}蛟九・Word繝輔ぃ繧､繝ｫ繧貞・逅・＠縺ｾ縺励◆", "INFO")
        
        # 9. N繝輔か繝ｫ繝縺ｨ譛ｬ譁・ヵ繧ｩ繝ｫ繝縺ｮ蟄伜惠遒ｺ隱・        ncode_folder = self.word_processor.find_ncode_folder(n_code)
        if not ncode_folder:
            raise ValueError(f"N繧ｳ繝ｼ繝峨ヵ繧ｩ繝ｫ繝縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ: {n_code}")
        
        honbun_folder = self.word_processor.find_honbun_folder(ncode_folder)
        if not honbun_folder:
            raise ValueError(f"譛ｬ譁・ヵ繧ｩ繝ｫ繝縺ｮ蝣ｴ謇繧堤音螳壹〒縺阪∪縺帙ｓ: {ncode_folder}")
        
        # 10. 譛ｬ譁・ヵ繧ｩ繝ｫ繝繝代せ遒ｺ隱搾ｼ郁ｦ∽ｻｶ2.6・・        self.emit_log("譛ｬ譁・ヵ繧ｩ繝ｫ繝繝代せ遒ｺ隱阪ｒ陦ｨ遉ｺ荳ｭ...", "INFO")
        selected_files = self._show_file_placement_confirmation(str(honbun_folder), processed_files)
        
        if not selected_files:
            raise ValueError("繝ｦ繝ｼ繧ｶ繝ｼ縺ｫ繧医▲縺ｦ蜃ｦ逅・′繧ｭ繝｣繝ｳ繧ｻ繝ｫ縺輔ｌ縺ｾ縺励◆")
        
        # 11. 繝輔ぃ繧､繝ｫ驟咲ｽｮ蜃ｦ逅・ｒ螳溯｡・        self.emit_log(f"驕ｸ謚槭＆繧後◆{len(selected_files)}蛟九・繝輔ぃ繧､繝ｫ繧呈悽譁・ヵ繧ｩ繝ｫ繝縺ｫ驟咲ｽｮ荳ｭ...", "INFO")
        copy_result = self._copy_files_to_honbun_folder(selected_files, honbun_folder)
        
        if not copy_result:
            raise ValueError("繝輔ぃ繧､繝ｫ驟咲ｽｮ縺ｫ螟ｱ謨励＠縺ｾ縺励◆")
        
        self.emit_log(f"笨・{n_code} 縺ｮ蜃ｦ逅・′螳御ｺ・＠縺ｾ縺励◆", "INFO")
    
    def emit_log(self, message: str, level: str = "INFO"):
        """繝ｭ繧ｰ繝｡繝・そ繝ｼ繧ｸ繧帝∽ｿ｡"""
        # 繝ｭ繧ｰ繝ｬ繝吶Ν繧呈焚蛟､縺ｫ螟画鋤
        import logging
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        numeric_level = level_map.get(level.upper(), logging.INFO)
        self.logger.log(numeric_level, message)
        self.log_message.emit(message, level)
    
    def emit_progress(self, value: int):
        """騾ｲ謐励ｒ騾∽ｿ｡"""
        self.progress_updated.emit(value)
    
    def emit_status(self, message: str):
        """繧ｹ繝・・繧ｿ繧ｹ繧帝∽ｿ｡"""
        self.status_updated.emit(message)
    
    def _copy_files_to_honbun_folder(self, processed_files: List[Path], honbun_folder: Path) -> bool:
        """
        蜃ｦ逅・ｸ医∩繝輔ぃ繧､繝ｫ繧呈悽譁・ヵ繧ｩ繝ｫ繝縺ｫ驟咲ｽｮ
        
        Args:
            processed_files: 蜃ｦ逅・ｸ医∩繝輔ぃ繧､繝ｫ縺ｮ繝代せ繝ｪ繧ｹ繝・            honbun_folder: 驟咲ｽｮ蜈医・譛ｬ譁・ヵ繧ｩ繝ｫ繝
        
        Returns:
            驟咲ｽｮ縺梧・蜉溘＠縺溷ｴ蜷・rue
        """
        try:
            import shutil
            
            # 譛ｬ譁・ヵ繧ｩ繝ｫ繝縺悟ｭ伜惠縺励↑縺・ｴ蜷医・菴懈・
            honbun_folder.mkdir(parents=True, exist_ok=True)
            self.emit_log(f"譛ｬ譁・ヵ繧ｩ繝ｫ繝繧堤｢ｺ隱・菴懈・: {honbun_folder}", "INFO")
            
            success_count = 0
            for file_path in processed_files:
                try:
                    target_path = honbun_folder / file_path.name
                    shutil.copy2(file_path, target_path)
                    success_count += 1
                    self.emit_log(f"繝輔ぃ繧､繝ｫ繧ｳ繝斐・螳御ｺ・ {file_path.name}", "INFO")
                except Exception as e:
                    self.emit_log(f"繝輔ぃ繧､繝ｫ繧ｳ繝斐・繧ｨ繝ｩ繝ｼ {file_path.name}: {e}", "ERROR")
            
            self.emit_log(f"繝輔ぃ繧､繝ｫ驟咲ｽｮ螳御ｺ・ {success_count}/{len(processed_files)} 繝輔ぃ繧､繝ｫ", "INFO")
            return success_count > 0
            
        except Exception as e:
            self.emit_log(f"繝輔ぃ繧､繝ｫ驟咲ｽｮ蜃ｦ逅・お繝ｩ繝ｼ: {e}", "ERROR")
            return False
    
    def _show_file_placement_confirmation(self, honbun_folder_path: str, file_list: List[Path]) -> List[Path]:
        """
        繝輔ぃ繧､繝ｫ驟咲ｽｮ遒ｺ隱阪ム繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ・亥酔譛溽噪縺ｫ・・        
        Args:
            honbun_folder_path: 譛ｬ譁・ヵ繧ｩ繝ｫ繝縺ｮ繝代せ
            file_list: 蜃ｦ逅・ｸ医∩繝輔ぃ繧､繝ｫ縺ｮ繝ｪ繧ｹ繝・        
        Returns:
            驕ｸ謚槭＆繧後◆繝輔ぃ繧､繝ｫ縺ｮ繝ｪ繧ｹ繝茨ｼ医く繝｣繝ｳ繧ｻ繝ｫ縺ｮ蝣ｴ蜷医・遨ｺ繝ｪ繧ｹ繝茨ｼ・        """
        import time
        
        self.file_placement_result = None
        
        # 繧ｷ繧ｰ繝翫Ν繧堤匱陦後＠縺ｦ遒ｺ隱阪ム繧､繧｢繝ｭ繧ｰ陦ｨ遉ｺ繧定ｦ∵ｱ・        self.file_placement_confirmation_needed.emit(honbun_folder_path, file_list, self.on_file_placement_confirmed)
        
        # 邨先棡繧貞ｾ・ｩ滂ｼ・I繧ｹ繝ｬ繝・ラ縺ｧ蜃ｦ逅・＆繧後ｋ縺ｾ縺ｧ・・        timeout = 60  # 1蛻・・繧ｿ繧､繝繧｢繧ｦ繝・        start_time = time.time()
        while self.file_placement_result is None and (time.time() - start_time) < timeout:
            time.sleep(0.1)
            # GUI繧､繝吶Φ繝医Ν繝ｼ繝励ｒ蜃ｦ逅・☆繧九◆繧√↓蠢・ｦ・            from PyQt6.QtCore import QCoreApplication
            QCoreApplication.processEvents()
        
        if self.file_placement_result is None:
            self.emit_log("繝輔ぃ繧､繝ｫ驟咲ｽｮ遒ｺ隱阪′繧ｿ繧､繝繧｢繧ｦ繝医＠縺ｾ縺励◆", "ERROR")
            return []
        
        return self.file_placement_result if self.file_placement_result else []
    
    def on_file_placement_confirmed(self, selected_files: List[Path]):
        """繝輔ぃ繧､繝ｫ驟咲ｽｮ遒ｺ隱阪・邨先棡繧貞女菫｡"""
        self.file_placement_result = selected_files
        self.emit_log(f"繝輔ぃ繧､繝ｫ驟咲ｽｮ遒ｺ隱咲ｵ先棡: {len(selected_files)}蛟九・繝輔ぃ繧､繝ｫ繧帝∈謚・, "INFO")
    
    def _confirm_path(self, title: str, message: str) -> bool:
        """
        繝代せ遒ｺ隱阪ム繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ・亥酔譛溽噪縺ｫ・・        
        Args:
            title: 繝繧､繧｢繝ｭ繧ｰ繧ｿ繧､繝医Ν
            message: 遒ｺ隱阪Γ繝・そ繝ｼ繧ｸ
        
        Returns:
            繝ｦ繝ｼ繧ｶ繝ｼ縺梧価隱阪＠縺溷ｴ蜷・rue
        """
        # 邁｡譏鍋噪縺ｪ螳溯｣・ｼ亥ｮ滄圀縺ｮGUI縺ｧ縺ｯ驕ｩ蛻・↑繝繧､繧｢繝ｭ繧ｰ繧剃ｽｿ逕ｨ・・        self.emit_log(f"遒ｺ隱・ {message}", "INFO")
        return True  # 繝・ヵ繧ｩ繝ｫ繝医〒True繧定ｿ斐☆
    
    def set_selected_work_folder(self, folder_path: str):
        """驕ｸ謚槭＆繧後◆菴懈･ｭ繝輔か繝ｫ繝繧定ｨｭ螳・""
        self.selected_work_folder = Path(folder_path) if folder_path else None
        self.folder_selection_completed = True
    
    def cleanup(self):
        """繝ｪ繧ｽ繝ｼ繧ｹ繧偵け繝ｪ繝ｼ繝ｳ繧｢繝・・"""
        if self._email_monitor:
            self._email_monitor.close()
        if self._web_client:
            self._web_client.close()
        self.file_manager.cleanup_temp_files()