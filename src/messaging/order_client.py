"""
ZeroMQ-based order client for sending orders to the matching engine.
"""

import zmq
import logging
from typing import Optional
from .message_types import OrderMessage, ExecutionMessage


class OrderClient:
    """
    ZeroMQ client for sending orders to the matching engine and receiving executions.
    
    This client uses a REQ-REP pattern for synchronous order submission,
    or PUB-SUB pattern for asynchronous order submission with separate execution listener.
    """
    
    def __init__(
        self,
        order_endpoint: str = "tcp://localhost:5555",
        execution_endpoint: Optional[str] = None,
        timeout: int = 5000
    ):
        """
        Initialize the order client.
        
        Args:
            order_endpoint: ZeroMQ endpoint for sending orders (REQ socket)
            execution_endpoint: ZeroMQ endpoint for receiving executions (SUB socket)
            timeout: Timeout in milliseconds for REQ-REP operations
        """
        self.order_endpoint = order_endpoint
        self.execution_endpoint = execution_endpoint
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        self.context = zmq.Context()
        self.order_socket = None
        self.execution_socket = None
        self._connected = False
    
    def connect(self):
        """
        Connect to the matching engine endpoints.
        """
        if self._connected:
            self.logger.warning("Client already connected")
            return
        
        try:
            # Create REQ socket for sending orders
            self.order_socket = self.context.socket(zmq.REQ)
            self.order_socket.setsockopt(zmq.RCVTIMEO, self.timeout)
            self.order_socket.setsockopt(zmq.SNDTIMEO, self.timeout)
            self.order_socket.connect(self.order_endpoint)
            self.logger.info(f"Connected order socket to {self.order_endpoint}")
            
            # Create SUB socket for receiving executions if endpoint provided
            if self.execution_endpoint:
                self.execution_socket = self.context.socket(zmq.SUB)
                self.execution_socket.connect(self.execution_endpoint)
                self.execution_socket.setsockopt_string(zmq.SUBSCRIBE, "")
                self.logger.info(f"Connected execution socket to {self.execution_endpoint}")
            
            self._connected = True
            
        except zmq.ZMQError as e:
            self.logger.error(f"Failed to connect: {e}")
            self.close()
            raise
    
    def send_order(self, order: OrderMessage) -> Optional[ExecutionMessage]:
        """
        Send an order to the matching engine and wait for response.
        
        Args:
            order: OrderMessage to send
            
        Returns:
            ExecutionMessage response from the matching engine, or None if timeout
            
        Raises:
            ConnectionError: If not connected to the matching engine
            zmq.ZMQError: If ZeroMQ communication fails
        """
        if not self._connected or not self.order_socket:
            raise ConnectionError("Not connected to matching engine. Call connect() first.")
        
        try:
            # Send order as JSON
            order_json = order.to_json()
            self.logger.debug(f"Sending order: {order_json}")
            self.order_socket.send_string(order_json)
            
            # Wait for response
            response_json = self.order_socket.recv_string()
            self.logger.debug(f"Received response: {response_json}")
            
            # Parse execution message
            execution = ExecutionMessage.from_json(response_json)
            return execution
            
        except zmq.Again:
            self.logger.error(f"Timeout waiting for response after {self.timeout}ms")
            # Reset socket after timeout (ZMQ REQ-REP requires this)
            self._reset_order_socket()
            return None
            
        except zmq.ZMQError as e:
            self.logger.error(f"ZeroMQ error: {e}")
            raise
    
    def receive_execution(self, timeout_ms: Optional[int] = None) -> Optional[ExecutionMessage]:
        """
        Receive an execution message from the execution socket (async mode).
        
        Args:
            timeout_ms: Timeout in milliseconds, None for blocking
            
        Returns:
            ExecutionMessage or None if timeout
            
        Raises:
            ConnectionError: If execution socket not configured
        """
        if not self.execution_socket:
            raise ConnectionError("Execution socket not configured")
        
        try:
            if timeout_ms is not None:
                self.execution_socket.setsockopt(zmq.RCVTIMEO, timeout_ms)
            
            message_json = self.execution_socket.recv_string()
            execution = ExecutionMessage.from_json(message_json)
            return execution
            
        except zmq.Again:
            return None
            
        except zmq.ZMQError as e:
            self.logger.error(f"Error receiving execution: {e}")
            raise
    
    def _reset_order_socket(self):
        """Reset the order socket after a timeout."""
        if self.order_socket:
            self.order_socket.close()
        
        self.order_socket = self.context.socket(zmq.REQ)
        self.order_socket.setsockopt(zmq.RCVTIMEO, self.timeout)
        self.order_socket.setsockopt(zmq.SNDTIMEO, self.timeout)
        self.order_socket.connect(self.order_endpoint)
    
    def close(self):
        """
        Close all sockets and terminate the ZeroMQ context.
        """
        if self.order_socket:
            self.order_socket.close()
            self.order_socket = None
        
        if self.execution_socket:
            self.execution_socket.close()
            self.execution_socket = None
        
        if self.context:
            self.context.term()
            self.context = None
        
        self._connected = False
        self.logger.info("Order client closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
