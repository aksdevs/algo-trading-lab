"""
Message type definitions for order and execution messages.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional
import json
from datetime import datetime, timezone


class OrderSide(Enum):
    """Order side enumeration."""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    """Order type enumeration."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"


@dataclass
class OrderMessage:
    """
    Order message to be sent to the matching engine.
    
    Attributes:
        order_id: Unique order identifier
        symbol: Trading symbol/ticker
        side: Order side (BUY/SELL)
        order_type: Order type (MARKET/LIMIT)
        quantity: Order quantity
        price: Limit price (optional for MARKET orders)
        timestamp: Order timestamp
    """
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_json(self) -> str:
        """
        Serialize the order message to JSON.
        
        Returns:
            JSON string representation of the order
        """
        data = {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side.value,
            'order_type': self.order_type.value,
            'quantity': self.quantity,
            'price': self.price,
            'timestamp': self.timestamp
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'OrderMessage':
        """
        Deserialize an order message from JSON.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            OrderMessage instance
        """
        data = json.loads(json_str)
        return cls(
            order_id=data['order_id'],
            symbol=data['symbol'],
            side=OrderSide(data['side']),
            order_type=OrderType(data['order_type']),
            quantity=data['quantity'],
            price=data.get('price'),
            timestamp=data.get('timestamp')
        )


@dataclass
class ExecutionMessage:
    """
    Execution message received from the matching engine.
    
    Attributes:
        execution_id: Unique execution identifier
        order_id: Original order identifier
        symbol: Trading symbol/ticker
        side: Order side (BUY/SELL)
        quantity: Executed quantity
        price: Execution price
        status: Execution status (FILLED, PARTIAL, REJECTED, etc.)
        timestamp: Execution timestamp
        message: Optional status message
    """
    execution_id: str
    order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    status: str
    timestamp: Optional[str] = None
    message: Optional[str] = None
    
    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_json(self) -> str:
        """
        Serialize the execution message to JSON.
        
        Returns:
            JSON string representation of the execution
        """
        data = {
            'execution_id': self.execution_id,
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side.value,
            'quantity': self.quantity,
            'price': self.price,
            'status': self.status,
            'timestamp': self.timestamp,
            'message': self.message
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ExecutionMessage':
        """
        Deserialize an execution message from JSON.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            ExecutionMessage instance
        """
        data = json.loads(json_str)
        return cls(
            execution_id=data['execution_id'],
            order_id=data['order_id'],
            symbol=data['symbol'],
            side=OrderSide(data['side']),
            quantity=data['quantity'],
            price=data['price'],
            status=data['status'],
            timestamp=data.get('timestamp'),
            message=data.get('message')
        )
