"""Basic authentication provider implementation

Provides HTTP Basic Authentication support with secure credential handling.
"""

import os
from typing import Tuple, Dict
from requests.auth import HTTPBasicAuth, AuthBase

from .interfaces import AuthenticationProvider, AuthenticationError
from utils.logger import get_logger


class BasicAuthProvider(AuthenticationProvider):
    """HTTP Basic Authentication provider
    
    Supports credential retrieval from environment variables with fallback
    to provided defaults. Never stores credentials as instance variables
    for security.
    """
    
    def __init__(self, 
                 username_env_var: str,
                 password_env_var: str,
                 default_username: str = None,
                 default_password: str = None,
                 service_name: str = "Unknown Service"):
        """Initialize Basic Auth provider
        
        Args:
            username_env_var: Environment variable name for username
            password_env_var: Environment variable name for password  
            default_username: Fallback username (use sparingly)
            default_password: Fallback password (use sparingly)
            service_name: Service name for logging and error messages
        """
        self._username_env_var = username_env_var
        self._password_env_var = password_env_var
        self._default_username = default_username
        self._default_password = default_password
        self._service_name = service_name
        self._logger = get_logger(f"{__name__}.{service_name}")
        
    def get_credentials(self) -> Tuple[str, str]:
        """Get username and password from environment or defaults
        
        Priority order:
        1. Environment variables
        2. Provided defaults
        3. Raise AuthenticationError
        
        Returns:
            Tuple[str, str]: (username, password)
            
        Raises:
            AuthenticationError: If no valid credentials found
        """
        username = os.getenv(self._username_env_var)
        password = os.getenv(self._password_env_var)
        
        # Use environment variables if available
        if username and password:
            self._logger.debug(f"Using environment credentials for {self._service_name}")
            return username, password
        
        # Fall back to defaults if provided
        if self._default_username and self._default_password:
            self._logger.warning(f"Using default credentials for {self._service_name} - consider setting environment variables {self._username_env_var} and {self._password_env_var}")
            return self._default_username, self._default_password
        
        # No credentials available
        missing_vars = []
        if not username:
            missing_vars.append(self._username_env_var)
        if not password:
            missing_vars.append(self._password_env_var)
            
        raise AuthenticationError(
            f"Authentication credentials not found for {self._service_name}. "
            f"Missing environment variables: {', '.join(missing_vars)}. "
            f"Please set these environment variables or provide defaults."
        )
    
    def create_auth_object(self) -> AuthBase:
        """Create HTTPBasicAuth object for requests
        
        Returns:
            HTTPBasicAuth: Configured basic auth object
            
        Raises:
            AuthenticationError: If credentials cannot be retrieved
        """
        try:
            username, password = self.get_credentials()
            return HTTPBasicAuth(username, password)
        except Exception as e:
            raise AuthenticationError(
                f"Failed to create authentication object for {self._service_name}",
                cause=e
            )
    
    def validate_credentials(self) -> bool:
        """Validate that credentials are available and non-empty
        
        Returns:
            bool: True if valid credentials available
        """
        try:
            username, password = self.get_credentials()
            return bool(username.strip()) and bool(password.strip())
        except AuthenticationError:
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get additional authentication headers
        
        For Basic Auth, no additional headers are typically needed.
        
        Returns:
            Dict[str, str]: Empty dictionary
        """
        return {}
    
    def __repr__(self) -> str:
        """String representation for debugging (without sensitive data)"""
        return f"BasicAuthProvider(service={self._service_name}, env_vars=[{self._username_env_var}, {self._password_env_var}])"