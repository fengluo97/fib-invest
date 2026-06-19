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
        result = await session.get(Symbol, "000001.sz")
        assert result is not None
        assert result.name == "测试"


async def test_get_bars_cached(service):
    df = await service.get_bars("000001", date(2026, 6, 1), date(2026, 6, 5))
    assert df is not None
    assert len(df) == 5
    assert "close" in df.columns
