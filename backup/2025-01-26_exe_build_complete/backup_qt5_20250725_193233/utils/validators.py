"""入力検証モジュール"""
import re
from pathlib import Path
from typing import List, Tuple, Optional


class Validators:
    """入力値の検証を行うクラス"""
    
    @staticmethod
    def validate_n_code(n_code: str) -> Tuple[bool, Optional[str]]:
        """
        Nコードの形式を検証
        
        Args:
            n_code: 検証するNコード
        
        Returns:
            (検証結果, エラーメッセージ)のタプル
        """
        n_code = n_code.strip()
        
        if not n_code:
            return False, "Nコードが入力されていません"
        
        # Nコードの形式: N + 5桁の数字
        pattern = r'^N\d{5}$'
        if not re.match(pattern, n_code, re.IGNORECASE):
            return False, f"無効なNコード形式: {n_code} (正しい形式: N00001)"
        
        return True, None
    
    @staticmethod
    def validate_n_codes(n_codes_text: str) -> Tuple[List[str], List[str]]:
        """
        複数のNコードを検証
        
        Args:
            n_codes_text: カンマ、タブ、または改行で区切られたNコードのテキスト
        
        Returns:
            (有効なNコードのリスト, エラーメッセージのリスト)のタプル
        """
        # カンマ、タブ、改行で分割（スペースも含む）
        n_codes = re.split(r'[,\t\n\s]+', n_codes_text)
        n_codes = [code.strip() for code in n_codes if code.strip()]
        
        valid_codes = []
        errors = []
        
        for code in n_codes:
            is_valid, error = Validators.validate_n_code(code)
            if is_valid:
                # 大文字に統一
                valid_codes.append(code.upper())
            else:
                errors.append(error)
        
        return valid_codes, errors
    
    @staticmethod
    def validate_file_path(path: str, must_exist: bool = True) -> Tuple[bool, Optional[str]]:
        """
        ファイルパスを検証
        
        Args:
            path: 検証するパス
            must_exist: ファイルが存在する必要があるか
        
        Returns:
            (検証結果, エラーメッセージ)のタプル
        """
        if not path:
            return False, "パスが指定されていません"
        
        path_obj = Path(path)
        
        if must_exist and not path_obj.exists():
            return False, f"パスが存在しません: {path}"
        
        return True, None
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        メールアドレスを検証
        
        Args:
            email: 検証するメールアドレス
        
        Returns:
            (検証結果, エラーメッセージ)のタプル
        """
        if not email:
            return False, "メールアドレスが入力されていません"
        
        # 簡易的なメールアドレス検証
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, f"無効なメールアドレス形式: {email}"
        
        return True, None
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, Optional[str]]:
        """
        URLを検証
        
        Args:
            url: 検証するURL
        
        Returns:
            (検証結果, エラーメッセージ)のタプル
        """
        if not url:
            return False, "URLが入力されていません"
        
        # 簡易的なURL検証
        pattern = r'^https?://[^\s]+$'
        if not re.match(pattern, url):
            return False, f"無効なURL形式: {url}"
        
        return True, None