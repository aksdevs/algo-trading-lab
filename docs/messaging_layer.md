# Messaging Layer Documentation

## Overview

The messaging layer provides ZeroMQ-based communication between the Python strategy/backtest service (`strat-backtest-py`) and the C++ matching engine (`match-engine-core`). This enables the Python service to submit orders and receive execution notifications.

## Architecture

### Communication Patterns

The messaging layer supports two communication patterns:

1. **Request-Reply (REQ-REP)**: Synchronous order submission
   - Python service sends order via REQ socket
   - Matching engine responds with execution via REP socket
   - Guarantees response for each order

2. **Publish-Subscribe (PUB-SUB)**: Asynchronous execution notifications
   - Python service subscribes to execution notifications
   - Matching engine publishes executions to all subscribers
   - Useful for monitoring or multiple strategy instances

### Message Format

Messages are serialized as JSON for interoperability between Python and C++. Future versions may support Protocol Buffers for better performance.

#### Order Message

```json
{
  "order_id": "ORD20240101120000",
  "symbol": "AAPL",
  "side": "BUY",
  "order_type": "LIMIT",
  "quantity": 100,
  "price": 150.50,
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

#### Execution Message

```json
{
  "execution_id": "EXE20240101120001",
  "order_id": "ORD20240101120000",
  "symbol": "AAPL",
  "side": "BUY",
  "quantity": 100,
  "price": 150.50,
  "status": "FILLED",
  "timestamp": "2024-01-01T12:00:01.000Z",
  "message": "Order fully filled"
}
```

## Components

### OrderClient

The `OrderClient` class provides the interface for sending orders to the matching engine.

**Key Features:**
- ZeroMQ REQ-REP pattern for synchronous order submission
- Configurable timeouts for order responses
- Context manager support for automatic cleanup
- Connection pooling and socket reset on timeout

**Usage:**

```python
from src.messaging import OrderClient

# Initialize with default settings
client = OrderClient()
client.connect()

# Or use as context manager
with OrderClient() as client:
    execution = client.send_order(order)
```

### Message Types

#### OrderMessage

Represents an order to be sent to the matching engine.

**Attributes:**
- `order_id` (str): Unique order identifier
- `symbol` (str): Trading symbol/ticker
- `side` (OrderSide): BUY or SELL
- `order_type` (OrderType): MARKET or LIMIT
- `quantity` (float): Order quantity
- `price` (float, optional): Limit price for LIMIT orders
- `timestamp` (str, optional): ISO 8601 timestamp

**Methods:**
- `to_json()`: Serialize to JSON string
- `from_json(json_str)`: Deserialize from JSON string

#### ExecutionMessage

Represents an execution notification from the matching engine.

**Attributes:**
- `execution_id` (str): Unique execution identifier
- `order_id` (str): Original order identifier
- `symbol` (str): Trading symbol/ticker
- `side` (OrderSide): BUY or SELL
- `quantity` (float): Executed quantity
- `price` (float): Execution price
- `status` (str): Execution status (FILLED, PARTIAL, REJECTED, etc.)
- `timestamp` (str, optional): ISO 8601 timestamp
- `message` (str, optional): Status message

**Methods:**
- `to_json()`: Serialize to JSON string
- `from_json(json_str)`: Deserialize from JSON string

### Configuration

The `MessagingConfig` class provides centralized configuration management.

**Environment Variables:**
- `MATCHING_ENGINE_ORDER_ENDPOINT`: Order submission endpoint (default: `tcp://localhost:5555`)
- `MATCHING_ENGINE_EXECUTION_ENDPOINT`: Execution notification endpoint (default: `tcp://localhost:5556`)
- `MESSAGING_TIMEOUT_MS`: Request timeout in milliseconds (default: `5000`)

## Integration Guide

### Basic Integration

```python
from src.messaging import OrderClient, OrderMessage, OrderSide, OrderType
from src.messaging.config import MessagingConfig

# Get configuration
config = MessagingConfig.create_client_config()

# Create client
with OrderClient(**config) as client:
    # Create order
    order = OrderMessage(
        order_id="ORD001",
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=100,
        price=150.50
    )
    
    # Send and receive execution
    execution = client.send_order(order)
    if execution:
        print(f"Status: {execution.status}")
```

### Strategy Integration

To integrate with a trading strategy:

```python
from src.strategies.base_strategy import BaseStrategy
from src.messaging import OrderClient, OrderMessage, OrderSide, OrderType

class MyStrategy(BaseStrategy):
    def __init__(self, name, parameters=None):
        super().__init__(name, parameters)
        self.order_client = OrderClient()
        self.order_client.connect()
    
    def execute_signal(self, signal, price):
        """Execute a trading signal by sending order to matching engine."""
        order = OrderMessage(
            order_id=f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}",
            symbol=self.symbol,
            side=OrderSide.BUY if signal > 0 else OrderSide.SELL,
            order_type=OrderType.LIMIT,
            quantity=self.position_size,
            price=price
        )
        
        execution = self.order_client.send_order(order)
        return execution
    
    def cleanup(self):
        """Cleanup resources."""
        if self.order_client:
            self.order_client.close()
```

## Testing

### Unit Tests

Run the messaging layer tests:

```bash
pytest tests/test_messaging.py -v
```

### Integration Testing

For integration testing with a running matching engine:

1. Start the matching engine service:
```bash
# On the matching engine host
./match-engine-core --port 5555
```

2. Configure the endpoint:
```bash
export MATCHING_ENGINE_ORDER_ENDPOINT=tcp://localhost:5555
```

3. Run the example:
```bash
python src/messaging/example_usage.py
```

## Error Handling

### Connection Errors

If the matching engine is not available, `OrderClient.connect()` will raise a `zmq.ZMQError`. Handle this gracefully:

```python
try:
    with OrderClient() as client:
        execution = client.send_order(order)
except zmq.ZMQError as e:
    logger.error(f"Failed to connect to matching engine: {e}")
```

### Timeout Errors

If no response is received within the timeout period, `send_order()` returns `None`:

```python
execution = client.send_order(order)
if execution is None:
    logger.warning("Order timeout - no response from matching engine")
```

The client automatically resets the socket after a timeout to maintain correct REQ-REP state.

## Performance Considerations

### Latency

- ZeroMQ provides microsecond-level latency for local communication
- JSON serialization adds ~10-50 microseconds overhead per message
- Consider Protocol Buffers for ultra-low latency requirements

### Throughput

- Single-threaded REQ-REP can handle ~10k-50k messages/second
- For higher throughput, consider:
  - Multiple OrderClient instances (connection pooling)
  - Asynchronous patterns with DEALER-ROUTER sockets
  - Message batching

### Resource Management

- Always close OrderClient when done (use context manager)
- Socket resources are limited by OS (typically 1024 file descriptors)
- Monitor memory usage if keeping many connections open

## Future Enhancements

### Planned Features

1. **Protocol Buffers Support**
   - Binary serialization for reduced latency
   - Schema validation
   - Backward compatibility

2. **Connection Pooling**
   - Multiple client connections for throughput
   - Automatic failover

3. **Async/Await Support**
   - Python asyncio integration
   - Non-blocking order submission

4. **Enhanced Error Recovery**
   - Automatic reconnection
   - Exponential backoff
   - Circuit breaker pattern

5. **Monitoring and Metrics**
   - Message latency tracking
   - Throughput monitoring
   - Error rate tracking

## Troubleshooting

### Common Issues

**Issue: "Connection refused"**
- Ensure matching engine is running
- Check firewall settings
- Verify endpoint configuration

**Issue: "Operation cannot be accomplished in current state"**
- ZMQ REQ-REP sockets require alternating send/receive
- Socket was likely in invalid state due to timeout
- Client automatically resets socket, retry the operation

**Issue: "Address already in use"**
- Port is already bound by another process
- Use `netstat -an | grep 5555` to check
- Choose a different port or stop conflicting process

### Debug Logging

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Related Documentation

- [ZeroMQ Guide](https://zeromq.org/get-started/)
- [match-engine-core Documentation](https://github.com/aksdevs/match-engine-core)
- [Project Roadmap](https://github.com/aksdevs/algo-trading-lab/issues)
