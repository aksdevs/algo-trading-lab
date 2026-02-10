# Algo Trading Lab (strat-backtest-py)

This repository provides a Python-based algorithmic trading strategy and backtesting service. It is part of a microservice architecture for algorithmic trading systems. Source code is organized under the `src/` package so components can be used together or independently.

## Microservice Architecture

This service is designed to work with other microservices in the algo trading ecosystem:
- **strat-backtest-py** (this repo): Python strategy development and backtesting
- **match-engine-core**: C++ high-performance matching engine
- Communication via ZeroMQ messaging layer using JSON

## Included Packages
- `src/data`: data fetching and preprocessing utilities
- `src/strategies`: strategy interfaces and example strategies
- `src/backtesting`: backtesting engine, risk analysis, and visualization helpers
- `src/messaging`: ZeroMQ-based messaging layer for order/execution communication
- `src/utils`: configuration and logging helpers

Quick start
1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run tests:

```bash
pip install pytest
pytest -q
```

## Messaging Layer

The messaging layer enables communication with the matching engine via ZeroMQ. Orders are sent as JSON messages and executions are received back.

### Configuration

Configure endpoints via environment variables:
```bash
export MATCHING_ENGINE_ORDER_ENDPOINT=tcp://localhost:5555
export MATCHING_ENGINE_EXECUTION_ENDPOINT=tcp://localhost:5556
export MESSAGING_TIMEOUT_MS=5000
```

### Example Usage

```python
from src.messaging import OrderClient, OrderMessage, OrderSide, OrderType
from src.messaging.config import MessagingConfig

# Create order client
config = MessagingConfig.create_client_config()
with OrderClient(**config) as client:
    # Create and send order
    order = OrderMessage(
        order_id="ORD001",
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=100,
        price=150.50
    )
    
    # Send order and receive execution
    execution = client.send_order(order)
    if execution:
        print(f"Order filled: {execution.status}")
```

See `src/messaging/example_usage.py` for complete examples.

## Architecture Roadmap

This project follows a phased development roadmap:

**Phase 1: L2 Limit Order Book (C++)**
- Matching engine implementation in C++

**Phase 2: FIX/WebSocket Integration (Python)**
- Market connectivity protocols

**Phase 3: Performance Testing**
- Google Benchmark integration
- Latency optimization

**Phase 4: Strategy Wrapper**
- pybind11 integration for C++ strategy execution

Notes
- Run commands from the repository root so `src` imports resolve.
- `requirements.txt` is a merged list; pin versions as necessary for your environment.
- License: see `LICENSE` in the repository root.
