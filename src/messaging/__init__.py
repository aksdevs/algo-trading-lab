"""
Messaging layer module for ZeroMQ-based communication.

This module provides order message transport between the Python strategy/backtest
service and the C++ matching engine using ZeroMQ.
"""

from .order_client import OrderClient
from .message_types import OrderMessage, ExecutionMessage, OrderSide, OrderType
from .config import MessagingConfig

__all__ = [
    'OrderClient',
    'OrderMessage',
    'ExecutionMessage',
    'OrderSide',
    'OrderType',
    'MessagingConfig',
]
