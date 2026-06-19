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
