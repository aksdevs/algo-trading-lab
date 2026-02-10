"""
Tests for messaging layer components.
"""

import pytest
import json
from src.messaging.message_types import (
    OrderMessage, ExecutionMessage, OrderSide, OrderType
)
from src.messaging.order_client import OrderClient
from src.messaging.config import MessagingConfig
from unittest.mock import Mock, patch, MagicMock
import zmq


class TestMessageTypes:
    """Test message serialization and deserialization."""
    
    def test_order_message_creation(self):
        """Test creating an order message."""
        order = OrderMessage(
            order_id="ORD001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=100,
            price=150.50
        )
        
        assert order.order_id == "ORD001"
        assert order.symbol == "AAPL"
        assert order.side == OrderSide.BUY
        assert order.order_type == OrderType.LIMIT
        assert order.quantity == 100
        assert order.price == 150.50
        assert order.timestamp is not None
    
    def test_order_message_json_serialization(self):
        """Test order message serialization to JSON."""
        order = OrderMessage(
            order_id="ORD002",
            symbol="GOOGL",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=50,
            timestamp="2024-01-01T12:00:00"
        )
        
        json_str = order.to_json()
        data = json.loads(json_str)
        
        assert data['order_id'] == "ORD002"
        assert data['symbol'] == "GOOGL"
        assert data['side'] == "SELL"
        assert data['order_type'] == "MARKET"
        assert data['quantity'] == 50
        assert data['timestamp'] == "2024-01-01T12:00:00"
    
    def test_order_message_json_deserialization(self):
        """Test order message deserialization from JSON."""
        json_str = json.dumps({
            'order_id': 'ORD003',
            'symbol': 'TSLA',
            'side': 'BUY',
            'order_type': 'LIMIT',
            'quantity': 25,
            'price': 200.00,
            'timestamp': '2024-01-01T13:00:00'
        })
        
        order = OrderMessage.from_json(json_str)
        
        assert order.order_id == "ORD003"
        assert order.symbol == "TSLA"
        assert order.side == OrderSide.BUY
        assert order.order_type == OrderType.LIMIT
        assert order.quantity == 25
        assert order.price == 200.00
    
    def test_execution_message_creation(self):
        """Test creating an execution message."""
        execution = ExecutionMessage(
            execution_id="EXE001",
            order_id="ORD001",
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            price=150.50,
            status="FILLED"
        )
        
        assert execution.execution_id == "EXE001"
        assert execution.order_id == "ORD001"
        assert execution.status == "FILLED"
        assert execution.timestamp is not None
    
    def test_execution_message_json_roundtrip(self):
        """Test execution message JSON serialization and deserialization."""
        execution = ExecutionMessage(
            execution_id="EXE002",
            order_id="ORD002",
            symbol="GOOGL",
            side=OrderSide.SELL,
            quantity=50,
            price=100.25,
            status="PARTIAL",
            message="Partially filled"
        )
        
        json_str = execution.to_json()
        recovered = ExecutionMessage.from_json(json_str)
        
        assert recovered.execution_id == execution.execution_id
        assert recovered.order_id == execution.order_id
        assert recovered.symbol == execution.symbol
        assert recovered.side == execution.side
        assert recovered.quantity == execution.quantity
        assert recovered.price == execution.price
        assert recovered.status == execution.status
        assert recovered.message == execution.message


class TestOrderClient:
    """Test ZeroMQ order client."""
    
    @patch('src.messaging.order_client.zmq.Context')
    def test_client_initialization(self, mock_context):
        """Test client initialization."""
        client = OrderClient(
            order_endpoint="tcp://localhost:5555",
            timeout=3000
        )
        
        assert client.order_endpoint == "tcp://localhost:5555"
        assert client.timeout == 3000
        assert not client._connected
    
    @patch('src.messaging.order_client.zmq.Context')
    def test_client_connect(self, mock_context):
        """Test client connection."""
        mock_socket = MagicMock()
        mock_context_instance = MagicMock()
        mock_context_instance.socket.return_value = mock_socket
        mock_context.return_value = mock_context_instance
        
        client = OrderClient()
        client.connect()
        
        assert client._connected
        mock_socket.connect.assert_called()
    
    @patch('src.messaging.order_client.zmq.Context')
    def test_send_order_not_connected(self, mock_context):
        """Test sending order when not connected raises error."""
        client = OrderClient()
        order = OrderMessage(
            order_id="ORD001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100
        )
        
        with pytest.raises(ConnectionError):
            client.send_order(order)
    
    @patch('src.messaging.order_client.zmq.Context')
    def test_send_order_success(self, mock_context):
        """Test successful order sending."""
        mock_socket = MagicMock()
        mock_context_instance = MagicMock()
        mock_context_instance.socket.return_value = mock_socket
        mock_context.return_value = mock_context_instance
        
        # Mock execution response
        execution_json = json.dumps({
            'execution_id': 'EXE001',
            'order_id': 'ORD001',
            'symbol': 'AAPL',
            'side': 'BUY',
            'quantity': 100,
            'price': 150.00,
            'status': 'FILLED',
            'timestamp': '2024-01-01T12:00:00'
        })
        mock_socket.recv_string.return_value = execution_json
        
        client = OrderClient()
        client.connect()
        
        order = OrderMessage(
            order_id="ORD001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100
        )
        
        execution = client.send_order(order)
        
        assert execution is not None
        assert execution.execution_id == "EXE001"
        assert execution.status == "FILLED"
        mock_socket.send_string.assert_called_once()
    
    @patch('src.messaging.order_client.zmq.Context')
    def test_context_manager(self, mock_context):
        """Test client as context manager."""
        mock_socket = MagicMock()
        mock_context_instance = MagicMock()
        mock_context_instance.socket.return_value = mock_socket
        mock_context.return_value = mock_context_instance
        
        with OrderClient() as client:
            assert client._connected
        
        # After exiting context, should be closed
        mock_socket.close.assert_called()


class TestMessagingConfig:
    """Test messaging configuration."""
    
    def test_default_endpoints(self):
        """Test default endpoint configuration."""
        order_endpoint = MessagingConfig.get_order_endpoint()
        assert order_endpoint == MessagingConfig.DEFAULT_ORDER_ENDPOINT
    
    @patch.dict('os.environ', {'MATCHING_ENGINE_ORDER_ENDPOINT': 'tcp://custom:5555'})
    def test_custom_order_endpoint(self):
        """Test custom order endpoint from environment."""
        order_endpoint = MessagingConfig.get_order_endpoint()
        assert order_endpoint == 'tcp://custom:5555'
    
    @patch.dict('os.environ', {'MESSAGING_TIMEOUT_MS': '10000'})
    def test_custom_timeout(self):
        """Test custom timeout from environment."""
        timeout = MessagingConfig.get_timeout()
        assert timeout == 10000
    
    def test_create_client_config(self):
        """Test creating client configuration dictionary."""
        config = MessagingConfig.create_client_config()
        
        assert 'order_endpoint' in config
        assert 'execution_endpoint' in config
        assert 'timeout' in config
