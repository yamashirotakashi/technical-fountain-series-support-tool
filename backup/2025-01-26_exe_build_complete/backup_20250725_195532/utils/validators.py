"""蜈･蜉帶､懆ｨｼ繝｢繧ｸ繝･繝ｼ繝ｫ"""
import re
from pathlib import Path
from typing import List, Tuple, Optional


class Validators:
    """蜈･蜉帛､縺ｮ讀懆ｨｼ繧定｡後≧繧ｯ繝ｩ繧ｹ"""
    
    @staticmethod
    def validate_n_code(n_code: str) -> Tuple[bool, Optional[str]]:
        """
        N繧ｳ繝ｼ繝峨・蠖｢蠑上ｒ讀懆ｨｼ
        
        Args:
            n_code: 讀懆ｨｼ縺吶ｋN繧ｳ繝ｼ繝・        
        Returns:
            (讀懆ｨｼ邨先棡, 繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ)縺ｮ繧ｿ繝励Ν
        """
        n_code = n_code.strip()
        
        if not n_code:
            return False, "N繧ｳ繝ｼ繝峨′蜈･蜉帙＆繧後※縺・∪縺帙ｓ"
        
        # N繧ｳ繝ｼ繝峨・蠖｢蠑・ N + 5譯√・謨ｰ蟄・        pattern = r'^N\d{5}$'
        if not re.match(pattern, n_code, re.IGNORECASE):
            return False, f"辟｡蜉ｹ縺ｪN繧ｳ繝ｼ繝牙ｽ｢蠑・ {n_code} (豁｣縺励＞蠖｢蠑・ N00001)"
        
        return True, None
    
    @staticmethod
    def validate_n_codes(n_codes_text: str) -> Tuple[List[str], List[str]]:
        """
        隍・焚縺ｮN繧ｳ繝ｼ繝峨ｒ讀懆ｨｼ
        
        Args:
            n_codes_text: 繧ｫ繝ｳ繝槭√ち繝悶√∪縺溘・謾ｹ陦後〒蛹ｺ蛻・ｉ繧後◆N繧ｳ繝ｼ繝峨・繝・く繧ｹ繝・        
        Returns:
            (譛牙柑縺ｪN繧ｳ繝ｼ繝峨・繝ｪ繧ｹ繝・ 繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ縺ｮ繝ｪ繧ｹ繝・縺ｮ繧ｿ繝励Ν
        """
        # 繧ｫ繝ｳ繝槭√ち繝悶∵隼陦後〒蛻・牡・医せ繝壹・繧ｹ繧ょ性繧・・        n_codes = re.split(r'[,\t\n\s]+', n_codes_text)
        n_codes = [code.strip() for code in n_codes if code.strip()]
        
        valid_codes = []
        errors = []
        
        for code in n_codes:
            is_valid, error = Validators.validate_n_code(code)
            if is_valid:
                # 螟ｧ譁・ｭ励↓邨ｱ荳
                valid_codes.append(code.upper())
            else:
                errors.append(error)
        
        return valid_codes, errors
    
    @staticmethod
    def validate_file_path(path: str, must_exist: bool = True) -> Tuple[bool, Optional[str]]:
        """
        繝輔ぃ繧､繝ｫ繝代せ繧呈､懆ｨｼ
        
        Args:
            path: 讀懆ｨｼ縺吶ｋ繝代せ
            must_exist: 繝輔ぃ繧､繝ｫ縺悟ｭ伜惠縺吶ｋ蠢・ｦ√′縺ゅｋ縺・        
        Returns:
            (讀懆ｨｼ邨先棡, 繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ)縺ｮ繧ｿ繝励Ν
        """
        if not path:
            return False, "繝代せ縺梧欠螳壹＆繧後※縺・∪縺帙ｓ"
        
        path_obj = Path(path)
        
        if must_exist and not path_obj.exists():
            return False, f"繝代せ縺悟ｭ伜惠縺励∪縺帙ｓ: {path}"
        
        return True, None
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        繝｡繝ｼ繝ｫ繧｢繝峨Ξ繧ｹ繧呈､懆ｨｼ
        
        Args:
            email: 讀懆ｨｼ縺吶ｋ繝｡繝ｼ繝ｫ繧｢繝峨Ξ繧ｹ
        
        Returns:
            (讀懆ｨｼ邨先棡, 繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ)縺ｮ繧ｿ繝励Ν
        """
        if not email:
            return False, "繝｡繝ｼ繝ｫ繧｢繝峨Ξ繧ｹ縺悟・蜉帙＆繧後※縺・∪縺帙ｓ"
        
        # 邁｡譏鍋噪縺ｪ繝｡繝ｼ繝ｫ繧｢繝峨Ξ繧ｹ讀懆ｨｼ
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, f"辟｡蜉ｹ縺ｪ繝｡繝ｼ繝ｫ繧｢繝峨Ξ繧ｹ蠖｢蠑・ {email}"
        
        return True, None
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, Optional[str]]:
        """
        URL繧呈､懆ｨｼ
        
        Args:
            url: 讀懆ｨｼ縺吶ｋURL
        
        Returns:
            (讀懆ｨｼ邨先棡, 繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ)縺ｮ繧ｿ繝励Ν
        """
        if not url:
            return False, "URL縺悟・蜉帙＆繧後※縺・∪縺帙ｓ"
        
        # 邁｡譏鍋噪縺ｪURL讀懆ｨｼ
        pattern = r'^https?://[^\s]+$'
        if not re.match(pattern, url):
            return False, f"辟｡蜉ｹ縺ｪURL蠖｢蠑・ {url}"
        
        return True, None