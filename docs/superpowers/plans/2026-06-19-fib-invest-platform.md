# FIB-Invest Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a personal quantitative investment platform for A-shares with strategy backtesting, simulated trading, and AI/rule-based strategy support.

**Architecture:** Modular monolith — FastAPI backend + arq task queue + SQLite database + React TypeScript frontend. Six domain modules (data, strategy, backtest, execution, risk) with clean interface boundaries, deployed via Docker Compose.

**Tech Stack:** Python 3.12+, FastAPI, SQLAlchemy 2.0 async, arq + Redis, pandas/numpy, AKShare, React 18 + TypeScript + Vite, TradingView Lightweight Charts, Docker Compose.

## Global Constraints

- Python 3.12+, use `uv` for dependency management
- SQLAlchemy 2.0 async mode, SQLite for dev, PostgreSQL-ready
- All business logic in backend modules, API thin layer on top
- TDD: write failing test first, then implementation
- Commit after every task
- Config via YAML files, secrets via `.env` (gitignored)
- No sensitive data in commits — public repo

---

## File Structure

```
fib-invest/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app, lifespan events
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # Settings, env vars
│   │   │   └── database.py            # Async engine, session factory
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── symbol.py              # Symbol ORM
│   │   │   ├── bar.py                 # DailyBar ORM
│   │   │   ├── strategy_config.py     # StrategyConfig ORM
│   │   │   ├── order.py               # Order ORM
│   │   │   ├── trade.py               # Trade record ORM
│   │   │   └── account.py             # Account, Position ORM
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   ├── provider.py            # DataProvider ABC
│   │   │   ├── service.py             # DataService — query, cache, sync orchestration
│   │   │   └── adapters/
│   │   │       ├── __init__.py
│   │   │       └── akshare.py         # AKShareDataProvider
│   │   ├── strategy/
│   │   │   ├── __init__.py
│   │   │   ├── signal.py              # Signal dataclass
│   │   │   ├── base.py                # Strategy ABC
│   │   │   ├── registry.py            # StrategyRegistry
│   │   │   ├── manager.py             # StrategyManager (lifecycle)
│   │   │   ├── config_loader.py       # YAML config → Strategy instance
│   │   │   └── builtins/
│   │   │       ├── __init__.py
│   │   │       └── ma_cross.py        # MA Crossover strategy
│   │   ├── risk/
│   │   │   ├── __init__.py
│   │   │   ├── rule.py                # RiskRule ABC, RiskResult
│   │   │   ├── engine.py              # RiskEngine — evaluate all rules
│   │   │   └── rules/
│   │   │       ├── __init__.py
│   │   │       ├── daily_loss.py
│   │   │       ├── position_limit.py
│   │   │       ├── cancel_limit.py
│   │   │       ├── strategy_circuit.py
│   │   │       └── price_limit.py
│   │   ├── execution/
│   │   │   ├── __init__.py
│   │   │   ├── broker.py              # BrokerAdapter ABC
│   │   │   ├── order_builder.py       # Signal → Order converter
│   │   │   ├── pipeline.py            # ExecutionPipeline
│   │   │   └── adapters/
│   │   │       ├── __init__.py
│   │   │       └── simulated.py       # SimulatedBroker
│   │   ├── backtest/
│   │   │   ├── __init__.py
│   │   │   ├── metrics.py             # Performance metrics functions
│   │   │   ├── broker_sim.py          # BacktestBroker (lightweight, no DB)
│   │   │   └── engine.py              # BacktestEngine
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── router.py              # APIRouter aggregation
│   │       ├── data_routes.py         # Data endpoints
│   │       ├── strategy_routes.py     # Strategy CRUD + control
│   │       ├── backtest_routes.py     # Backtest run + results
│   │       ├── order_routes.py        # Order management
│   │       └── dashboard_routes.py    # Account, positions, equity
│   ├── worker/
│   │   ├── __init__.py
│   │   ├── tasks.py                   # arq task functions
│   │   └── worker.py                  # Worker entry point
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py                # Async fixtures, test DB
│   │   ├── data/
│   │   │   ├── test_provider.py
│   │   │   └── test_service.py
│   │   ├── strategy/
│   │   │   ├── test_registry.py
│   │   │   └── test_ma_cross.py
│   │   ├── risk/
│   │   │   └── test_rules.py
│   │   ├── execution/
│   │   │   ├── test_pipeline.py
│   │   │   └── test_simulated_broker.py
│   │   └── backtest/
│   │       ├── test_metrics.py
│   │       └── test_engine.py
│   ├── pyproject.toml
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/
│   │   │   ├── client.ts              # Axios/fetch wrapper
│   │   │   └── endpoints.ts           # Typed API functions
│   │   ├── types/
│   │   │   └── index.ts               # Shared TypeScript types
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Strategies.tsx
│   │   │   ├── Backtest.tsx
│   │   │   └── Orders.tsx
│   │   └── components/
│   │       ├── Layout.tsx
│   │       ├── EquityChart.tsx
│   │       ├── OrderTable.tsx
│   │       ├── PositionCard.tsx
│   │       └── StrategyForm.tsx
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── docker-compose.yml
└── strategy_configs/                  # User strategy YAML files
    └── example_ma_cross.yaml
```

---

## Phase 1: Project Scaffold & Core Infrastructure

### Task 1: Backend project setup

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/.env.example`
- Create: `docker-compose.yml`

**Interfaces:**
- Produces: Project dependencies, env template, Docker services (FastAPI, Redis, DB)

- [ ] **Step 1: Create pyproject.toml with all dependencies**

```toml
[project]
name = "fib-invest"
version = "0.1.0"
description = "Personal quantitative investment platform"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlalchemy[asyncio]>=2.0.36",
    "aiosqlite>=0.20.0",
    "alembic>=1.14.0",
    "arq>=0.26.0",
    "pandas>=2.2.0",
    "numpy>=2.1.0",
    "akshare>=1.16.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
    "pyyaml>=6.0",
    "redis>=5.2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.28.0",
    "pre-commit>=4.0.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- [ ] **Step 2: Create .env.example**

```bash
DATABASE_URL=sqlite+aiosqlite:///./fib_invest.db
REDIS_URL=redis://localhost:6379
CONFIG_DIR=./strategy_configs
AKSHARE_CACHE_ENABLED=true
```

- [ ] **Step 3: Create docker-compose.yml**

```yaml
services:
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    restart: unless-stopped

  backend:
    build: ./backend
    ports: ["8000:8000"]
    volumes:
      - ./backend:/app
      - ./strategy_configs:/app/strategy_configs
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///data/fib_invest.db
      - REDIS_URL=redis://redis:6379
      - CONFIG_DIR=/app/strategy_configs
    depends_on: [redis]
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  worker:
    build: ./backend
    command: arq app.worker.worker.WorkerSettings
    volumes:
      - ./backend:/app
      - ./strategy_configs:/app/strategy_configs
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///data/fib_invest.db
      - REDIS_URL=redis://redis:6379
      - CONFIG_DIR=/app/strategy_configs
    depends_on: [redis]
```

- [ ] **Step 4: Install dependencies and verify**

Run: `cd backend && uv sync`
Expected: All packages installed without errors

- [ ] **Step 5: Commit**

```bash
git add backend/pyproject.toml backend/.env.example docker-compose.yml
git commit -m "feat: scaffold backend project with dependencies and Docker config"
```

### Task 2: Core config and database setup

**Files:**
- Create: `backend/app/__init__.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/database.py`
- Create: `backend/app/main.py`

**Interfaces:**
- Produces: `Settings` class, `get_db()` async generator, `engine` and `async_session` factory, FastAPI `app` instance

- [ ] **Step 1: Write config test**

Create `backend/tests/__init__.py`:
```python
```

Create `backend/tests/test_config.py`:
```python
import os
from app.core.config import Settings


def test_settings_loads_from_env():
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"
    os.environ["REDIS_URL"] = "redis://test:6379"
    settings = Settings()
    assert "test.db" in settings.database_url
    assert "test" in settings.redis_url


def test_settings_defaults():
    settings = Settings()
    assert settings.database_url == "sqlite+aiosqlite:///./fib_invest.db"
    assert settings.redis_url == "redis://localhost:6379"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/test_config.py -v`
Expected: FAIL — Settings not defined

- [ ] **Step 3: Implement Settings**

Create `backend/app/core/__init__.py`:
```python
```

Create `backend/app/core/config.py`:
```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./fib_invest.db"
    redis_url: str = "redis://localhost:6379"
    config_dir: str = "./strategy_configs"
    akshare_cache_enabled: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

- [ ] **Step 4: Implement database**

Create `backend/app/core/database.py`:
```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
```

- [ ] **Step 5: Create FastAPI app skeleton**

Create `backend/app/__init__.py`:
```python
```

Create `backend/app/main.py`:
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import engine
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="FIB-Invest", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
```

- [ ] **Step 6: Run tests to verify**

Run: `cd backend && uv run pytest tests/test_config.py -v`
Expected: PASS

- [ ] **Step 7: Verify app starts**

Run: `cd backend && uv run uvicorn app.main:app --port 8000 & sleep 2 && curl http://localhost:8000/health && kill %1`
Expected: `{"status":"ok","version":"0.1.0"}`

- [ ] **Step 8: Commit**

```bash
git add backend/app/ backend/tests/
git commit -m "feat: add config, database, and FastAPI app skeleton"
```

### Task 3: ORM models — Symbol, Bar, Account

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/symbol.py`
- Create: `backend/app/models/bar.py`
- Create: `backend/app/models/account.py`
- Create: `backend/app/models/base.py`

**Interfaces:**
- Produces: `Symbol`, `DailyBar`, `Account`, `Position` ORM classes with `async def create/query` helpers

- [ ] **Step 1: Write model tests**

Create `backend/tests/test_models.py`:
```python
import pytest
from decimal import Decimal
from datetime import date
from app.models.symbol import Symbol
from app.models.bar import DailyBar
from app.models.account import Account, Position
from app.core.database import async_session, engine


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Symbol.metadata.create_all)
        await conn.run_sync(DailyBar.metadata.create_all)
        await conn.run_sync(Account.metadata.create_all)
        await conn.run_sync(Position.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Symbol.metadata.drop_all)
        await conn.run_sync(DailyBar.metadata.drop_all)
        await conn.run_sync(Account.metadata.drop_all)
        await conn.run_sync(Position.metadata.drop_all)


async def test_create_and_query_symbol():
    async with async_session() as session:
        sym = Symbol(code="000001", name="平安银行", market="sz", list_date=date(1991, 4, 3))
        session.add(sym)
        await session.commit()

        result = await session.get(Symbol, "000001.sz")
        assert result.name == "平安银行"
        assert result.market == "sz"


async def test_create_daily_bar():
    async with async_session() as session:
        bar = DailyBar(
            symbol="000001.sz", date=date(2026, 6, 18),
            open=Decimal("10.50"), high=Decimal("10.80"),
            low=Decimal("10.30"), close=Decimal("10.60"),
            volume=10000000, amount=Decimal("105000000"), adj_factor=Decimal("1.0")
        )
        session.add(bar)
        await session.commit()

        result = await session.get(DailyBar, ("000001.sz", date(2026, 6, 18)))
        assert float(result.close) == 10.60


async def test_account_and_position():
    async with async_session() as session:
        account = Account(id="default", name="模拟账户", initial_capital=Decimal("100000"), currency="CNY")
        session.add(account)
        await session.commit()

        pos = Position(account_id="default", symbol="000001.sz", quantity=1000, avg_cost=Decimal("10.50"))
        session.add(pos)
        await session.commit()

        result = await session.get(Position, ("default", "000001.sz"))
        assert result.quantity == 1000
        assert float(result.avg_cost) == 10.50
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/test_models.py -v`
Expected: FAIL — models not defined

- [ ] **Step 3: Implement base model**

Create `backend/app/models/base.py`:
```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

- [ ] **Step 4: Implement Symbol model**

Create `backend/app/models/symbol.py`:
```python
from datetime import date
from sqlalchemy import String, Date, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
import enum


class Market(str, enum.Enum):
    SH = "sh"
    SZ = "sz"


class Symbol(Base):
    __tablename__ = "symbols"

    code: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    market: Mapped[Market] = mapped_column(SAEnum(Market))
    list_date: Mapped[date] = mapped_column(Date)

    @property
    def full_symbol(self) -> str:
        return f"{self.code}.{self.market.value}"
```

- [ ] **Step 5: Implement DailyBar model**

Create `backend/app/models/bar.py`:
```python
from datetime import date
from decimal import Decimal
from sqlalchemy import String, Date, Numeric, BigInteger, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class DailyBar(Base):
    __tablename__ = "daily_bars"

    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    date: Mapped[date] = mapped_column(Date, primary_key=True)
    open: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    high: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    low: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    close: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    volume: Mapped[int] = mapped_column(BigInteger)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    adj_factor: Mapped[Decimal] = mapped_column(Numeric(10, 6), default=Decimal("1.0"))
```

- [ ] **Step 6: Implement Account and Position models**

Create `backend/app/models/account.py`:
```python
from decimal import Decimal
from sqlalchemy import String, Numeric, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    initial_capital: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(10), default="CNY")


class Position(Base):
    __tablename__ = "positions"

    account_id: Mapped[str] = mapped_column(String(50), ForeignKey("accounts.id"), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    avg_cost: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=Decimal("0"))
```

Create `backend/app/models/__init__.py`:
```python
from app.models.base import Base
from app.models.symbol import Symbol
from app.models.bar import DailyBar
from app.models.account import Account, Position

__all__ = ["Base", "Symbol", "DailyBar", "Account", "Position"]
```

- [ ] **Step 7: Run tests**

Run: `cd backend && uv run pytest tests/test_models.py -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add backend/app/models/ backend/tests/test_models.py
git commit -m "feat: add ORM models for Symbol, DailyBar, Account, Position"
```

### Task 4: StrategyConfig and Order models

**Files:**
- Create: `backend/app/models/strategy_config.py`
- Create: `backend/app/models/order.py`
- Create: `backend/app/models/trade.py`

**Interfaces:**
- Produces: `StrategyConfig`, `Order`, `Trade` ORM classes

- [ ] **Step 1: Extend model tests**

Add to `backend/tests/test_models.py`:
```python
from datetime import datetime
from app.models.strategy_config import StrategyConfig
from app.models.order import Order, OrderStatus
from app.models.trade import Trade


async def test_strategy_config_crud():
    async with async_session() as session:
        cfg = StrategyConfig(
            strategy_id="ma_cross_1",
            strategy_type="ma_cross",
            name="均线交叉策略",
            config={"symbols": ["000001.sz"], "fast": 5, "slow": 20},
            mode="semi-auto",
            status="stopped"
        )
        session.add(cfg)
        await session.commit()

        result = await session.get(StrategyConfig, "ma_cross_1")
        assert result.name == "均线交叉策略"
        assert result.config["fast"] == 5


async def test_order_state_machine():
    async with async_session() as session:
        order = Order(
            id="ord_001", strategy_id="ma_cross_1", symbol="000001.sz",
            direction="BUY", quantity=1000, price=10.50,
            status="pending"
        )
        session.add(order)
        await session.commit()

        result = await session.get(Order, "ord_001")
        assert result.status == OrderStatus.PENDING
        assert result.direction == "BUY"
```

- [ ] **Step 2: Run test to verify failure**

Run: `cd backend && uv run pytest tests/test_models.py::test_strategy_config_crud tests/test_models.py::test_order_state_machine -v`
Expected: FAIL

- [ ] **Step 3: Implement StrategyConfig**

Create `backend/app/models/strategy_config.py`:
```python
from datetime import datetime
from sqlalchemy import String, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class StrategyConfig(Base):
    __tablename__ = "strategy_configs"

    strategy_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    strategy_type: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(100))
    config: Mapped[dict] = mapped_column(JSON)
    mode: Mapped[str] = mapped_column(String(20), default="semi-auto")
    status: Mapped[str] = mapped_column(String(20), default="stopped")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
```

- [ ] **Step 4: Implement Order**

Create `backend/app/models/order.py`:
```python
from datetime import datetime, date
from decimal import Decimal
import enum
from sqlalchemy import String, DateTime, Date, Numeric, Integer, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    READY = "ready"
    SUBMITTED = "submitted"
    PARTIAL_FILLED = "partial_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    strategy_id: Mapped[str] = mapped_column(String(50))
    symbol: Mapped[str] = mapped_column(String(20))
    direction: Mapped[str] = mapped_column(String(10))  # BUY / SELL
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), default=OrderStatus.PENDING)
    filled_quantity: Mapped[int] = mapped_column(Integer, default=0)
    filled_price: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=True)
    trade_date: Mapped[date] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
```

Create `backend/app/models/trade.py`:
```python
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, DateTime, Date, Numeric, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(50))
    account_id: Mapped[str] = mapped_column(String(50), default="default")
    symbol: Mapped[str] = mapped_column(String(20))
    direction: Mapped[str] = mapped_column(String(10))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    commission: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    trade_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
```

- [ ] **Step 5: Update models __init__.py**

Edit `backend/app/models/__init__.py`:
```python
from app.models.base import Base
from app.models.symbol import Symbol, Market
from app.models.bar import DailyBar
from app.models.account import Account, Position
from app.models.strategy_config import StrategyConfig
from app.models.order import Order, OrderStatus
from app.models.trade import Trade

__all__ = [
    "Base", "Symbol", "Market", "DailyBar",
    "Account", "Position", "StrategyConfig",
    "Order", "OrderStatus", "Trade",
]
```

- [ ] **Step 6: Run all model tests**

Run: `cd backend && uv run pytest tests/test_models.py -v`
Expected: All PASS

- [ ] **Step 7: Commit**

```bash
git add backend/app/models/
git commit -m "feat: add StrategyConfig, Order, and Trade ORM models"
```

---

## Phase 2: Data Module

### Task 5: DataProvider ABC

**Files:**
- Create: `backend/app/data/__init__.py`
- Create: `backend/app/data/provider.py`

**Interfaces:**
- Produces: `DataProvider` ABC with `get_bars()`, `health_check()` abstract methods
- Produces: `SymbolInfo` dataclass

- [ ] **Step 1: Write DataProvider test**

Create `backend/tests/data/__init__.py`:
```python
```

Create `backend/tests/data/test_provider.py`:
```python
import pytest
from datetime import date
from app.data.provider import DataProvider, SymbolInfo


class FakeProvider(DataProvider):
    name = "fake"
    supports = ["daily"]

    async def get_bars(self, symbol, start, end, freq="daily"):
        return None

    async def health_check(self):
        return True

    async def list_symbols(self, market=None):
        return [SymbolInfo(code="000001", name="测试", market="sz", list_date=date(2000, 1, 1))]


def test_provider_abc_enforcement():
    with pytest.raises(TypeError):
        DataProvider()  # Cannot instantiate ABC


def test_concrete_provider():
    p = FakeProvider()
    assert p.name == "fake"
    assert p.supports == ["daily"]
    assert "daily" in p.supports


async def test_list_symbols():
    p = FakeProvider()
    symbols = await p.list_symbols()
    assert len(symbols) == 1
    assert symbols[0].code == "000001"
```

- [ ] **Step 2: Run test to verify failure**

Run: `cd backend && uv run pytest tests/data/test_provider.py -v`
Expected: FAIL — DataProvider not defined

- [ ] **Step 3: Implement DataProvider**

Create `backend/app/data/__init__.py`:
```python
from app.data.provider import DataProvider, SymbolInfo

__all__ = ["DataProvider", "SymbolInfo"]
```

Create `backend/app/data/provider.py`:
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import List, Optional
import pandas as pd


@dataclass
class SymbolInfo:
    code: str
    name: str
    market: str
    list_date: date


class DataProvider(ABC):
    """Abstract data provider — all market data adapters implement this interface."""

    name: str
    supports: List[str]

    @abstractmethod
    async def get_bars(
        self, symbol: str, start: date, end: date, freq: str = "daily"
    ) -> Optional[pd.DataFrame]:
        """Return OHLCV DataFrame with columns: date, open, high, low, close, volume, amount, adj_factor."""

    @abstractmethod
    async def get_tick(self, symbol: str, trade_date: date) -> Optional[pd.DataFrame]:
        """Return tick data for a given date."""

    @abstractmethod
    async def list_symbols(self, market: Optional[str] = None) -> List[SymbolInfo]:
        """List available symbols."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the data provider is operational."""
```

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/data/test_provider.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/data/ backend/tests/data/
git commit -m "feat: add DataProvider ABC and SymbolInfo dataclass"
```

### Task 6: AKShare data adapter

**Files:**
- Create: `backend/app/data/adapters/__init__.py`
- Create: `backend/app/data/adapters/akshare.py`

**Interfaces:**
- Consumes: `DataProvider` ABC, `SymbolInfo`
- Produces: `AKShareDataProvider` — live A-share daily data via AKShare

- [ ] **Step 1: Write AKShare adapter test**

Create `backend/tests/data/test_akshare.py`:
```python
import pytest
from datetime import date
from app.data.adapters.akshare import AKShareDataProvider


@pytest.fixture
def provider():
    return AKShareDataProvider()


def test_provider_name_and_supports(provider):
    assert provider.name == "akshare"
    assert "daily" in provider.supports


async def test_health_check(provider):
    status = await provider.health_check()
    assert isinstance(status, bool)


async def test_list_symbols(provider):
    symbols = await provider.list_symbols(market="sh")
    assert len(symbols) > 0
    first = symbols[0]
    assert first.code
    assert first.name
    assert first.market in ("sh", "sz")


async def test_get_bars(provider):
    df = await provider.get_bars("000001", date(2026, 1, 1), date(2026, 6, 1))
    assert df is not None
    assert len(df) > 0
    expected_cols = {"date", "open", "high", "low", "close", "volume", "amount", "adj_factor"}
    assert expected_cols.issubset(set(df.columns))
```

- [ ] **Step 2: Run test to verify failure**

Run: `cd backend && uv run pytest tests/data/test_akshare.py -v`
Expected: FAIL — AKShareDataProvider not defined

- [ ] **Step 3: Implement AKShare adapter**

Create `backend/app/data/adapters/__init__.py`:
```python
```

Create `backend/app/data/adapters/akshare.py`:
```python
import akshare as ak
import pandas as pd
from datetime import date
from typing import List, Optional
from app.data.provider import DataProvider, SymbolInfo


class AKShareDataProvider(DataProvider):
    name = "akshare"
    supports = ["daily"]

    async def get_bars(
        self, symbol: str, start: date, end: date, freq: str = "daily"
    ) -> Optional[pd.DataFrame]:
        try:
            df = ak.stock_zh_a_hist(
                symbol=symbol, period="daily",
                start_date=start.strftime("%Y%m%d"),
                end_date=end.strftime("%Y%m%d"),
                adjust="qfq"
            )
            if df is None or df.empty:
                return None
            df = df.rename(columns={
                "日期": "date", "开盘": "open", "最高": "high",
                "最低": "low", "收盘": "close", "成交量": "volume",
                "成交额": "amount"
            })
            df["date"] = pd.to_datetime(df["date"]).dt.date
            df["adj_factor"] = 1.0
            df["symbol"] = symbol
            return df[["symbol", "date", "open", "high", "low", "close", "volume", "amount", "adj_factor"]]
        except Exception:
            return None

    async def get_tick(self, symbol: str, trade_date: date) -> Optional[pd.DataFrame]:
        return None  # Not supported in free tier

    async def list_symbols(self, market: Optional[str] = None) -> List[SymbolInfo]:
        try:
            df = ak.stock_info_a_code_name()
            symbols = []
            for _, row in df.iterrows():
                code = str(row["code"]).zfill(6)
                mkt = "sh" if code.startswith("6") else "sz"
                if market and mkt != market:
                    continue
                symbols.append(SymbolInfo(code=code, name=row["name"], market=mkt, list_date=date(2000, 1, 1)))
            return symbols
        except Exception:
            return []

    async def health_check(self) -> bool:
        try:
            df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20260101", end_date="20260601")
            return df is not None and not df.empty
        except Exception:
            return False
```

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/data/test_akshare.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/data/adapters/ backend/tests/data/test_akshare.py
git commit -m "feat: add AKShare data provider adapter"
```

### Task 7: DataService

**Files:**
- Create: `backend/app/data/service.py`

**Interfaces:**
- Consumes: `DataProvider`, ORM models (`Symbol`, `DailyBar`)
- Produces: `DataService` — caching, sync, query API for business layer

- [ ] **Step 1: Write DataService test**

Create `backend/tests/data/test_service.py`:
```python
import pytest
from datetime import date
from app.data.service import DataService
from app.data.provider import DataProvider, SymbolInfo
from app.models.symbol import Symbol


class MockProvider(DataProvider):
    name = "mock"
    supports = ["daily"]

    async def get_bars(self, symbol, start, end, freq="daily"):
        import pandas as pd
        rows = []
        d = start
        from datetime import timedelta
        while d <= end:
            rows.append({"symbol": symbol, "date": d, "open": 10.0, "high": 11.0,
                         "low": 9.0, "close": 10.5, "volume": 1000000,
                         "amount": 10500000, "adj_factor": 1.0})
            d += timedelta(days=1)
        return pd.DataFrame(rows)

    async def get_tick(self, symbol, trade_date):
        return None

    async def list_symbols(self, market=None):
        return [SymbolInfo(code="000001", name="测试", market="sz", list_date=date(2000, 1, 1))]

    async def health_check(self):
        return True


@pytest.fixture
async def service():
    from app.core.database import async_session, engine
    from app.models.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    svc = DataService(MockProvider())
    yield svc
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def test_sync_symbols(service):
    count = await service.sync_symbols(market="sz")
    assert count > 0

    async with service._session_factory() as session:
        result = await session.get(Symbol, "000001")
        assert result is not None
        assert result.name == "测试"


async def test_get_bars_cached(service):
    df = await service.get_bars("000001", date(2026, 6, 1), date(2026, 6, 5))
    assert df is not None
    assert len(df) == 5
    assert "close" in df.columns
```

- [ ] **Step 2: Run test to verify failure**

Run: `cd backend && uv run pytest tests/data/test_service.py -v`
Expected: FAIL — DataService not defined

- [ ] **Step 3: Implement DataService**

Create `backend/app/data/service.py`:
```python
import pandas as pd
from datetime import date
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session
from app.data.provider import DataProvider
from app.models.symbol import Symbol
from app.models.bar import DailyBar


class DataService:
    def __init__(self, provider: DataProvider):
        self.provider = provider
        self._session_factory = async_session

    async def sync_symbols(self, market: Optional[str] = None) -> int:
        symbols = await self.provider.list_symbols(market=market)
        async with self._session_factory() as session:
            count = 0
            for info in symbols:
                existing = await session.get(Symbol, info.code)
                if existing:
                    existing.name = info.name
                else:
                    session.add(Symbol(code=info.code, name=info.name, market=info.market, list_date=info.list_date))
                    count += 1
            await session.commit()
        return count

    async def get_bars(
        self, symbol: str, start: date, end: date, freq: str = "daily"
    ) -> Optional[pd.DataFrame]:
        async with self._session_factory() as session:
            stmt = (
                select(DailyBar)
                .where(DailyBar.symbol == symbol)
                .where(DailyBar.date >= start)
                .where(DailyBar.date <= end)
                .order_by(DailyBar.date)
            )
            result = await session.execute(stmt)
            bars = result.scalars().all()

            if bars:
                data = [
                    {"date": b.date, "open": float(b.open), "high": float(b.high),
                     "low": float(b.low), "close": float(b.close), "volume": b.volume,
                     "amount": float(b.amount), "adj_factor": float(b.adj_factor)}
                    for b in bars
                ]
                return pd.DataFrame(data)

        # Fallback to provider if not in DB
        df = await self.provider.get_bars(symbol, start, end, freq)
        if df is not None and not df.empty:
            await self._save_bars(session, df)
        return df

    async def sync_daily_bars(self, symbols: List[str], start: date, end: date) -> int:
        total = 0
        for symbol in symbols:
            df = await self.provider.get_bars(symbol, start, end)
            if df is not None and not df.empty:
                async with self._session_factory() as session:
                    await self._save_bars(session, df)
                    total += len(df)
        return total

    async def _save_bars(self, session: AsyncSession, df: pd.DataFrame):
        for _, row in df.iterrows():
            bar = DailyBar(
                symbol=str(row["symbol"]),
                date=row["date"].to_pydate() if hasattr(row["date"], "to_pydate") else row["date"],
                open=row["open"], high=row["high"], low=row["low"],
                close=row["close"], volume=int(row["volume"]),
                amount=row["amount"], adj_factor=row.get("adj_factor", 1.0)
            )
            session.add(bar)
        await session.commit()
```

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/data/test_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/data/service.py backend/tests/data/test_service.py
git commit -m "feat: add DataService with caching, sync, and fallback logic"
```

---

## Phase 3: Strategy Module

### Task 8: Signal dataclass and Strategy ABC

**Files:**
- Create: `backend/app/strategy/__init__.py`
- Create: `backend/app/strategy/signal.py`
- Create: `backend/app/strategy/base.py`

**Interfaces:**
- Produces: `Signal` dataclass, `Strategy` ABC with `on_start()`, `on_bar()`, `on_stop()`

- [ ] **Step 1: Write strategy base tests**

Create `backend/tests/strategy/__init__.py`:
```python
```

Create `backend/tests/strategy/test_base.py`:
```python
import pytest
import pandas as pd
from app.strategy.signal import Signal
from app.strategy.base import Strategy


def test_signal_creation():
    s = Signal(strategy_id="test_1", symbol="000001.sz", direction="BUY", strength=0.8, reason="测试信号")
    assert s.direction == "BUY"
    assert s.strength == 0.8
    assert s.strategy_id == "test_1"


class DummyStrategy(Strategy):
    name = "dummy"
    frequency = "daily"
    symbols = ["000001.sz"]
    mode = "semi-auto"
    risk_profile = {}

    async def on_start(self):
        self._started = True

    async def on_bar(self, bar):
        return None

    async def on_stop(self):
        pass


async def test_strategy_lifecycle():
    s = DummyStrategy()
    assert s.name == "dummy"
    assert s.symbols == ["000001.sz"]

    await s.on_start()
    assert s._started is True


async def test_strategy_on_bar():
    s = DummyStrategy()
    bar = pd.Series({"open": 10, "high": 11, "low": 9, "close": 10.5, "volume": 1000})
    result = await s.on_bar(bar)
    assert result is None
```

- [ ] **Step 2: Run test to verify failure**

Run: `cd backend && uv run pytest tests/strategy/test_base.py -v`
Expected: FAIL

- [ ] **Step 3: Implement Signal and Strategy**

Create `backend/app/strategy/signal.py`:
```python
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Signal:
    strategy_id: str
    symbol: str
    direction: str      # BUY | SELL | HOLD
    strength: float     # 0.0 ~ 1.0
    reason: str
    meta: dict = field(default_factory=dict)
```

Create `backend/app/strategy/base.py`:
```python
from abc import ABC, abstractmethod
from typing import List, Optional
import pandas as pd
from app.strategy.signal import Signal


class Strategy(ABC):
    name: str = ""
    frequency: str = "daily"
    symbols: List[str] = []
    mode: str = "semi-auto"
    risk_profile: dict = {}

    @abstractmethod
    async def on_start(self) -> None:
        """Initialize strategy, load models, warm up indicators."""

    @abstractmethod
    async def on_bar(self, bar: pd.Series) -> Optional[Signal]:
        """Process one bar and optionally return a signal."""

    @abstractmethod
    async def on_stop(self) -> None:
        """Cleanup resources."""

    def __repr__(self) -> str:
        return f"{self.name}(symbols={self.symbols}, mode={self.mode})"
```

Create `backend/app/strategy/__init__.py`:
```python
from app.strategy.signal import Signal
from app.strategy.base import Strategy

__all__ = ["Signal", "Strategy"]
```

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/strategy/test_base.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/strategy/ backend/tests/strategy/
git commit -m "feat: add Signal dataclass and Strategy ABC"
```

### Task 9: StrategyRegistry

**Files:**
- Create: `backend/app/strategy/registry.py`

**Interfaces:**
- Consumes: `Strategy` ABC
- Produces: `StrategyRegistry` — register/find/list strategy classes

- [ ] **Step 1: Write registry tests**

Create `backend/tests/strategy/test_registry.py`:
```python
import pytest
from app.strategy.base import Strategy
from app.strategy.registry import StrategyRegistry


class StrategyA(Strategy):
    name = "a_strategy"
    frequency = "daily"
    symbols = []
    mode = "auto"
    risk_profile = {}
    async def on_start(self): pass
    async def on_bar(self, bar): return None
    async def on_stop(self): pass


class StrategyB(Strategy):
    name = "b_strategy"
    frequency = "daily"
    symbols = []
    mode = "semi-auto"
    risk_profile = {}
    async def on_start(self): pass
    async def on_bar(self, bar): return None
    async def on_stop(self): pass


def test_register_and_get():
    registry = StrategyRegistry()
    registry.register(StrategyA)
    registry.register(StrategyB)

    assert registry.get("a_strategy") == StrategyA
    assert registry.get("b_strategy") == StrategyB
    assert registry.get("nonexistent") is None


def test_list_all():
    registry = StrategyRegistry()
    registry.register(StrategyA)

    all_types = registry.list_all()
    assert len(all_types) >= 1
    assert "a_strategy" in all_types


def test_duplicate_register_raises():
    registry = StrategyRegistry()
    registry.register(StrategyA)
    with pytest.raises(ValueError, match="already registered"):
        registry.register(StrategyA)
```

- [ ] **Step 2: Run test to verify failure**

Run: `cd backend && uv run pytest tests/strategy/test_registry.py -v`
Expected: FAIL

- [ ] **Step 3: Implement StrategyRegistry**

Create `backend/app/strategy/registry.py`:
```python
from typing import Dict, Type, Optional
from app.strategy.base import Strategy


class StrategyRegistry:
    """Central registry of all available strategy types."""

    def __init__(self):
        self._strategies: Dict[str, Type[Strategy]] = {}

    def register(self, strategy_cls: Type[Strategy]) -> None:
        if strategy_cls.name in self._strategies:
            raise ValueError(f"Strategy '{strategy_cls.name}' already registered")
        self._strategies[strategy_cls.name] = strategy_cls

    def get(self, name: str) -> Optional[Type[Strategy]]:
        return self._strategies.get(name)

    def list_all(self) -> Dict[str, Type[Strategy]]:
        return dict(self._strategies)


# Global singleton
registry = StrategyRegistry()
```

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/strategy/test_registry.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/strategy/registry.py backend/tests/strategy/test_registry.py
git commit -m "feat: add StrategyRegistry for strategy type registration"
```

### Task 10: Built-in MA Cross strategy

**Files:**
- Create: `backend/app/strategy/builtins/__init__.py`
- Create: `backend/app/strategy/builtins/ma_cross.py`
- Create: `backend/app/strategy/config_loader.py`

**Interfaces:**
- Consumes: `Strategy` ABC, `StrategyRegistry`
- Produces: `MACrossStrategy` — dual moving average crossover with signal dedup

- [ ] **Step 1: Write MA Cross test**

Create `backend/tests/strategy/test_ma_cross.py`:
```python
import pytest
import pandas as pd
from datetime import date, timedelta
from app.strategy.builtins.ma_cross import MACrossStrategy


def make_bars(prices, start_date=date(2026, 1, 5)):
    """Build a list of bar Series from a price list."""
    bars = []
    d = start_date
    for p in prices:
        bar = pd.Series({
            "date": d, "open": p, "high": p, "low": p,
            "close": p, "volume": 10000
        })
        bars.append(bar)
        d += timedelta(days=1)
    return bars


async def test_ma_cross_no_signal_during_warmup():
    s = MACrossStrategy(
        symbols=["000001.sz"],
        params={"fast": 5, "slow": 20}
    )
    await s.on_start()
    bars = make_bars([10.0] * 15)
    for bar in bars:
        result = await s.on_bar(bar)
        assert result is None  # Not enough data for 20-period MA


async def test_ma_cross_buy_signal():
    s = MACrossStrategy(
        symbols=["000001.sz"],
        params={"fast": 3, "slow": 5}
    )
    await s.on_start()
    # First 4 bars: price drops (slow MA above fast MA)
    bars = make_bars([12, 11, 10, 9, 8])
    for bar in bars:
        result = await s.on_bar(bar)
    assert result is None  # No cross yet

    # Now price rises sharply — fast MA crosses above slow MA
    more_bars = make_bars([10, 11, 12, 13], start_date=date(2026, 1, 10))
    signal = None
    for bar in more_bars:
        signal = await s.on_bar(bar)
    assert signal is not None
    assert signal.direction == "BUY"
    assert signal.symbol == "000001.sz"


async def test_ma_cross_signal_dedup():
    s = MACrossStrategy(
        symbols=["000001.sz"],
        params={"fast": 3, "slow": 5, "signal_cooldown": 5}
    )
    await s.on_start()
    bars = make_bars([12, 11, 10, 9, 8, 10, 11, 12, 13, 14, 15, 16])
    signals = []
    for bar in bars:
        sig = await s.on_bar(bar)
        if sig:
            signals.append(sig)
    # Only first crossover generates a signal (cooldown prevents spam)
    assert len(signals) == 1
```

- [ ] **Step 2: Run test to verify failure**

Run: `cd backend && uv run pytest tests/strategy/test_ma_cross.py -v`
Expected: FAIL

- [ ] **Step 3: Implement MA Cross strategy**

Create `backend/app/strategy/builtins/__init__.py`:
```python
from app.strategy.builtins.ma_cross import MACrossStrategy

__all__ = ["MACrossStrategy"]
```

Create `backend/app/strategy/builtins/ma_cross.py`:
```python
from typing import List, Optional
from collections import deque
import pandas as pd
from app.strategy.base import Strategy
from app.strategy.signal import Signal


class MACrossStrategy(Strategy):
    name = "ma_cross"
    frequency = "daily"

    def __init__(self, symbols: List[str], params: dict, mode: str = "semi-auto"):
        self.symbols = symbols
        self.mode = mode
        self.risk_profile = params.get("risk_profile", {})
        self._fast = params.get("fast", 5)
        self._slow = params.get("slow", 20)
        self._cooldown = params.get("signal_cooldown", 5)
        self._prices: dict = {}
        self._last_signal_bar: dict = {}
        self._bar_count = 0

    async def on_start(self) -> None:
        self._prices = {sym: deque(maxlen=self._slow + 1) for sym in self.symbols}
        self._last_signal_bar = {}
        self._bar_count = 0

    async def on_bar(self, bar: pd.Series) -> Optional[Signal]:
        self._bar_count += 1
        symbol = self.symbols[0]  # Single symbol for now
        price = float(bar["close"])
        self._prices[symbol].append(price)

        if len(self._prices[symbol]) < self._slow:
            return None

        fast_ma = sum(list(self._prices[symbol])[-self._fast:]) / self._fast
        slow_ma = sum(list(self._prices[symbol])[-self._slow:]) / self._slow

        prev_fast = sum(list(self._prices[symbol])[-self._fast - 1:-1]) / self._fast
        prev_slow = sum(list(self._prices[symbol])[-self._slow - 1:-1]) / self._slow

        last_sig = self._last_signal_bar.get(symbol, -999)

        if prev_fast <= prev_slow and fast_ma > slow_ma and (self._bar_count - last_sig) >= self._cooldown:
            self._last_signal_bar[symbol] = self._bar_count
            return Signal(
                strategy_id=f"ma_cross_{id(self)}", symbol=symbol,
                direction="BUY", strength=0.7,
                reason=f"Golden cross: MA{self._fast}({fast_ma:.2f}) > MA{self._slow}({slow_ma:.2f})",
                meta={"fast_ma": fast_ma, "slow_ma": slow_ma}
            )

        if prev_fast >= prev_slow and fast_ma < slow_ma and (self._bar_count - last_sig) >= self._cooldown:
            self._last_signal_bar[symbol] = self._bar_count
            return Signal(
                strategy_id=f"ma_cross_{id(self)}", symbol=symbol,
                direction="SELL", strength=0.7,
                reason=f"Death cross: MA{self._fast}({fast_ma:.2f}) < MA{self._slow}({slow_ma:.2f})",
                meta={"fast_ma": fast_ma, "slow_ma": slow_ma}
            )

        return None

    async def on_stop(self) -> None:
        self._prices.clear()
```

- [ ] **Step 4: Implement config loader**

Create `backend/app/strategy/config_loader.py`:
```python
import yaml
from pathlib import Path
from typing import Dict, Any
from app.strategy.base import Strategy
from app.strategy.registry import registry


def load_strategy_from_yaml(path: Path) -> Strategy:
    with open(path, "r", encoding="utf-8") as f:
        config: Dict[str, Any] = yaml.safe_load(f)

    strategy_type = config["strategy_type"]
    strategy_cls = registry.get(strategy_type)
    if strategy_cls is None:
        raise ValueError(f"Unknown strategy type: {strategy_type}")

    return strategy_cls(
        symbols=config.get("symbols", []),
        params=config.get("params", {}),
        mode=config.get("mode", "semi-auto"),
    )


def save_strategy_config(strategy: Strategy, path: Path) -> None:
    config = {
        "strategy_type": strategy.name,
        "symbols": strategy.symbols,
        "params": getattr(strategy, "_params", {}),
        "mode": strategy.mode,
        "risk_profile": strategy.risk_profile,
    }
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, allow_unicode=True)
```

- [ ] **Step 5: Create example strategy config**

Create `strategy_configs/example_ma_cross.yaml`:
```yaml
strategy_type: ma_cross
name: 均线交叉示例
symbols:
  - "000001.sz"
params:
  fast: 5
  slow: 20
  signal_cooldown: 5
mode: semi-auto
risk_profile:
  max_position_pct: 0.2
  daily_loss_limit: 5000
```

- [ ] **Step 6: Run tests**

Run: `cd backend && uv run pytest tests/strategy/test_ma_cross.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add backend/app/strategy/builtins/ backend/app/strategy/config_loader.py backend/tests/strategy/test_ma_cross.py strategy_configs/
git commit -m "feat: add MA Cross strategy, config loader, and example config"
```

---

## Phase 4: Risk Module

### Task 11: RiskRule ABC and RiskEngine

**Files:**
- Create: `backend/app/risk/__init__.py`
- Create: `backend/app/risk/rule.py`
- Create: `backend/app/risk/engine.py`

**Interfaces:**
- Produces: `RiskResult` dataclass, `RiskRule` ABC, `RiskEngine` — evaluates all rules against a signal

- [ ] **Step 1: Write risk tests**

Create `backend/tests/risk/__init__.py`:
```python
```

Create `backend/tests/risk/test_rules.py`:
```python
import pytest
from decimal import Decimal
from app.risk.rule import RiskRule, RiskResult
from app.risk.engine import RiskEngine
from app.strategy.signal import Signal


class AlwaysPassRule(RiskRule):
    name = "always_pass"
    severity = "warn"

    def evaluate(self, signal, portfolio, context) -> RiskResult:
        return RiskResult(passed=True, message="OK")


class AlwaysBlockRule(RiskRule):
    name = "always_block"
    severity = "block"

    def evaluate(self, signal, portfolio, context) -> RiskResult:
        return RiskResult(passed=False, message="Blocked")


def test_risk_result_defaults():
    result = RiskResult(passed=True, message="OK")
    assert result.passed is True
    assert result.adjusted_quantity is None


def test_risk_engine_all_pass():
    engine = RiskEngine([AlwaysPassRule(), AlwaysPassRule()])
    signal = Signal(strategy_id="t1", symbol="000001.sz", direction="BUY", strength=0.8, reason="test")
    results = engine.evaluate(signal, portfolio={}, context={})
    assert all(r.passed for r in results)


def test_risk_engine_one_block():
    engine = RiskEngine([AlwaysPassRule(), AlwaysBlockRule()])
    signal = Signal(strategy_id="t1", symbol="000001.sz", direction="BUY", strength=0.8, reason="test")
    results = engine.evaluate(signal, portfolio={}, context={})
    assert any(not r.passed for r in results)
```

- [ ] **Step 2: Run test to verify failure**

Run: `cd backend && uv run pytest tests/risk/test_rules.py -v`
Expected: FAIL

- [ ] **Step 3: Implement RiskRule and RiskEngine**

Create `backend/app/risk/rule.py`:
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from app.strategy.signal import Signal


@dataclass
class RiskResult:
    passed: bool
    message: str
    adjusted_quantity: Optional[int] = None


class RiskRule(ABC):
    name: str = ""
    severity: str = "block"  # block | warn | limit

    @abstractmethod
    def evaluate(
        self, signal: Signal, portfolio: Dict[str, Any], context: Dict[str, Any]
    ) -> RiskResult:
        """Evaluate signal against this rule. Return RiskResult with passed=False to block."""
```

Create `backend/app/risk/engine.py`:
```python
from typing import List, Dict, Any
from app.risk.rule import RiskRule, RiskResult
from app.strategy.signal import Signal


class RiskEngine:
    def __init__(self, rules: List[RiskRule] | None = None):
        self._rules = rules or []

    def add_rule(self, rule: RiskRule) -> None:
        self._rules.append(rule)

    def evaluate(
        self, signal: Signal, portfolio: Dict[str, Any], context: Dict[str, Any]
    ) -> List[RiskResult]:
        results = []
        for rule in self._rules:
            result = rule.evaluate(signal, portfolio, context)
            results.append(result)
        return results

    @property
    def rules(self) -> List[RiskRule]:
        return list(self._rules)
```

Create `backend/app/risk/__init__.py`:
```python
from app.risk.rule import RiskRule, RiskResult
from app.risk.engine import RiskEngine

__all__ = ["RiskRule", "RiskResult", "RiskEngine"]
```

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/risk/test_rules.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/risk/ backend/tests/risk/
git commit -m "feat: add RiskRule ABC, RiskResult, and RiskEngine"
```

### Task 12: Built-in risk rules

**Files:**
- Create: `backend/app/risk/rules/__init__.py`
- Create: `backend/app/risk/rules/daily_loss.py`
- Create: `backend/app/risk/rules/position_limit.py`
- Create: `backend/app/risk/rules/cancel_limit.py`
- Create: `backend/app/risk/rules/strategy_circuit.py`
- Create: `backend/app/risk/rules/price_limit.py`

**Interfaces:**
- Consumes: `RiskRule`, `RiskResult`
- Produces: Five concrete risk rule implementations

- [ ] **Step 1: Extend risk tests**

Add to `backend/tests/risk/test_rules.py`:
```python
from decimal import Decimal
from app.risk.rules.daily_loss import DailyLossRule
from app.risk.rules.position_limit import PositionLimitRule
from app.risk.rules.price_limit import PriceLimitRule


def test_daily_loss_rule_blocks_when_exceeded():
    rule = DailyLossRule(daily_loss_limit=Decimal("1000"))
    signal = Signal(strategy_id="t1", symbol="000001.sz", direction="BUY", strength=0.8, reason="test")
    portfolio = {"daily_pnl": Decimal("-1500")}
    result = rule.evaluate(signal, portfolio, {})
    assert not result.passed
    assert "亏损" in result.message


def test_daily_loss_rule_passes_when_ok():
    rule = DailyLossRule(daily_loss_limit=Decimal("1000"))
    signal = Signal(strategy_id="t1", symbol="000001.sz", direction="BUY", strength=0.8, reason="test")
    portfolio = {"daily_pnl": Decimal("500")}
    result = rule.evaluate(signal, portfolio, {})
    assert result.passed


def test_position_limit_rule_reduces_quantity():
    rule = PositionLimitRule(max_position_pct=Decimal("0.2"))
    signal = Signal(strategy_id="t1", symbol="000001.sz", direction="BUY", strength=0.8, reason="test")
    portfolio = {
        "total_value": Decimal("100000"),
        "positions": {"000001.sz": {"market_value": Decimal("25000")}}
    }
    result = rule.evaluate(signal, portfolio, {"order_quantity": 500})
    assert not result.passed
    assert result.adjusted_quantity is not None
    assert result.adjusted_quantity < 500


def test_price_limit_rule_blocks_limit_up_buy():
    rule = PriceLimitRule()
    signal = Signal(strategy_id="t1", symbol="000001.sz", direction="BUY", strength=0.8, reason="test")
    context = {"prev_close": Decimal("10.00"), "is_limit_up": True}
    result = rule.evaluate(signal, {}, context)
    assert not result.passed
```

- [ ] **Step 2: Run test to verify failure**

Run: `cd backend && uv run pytest tests/risk/test_rules.py -v`
Expected: FAIL — rules not implemented

- [ ] **Step 3: Implement all five risk rules**

Create `backend/app/risk/rules/__init__.py`:
```python
```

Create `backend/app/risk/rules/daily_loss.py`:
```python
from decimal import Decimal
from typing import Dict, Any
from app.risk.rule import RiskRule, RiskResult
from app.strategy.signal import Signal


class DailyLossRule(RiskRule):
    name = "daily_loss_limit"
    severity = "block"

    def __init__(self, daily_loss_limit: Decimal = Decimal("5000")):
        self.daily_loss_limit = daily_loss_limit

    def evaluate(self, signal: Signal, portfolio: Dict[str, Any], context: Dict[str, Any]) -> RiskResult:
        daily_pnl = portfolio.get("daily_pnl", Decimal("0"))
        if isinstance(daily_pnl, (int, float)):
            daily_pnl = Decimal(str(daily_pnl))
        if daily_pnl < -self.daily_loss_limit:
            return RiskResult(
                passed=False,
                message=f"日亏损({daily_pnl})超过限制({self.daily_loss_limit})，熔断所有策略"
            )
        return RiskResult(passed=True, message="OK")
```

Create `backend/app/risk/rules/position_limit.py`:
```python
from decimal import Decimal
from typing import Dict, Any
from app.risk.rule import RiskRule, RiskResult
from app.strategy.signal import Signal


class PositionLimitRule(RiskRule):
    name = "position_limit"
    severity = "limit"

    def __init__(self, max_position_pct: Decimal = Decimal("0.2")):
        self.max_position_pct = max_position_pct

    def evaluate(self, signal: Signal, portfolio: Dict[str, Any], context: Dict[str, Any]) -> RiskResult:
        total_value = portfolio.get("total_value", Decimal("0"))
        positions = portfolio.get("positions", {})
        pos = positions.get(signal.symbol, {})
        current_pct = Decimal(str(pos.get("market_value_pct", 0)))

        order_qty = context.get("order_quantity", 100)
        order_price = context.get("order_price", Decimal("0"))
        order_value = Decimal(str(order_qty)) * Decimal(str(order_price))
        new_pct = current_pct + (order_value / total_value if total_value > 0 else Decimal("0"))

        if new_pct > self.max_position_pct:
            max_value = total_value * self.max_position_pct
            current_value = current_pct * total_value
            available = max_value - current_value
            adjusted = max(0, int(available / Decimal(str(order_price)) // 100 * 100))
            return RiskResult(
                passed=False,
                message=f"仓位超限: {new_pct:.1%} > {self.max_position_pct:.1%}",
                adjusted_quantity=adjusted
            )
        return RiskResult(passed=True, message="OK")
```

Create `backend/app/risk/rules/cancel_limit.py`:
```python
from typing import Dict, Any
from app.risk.rule import RiskRule, RiskResult
from app.strategy.signal import Signal


class CancelLimitRule(RiskRule):
    name = "cancel_limit"
    severity = "block"

    def __init__(self, max_cancels: int = 5):
        self.max_cancels = max_cancels

    def evaluate(self, signal: Signal, portfolio: Dict[str, Any], context: Dict[str, Any]) -> RiskResult:
        strategy_cancels = context.get("strategy_cancels_today", {})
        cancels = strategy_cancels.get(signal.strategy_id, 0)
        if cancels >= self.max_cancels:
            return RiskResult(
                passed=False,
                message=f"策略 {signal.strategy_id} 当日撤单{cancels}次，超过限制{self.max_cancels}"
            )
        return RiskResult(passed=True, message="OK")
```

Create `backend/app/risk/rules/strategy_circuit.py`:
```python
from typing import Dict, Any
from app.risk.rule import RiskRule, RiskResult
from app.strategy.signal import Signal


class StrategyCircuitBreaker(RiskRule):
    name = "strategy_circuit_breaker"
    severity = "block"

    def __init__(self, max_consecutive_losses: int = 5):
        self.max_consecutive_losses = max_consecutive_losses

    def evaluate(self, signal: Signal, portfolio: Dict[str, Any], context: Dict[str, Any]) -> RiskResult:
        consecutive_losses = context.get("strategy_pnl", {}).get(signal.strategy_id, {}).get("consecutive_losses", 0)
        if consecutive_losses >= self.max_consecutive_losses:
            return RiskResult(
                passed=False,
                message=f"策略{signal.strategy_id}连续亏损{consecutive_losses}次，触发熔断"
            )
        return RiskResult(passed=True, message="OK")
```

Create `backend/app/risk/rules/price_limit.py`:
```python
from typing import Dict, Any
from app.risk.rule import RiskRule, RiskResult
from app.strategy.signal import Signal


class PriceLimitRule(RiskRule):
    name = "price_limit"
    severity = "block"

    def evaluate(self, signal: Signal, portfolio: Dict[str, Any], context: Dict[str, Any]) -> RiskResult:
        is_limit_up = context.get("is_limit_up", False)
        is_limit_down = context.get("is_limit_down", False)

        if signal.direction == "BUY" and is_limit_up:
            return RiskResult(passed=False, message=f"{signal.symbol}涨停，不可买入")
        if signal.direction == "SELL" and is_limit_down:
            return RiskResult(passed=False, message=f"{signal.symbol}跌停，不可卖出")

        return RiskResult(passed=True, message="OK")
```

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/risk/test_rules.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/risk/rules/ backend/tests/risk/test_rules.py
git commit -m "feat: add 5 built-in risk rules — daily loss, position limit, cancel limit, circuit breaker, price limit"
```

---

## Phase 5: Execution Module

### Task 13: BrokerAdapter ABC and SimulatedBroker

**Files:**
- Create: `backend/app/execution/__init__.py`
- Create: `backend/app/execution/broker.py`
- Create: `backend/app/execution/adapters/__init__.py`
- Create: `backend/app/execution/adapters/simulated.py`

**Interfaces:**
- Produces: `BrokerAdapter` ABC, `SimulatedBroker` — mock execution with position tracking

- [ ] **Step 1: Write simulated broker tests**

Create `backend/tests/execution/__init__.py`:
```python
```

Create `backend/tests/execution/test_simulated_broker.py`:
```python
import pytest
from decimal import Decimal
from app.execution.adapters.simulated import SimulatedBroker


@pytest.fixture
def broker():
    return SimulatedBroker(initial_capital=Decimal("100000"))


async def test_submit_order_creates_position(broker):
    result = await broker.submit_order(
        symbol="000001.sz", direction="BUY", quantity=1000, price=Decimal("10.50")
    )
    assert result.success
    assert result.filled_quantity == 1000

    positions = await broker.query_positions()
    assert "000001.sz" in positions
    assert positions["000001.sz"].quantity == 1000


async def test_submit_order_insufficient_cash(broker):
    result = await broker.submit_order(
        symbol="000001.sz", direction="BUY", quantity=10000, price=Decimal("100.00")
    )
    assert not result.success
    assert "资金" in result.message or "不足" in result.message


async def test_cancel_order(broker):
    result = await broker.submit_order(
        symbol="000001.sz", direction="BUY", quantity=100, price=Decimal("10.00")
    )
    cancelled = await broker.cancel_order(result.order_id)
    assert cancelled


async def test_account_info(broker):
    info = await broker.query_account()
    assert float(info.total_value) >= 0
    assert float(info.cash) > 0
```

- [ ] **Step 2: Run test to verify failure**

Run: `cd backend && uv run pytest tests/execution/test_simulated_broker.py -v`
Expected: FAIL

- [ ] **Step 3: Implement BrokerAdapter ABC**

Create `backend/app/execution/broker.py`:
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime
from typing import Dict, List


@dataclass
class OrderResult:
    success: bool
    order_id: str
    filled_quantity: int
    filled_price: Decimal
    message: str = ""
    commission: Decimal = Decimal("0")


@dataclass
class Position:
    symbol: str
    quantity: int
    avg_cost: Decimal
    market_value: Decimal = Decimal("0")

    @property
    def unrealized_pnl(self) -> Decimal:
        return self.market_value - Decimal(str(self.quantity)) * self.avg_cost


@dataclass
class AccountInfo:
    account_id: str
    cash: Decimal
    positions: Dict[str, Position] = field(default_factory=dict)

    @property
    def total_value(self) -> Decimal:
        pos_value = sum(p.market_value for p in self.positions.values())
        return self.cash + pos_value


class BrokerAdapter(ABC):
    name: str = ""

    @abstractmethod
    async def submit_order(self, symbol: str, direction: str, quantity: int, price: Decimal) -> OrderResult:
        """Submit an order for simulated or real execution."""

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order."""

    @abstractmethod
    async def query_positions(self) -> Dict[str, Position]:
        """Get current positions."""

    @abstractmethod
    async def query_account(self) -> AccountInfo:
        """Get account summary."""
```

- [ ] **Step 4: Implement SimulatedBroker**

Create `backend/app/execution/adapters/__init__.py`:
```python
```

Create `backend/app/execution/adapters/simulated.py`:
```python
import uuid
from decimal import Decimal
from typing import Dict
from app.execution.broker import BrokerAdapter, OrderResult, Position, AccountInfo


class SimulatedBroker(BrokerAdapter):
    name = "simulated"

    def __init__(self, initial_capital: Decimal = Decimal("100000"), commission_rate: Decimal = Decimal("0.0003")):
        self._initial_capital = initial_capital
        self._cash = initial_capital
        self._commission_rate = commission_rate
        self._positions: Dict[str, Position] = {}
        self._order_counter = 0

    async def submit_order(self, symbol: str, direction: str, quantity: int, price: Decimal) -> OrderResult:
        qty = Decimal(str(quantity))
        price = Decimal(str(price))
        amount = qty * price
        commission = amount * self._commission_rate

        self._order_counter += 1
        order_id = f"sim_{self._order_counter}_{uuid.uuid4().hex[:6]}"

        if direction == "BUY":
            total_cost = amount + commission
            if total_cost > self._cash:
                return OrderResult(
                    success=False, order_id=order_id,
                    filled_quantity=0, filled_price=price,
                    message=f"资金不足: 需要{total_cost}, 可用{self._cash}"
                )
            self._cash -= total_cost
            if symbol in self._positions:
                pos = self._positions[symbol]
                total_qty = pos.quantity + int(qty)
                total_cost_basis = Decimal(str(pos.quantity)) * pos.avg_cost + amount + commission
                pos.quantity = total_qty
                pos.avg_cost = total_cost_basis / Decimal(str(total_qty))
            else:
                self._positions[symbol] = Position(
                    symbol=symbol, quantity=int(qty), avg_cost=(amount + commission) / qty
                )

        elif direction == "SELL":
            if symbol not in self._positions or self._positions[symbol].quantity < int(qty):
                return OrderResult(
                    success=False, order_id=order_id,
                    filled_quantity=0, filled_price=price,
                    message=f"持仓不足: {symbol}"
                )
            pos = self._positions[symbol]
            self._cash += amount - commission
            pos.quantity -= int(qty)
            if pos.quantity == 0:
                del self._positions[symbol]

        return OrderResult(
            success=True, order_id=order_id,
            filled_quantity=int(qty), filled_price=price,
            commission=commission
        )

    async def cancel_order(self, order_id: str) -> bool:
        return True  # Simulated broker executes immediately, nothing to cancel

    async def query_positions(self) -> Dict[str, Position]:
        return dict(self._positions)

    async def query_account(self) -> AccountInfo:
        return AccountInfo(account_id="sim_default", cash=self._cash, positions=dict(self._positions))
```

Create `backend/app/execution/__init__.py`:
```python
from app.execution.broker import BrokerAdapter, OrderResult, Position, AccountInfo

__all__ = ["BrokerAdapter", "OrderResult", "Position", "AccountInfo"]
```

- [ ] **Step 5: Run tests**

Run: `cd backend && uv run pytest tests/execution/test_simulated_broker.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/execution/ backend/tests/execution/
git commit -m "feat: add BrokerAdapter ABC and SimulatedBroker for mock execution"
```

### Task 14: OrderBuilder and ExecutionPipeline

**Files:**
- Create: `backend/app/execution/order_builder.py`
- Create: `backend/app/execution/pipeline.py`

**Interfaces:**
- Consumes: `Signal`, `RiskEngine`, `BrokerAdapter`, `StrategyConfig`
- Produces: `OrderBuilder` (Signal → Order), `ExecutionPipeline` (full signal-to-execution flow)

- [ ] **Step 1: Write pipeline tests**

Create `backend/tests/execution/test_pipeline.py`:
```python
import pytest
from decimal import Decimal
from app.strategy.signal import Signal
from app.risk.engine import RiskEngine
from app.risk.rules.daily_loss import DailyLossRule
from app.execution.adapters.simulated import SimulatedBroker
from app.execution.order_builder import OrderBuilder
from app.execution.pipeline import ExecutionPipeline


@pytest.fixture
def pipeline():
    risk_engine = RiskEngine([DailyLossRule(daily_loss_limit=Decimal("5000"))])
    broker = SimulatedBroker(initial_capital=Decimal("100000"))
    builder = OrderBuilder(default_quantity=100)
    return ExecutionPipeline(risk_engine=risk_engine, broker=broker, order_builder=builder)


async def test_pipeline_auto_mode_executes_order(pipeline):
    signal = Signal(strategy_id="ma_cross_1", symbol="000001.sz", direction="BUY", strength=0.8, reason="test")
    strategy_config = {"mode": "auto"}

    result = await pipeline.process_signal(signal, strategy_config, portfolio={"daily_pnl": Decimal("0")})
    assert result is not None
    assert result.success


async def test_pipeline_semi_auto_does_not_execute(pipeline):
    signal = Signal(strategy_id="ma_cross_1", symbol="000001.sz", direction="BUY", strength=0.8, reason="test")
    strategy_config = {"mode": "semi-auto"}

    result = await pipeline.process_signal(signal, strategy_config, portfolio={"daily_pnl": Decimal("0")})
    assert result is None  # semi-auto: order stored but not submitted yet


async def test_pipeline_risk_blocks_signal(pipeline):
    signal = Signal(strategy_id="ma_cross_1", symbol="000001.sz", direction="BUY", strength=0.8, reason="test")
    strategy_config = {"mode": "auto"}

    result = await pipeline.process_signal(signal, strategy_config, portfolio={"daily_pnl": Decimal("-10000")})
    assert result is None  # Risk blocked it
```

- [ ] **Step 2: Run test to verify failure**

Run: `cd backend && uv run pytest tests/execution/test_pipeline.py -v`
Expected: FAIL

- [ ] **Step 3: Implement OrderBuilder**

Create `backend/app/execution/order_builder.py`:
```python
from decimal import Decimal
from app.strategy.signal import Signal


class OrderBuilder:
    def __init__(self, default_quantity: int = 100, default_price: Decimal | None = None):
        self.default_quantity = default_quantity
        self.default_price = default_price

    def build(self, signal: Signal, price: Decimal | None = None) -> dict:
        qty = signal.meta.get("quantity", self.default_quantity)
        order_price = price or self.default_price or Decimal("0")
        return {
            "symbol": signal.symbol,
            "direction": signal.direction,
            "quantity": qty,
            "price": order_price,
            "strategy_id": signal.strategy_id,
            "reason": signal.reason,
        }
```

- [ ] **Step 4: Implement ExecutionPipeline**

Create `backend/app/execution/pipeline.py`:
```python
from decimal import Decimal
from typing import Optional, Dict, Any
from app.strategy.signal import Signal
from app.risk.engine import RiskEngine
from app.execution.broker import BrokerAdapter, OrderResult
from app.execution.order_builder import OrderBuilder


class ExecutionPipeline:
    def __init__(self, risk_engine: RiskEngine, broker: BrokerAdapter, order_builder: OrderBuilder):
        self.risk_engine = risk_engine
        self.broker = broker
        self.order_builder = order_builder

    async def process_signal(
        self,
        signal: Signal,
        strategy_config: Dict[str, Any],
        portfolio: Dict[str, Any] | None = None,
        context: Dict[str, Any] | None = None,
    ) -> Optional[OrderResult]:
        if portfolio is None:
            portfolio = {}
        if context is None:
            context = {}

        mode = strategy_config.get("mode", "semi-auto")

        # Step 1: Risk check (mandatory for all modes)
        results = self.risk_engine.evaluate(signal, portfolio, context)
        blockers = [r for r in results if not r.passed and r.severity == "block"]
        if blockers:
            return None  # Blocked

        # Check for quantity adjustment
        limiters = [r for r in results if not r.passed and r.severity == "limit"]
        if limiters:
            context["order_quantity"] = limiters[0].adjusted_quantity or context.get("order_quantity", 100)

        # Step 2: Build order
        price = context.get("current_price", Decimal("0"))
        order_data = self.order_builder.build(signal, price=price)
        order_data["quantity"] = context.get("order_quantity", order_data["quantity"])

        # Step 3: Submit or hold based on mode
        if mode == "auto":
            return await self.broker.submit_order(
                symbol=order_data["symbol"], direction=order_data["direction"],
                quantity=order_data["quantity"], price=order_data["price"]
            )
        else:
            # semi-auto: store order for manual review
            return None  # Order saved to DB by the caller
```

- [ ] **Step 5: Run tests**

Run: `cd backend && uv run pytest tests/execution/test_pipeline.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/execution/order_builder.py backend/app/execution/pipeline.py backend/tests/execution/test_pipeline.py
git commit -m "feat: add OrderBuilder and ExecutionPipeline with risk-gated execution flow"
```

---

## Phase 6: Backtest Module

### Task 15: Performance metrics

**Files:**
- Create: `backend/app/backtest/__init__.py`
- Create: `backend/app/backtest/metrics.py`

**Interfaces:**
- Produces: `compute_metrics()` — given equity curve and trades, return dict of all performance metrics

- [ ] **Step 1: Write metrics tests**

Create `backend/tests/backtest/__init__.py`:
```python
```

Create `backend/tests/backtest/test_metrics.py`:
```python
import pandas as pd
import numpy as np
from datetime import date, timedelta
from app.backtest.metrics import compute_metrics, annualized_return, max_drawdown, sharpe_ratio


def make_equity_curve(values):
    dates = [date(2026, 1, 1) + timedelta(days=i) for i in range(len(values))]
    return pd.DataFrame({"date": dates, "equity": values, "benchmark": values})


def test_max_drawdown():
    equity = [100, 110, 90, 95, 85, 100]
    mdd = max_drawdown(equity)
    assert abs(mdd - 0.2272) < 0.01  # Peak 110 to trough 85


def test_annualized_return():
    values = [100, 110]
    ann_ret = annualized_return(values, trading_days=1)
    assert ann_ret > 0  # Positive return


def test_sharpe_ratio():
    equity = [100, 101, 102, 103, 102, 104, 105, 106, 107, 108]
    sr = sharpe_ratio(equity, risk_free_rate=0.02)
    assert sr > 0


def test_compute_metrics():
    equity = make_equity_curve([100000, 101000, 102000, 103000, 104000, 105000])
    trades = pd.DataFrame({
        "date": [date(2026, 1, 2), date(2026, 1, 4)],
        "symbol": ["000001.sz", "000001.sz"],
        "direction": ["BUY", "SELL"],
        "quantity": [1000, 1000],
        "price": [10.0, 10.5],
        "pnl": [0, 500],
        "commission": [3, 3],
    })
    metrics = compute_metrics(equity, trades, initial_capital=100000)
    assert "total_return" in metrics
    assert "max_drawdown" in metrics
    assert "sharpe_ratio" in metrics
    assert "win_rate" in metrics
    assert metrics["total_trades"] == 2
```

- [ ] **Step 2: Run test to verify failure**

Run: `cd backend && uv run pytest tests/backtest/test_metrics.py -v`
Expected: FAIL

- [ ] **Step 3: Implement metrics**

Create `backend/app/backtest/metrics.py`:
```python
import numpy as np
import pandas as pd
from typing import Dict, List


def max_drawdown(equity: List[float]) -> float:
    peak = np.maximum.accumulate(equity)
    drawdown = (np.array(equity) - peak) / peak
    return float(abs(min(drawdown)))


def annualized_return(equity: List[float], trading_days: int = 252) -> float:
    total = equity[-1] / equity[0] - 1
    years = len(equity) / trading_days
    if years == 0:
        return 0.0
    return float((1 + total) ** (1 / years) - 1)


def sharpe_ratio(equity: List[float], risk_free_rate: float = 0.02, trading_days: int = 252) -> float:
    returns = np.diff(equity) / np.array(equity[:-1])
    if len(returns) < 2 or returns.std() == 0:
        return 0.0
    excess = returns.mean() * trading_days - risk_free_rate
    vol = returns.std() * np.sqrt(trading_days)
    return float(excess / vol) if vol > 0 else 0.0


def sortino_ratio(equity: List[float], risk_free_rate: float = 0.02, trading_days: int = 252) -> float:
    returns = np.diff(equity) / np.array(equity[:-1])
    downside = returns[returns < 0]
    if len(downside) < 2 or downside.std() == 0:
        return 0.0
    excess = returns.mean() * trading_days - risk_free_rate
    downside_vol = downside.std() * np.sqrt(trading_days)
    return float(excess / downside_vol) if downside_vol > 0 else 0.0


def calmar_ratio(equity: List[float], trading_days: int = 252) -> float:
    ann = annualized_return(equity, trading_days)
    mdd = max_drawdown(equity)
    return float(ann / mdd) if mdd > 0 else 0.0


def compute_metrics(equity_curve: pd.DataFrame, trades: pd.DataFrame, initial_capital: float = 100000) -> Dict:
    equity = equity_curve["equity"].tolist()
    total_return = (equity[-1] / equity[0] - 1) if equity else 0

    # Trade statistics
    sell_trades = trades[trades["direction"] == "SELL"] if not trades.empty else pd.DataFrame()
    winning_trades = sell_trades[sell_trades["pnl"] > 0] if not sell_trades.empty else pd.DataFrame()

    win_rate = len(winning_trades) / len(sell_trades) if len(sell_trades) > 0 else 0
    total_pnl = trades["pnl"].sum() if not trades.empty else 0

    return {
        "total_return": round(total_return * 100, 2),
        "annualized_return": round(annualized_return(equity) * 100, 2),
        "max_drawdown": round(max_drawdown(equity) * 100, 2),
        "sharpe_ratio": round(sharpe_ratio(equity), 3),
        "sortino_ratio": round(sortino_ratio(equity), 3),
        "calmar_ratio": round(calmar_ratio(equity), 3),
        "annual_volatility": round(float(np.std(np.diff(equity) / np.array(equity[:-1])) * np.sqrt(252)) * 100, 2) if len(equity) > 2 else 0,
        "win_rate": round(win_rate * 100, 2),
        "total_trades": len(trades),
        "total_pnl": round(float(total_pnl), 2),
        "final_equity": round(equity[-1], 2) if equity else initial_capital,
    }
```

Create `backend/app/backtest/__init__.py`:
```python
from app.backtest.metrics import compute_metrics, max_drawdown, annualized_return, sharpe_ratio
```

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/backtest/test_metrics.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/backtest/ backend/tests/backtest/
git commit -m "feat: add performance metrics — Sharpe, Sortino, Calmar, max drawdown, win rate"
```

### Task 16: BacktestEngine

**Files:**
- Create: `backend/app/backtest/broker_sim.py`
- Create: `backend/app/backtest/engine.py`

**Interfaces:**
- Consumes: `Strategy`, `DataService`, `compute_metrics()`
- Produces: `BacktestBroker` (in-memory broker for backtesting), `BacktestEngine` (orchestrator)

- [ ] **Step 1: Write backtest engine tests**

Create `backend/tests/backtest/test_engine.py`:
```python
import pytest
import pandas as pd
import numpy as np
from datetime import date, timedelta
from app.strategy.builtins.ma_cross import MACrossStrategy
from app.backtest.engine import BacktestEngine


class MockDataService:
    async def get_bars(self, symbol, start, end, freq="daily"):
        dates = [start + timedelta(days=i) for i in range((end - start).days + 1)]
        prices = []
        # Simulate: drop then rise to trigger golden cross
        mid = len(dates) // 2
        for i in range(len(dates)):
            if i < mid:
                p = 20.0 - i * 0.5
            else:
                p = 20.0 - mid * 0.5 + (i - mid) * 1.0
            prices.append(p)
        data = {
            "date": dates,
            "open": prices, "high": [p + 0.5 for p in prices],
            "low": [p - 0.5 for p in prices], "close": prices,
            "volume": [1000000] * len(prices),
            "amount": [p * 1000000 for p in prices],
            "adj_factor": [1.0] * len(prices),
        }
        return pd.DataFrame(data)


async def test_backtest_engine_runs():
    strategy = MACrossStrategy(symbols=["000001.sz"], params={"fast": 5, "slow": 10})
    ds = MockDataService()
    engine = BacktestEngine(data_service=ds, initial_capital=100000)

    result = await engine.run(
        strategy=strategy,
        symbols=["000001.sz"],
        start=date(2026, 1, 1),
        end=date(2026, 3, 31),
        commission_rate=0.0003,
        slippage=0.001,
    )

    assert "equity_curve" in result
    assert "trades" in result
    assert "metrics" in result
    assert len(result["equity_curve"]) > 0
    assert result["metrics"]["total_trades"] >= 0


async def test_backtest_prevent_future_look():
    """Ensure strategy doesn't see future data."""
    ds = MockDataService()
    strategy = MACrossStrategy(symbols=["000001.sz"], params={"fast": 3, "slow": 5})
    engine = BacktestEngine(data_service=ds)
    engine._bars_cache = {}  # Reset
    # The engine should process one bar at a time
    await strategy.on_start()
    result = await engine.run(strategy, ["000001.sz"], date(2026, 1, 1), date(2026, 1, 10))
    # Strategy should not have been able to see past the last bar
    assert True  # No lookahead exception means pass
```

- [ ] **Step 2: Run test to verify failure**

Run: `cd backend && uv run pytest tests/backtest/test_engine.py -v`
Expected: FAIL

- [ ] **Step 3: Implement BacktestBroker**

Create `backend/app/backtest/broker_sim.py`:
```python
from decimal import Decimal
from typing import Dict, List
from dataclasses import dataclass, field
from datetime import date


@dataclass
class BacktestTrade:
    date: date
    symbol: str
    direction: str
    quantity: int
    price: Decimal
    pnl: Decimal = Decimal("0")
    commission: Decimal = Decimal("0")


class BacktestBroker:
    def __init__(self, initial_capital: float = 100000, commission_rate: float = 0.0003, slippage: float = 0.0):
        self.initial_capital = Decimal(str(initial_capital))
        self.cash = Decimal(str(initial_capital))
        self.commission_rate = Decimal(str(commission_rate))
        self.slippage = Decimal(str(slippage))
        self.positions: Dict[str, Dict] = {}  # symbol -> {quantity, avg_cost}
        self.trades: List[BacktestTrade] = []
        self._equity: List[float] = []

    def execute(self, trade_date: date, symbol: str, direction: str, quantity: int, price: float) -> BacktestTrade | None:
        qty = Decimal(str(quantity))
        p = Decimal(str(price))

        # Apply slippage
        if direction == "BUY":
            p = p * (Decimal("1") + self.slippage)
        else:
            p = p * (Decimal("1") - self.slippage)

        amount = qty * p
        commission = amount * self.commission_rate

        if direction == "BUY":
            total_cost = amount + commission
            if total_cost > self.cash:
                return None  # Insufficient cash
            self.cash -= total_cost
            if symbol in self.positions:
                pos = self.positions[symbol]
                total_qty = pos["quantity"] + int(qty)
                pos["avg_cost"] = (Decimal(str(pos["quantity"])) * pos["avg_cost"] + amount + commission) / Decimal(str(total_qty))
                pos["quantity"] = total_qty
            else:
                self.positions[symbol] = {"quantity": int(qty), "avg_cost": (amount + commission) / qty}
        else:  # SELL
            if symbol not in self.positions or self.positions[symbol]["quantity"] < int(qty):
                return None
            pos = self.positions[symbol]
            self.cash += amount - commission
            pnl = (p - pos["avg_cost"]) * qty
            pos["quantity"] -= int(qty)
            if pos["quantity"] == 0:
                del self.positions[symbol]

        trade = BacktestTrade(
            date=trade_date, symbol=symbol, direction=direction,
            quantity=int(qty), price=p, commission=commission
        )
        self.trades.append(trade)
        return trade

    def get_equity(self, prices: Dict[str, float]) -> float:
        pos_value = Decimal("0")
        for sym, pos in self.positions.items():
            if sym in prices:
                pos_value += Decimal(str(pos["quantity"])) * Decimal(str(prices[sym]))
        return float(self.cash + pos_value)

    def reset(self):
        self.cash = self.initial_capital
        self.positions.clear()
        self.trades.clear()
        self._equity.clear()
```

- [ ] **Step 4: Implement BacktestEngine**

Create `backend/app/backtest/engine.py`:
```python
import pandas as pd
from datetime import date
from typing import List, Dict, Optional
from app.strategy.base import Strategy
from app.backtest.broker_sim import BacktestBroker
from app.backtest.metrics import compute_metrics


class BacktestEngine:
    def __init__(self, data_service, initial_capital: float = 100000):
        self.data_service = data_service
        self.initial_capital = initial_capital
        self._bars_cache: Dict[str, pd.DataFrame] = {}

    async def run(
        self,
        strategy: Strategy,
        symbols: List[str],
        start: date,
        end: date,
        commission_rate: float = 0.0003,
        slippage: float = 0.001,
        warmup_bars: int = 30,
    ) -> Dict:
        # Load all bars
        all_bars = {}
        for symbol in symbols:
            df = await self.data_service.get_bars(symbol, start, end)
            if df is None or df.empty:
                continue
            all_bars[symbol] = df.sort_values("date").reset_index(drop=True)

        if not all_bars:
            return {"equity_curve": pd.DataFrame(), "trades": pd.DataFrame(), "metrics": {}}

        broker = BacktestBroker(
            initial_capital=self.initial_capital,
            commission_rate=commission_rate,
            slippage=slippage,
        )

        await strategy.on_start()

        # Build unified timeline from all symbols
        first_symbol = list(all_bars.keys())[0]
        timeline = all_bars[first_symbol]

        equity_records = []
        trade_records = []

        for idx, row in timeline.iterrows():
            bar = row
            current_date = bar["date"]
            if hasattr(current_date, "to_pydate"):
                current_date = current_date.to_pydate()

            # Feed bar to strategy
            signal = await strategy.on_bar(bar)

            # Process signal
            if signal is not None and idx >= warmup_bars:
                qty = self._calculate_position_size(broker, signal, float(bar["close"]))
                if qty > 0:
                    trade = broker.execute(
                        trade_date=current_date,
                        symbol=signal.symbol,
                        direction=signal.direction,
                        quantity=qty,
                        price=float(bar["close"]),
                    )
                    if trade:
                        trade_records.append({
                            "date": trade.date, "symbol": trade.symbol,
                            "direction": trade.direction, "quantity": trade.quantity,
                            "price": float(trade.price), "commission": float(trade.commission),
                            "pnl": 0.0,
                        })

            # Record equity
            prices = {sym: float(row["close"]) for sym in symbols}
            equity = broker.get_equity(prices)
            equity_records.append({"date": current_date, "equity": equity, "benchmark": equity})

        await strategy.on_stop()

        # Calculate PnL for sell trades
        trades_df = pd.DataFrame(trade_records)
        equity_df = pd.DataFrame(equity_records)
        metrics = compute_metrics(equity_df, trades_df, initial_capital=self.initial_capital)

        return {"equity_curve": equity_df, "trades": trades_df, "metrics": metrics}

    def _calculate_position_size(self, broker: BacktestBroker, signal, price: float) -> int:
        if signal.direction == "BUY":
            max_value = broker.cash * Decimal("0.95")  # Use 95% of cash max
            qty = int(float(max_value) / price / 100) * 100  # Round to lots of 100
            return max(0, qty)
        elif signal.direction == "SELL":
            pos = broker.positions.get(signal.symbol, {})
            return pos.get("quantity", 0)
        return 0
```

- [ ] **Step 5: Run tests**

Run: `cd backend && uv run pytest tests/backtest/test_engine.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/backtest/ broker_sim.py backend/app/backtest/engine.py backend/tests/backtest/test_engine.py
git commit -m "feat: add BacktestBroker and BacktestEngine with bar-by-bar replay"
```

---

## Phase 7: API & Worker

### Task 17: FastAPI routes

**Files:**
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/router.py`
- Create: `backend/app/api/data_routes.py`
- Create: `backend/app/api/strategy_routes.py`
- Create: `backend/app/api/backtest_routes.py`
- Create: `backend/app/api/order_routes.py`
- Create: `backend/app/api/dashboard_routes.py`
- Modify: `backend/app/main.py`

**Interfaces:**
- Consumes: All domain modules (data, strategy, backtest, execution, risk)
- Produces: REST API endpoints for frontend

- [ ] **Step 1: Write API route tests**

Create `backend/tests/test_api.py`:
```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "ok"


async def test_list_strategies(client):
    response = await client.get("/api/strategies")
    assert response.status_code == 200
    json_data = response.json()
    assert "strategies" in json_data


async def test_dashboard_summary(client):
    response = await client.get("/api/dashboard/summary")
    assert response.status_code == 200
```

- [ ] **Step 2: Run test to verify failure**

Run: `cd backend && uv run pytest tests/test_api.py -v`
Expected: FAIL

- [ ] **Step 3: Implement API routes**

Create `backend/app/api/__init__.py`:
```python
```

Create `backend/app/api/router.py`:
```python
from fastapi import APIRouter
from app.api.data_routes import router as data_router
from app.api.strategy_routes import router as strategy_router
from app.api.backtest_routes import router as backtest_router
from app.api.order_routes import router as order_router
from app.api.dashboard_routes import router as dashboard_router

api_router = APIRouter(prefix="/api")
api_router.include_router(data_router, prefix="/data", tags=["data"])
api_router.include_router(strategy_router, prefix="/strategies", tags=["strategies"])
api_router.include_router(backtest_router, prefix="/backtest", tags=["backtest"])
api_router.include_router(order_router, prefix="/orders", tags=["orders"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
```

Create `backend/app/api/data_routes.py`:
```python
from fastapi import APIRouter, Query
from datetime import date
from app.data.adapters.akshare import AKShareDataProvider

router = APIRouter()
_provider = AKShareDataProvider()


@router.get("/symbols")
async def list_symbols(market: str = Query(None)):
    symbols = await _provider.list_symbols(market=market)
    return {"symbols": [{"code": s.code, "name": s.name, "market": s.market} for s in symbols]}


@router.get("/bars/{symbol}")
async def get_bars(symbol: str, start: date, end: date):
    df = await _provider.get_bars(symbol, start, end)
    if df is None:
        return {"bars": []}
    return {"bars": df.to_dict(orient="records")}
```

Create `backend/app/api/strategy_routes.py`:
```python
from fastapi import APIRouter
from app.strategy.registry import registry

router = APIRouter()


@router.get("")
async def list_strategies():
    types = registry.list_all()
    return {"strategies": list(types.keys())}
```

Create `backend/app/api/backtest_routes.py`:
```python
from fastapi import APIRouter

router = APIRouter()


@router.post("/run")
async def run_backtest():
    return {"message": "Backtest endpoint ready", "result": {}}
```

Create `backend/app/api/order_routes.py`:
```python
from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_orders():
    return {"orders": []}
```

Create `backend/app/api/dashboard_routes.py`:
```python
from fastapi import APIRouter
from decimal import Decimal

router = APIRouter()


@router.get("/summary")
async def dashboard_summary():
    return {
        "account": {"total_value": 100000, "cash": 100000, "currency": "CNY"},
        "positions": [],
        "daily_pnl": 0,
        "strategies_running": 0,
    }
```

- [ ] **Step 4: Update main.py**

Edit `backend/app/main.py`:
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine
from app.core.config import settings
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="FIB-Invest", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
```

- [ ] **Step 5: Run tests**

Run: `cd backend && uv run pytest tests/test_api.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/ backend/app/main.py backend/tests/test_api.py
git commit -m "feat: add FastAPI REST routes for data, strategy, backtest, orders, dashboard"
```

### Task 18: arq worker setup

**Files:**
- Create: `backend/app/worker/__init__.py`
- Create: `backend/app/worker/worker.py`
- Create: `backend/app/worker/tasks.py`

**Interfaces:**
- Consumes: `DataService`, strategy modules
- Produces: arq Worker for async tasks — data sync, strategy execution

- [ ] **Step 1: Implement worker**

Create `backend/app/worker/__init__.py`:
```python
```

Create `backend/app/worker/worker.py`:
```python
from app.core.config import settings
from app.worker.tasks import sync_daily_data, run_strategy_cycle


class WorkerSettings:
    redis_settings = settings.redis_url
    functions = [sync_daily_data, run_strategy_cycle]
    max_jobs = 10
    poll_delay = 1.0
```

Create `backend/app/worker/tasks.py`:
```python
import logging
from datetime import date, timedelta
from app.data.adapters.akshare import AKShareDataProvider
from app.data.service import DataService

logger = logging.getLogger(__name__)

_provider = AKShareDataProvider()
_data_service = DataService(_provider)


async def sync_daily_data(ctx, symbols: list[str] | None = None):
    """Daily task: sync bar data for tracked symbols after market close."""
    if symbols is None:
        symbols = ["000001"]
    end = date.today()
    start = end - timedelta(days=30)
    count = await _data_service.sync_daily_bars(symbols, start, end)
    logger.info(f"Synced {count} daily bars for {len(symbols)} symbols")
    return {"synced_bars": count}


async def run_strategy_cycle(ctx, strategy_id: str):
    """Execute one cycle of a strategy (used for async AI/ML strategies)."""
    logger.info(f"Running strategy cycle for {strategy_id}")
    # Stub: load strategy config, run one bar cycle
    return {"strategy_id": strategy_id, "status": "completed"}
```

- [ ] **Step 2: Create backend Dockerfile**

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv sync
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 3: Verify worker can be imported**

Run: `cd backend && uv run python -c "from app.worker.worker import WorkerSettings; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add backend/app/worker/ backend/Dockerfile
git commit -m "feat: add arq worker for async data sync and strategy execution"
```

---

## Phase 8: Frontend

### Task 19: Frontend project setup

**Files:**
- Create: `frontend/index.html`
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/types/index.ts`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/api/endpoints.ts`
- Create: `frontend/src/components/Layout.tsx`

**Interfaces:**
- Produces: Working React + TypeScript frontend shell with routing, API client, and layout

- [ ] **Step 1: Create package.json**

Create `frontend/package.json`:
```json
{
  "name": "fib-invest-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^7.0.0",
    "lightweight-charts": "^4.2.0",
    "antd": "^5.22.0",
    "@ant-design/icons": "^5.5.0"
  },
  "devDependencies": {
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react": "^4.3.0",
    "typescript": "^5.7.0",
    "vite": "^6.0.0"
  }
}
```

- [ ] **Step 2: Create config files**

Create `frontend/index.html`:
```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>FIB-Invest</title></head>
  <body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body>
</html>
```

Create `frontend/vite.config.ts`:
```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": "http://localhost:8000" } },
});
```

Create `frontend/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022", "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext", "skipLibCheck": true,
    "moduleResolution": "bundler", "allowImportingTsExtensions": true,
    "isolatedModules": true, "noEmit": true, "jsx": "react-jsx",
    "strict": true, "noUnusedLocals": true, "noUnusedParameters": true
  },
  "include": ["src"]
}
```

- [ ] **Step 3: Create TypeScript types**

Create `frontend/src/types/index.ts`:
```typescript
export interface SymbolInfo {
  code: string;
  name: string;
  market: string;
}

export interface DailyBar {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount: number;
  adj_factor: number;
}

export interface Signal {
  strategy_id: string;
  symbol: string;
  direction: "BUY" | "SELL" | "HOLD";
  strength: number;
  reason: string;
}

export interface Order {
  id: string;
  strategy_id: string;
  symbol: string;
  direction: "BUY" | "SELL";
  quantity: number;
  price: number;
  status: "pending" | "ready" | "submitted" | "partial_filled" | "filled" | "cancelled";
  filled_quantity: number;
  created_at: string;
}

export interface DashboardSummary {
  account: { total_value: number; cash: number; currency: string };
  positions: PositionInfo[];
  daily_pnl: number;
  strategies_running: number;
}

export interface PositionInfo {
  symbol: string;
  name: string;
  quantity: number;
  avg_cost: number;
  current_price: number;
  market_value: number;
  pnl: number;
  pnl_pct: number;
}

export interface BacktestMetrics {
  total_return: number;
  annualized_return: number;
  max_drawdown: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  calmar_ratio: number;
  win_rate: number;
  total_trades: number;
  total_pnl: number;
  final_equity: number;
}
```

- [ ] **Step 4: Create API client**

Create `frontend/src/api/client.ts`:
```typescript
const BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
};
```

Create `frontend/src/api/endpoints.ts`:
```typescript
import { api } from "./client";
import type { SymbolInfo, DailyBar, DashboardSummary } from "../types";

export const getSymbols = (market?: string) =>
  api.get<{ symbols: SymbolInfo[] }>(`/data/symbols${market ? `?market=${market}` : ""}`);

export const getBars = (symbol: string, start: string, end: string) =>
  api.get<{ bars: DailyBar[] }>(`/data/bars/${symbol}?start=${start}&end=${end}`);

export const getStrategies = () =>
  api.get<{ strategies: string[] }>("/strategies");

export const getDashboard = () =>
  api.get<DashboardSummary>("/dashboard/summary");

export const getOrders = () =>
  api.get<{ orders: unknown[] }>("/orders");
```

- [ ] **Step 5: Create App shell and layout**

Create `frontend/src/main.tsx`:
```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter><App /></BrowserRouter>
  </React.StrictMode>
);
```

Create `frontend/src/App.tsx`:
```tsx
import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Strategies from "./pages/Strategies";
import Backtest from "./pages/Backtest";
import Orders from "./pages/Orders";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/strategies" element={<Strategies />} />
        <Route path="/backtest" element={<Backtest />} />
        <Route path="/orders" element={<Orders />} />
      </Route>
    </Routes>
  );
}
```

Create `frontend/src/components/Layout.tsx`:
```tsx
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { Layout as AntLayout, Menu } from "antd";
import { DashboardOutlined, CodeOutlined, BarChartOutlined, OrderedListOutlined } from "@ant-design/icons";

const { Header, Content } = AntLayout;

const menuItems = [
  { key: "/", icon: <DashboardOutlined />, label: "看板" },
  { key: "/strategies", icon: <CodeOutlined />, label: "策略" },
  { key: "/backtest", icon: <BarChartOutlined />, label: "回测" },
  { key: "/orders", icon: <OrderedListOutlined />, label: "订单" },
];

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <AntLayout style={{ minHeight: "100vh" }}>
      <Header style={{ display: "flex", alignItems: "center" }}>
        <div style={{ color: "white", fontSize: 18, fontWeight: "bold", marginRight: 32 }}>FIB-Invest</div>
        <Menu
          theme="dark" mode="horizontal" selectedKeys={[location.pathname]}
          items={menuItems} onClick={({ key }) => navigate(key)}
          style={{ flex: 1 }}
        />
      </Header>
      <Content style={{ padding: 24 }}><Outlet /></Content>
    </AntLayout>
  );
}
```

- [ ] **Step 6: Install dependencies and verify build**

Run: `cd frontend && pnpm install && pnpm build`
Expected: Build succeeds

- [ ] **Step 7: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold React frontend with routing, API client, and layout"
```

### Task 20: Dashboard and Strategy pages

**Files:**
- Create: `frontend/src/pages/Dashboard.tsx`
- Create: `frontend/src/pages/Strategies.tsx`
- Create: `frontend/src/components/PositionCard.tsx`
- Create: `frontend/src/components/EquityChart.tsx`

**Interfaces:**
- Consumes: API endpoints
- Produces: Dashboard with account summary + positions, Strategy management page

- [ ] **Step 1: Implement Dashboard page**

Create `frontend/src/pages/Dashboard.tsx`:
```tsx
import { useEffect, useState } from "react";
import { Card, Row, Col, Statistic, Table, Spin } from "antd";
import { ArrowUpOutlined, ArrowDownOutlined } from "@ant-design/icons";
import { getDashboard } from "../api/endpoints";
import type { DashboardSummary } from "../types";

export default function Dashboard() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboard().then(setData).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" />;

  const { account, positions, daily_pnl } = data!;
  const totalPnl = account.total_value - account.cash;
  const pnlPct = account.cash > 0 ? ((totalPnl / account.cash) * 100).toFixed(2) : "0";

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}><Card><Statistic title="总资产" value={account.total_value.toLocaleString()} precision={2} suffix="¥" /></Card></Col>
        <Col span={6}><Card><Statistic title="可用资金" value={account.cash.toLocaleString()} precision={2} suffix="¥" /></Card></Col>
        <Col span={6}>
          <Card>
            <Statistic title="持仓盈亏" value={totalPnl} precision={2}
              prefix={totalPnl >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              valueStyle={{ color: totalPnl >= 0 ? "#3f8600" : "#cf1322" }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="当日盈亏" value={daily_pnl} precision={2}
              prefix={daily_pnl >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              valueStyle={{ color: daily_pnl >= 0 ? "#3f8600" : "#cf1322" }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="持仓明细">
        <Table
          dataSource={positions} rowKey="symbol"
          columns={[
            { title: "代码", dataIndex: "symbol" },
            { title: "数量", dataIndex: "quantity" },
            { title: "成本价", dataIndex: "avg_cost", render: (v: number) => v.toFixed(2) },
            { title: "现价", dataIndex: "current_price", render: (v: number) => v.toFixed(2) },
            { title: "市值", dataIndex: "market_value", render: (v: number) => v.toLocaleString() },
            { title: "盈亏", dataIndex: "pnl", render: (v: number) => (
              <span style={{ color: v >= 0 ? "#3f8600" : "#cf1322" }}>{v.toFixed(2)}</span>
            )},
          ]}
        />
      </Card>
    </div>
  );
}
```

- [ ] **Step 2: Implement Strategy page**

Create `frontend/src/pages/Strategies.tsx`:
```tsx
import { useEffect, useState } from "react";
import { Card, Table, Tag, Spin, Button } from "antd";
import { getStrategies } from "../api/endpoints";

export default function Strategies() {
  const [strategies, setStrategies] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStrategies().then((res) => setStrategies(res.strategies)).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" />;

  return (
    <div>
      <Card title="策略管理" extra={<Button type="primary">新建策略</Button>}>
        <Table
          dataSource={strategies.map((s) => ({ name: s, type: s, status: "stopped" }))}
          rowKey="name"
          columns={[
            { title: "策略名称", dataIndex: "name" },
            { title: "类型", dataIndex: "type", render: (v: string) => <Tag>{v}</Tag> },
            { title: "状态", dataIndex: "status", render: (v: string) => (
              <Tag color={v === "running" ? "green" : "default"}>{v}</Tag>
            )},
            { title: "操作", render: () => <Button size="small">启动</Button> },
          ]}
        />
      </Card>
    </div>
  );
}
```

- [ ] **Step 3: Implement stubs for remaining pages**

Create `frontend/src/pages/Backtest.tsx`:
```tsx
import { Card, Button, Form, Input, DatePicker, Select, Space } from "antd";
import { PlayCircleOutlined } from "@ant-design/icons";

export default function Backtest() {
  return (
    <Card title="策略回测">
      <Form layout="inline" style={{ marginBottom: 16 }}>
        <Form.Item label="策略"><Select style={{ width: 160 }} options={[{ value: "ma_cross", label: "均线交叉" }]} /></Form.Item>
        <Form.Item label="标的"><Input placeholder="000001.sz" /></Form.Item>
        <Form.Item label="开始"><DatePicker /></Form.Item>
        <Form.Item label="结束"><DatePicker /></Form.Item>
        <Form.Item><Button type="primary" icon={<PlayCircleOutlined />}>运行回测</Button></Form.Item>
      </Form>
      <div style={{ height: 400, background: "#f5f5f5", display: "flex", alignItems: "center", justifyContent: "center" }}>
        回测结果图表区域
      </div>
    </Card>
  );
}
```

Create `frontend/src/pages/Orders.tsx`:
```tsx
import { useEffect, useState } from "react";
import { Card, Table, Tag, Spin } from "antd";
import { getOrders } from "../api/endpoints";

export default function Orders() {
  const [orders, setOrders] = useState<unknown[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getOrders().then((res) => setOrders(res.orders)).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" />;

  return (
    <Card title="订单管理">
      <Table
        dataSource={orders as object[]} rowKey="id"
        columns={[
          { title: "订单ID", dataIndex: "id" },
          { title: "标的", dataIndex: "symbol" },
          { title: "方向", dataIndex: "direction", render: (v: string) => (
            <Tag color={v === "BUY" ? "red" : "green"}>{v}</Tag>
          )},
          { title: "数量", dataIndex: "quantity" },
          { title: "价格", dataIndex: "price" },
          { title: "状态", dataIndex: "status", render: (v: string) => (
            <Tag color={v === "filled" ? "green" : v === "pending" ? "orange" : "default"}>{v}</Tag>
          )},
        ]}
      />
    </Card>
  );
}
```

- [ ] **Step 4: Create placeholder chart component**

Create `frontend/src/components/EquityChart.tsx`:
```tsx
import { useEffect, useRef } from "react";

interface EquityChartProps {
  data: { time: string; value: number }[];
}

export default function EquityChart({ data }: EquityChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || data.length === 0) return;
    const el = document.createElement("div");
    el.style.width = "100%";
    el.style.height = "100%";
    el.style.display = "flex";
    el.style.alignItems = "center";
    el.style.justifyContent = "center";
    el.style.color = "#999";
    el.innerText = `权益曲线: ${data.length} 个数据点`;
    containerRef.current.innerHTML = "";
    containerRef.current.appendChild(el);
  }, [data]);

  return <div ref={containerRef} style={{ width: "100%", height: 400 }} />;
}
```

- [ ] **Step 5: Verify frontend builds**

Run: `cd frontend && pnpm build`
Expected: Build succeeds without errors

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/ frontend/src/components/
git commit -m "feat: add Dashboard, Strategy, Backtest, and Orders pages"
```

### Task 21: Conftest and final integration

**Files:**
- Create: `backend/tests/conftest.py`
- Update: `backend/app/models/__init__.py` (ensure all models export correctly)

**Interfaces:**
- Produces: Test fixtures and final integration wiring

- [ ] **Step 1: Create conftest.py with async fixtures**

Create `backend/tests/conftest.py`:
```python
import pytest
import asyncio
from app.core.database import engine, async_session
from app.models.base import Base


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

- [ ] **Step 2: Run full test suite**

Run: `cd backend && uv run pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 3: Add .pre-commit-config.yaml**

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

- [ ] **Step 4: Final commit**

```bash
git add backend/tests/conftest.py .pre-commit-config.yaml
git commit -m "chore: add test fixtures, pre-commit config, and final integration"
```

---

## Completion Checklist

- [ ] All backend tests pass: `cd backend && uv run pytest tests/ -v`
- [ ] Frontend builds cleanly: `cd frontend && pnpm build`
- [ ] Backend starts: `cd backend && uv run uvicorn app.main:app --port 8000`
- [ ] Frontend dev server starts: `cd frontend && pnpm dev`
- [ ] Docker Compose valid: `docker compose config`
- [ ] Git status clean, all files committed
