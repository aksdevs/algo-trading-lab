# Algo Trading Lab

This repository provides a consolidated algorithmic trading toolkit. Source code is organized under the `src/` package so components can be used together or independently.

Included packages
- `src/data`: data fetching and preprocessing utilities
- `src/strategies`: strategy interfaces and example strategies
- `src/backtesting`: backtesting engine, risk analysis, and visualization helpers
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

Notes
- Run commands from the repository root so `src` imports resolve.
- `requirements.txt` is a merged list; pin versions as necessary for your environment.
- License: see `LICENSE` in the repository root.

If you want a CLI entrypoint or CI configured to run tests automatically, I can add those next.
