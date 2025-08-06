"""Authentication interface definitions

Defines the contract for authentication providers to ensure
consistent authentication handling across the application.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any, Optional
from requests.auth import AuthBase


class AuthenticationProvider(ABC):
    """Abstract base class for authentication providers
    
    This interface defines the contract that all authentication providers
    must implement, ensuring consistent authentication behavior across
    different services and protocols.
    """
    
    @abstractmethod
    def get_credentials(self) -> Tuple[str, str]:
        """Get username and password credentials
        
        Returns:
            Tuple[str, str]: (username, password)
            
        Raises:
            AuthenticationError: If credentials cannot be retrieved
        """
        pass
    
    @abstractmethod
    def create_auth_object(self) -> AuthBase:
        """Create requests-compatible authentication object
        
        Returns:
            AuthBase: Authentication object for use with requests library
            
        Raises:
            AuthenticationError: If authentication object cannot be created
        """
        pass
    
    @abstractmethod
    def validate_credentials(self) -> bool:
        """Validate that credentials are available and properly formatted
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """Get additional authentication headers if needed
        
        Returns:
            Dict[str, str]: Dictionary of header name to header value
        """
        pass


class AuthenticationError(Exception):
    """Exception raised when authentication operations fail
    
    This exception is raised when:
    - Credentials cannot be retrieved
    - Credentials are invalid or malformed
    - Authentication objects cannot be created
    - Authentication validation fails
    """
    
    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.cause = cause
        
    def __str__(self) -> str:
        if self.cause:
            return f"{super().__str__()} (caused by: {self.cause})"
        return super().__str__()


class ConfigurationProvider(ABC):
    """Abstract interface for configuration providers
    
    This interface allows authentication providers to be decoupled
    from specific configuration implementations.
    """
    
    @abstractmethod
    def get_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key
        
        Args:
            key: Configuration key (may support dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        pass
    
    @abstractmethod
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section
        
        Args:
            section: Section name
            
        Returns:
            Dict[str, Any]: Configuration section as dictionary
        """
        pass