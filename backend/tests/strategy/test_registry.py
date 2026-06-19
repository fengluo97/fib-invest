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
