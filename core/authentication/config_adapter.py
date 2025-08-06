"""Configuration adapter for integrating with existing Config class

This adapter bridges the new ConfigurationProvider interface with
the existing application configuration system.
"""

from typing import Dict, Any
from .interfaces import ConfigurationProvider


class ConfigManagerAdapter(ConfigurationProvider):
    """Adapter to make ConfigManager compatible with ConfigurationProvider
    
    This adapter allows the new authentication system to work with the
    existing ConfigManager class without modifying its interface.
    """
    
    def __init__(self, config_manager):
        """Initialize adapter with existing config manager
        
        Args:
            config_manager: Instance of ConfigManager from core.config_manager
        """
        self._config_manager = config_manager
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value using ConfigManager's get method
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            # Try the standard get method first
            return self._config_manager.get(key, default)
        except AttributeError:
            # If get method doesn't exist, try alternative methods
            if hasattr(self._config_manager, 'get_value'):
                return self._config_manager.get_value(key, default)
            else:
                return default
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section
        
        Args:
            section: Section name
            
        Returns:
            Dict[str, Any]: Configuration section as dictionary
        """
        try:
            # Try the standard get method first
            return self._config_manager.get(section, {})
        except AttributeError:
            # If get method doesn't exist, try alternative methods
            if hasattr(self._config_manager, 'get_section'):
                return self._config_manager.get_section(section)
            else:
                return {}


class LegacyConfigAdapter(ConfigurationProvider):
    """Adapter for the legacy Config class from utils.config
    
    This adapter enables the legacy Config class to work with the new
    authentication system.
    """
    
    def __init__(self, config_instance):
        """Initialize adapter with legacy config instance
        
        Args:
            config_instance: Instance of legacy Config class
        """
        self._config = config_instance
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value from legacy config
        
        Maps dot notation keys to appropriate legacy config methods.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        # Handle NextPublishing API configuration
        if key.startswith("api.nextpublishing."):
            field = key.split(".")[-1]  # Get last part after final dot
            web_config = self._config.get_web_config()
            return web_config.get(field, default)
        
        # Handle other API configurations
        elif key.startswith("api."):
            parts = key.split(".")
            if len(parts) >= 3:
                service = parts[1]  # e.g., 'slack'
                field = parts[2]    # e.g., 'bot_token'
                # This would need to be extended based on legacy config structure
                return default
        
        # Handle paths configuration
        elif key.startswith("paths."):
            # Legacy config doesn't have structured path access
            # Return default for now
            return default
        
        # Fallback to default for unknown keys
        return default
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section from legacy config
        
        Args:
            section: Section name
            
        Returns:
            Dict[str, Any]: Configuration section as dictionary
        """
        if section == "api.nextpublishing":
            return self._config.get_web_config()
        elif section.startswith("api."):
            # Return empty dict for unsupported API sections
            return {}
        else:
            # Return empty dict for unknown sections
            return {}


def create_config_adapter(config_instance) -> ConfigurationProvider:
    """Factory function to create appropriate config adapter
    
    Automatically detects the type of configuration object and returns
    the appropriate adapter.
    
    Args:
        config_instance: Configuration instance (ConfigManager, legacy Config, 
                        ConfigManagerAdapter, LegacyConfigAdapter, or other ConfigurationProvider)
        
    Returns:
        ConfigurationProvider: Appropriate adapter instance
        
    Raises:
        TypeError: If config instance type is not supported
    """
    # Import ConfigurationProvider types here to avoid circular imports
    try:
        from core.configuration_provider import ConfigurationProvider as BaseConfigurationProvider
    except ImportError:
        # If import fails, define a simple interface check
        BaseConfigurationProvider = None
    
    # Check if it's already a ConfigurationProvider (ConfigManagerAdapter or LegacyConfigAdapter)
    if BaseConfigurationProvider and isinstance(config_instance, BaseConfigurationProvider):
        # Already a proper ConfigurationProvider, but need to wrap it for compatibility
        # Create a compatibility wrapper that maps get() to get_value()
        class UnifiedConfigWrapper(ConfigurationProvider):
            def __init__(self, provider):
                self._provider = provider
            
            def get_value(self, key: str, default: Any = None) -> Any:
                """Map get_value to the provider's get method"""
                return self._provider.get(key, default)
            
            def get_section(self, section: str) -> Dict[str, Any]:
                """Map get_section to the provider's get_section method"""
                return self._provider.get_section(section)
        
        return UnifiedConfigWrapper(config_instance)
    
    # Check if it's a ConfigManagerAdapter-like object (unified config system)
    elif hasattr(config_instance, 'get') and hasattr(config_instance, 'get_section') and hasattr(config_instance, 'validate'):
        # This is likely a ConfigManagerAdapter from the unified config system
        # Wrap it in our ConfigManagerAdapter for compatibility
        return ConfigManagerAdapter(config_instance)
    
    # Check if it's the new ConfigManager
    elif hasattr(config_instance, 'get') and hasattr(config_instance, 'get_api_config'):
        return ConfigManagerAdapter(config_instance)
    
    # Check if it's the legacy Config class
    elif hasattr(config_instance, 'get_web_config'):
        return LegacyConfigAdapter(config_instance)
    
    else:
        raise TypeError(
            f"Unsupported configuration type: {type(config_instance)}. "
            "Expected ConfigManager, legacy Config instance, or ConfigurationProvider."
        )