"""
Configuration for messaging layer endpoints and settings.
"""

import os
from typing import Optional


class MessagingConfig:
    """
    Configuration class for messaging layer settings.
    
    Settings can be overridden via environment variables:
    - MATCHING_ENGINE_ORDER_ENDPOINT: Order submission endpoint
    - MATCHING_ENGINE_EXECUTION_ENDPOINT: Execution notification endpoint
    - MESSAGING_TIMEOUT_MS: Request timeout in milliseconds
    """
    
    # Default endpoints
    DEFAULT_ORDER_ENDPOINT = "tcp://localhost:5555"
    DEFAULT_EXECUTION_ENDPOINT = "tcp://localhost:5556"
    DEFAULT_TIMEOUT_MS = 5000
    
    @classmethod
    def get_order_endpoint(cls) -> str:
        """Get the order endpoint from environment or default."""
        return os.getenv('MATCHING_ENGINE_ORDER_ENDPOINT', cls.DEFAULT_ORDER_ENDPOINT)
    
    @classmethod
    def get_execution_endpoint(cls) -> Optional[str]:
        """Get the execution endpoint from environment or default."""
        return os.getenv('MATCHING_ENGINE_EXECUTION_ENDPOINT', cls.DEFAULT_EXECUTION_ENDPOINT)
    
    @classmethod
    def get_timeout(cls) -> int:
        """Get the timeout in milliseconds from environment or default."""
        timeout_str = os.getenv('MESSAGING_TIMEOUT_MS', str(cls.DEFAULT_TIMEOUT_MS))
        try:
            return int(timeout_str)
        except ValueError:
            return cls.DEFAULT_TIMEOUT_MS
    
    @classmethod
    def create_client_config(cls) -> dict:
        """
        Create a configuration dictionary for OrderClient initialization.
        
        Returns:
            Dictionary with order_endpoint, execution_endpoint, and timeout
        """
        return {
            'order_endpoint': cls.get_order_endpoint(),
            'execution_endpoint': cls.get_execution_endpoint(),
            'timeout': cls.get_timeout()
        }
