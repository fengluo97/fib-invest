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
