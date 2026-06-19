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
