"""
Example: Strategy with ZeroMQ messaging integration

This example demonstrates how to integrate the messaging layer
with a trading strategy to send orders to a matching engine.
"""

import sys
import logging
from datetime import datetime
from src.messaging import OrderClient, OrderMessage, OrderSide, OrderType
from src.messaging.config import MessagingConfig


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_send_order():
    """
    Example: Send a single order to the matching engine.
    """
    logger.info("=== Example: Sending a single order ===")
    
    # Get configuration from environment or defaults
    config = MessagingConfig.create_client_config()
    logger.info(f"Connecting to: {config['order_endpoint']}")
    
    # Create order client using context manager
    try:
        with OrderClient(**config) as client:
            # Create a buy order
            order = OrderMessage(
                order_id=f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}",
                symbol="AAPL",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=100,
                price=150.50
            )
            
            logger.info(f"Sending order: {order.order_id} - {order.side.value} {order.quantity} {order.symbol} @ {order.price}")
            
            # Send order and wait for execution
            execution = client.send_order(order)
            
            if execution:
                logger.info(f"Received execution: {execution.execution_id} - Status: {execution.status}")
                logger.info(f"Filled: {execution.quantity} @ {execution.price}")
            else:
                logger.warning("No execution received (timeout)")
                
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        logger.info("Make sure the matching engine is running at the configured endpoint")
    except Exception as e:
        logger.error(f"Error: {e}")


def example_strategy_integration():
    """
    Example: Integration with a strategy that generates signals.
    
    This demonstrates how a strategy might send orders based on trading signals.
    """
    logger.info("=== Example: Strategy integration ===")
    
    # Simulated trading signals
    signals = [
        {'action': 'BUY', 'symbol': 'AAPL', 'quantity': 100, 'price': 150.00},
        {'action': 'BUY', 'symbol': 'GOOGL', 'quantity': 50, 'price': 2800.00},
        {'action': 'SELL', 'symbol': 'AAPL', 'quantity': 100, 'price': 155.00},
    ]
    
    config = MessagingConfig.create_client_config()
    
    try:
        with OrderClient(**config) as client:
            for i, signal in enumerate(signals):
                # Convert signal to order
                order = OrderMessage(
                    order_id=f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{i}",
                    symbol=signal['symbol'],
                    side=OrderSide.BUY if signal['action'] == 'BUY' else OrderSide.SELL,
                    order_type=OrderType.LIMIT,
                    quantity=signal['quantity'],
                    price=signal['price']
                )
                
                logger.info(f"Signal {i+1}: {order.side.value} {order.quantity} {order.symbol} @ {order.price}")
                
                # Send order
                execution = client.send_order(order)
                
                if execution:
                    logger.info(f"  -> Execution: {execution.status} - {execution.quantity} @ {execution.price}")
                else:
                    logger.warning(f"  -> No execution received")
                    
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        logger.info("Make sure the matching engine is running")
    except Exception as e:
        logger.error(f"Error: {e}")


def main():
    """
    Main function to run examples.
    """
    print("\nZeroMQ Messaging Layer Example")
    print("=" * 50)
    print("\nThis example demonstrates order submission to a matching engine.")
    print("Note: This requires a matching engine to be running at the configured endpoint.")
    print(f"Default endpoint: {MessagingConfig.DEFAULT_ORDER_ENDPOINT}")
    print("\nYou can override the endpoint with environment variables:")
    print("  export MATCHING_ENGINE_ORDER_ENDPOINT=tcp://localhost:5555")
    print("  export MESSAGING_TIMEOUT_MS=5000")
    print("=" * 50)
    
    try:
        # Run example 1: Send a single order
        example_send_order()
        print("\n" + "-" * 50 + "\n")
        
        # Run example 2: Strategy integration
        example_strategy_integration()
        
    except KeyboardInterrupt:
        logger.info("\nExample interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
