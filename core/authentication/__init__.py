"""Authentication module for technical fountain series support tool

This module provides authentication abstractions following SOLID principles
to eliminate hardcoded credentials and improve security.
"""

from .interfaces import AuthenticationProvider, AuthenticationError, ConfigurationProvider
from .basic_auth_provider import BasicAuthProvider
from .config_based_auth_provider import ConfigBasedAuthProvider
from .auth_factory import AuthenticationFactory, create_nextpublishing_auth
from .config_adapter import ConfigManagerAdapter, LegacyConfigAdapter, create_config_adapter

__all__ = [
    'AuthenticationProvider',
    'AuthenticationError',
    'ConfigurationProvider',
    'BasicAuthProvider', 
    'ConfigBasedAuthProvider',
    'AuthenticationFactory',
    'create_nextpublishing_auth',
    'ConfigManagerAdapter',
    'LegacyConfigAdapter',
    'create_config_adapter'
]