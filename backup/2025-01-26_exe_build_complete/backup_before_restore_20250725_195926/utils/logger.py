"""繝ｭ繧ｰ邂｡逅・Δ繧ｸ繝･繝ｼ繝ｫ"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class LoggerManager:
    """繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ蜈ｨ菴薙・繝ｭ繧ｰ繧堤ｮ｡逅・☆繧九け繝ｩ繧ｹ"""
    
    def __init__(self, log_dir: str = "logs", app_name: str = "TechnicalFountainTool"):
        """
        繝ｭ繧ｰ繝槭ロ繝ｼ繧ｸ繝｣繝ｼ繧貞・譛溷喧
        
        Args:
            log_dir: 繝ｭ繧ｰ繝輔ぃ繧､繝ｫ繧剃ｿ晏ｭ倥☆繧九ョ繧｣繝ｬ繧ｯ繝医Μ
            app_name: 繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ蜷・        """
        self.log_dir = Path(log_dir)
        self.app_name = app_name
        self.log_handlers = []
        
        # 繝ｭ繧ｰ繝・ぅ繝ｬ繧ｯ繝医Μ繧剃ｽ懈・
        self.log_dir.mkdir(exist_ok=True)
        
        # 繝ｭ繧ｰ繝輔ぃ繧､繝ｫ蜷阪ｒ逕滓・
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"{app_name}_{timestamp}.log"
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        謖・ｮ壹＆繧後◆蜷榊燕縺ｮ繝ｭ繧ｬ繝ｼ繧貞叙蠕・        
        Args:
            name: 繝ｭ繧ｬ繝ｼ蜷・        
        Returns:
            險ｭ螳壽ｸ医∩縺ｮ繝ｭ繧ｬ繝ｼ
        """
        logger = logging.getLogger(name)
        
        # 縺吶〒縺ｫ險ｭ螳壽ｸ医∩縺ｮ蝣ｴ蜷医・縺昴・縺ｾ縺ｾ霑斐☆
        if logger.handlers:
            return logger
        
        logger.setLevel(logging.DEBUG)
        
        # 繧ｳ繝ｳ繧ｽ繝ｼ繝ｫ繝上Φ繝峨Λ繝ｼ
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # 繝輔ぃ繧､繝ｫ繝上Φ繝峨Λ繝ｼ
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # 繝上Φ繝峨Λ繝ｼ繧定ｿｽ蜉
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        self.log_handlers.extend([console_handler, file_handler])
        
        return logger
    
    def add_gui_handler(self, gui_handler: logging.Handler):
        """
        GUI逕ｨ縺ｮ繝ｭ繧ｰ繝上Φ繝峨Λ繝ｼ繧定ｿｽ蜉
        
        Args:
            gui_handler: GUI縺ｫ陦ｨ遉ｺ縺吶ｋ縺溘ａ縺ｮ繝上Φ繝峨Λ繝ｼ
        """
        # 縺吶∋縺ｦ縺ｮ譌｢蟄倥・繝ｭ繧ｬ繝ｼ縺ｫGUI繝上Φ繝峨Λ繝ｼ繧定ｿｽ蜉
        for name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(name)
            if name.startswith(self.app_name):
                logger.addHandler(gui_handler)
        
        self.log_handlers.append(gui_handler)
    
    def close(self):
        """縺吶∋縺ｦ縺ｮ繝上Φ繝峨Λ繝ｼ繧帝哩縺倥ｋ"""
        for handler in self.log_handlers:
            handler.close()


# 繧ｷ繝ｳ繧ｰ繝ｫ繝医Φ繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ
_logger_manager = None


def get_logger_manager() -> LoggerManager:
    """繝ｭ繧ｰ繝槭ロ繝ｼ繧ｸ繝｣繝ｼ縺ｮ繧ｷ繝ｳ繧ｰ繝ｫ繝医Φ繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ繧貞叙蠕・""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager


def get_logger(name: str) -> logging.Logger:
    """
    繝ｭ繧ｬ繝ｼ繧貞叙蠕励☆繧九・繝ｫ繝代・髢｢謨ｰ
    
    Args:
        name: 繝ｭ繧ｬ繝ｼ蜷・    
    Returns:
        險ｭ螳壽ｸ医∩縺ｮ繝ｭ繧ｬ繝ｼ
    """
    return get_logger_manager().get_logger(name)