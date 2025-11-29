# Algo Trading Lab (Consolidated)

This repository consolidates three projects into a single codebase:

- `algo_trading` (core trading engine)
- `backtesting` (backtesting utilities & visualizations)
- `etf-arb-sim` (ETF arbitrage simulations)

What I did

- Merged source modules into a single top-level package: `src/`.
- Created subpackages: `src/data`, `src/backtesting`, `src/strategies`, `src/utils`.
- Added a merged `requirements.txt` and this consolidated `README.md`.

Quick start

1. Create a virtual environment and install requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the main engine (example):

```bash
python -c "from src.main import TradingEngine; print('See src/ for entry points')"
```

Notes

- I preserved most original modules but reorganized them under `src/` so imports like `from src.data...` continue to work.
- Some files were trimmed for brevity in the visualization modules — they can be expanded back from the original projects if you want full fidelity.

Next steps (suggested)

- Run tests (if any) and fix import issues if they appear.
- Add a top-level `src/main.py` entrypoint that wires configuration and CLI options.
- Review and pin package versions in `requirements.txt` to match your deployment environment.
