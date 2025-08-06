from __future__ import annotations
"""Input validation module"""
import re
from pathlib import Path
from typing import List, Tuple, Optional


class Validators:
    """Class for input validation"""
    
    @staticmethod
    def validate_n_code(n_code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate N-code format
        
        Args:
            n_code: N-code to validate
        
        Returns:
            Tuple of (validation result, error message)
        """
        n_code = n_code.strip()
        
        if not n_code:
            return False, "N-code is not entered"
        
        # N-code format: N + 5 digits
        pattern = r'^N\d{5}$'
        if not re.match(pattern, n_code, re.IGNORECASE):
            return False, f"Invalid N-code format: {n_code} (correct format: N00001)"
        
        return True, None
    
    @staticmethod
    def validate_n_codes(n_codes_text: str) -> Tuple[List[str], List[str]]:
        """
        Validate multiple N-codes
        
        Args:
            n_codes_text: N-codes text separated by comma, tab, or newline
        
        Returns:
            Tuple of (list of valid N-codes, list of error messages)
        """
        # Split by comma, tab, newline, and spaces
        n_codes = re.split(r'[,\t\n\s]+', n_codes_text)
        n_codes = [code.strip() for code in n_codes if code.strip()]
        
        valid_codes = []
        errors = []
        
        for code in n_codes:
            is_valid, error = Validators.validate_n_code(code)
            if is_valid:
                # Convert to uppercase
                valid_codes.append(code.upper())
            else:
                errors.append(error)
        
        return valid_codes, errors
    
    @staticmethod
    def validate_file_path(path: str, must_exist: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Validate file path
        
        Args:
            path: Path to validate
            must_exist: Whether the file must exist
        
        Returns:
            Tuple of (validation result, error message)
        """
        if not path:
            return False, "Path is not specified"
        
        path_obj = Path(path)
        
        if must_exist and not path_obj.exists():
            return False, f"Path does not exist: {path}"
        
        return True, None
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email address
        
        Args:
            email: Email address to validate
        
        Returns:
            Tuple of (validation result, error message)
        """
        if not email:
            return False, "Email address is not entered"
        
        # Simple email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, f"Invalid email address format: {email}"
        
        return True, None
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate URL
        
        Args:
            url: URL to validate
        
        Returns:
            Tuple of (validation result, error message)
        """
        if not url:
            return False, "URL is not entered"
        
        # Simple URL validation
        pattern = r'^https?://[^\s]+$'
        if not re.match(pattern, url):
            return False, f"Invalid URL format: {url}"
        
        return True, None