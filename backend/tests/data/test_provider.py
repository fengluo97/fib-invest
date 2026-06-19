import pytest
from datetime import date
from app.data.provider import DataProvider, SymbolInfo


class FakeProvider(DataProvider):
    name = "fake"
    supports = ["daily"]

    async def get_bars(self, symbol, start, end, freq="daily"):
        return None

    async def get_tick(self, symbol, trade_date):
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
