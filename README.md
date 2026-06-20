# FIB-Invest

Personal quantitative investment platform — A-share market data, strategy engine, backtesting, simulated trading, and risk management in a single Docker Compose stack.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   React SPA (TypeScript)                     │
│   Dashboard │ Market │ Strategies │ Backtest │ Orders       │
├──────────────────────────┬──────────────────────────────────┤
│                    FastAPI Server                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ Data     │ │ Strategy │ │ Backtest │ │ Task     │      │
│  │ Provider │ │ Engine   │ │ Engine   │ │ Queue    │      │
│  │ (AKShare)│ │          │ │          │ │ (arq)    │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│  ┌──────────┐ ┌──────────────────────────┐                 │
│  │ Execution│ │ Risk Engine              │   SQLite        │
│  │ Pipeline │ │ (composable rules)       │   / PostgreSQL  │
│  └──────────┘ └──────────────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

## Features

- **Market Data** — Daily OHLCV bars via AKShare, pluggable provider architecture for future commercial sources. Supports symbol search, K-line charts, and data inspection.
- **Strategy Engine** — Unified `Strategy` interface (`on_bar()`) with built-in dual moving average crossover. Supports technical indicators, multi-factor models, and AI/ML strategies (v3.0). Each strategy is configured via a YAML file.
- **Dual Execution Modes** — `auto` (signal → risk check → order submitted immediately) or `semi-auto` (signal → risk check → order held for manual approval).
- **Risk Management** — All signals pass through a mandatory risk pipeline with composable rules: daily loss limit, position size cap, cancel limit, strategy circuit breaker, price limit protection.
- **Backtesting** — Bar-by-bar historical replay with configurable commission, slippage, warm-up period, and complete performance metrics.
- **Performance Metrics** — Total return, annualized return, max drawdown, Sharpe ratio, Sortino ratio, Calmar ratio, volatility, win rate, PnL breakdown.
- **Async Task Worker** — arq + Redis for background data sync, strategy execution, and AI inference.
- **Docker Compose** — One-command startup: `docker compose up`.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python 3.12+), SQLAlchemy 2.0 (async), Alembic |
| Database | SQLite → PostgreSQL (one-line config swap) |
| Task Queue | arq + Redis |
| Data | AKShare, pandas, numpy |
| Frontend | React 19, TypeScript, Vite |
| UI | Ant Design 5, TradingView Lightweight Charts |
| Deployment | Docker Compose |

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose (or run services manually)

### Docker (recommended)

```bash
# Start all services (backend, worker, Redis)
docker compose up

# The API is available at http://localhost:8000
# Health check: http://localhost:8000/health
# API docs:    http://localhost:8000/docs
```

### Manual Development

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
pnpm install
pnpm dev          # http://localhost:5173

# Worker (requires Redis)
redis-server
arq app.worker.worker.WorkerSettings
```

## Project Structure

```
fib-invest/
├── backend/
│   ├── app/
│   │   ├── data/           # Data module — providers, adapters, service layer
│   │   │   └── adapters/   # AKShare adapter (pluggable)
│   │   ├── strategy/       # Strategy engine — base class, registry, builtins
│   │   │   └── builtins/   # Built-in strategies (ma_cross, ...)
│   │   ├── backtest/       # Backtest engine, simulated broker, metrics
│   │   ├── execution/      # Order pipeline, broker adapters, simulated broker
│   │   │   └── adapters/   # Broker adapter implementations
│   │   ├── risk/           # Risk engine and composable risk rules
│   │   │   └── rules/      # Built-in risk rules
│   │   ├── api/            # FastAPI route handlers
│   │   ├── models/         # SQLAlchemy ORM models
│   │   └── core/           # Configuration, database setup
│   ├── worker/             # arq background worker and tasks
│   └── tests/
├── frontend/
│   └── src/
│       ├── pages/          # Dashboard, Market, Strategies, Backtest, Orders
│       ├── components/     # Layout, EquityChart
│       ├── api/            # API client and endpoint definitions
│       └── types/          # TypeScript type definitions
├── strategy_configs/       # Per-strategy YAML configuration files
├── data/                   # Local database (git-ignored)
└── docker-compose.yml
```

## API Endpoints

| Prefix | Description |
|--------|-------------|
| `GET /health` | Health check |
| `GET /api/data/bars?symbol=&start=&end=` | OHLCV bars |
| `GET /api/data/symbols?keyword=` | Symbol search |
| `GET /api/data/symbols/available` | List tracked symbols |
| `GET /api/strategies/` | List strategy types and running instances |
| `POST /api/strategies/run` | Start a strategy instance |
| `POST /api/backtest/run` | Run a backtest |
| `GET /api/backtest/results/{job_id}` | Get backtest results |
| `GET /api/orders/` | List orders |
| `POST /api/orders/` | Confirm a pending order |
| `GET /api/dashboard/account` | Account summary and positions |
| `GET /api/dashboard/equity` | Equity curve data |

Full OpenAPI docs at `http://localhost:8000/docs`.

## Strategy Configuration

Create a YAML file in `strategy_configs/`:

```yaml
# strategy_configs/example_ma_cross.yaml
strategy_type: ma_cross
name: 均线交叉示例
symbols:
  - "000001.sz"
params:
  fast: 5
  slow: 20
  signal_cooldown: 5
  confirm_bars: 3
mode: semi-auto      # or "auto"
risk_profile:
  max_position_pct: 0.2
  daily_loss_limit: 5000
```

**Modes:**
- `semi-auto` — Signals generate **pending** orders; manual confirmation required before execution
- `auto` — Signals pass risk checks and are submitted immediately

## Writing a Custom Strategy

Implement the `Strategy` interface:

```python
from app.strategy.base import Strategy
from app.strategy.signal import Signal

class MyStrategy(Strategy):
    name = "my_strategy"
    frequency = "daily"

    async def on_start(self) -> None:
        """Initialize indicators, load models."""

    async def on_bar(self, bar) -> Signal | None:
        """Process one bar, return a signal or None."""

    async def on_stop(self) -> None:
        """Cleanup."""
```

Register it in `app/strategy/builtins/__init__.py` and it becomes available system-wide — including backtesting and live execution.

## Risk Rules

All built-in rules are composable per strategy:

| Rule | Description |
|------|-------------|
| `daily_loss` | Circuit break when daily P&L exceeds threshold |
| `position_limit` | Cap single-position exposure as % of portfolio |
| `price_limit` | Block orders on limit-up/limit-down stocks |
| `cancel_limit` | Suspend strategy after N cancellations |
| `strategy_circuit` | Pause strategy after N consecutive losses |

## Roadmap

| Version | Scope |
|---------|-------|
| v1.0 ✅ | Daily A-share data, technical strategies, backtest engine, simulated trading, risk management, web dashboard |
| v1.1 | Minute-level data, intraday strategies |
| v1.2 | Commercial data source adapters (TuShare Pro) |
| v2.0 | Live brokerage integration |
| v2.1 | Multi-market support (US equities, crypto) |
| v3.0 | AI/ML strategies — LLM agent decision-making, reinforcement learning |

## License

MIT
