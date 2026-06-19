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
