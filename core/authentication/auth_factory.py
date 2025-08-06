"""Authentication factory for creating authentication providers

Provides a centralized factory for creating and configuring authentication
providers based on configuration or explicit parameters.
"""

from typing import Optional, Dict, Any
from .interfaces import AuthenticationProvider, ConfigurationProvider
from .basic_auth_provider import BasicAuthProvider
from .config_based_auth_provider import ConfigBasedAuthProvider
from utils.logger import get_logger


class AuthenticationFactory:
    """Factory for creating authentication providers
    
    This factory centralizes the creation of authentication providers,
    allowing for consistent configuration and easy switching between
    different authentication methods.
    """
    
    def __init__(self, config_provider: Optional[ConfigurationProvider] = None):
        """Initialize authentication factory
        
        Args:
            config_provider: Optional configuration provider for config-based auth
        """
        self._config_provider = config_provider
        self._logger = get_logger(__name__)
    
    def create_basic_auth(self, 
                         service_name: str,
                         username_env_var: str,
                         password_env_var: str,
                         default_username: str = None,
                         default_password: str = None) -> BasicAuthProvider:
        """Create a basic authentication provider
        
        Args:
            service_name: Name of the service for logging
            username_env_var: Environment variable for username
            password_env_var: Environment variable for password
            default_username: Fallback username (use sparingly)
            default_password: Fallback password (use sparingly)
            
        Returns:
            BasicAuthProvider: Configured basic auth provider
        """
        self._logger.debug(f"Creating basic auth provider for {service_name}")
        return BasicAuthProvider(
            username_env_var=username_env_var,
            password_env_var=password_env_var,
            default_username=default_username,
            default_password=default_password,
            service_name=service_name
        )
    
    def create_config_based_auth(self,
                                service_name: str,
                                username_key: str,
                                password_key: str,
                                config_provider: Optional[ConfigurationProvider] = None) -> ConfigBasedAuthProvider:
        """Create a configuration-based authentication provider
        
        Args:
            service_name: Name of the service for logging
            username_key: Configuration key for username
            password_key: Configuration key for password
            config_provider: Optional config provider (uses factory default if None)
            
        Returns:
            ConfigBasedAuthProvider: Configured config-based auth provider
            
        Raises:
            ValueError: If no configuration provider available
        """
        provider = config_provider or self._config_provider
        if not provider:
            raise ValueError(
                f"No configuration provider available for {service_name}. "
                "Provide one to the factory or method call."
            )
        
        self._logger.debug(f"Creating config-based auth provider for {service_name}")
        return ConfigBasedAuthProvider(
            config_provider=provider,
            username_key=username_key,
            password_key=password_key,
            service_name=service_name
        )
    
    def create_nextpublishing_auth(self) -> AuthenticationProvider:
        """Create authentication provider for NextPublishing service
        
        Creates an authentication provider specifically configured for
        NextPublishing API access with proper fallbacks.
        
        Returns:
            AuthenticationProvider: Configured provider for NextPublishing
        """
        service_name = "NextPublishing"
        
        # Try config-based auth first if config provider available
        if self._config_provider:
            try:
                return self.create_config_based_auth(
                    service_name=service_name,
                    username_key="api.nextpublishing.username",
                    password_key="api.nextpublishing.password"
                )
            except Exception as e:
                self._logger.warning(f"Config-based auth failed for {service_name}: {e}")
        
        # Fall back to basic auth with environment variables
        self._logger.info(f"Using basic auth with environment variables for {service_name}")
        return self.create_basic_auth(
            service_name=service_name,
            username_env_var="NEXTPUB_USERNAME",
            password_env_var="NEXTPUB_PASSWORD",
            default_username="ep_user",  # Legacy fallback
            default_password="Nn7eUTX5"   # Legacy fallback
        )
    
    def auto_detect_auth_method(self, 
                               service_name: str,
                               config_username_key: str = None,
                               config_password_key: str = None,
                               env_username_var: str = None,
                               env_password_var: str = None) -> AuthenticationProvider:
        """Auto-detect and create the most appropriate auth provider
        
        Tries configuration-based auth first, then falls back to basic auth.
        
        Args:
            service_name: Name of the service
            config_username_key: Configuration key for username
            config_password_key: Configuration key for password
            env_username_var: Environment variable for username
            env_password_var: Environment variable for password
            
        Returns:
            AuthenticationProvider: Best available auth provider
        """
        # Try config-based first
        if (self._config_provider and 
            config_username_key and 
            config_password_key):
            try:
                provider = self.create_config_based_auth(
                    service_name=service_name,
                    username_key=config_username_key,
                    password_key=config_password_key
                )
                if provider.validate_credentials():
                    self._logger.info(f"Using config-based authentication for {service_name}")
                    return provider
            except Exception as e:
                self._logger.debug(f"Config-based auth not available for {service_name}: {e}")
        
        # Fall back to basic auth
        if env_username_var and env_password_var:
            self._logger.info(f"Using environment-based authentication for {service_name}")
            return self.create_basic_auth(
                service_name=service_name,
                username_env_var=env_username_var,
                password_env_var=env_password_var
            )
        
        raise ValueError(f"No authentication method available for {service_name}")
    
    def set_config_provider(self, config_provider: ConfigurationProvider):
        """Set or update the configuration provider
        
        Args:
            config_provider: New configuration provider
        """
        self._config_provider = config_provider
        self._logger.debug("Configuration provider updated")


# Convenience function for common use cases
def create_nextpublishing_auth(config_provider: Optional[ConfigurationProvider] = None) -> AuthenticationProvider:
    """Convenience function to create NextPublishing authentication
    
    Args:
        config_provider: Optional configuration provider
        
    Returns:
        AuthenticationProvider: Configured NextPublishing auth provider
    """
    factory = AuthenticationFactory(config_provider)
    return factory.create_nextpublishing_auth()