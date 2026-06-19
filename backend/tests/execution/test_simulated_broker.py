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
