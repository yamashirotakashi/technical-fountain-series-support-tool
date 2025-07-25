"""險ｭ螳夂ｮ｡逅・Δ繧ｸ繝･繝ｼ繝ｫ"""
import json
import os
from pathlib import Path
from typing import Any, Dict


class Config:
    """繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ險ｭ螳壹ｒ邂｡逅・☆繧九け繝ｩ繧ｹ"""
    
    def __init__(self, config_path: str = None):
        """
        險ｭ螳壹ｒ蛻晄悄蛹・        
        Args:
            config_path: 險ｭ螳壹ヵ繧｡繧､繝ｫ縺ｮ繝代せ・育怐逡･譎ゅ・繝・ヵ繧ｩ繝ｫ繝医ヱ繧ｹ繧剃ｽｿ逕ｨ・・        """
        if config_path is None:
            # 繝・ヵ繧ｩ繝ｫ繝医・險ｭ螳壹ヵ繧｡繧､繝ｫ繝代せ繧呈ｧ狗ｯ・            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "settings.json"
        
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """險ｭ螳壹ヵ繧｡繧､繝ｫ繧定ｪｭ縺ｿ霎ｼ繧"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"險ｭ螳壹ヵ繧｡繧､繝ｫ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        繝峨ャ繝郁ｨ俶ｳ輔〒險ｭ螳壼､繧貞叙蠕・        
        Args:
            key_path: 蜿門ｾ励☆繧九く繝ｼ縺ｮ繝代せ・井ｾ・ "google_sheet.sheet_id"・・            default: 繧ｭ繝ｼ縺悟ｭ伜惠縺励↑縺・ｴ蜷医・繝・ヵ繧ｩ繝ｫ繝亥､
        
        Returns:
            險ｭ螳壼､
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_google_sheet_config(self) -> Dict[str, str]:
        """Google Sheet髢｢騾｣縺ｮ險ｭ螳壹ｒ蜿門ｾ・""
        return self._config.get('google_sheet', {})
    
    def get_paths_config(self) -> Dict[str, str]:
        """繝代せ髢｢騾｣縺ｮ險ｭ螳壹ｒ蜿門ｾ・""
        return self._config.get('paths', {})
    
    def get_web_config(self) -> Dict[str, str]:
        """Web髢｢騾｣縺ｮ險ｭ螳壹ｒ蜿門ｾ・""
        return self._config.get('web', {})
    
    def get_email_config(self) -> Dict[str, Any]:
        """繝｡繝ｼ繝ｫ髢｢騾｣縺ｮ險ｭ螳壹ｒ蜿門ｾ・""
        return self._config.get('email', {})
    
    def get_credentials_path(self) -> Path:
        """Google隱崎ｨｼ諠・ｱ繝輔ぃ繧､繝ｫ縺ｮ繝代せ繧貞叙蠕暦ｼ育ｵｶ蟇ｾ繝代せ縺ｫ螟画鋤・・""
        creds_path = self.get('google_sheet.credentials_path')
        if creds_path:
            path = Path(creds_path)
            if not path.is_absolute():
                # 逶ｸ蟇ｾ繝代せ縺ｮ蝣ｴ蜷医・險ｭ螳壹ヵ繧｡繧､繝ｫ縺九ｉ縺ｮ逶ｸ蟇ｾ繝代せ縺ｨ縺励※隗｣豎ｺ
                path = (self.config_path.parent / path).resolve()
            return path
        return None


# 繧ｷ繝ｳ繧ｰ繝ｫ繝医Φ繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ
_config_instance = None


def get_config() -> Config:
    """險ｭ螳壹・繧ｷ繝ｳ繧ｰ繝ｫ繝医Φ繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ繧貞叙蠕・""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance