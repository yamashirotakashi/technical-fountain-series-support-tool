"""Configuration-based authentication provider

Provides authentication using configuration services with environment
variable override support.
"""

from typing import Tuple, Dict
from requests.auth import HTTPBasicAuth, AuthBase

from .interfaces import AuthenticationProvider, AuthenticationError, ConfigurationProvider
from utils.logger import get_logger


class ConfigBasedAuthProvider(AuthenticationProvider):
    """Authentication provider that uses configuration services
    
    This provider integrates with the application's configuration system
    to retrieve authentication credentials, with support for environment
    variable overrides and secure credential handling.
    """
    
    def __init__(self, 
                 config_provider: ConfigurationProvider,
                 username_key: str,
                 password_key: str,
                 service_name: str = "Unknown Service"):
        """Initialize configuration-based auth provider
        
        Args:
            config_provider: Configuration provider instance
            username_key: Configuration key for username (supports dot notation)
            password_key: Configuration key for password (supports dot notation)
            service_name: Service name for logging and error messages
        """
        self._config = config_provider
        self._username_key = username_key
        self._password_key = password_key
        self._service_name = service_name
        self._logger = get_logger(f"{__name__}.{service_name}")
    
    def get_credentials(self) -> Tuple[str, str]:
        """Get credentials from configuration provider
        
        Returns:
            Tuple[str, str]: (username, password)
            
        Raises:
            AuthenticationError: If credentials not found or invalid
        """
        try:
            username = self._config.get_value(self._username_key)
            password = self._config.get_value(self._password_key)
            
            if not username:
                raise AuthenticationError(
                    f"Username not found in configuration for {self._service_name}. "
                    f"Missing key: {self._username_key}"
                )
            
            if not password:
                raise AuthenticationError(
                    f"Password not found in configuration for {self._service_name}. "
                    f"Missing key: {self._password_key}"
                )
            
            self._logger.debug(f"Retrieved credentials from configuration for {self._service_name}")
            return str(username), str(password)
            
        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError(
                f"Failed to retrieve credentials from configuration for {self._service_name}",
                cause=e
            )
    
    def create_auth_object(self) -> AuthBase:
        """Create HTTPBasicAuth object using configuration
        
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
        """Validate that credentials are available in configuration
        
        Returns:
            bool: True if valid credentials available
        """
        try:
            username, password = self.get_credentials()
            return bool(username.strip()) and bool(password.strip())
        except AuthenticationError:
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get additional authentication headers from configuration
        
        Returns:
            Dict[str, str]: Additional headers if configured
        """
        # Check for additional headers in configuration
        headers = {}
        
        # Look for service-specific headers
        try:
            # Try to get headers from configuration
            # Format: service.auth.headers.header_name
            base_key = self._username_key.rsplit('.', 1)[0] if '.' in self._username_key else 'auth'
            headers_key = f"{base_key}.headers"
            
            headers_config = self._config.get_value(headers_key, {})
            if isinstance(headers_config, dict):
                headers.update(headers_config)
                
        except Exception as e:
            self._logger.debug(f"No additional headers found in configuration: {e}")
        
        return headers
    
    def __repr__(self) -> str:
        """String representation for debugging (without sensitive data)"""
        return f"ConfigBasedAuthProvider(service={self._service_name}, keys=[{self._username_key}, {self._password_key}])"